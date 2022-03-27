from browser import document, window
from .utils import lmap, flatten, transform_attr

# Global Vars
__nextUnitOfWork = list()
__currentRoot = None
__wipRoot = None
__deletions = None
__wipFiber = None
__hookIndex = None


def createElement(type, props, *children):
    return {
        "type": type,
        "key": props.pop("key", None),
        "props": {
            **props,
            "children": lmap(
                lambda child: child
                if isinstance(child, dict)
                else _createTextElement(child),
                flatten(children),
            ),
        },
    }


def _createTextElement(text):
    return {
        "type": "TEXT_ELEMENT",
        "key": None,
        "props": {"textContent": text, "children": []},
    }


def _createDom(fiber):
    dom = (
        document.createTextNode("")
        if fiber["type"] == "TEXT_ELEMENT"
        else document.createElement(fiber["type"])
    )

    _updateDom(dom, {}, fiber["props"])

    return dom


# checks
def isEvent(key):
    return key.startswith("on")


def isProperty(key):
    return key != "children" and not isEvent(key)


def isNew(prev, next):
    return lambda key: not (key in prev and key in next and prev[key] == next[key])


def isGone(prev, next):
    return lambda key: not (key in next)


def _updateDom(dom, prevProps, nextProps):
    # Remove Old or Changed Event Listener
    lmap(
        lambda name: dom.unbind(name.lower()[2:]),
        filter(
            lambda key: not (key in nextProps) or isNew(prevProps, nextProps)(key),
            filter(isEvent, prevProps.keys()),
        ),
    )

    # Remove Old Props
    def __reset(name):
        dom.attrs[name] = ""

    lmap(
        __reset,
        filter(isGone(prevProps, nextProps), filter(isProperty, prevProps.keys())),
    )

    # Set New or Changed props
    def __set_prop(name):
        if name == "style":
            # update style
            _transformDomStyle(dom, nextProps["style"])
        elif name == "className":
            # update class name
            if "className" in prevProps:
                dom.classList.remove(*prevProps["className"].split())
            dom.classList.add(*nextProps["className"].split())
        elif name == "textContent":

            dom.textContent = nextProps["textContent"]
        else:
            dom.attrs[name] = nextProps[name]

    lmap(
        __set_prop,
        filter(isNew(prevProps, nextProps), filter(isProperty, nextProps.keys())),
    )

    # Add event listeners

    lmap(
        lambda name: dom.bind(name.lower()[2:], nextProps[name]),
        filter(isNew(prevProps, nextProps), filter(isEvent, nextProps.keys())),
    )


def _transformDomStyle(dom, style):

    dom.style = {transform_attr(k): v for k, v in style.items()}


def _commitRoot():
    global __wipRoot, __deletions, __currentRoot
    lmap(_commitWork, __deletions)
    _commitWork("child" in __wipRoot and __wipRoot["child"])
    __currentRoot = __wipRoot
    __wipRoot = None


def _commitWork(fiber):
    if not fiber:
        return

    domParentFiber = fiber["parent"]
    while not domParentFiber["dom"]:
        domParentFiber = domParentFiber["parent"]
    domParent = domParentFiber["dom"]

    if fiber["effectTag"] == "PLACEMENT":
        if fiber["dom"]:
            domParent.appendChild(fiber["dom"])
        _runEffects(fiber)
    elif fiber["effectTag"] == "UPDATE" or (
        fiber["alternate"] != None and fiber["effectTag"] == "RE_ARRANGE"
    ):
        _cancelEffects(fiber)
        if fiber["dom"]:
            _updateDom(fiber["dom"], fiber["alternate"]["props"], fiber["props"])
        _runEffects(fiber)
    elif fiber["effectTag"] == "DELETION":
        _cancelEffects(fiber)
        _commitDeletion(fiber, domParent)
        return

    _commitWork("child" in fiber and fiber["child"])
    _commitWork("sibling" in fiber and fiber["sibling"])

    if fiber["effectTag"] == "RE_ARRANGE":
        _rearrangeChildren(fiber)


def _rearrangeChildren(fiber):
    parentDom = fiber["dom"]
    child = fiber["child"]  # temp reference to iterate
    while child:
        domNode = child
        while not domNode["dom"]:
            domNode = child["child"]

        parentDom.appendChild(domNode["dom"])
        child = "sibling" in child and child["sibling"]


def _commitDeletion(fiber, domParent):
    if fiber["dom"]:
        domParent.removeChild(fiber["dom"])
    else:
        _commitDeletion(fiber["child"], domParent)


def _cancelEffects(fiber):
    if "hooks" in fiber and fiber["hooks"]:
        lmap(
            lambda effectHook: effectHook["cancel"](),
            filter(
                lambda hook: "tag" in hook
                and hook["tag"] == "effect"
                and hook["effect"] != None
                and callable(hook["cancel"]),
                fiber["hooks"],
            ),
        )


def _runEffects(fiber):
    if "hooks" in fiber and fiber["hooks"]:

        def __apply_effect(effectHook):
            if "effect" in effectHook and callable(effectHook["effect"]):
                effectHook["cancel"] = effectHook["effect"]()

        lmap(
            __apply_effect,
            filter(
                lambda hook: "tag" in hook
                and hook["tag"] == "effect"
                and hook["effect"],
                fiber["hooks"],
            ),
        )


def render(element, container):
    global __wipRoot, __deletions, __nextUnitOfWork
    __wipRoot = {
        "dom": container,
        "props": {"children": [element]},
        "alternate": __currentRoot,
    }

    __deletions = []
    __nextUnitOfWork.append(__wipRoot)


def _workLoop(deadline):
    global __nextUnitOfWork, __wipRoot

    shouldYield = False
    forceCommit = False
    while not forceCommit and __nextUnitOfWork and not shouldYield:
        _currFiber = __nextUnitOfWork[0]
        # setState Calls
        if callable(_currFiber):
            if __wipRoot:
                # print("Force Commit!")
                forceCommit = True
                continue
            __nextUnitOfWork[0] = __nextUnitOfWork[0]()

        _nextFiber = _performUnitOfWork(__nextUnitOfWork.pop(0))
        if _nextFiber:
            __nextUnitOfWork.insert(0, _nextFiber)
        shouldYield = deadline.timeRemaining() < 1

    # commit after whole work tree is complete or when forceCommit flag is True
    if forceCommit or (not __nextUnitOfWork and __wipRoot):
        _commitRoot()
        if forceCommit:

            __nextUnitOfWork[0] = __nextUnitOfWork[0]()
            forceCommit = False

    # continue loop
    window.requestIdleCallback(_workLoop)


# start loop
window.requestIdleCallback(_workLoop)


def _performUnitOfWork(fiber):
    """
    Creates a fiber tree in top-down manner
    It starts with root node then goes to child, then to sibling
    """

    isFunctionalComponent = "type" in fiber and callable(fiber["type"])

    if isFunctionalComponent:
        _updateFunctionComponent(fiber)
    else:
        _updateHostComponent(fiber)

    if "child" in fiber and fiber["child"]:
        return fiber["child"]

    nextFiber = fiber
    while nextFiber:
        if "sibling" in nextFiber and nextFiber["sibling"]:
            return nextFiber["sibling"]

        nextFiber = "parent" in nextFiber and nextFiber["parent"]


def _updateFunctionComponent(fiber):
    global __wipFiber, __hookIndex

    __wipFiber = fiber
    __hookIndex = 0
    __wipFiber["hooks"] = []
    children = [fiber["type"](fiber["props"])]
    _reconcileChildren(fiber, children)


def useState(initial):
    global __wipFiber, __hookIndex, __currentRoot

    oldHook = (
        __wipFiber["alternate"]
        and __wipFiber["alternate"]["hooks"]
        and __wipFiber["alternate"]["hooks"][__hookIndex]
    )

    hook = {
        "state": oldHook["state"] if oldHook else initial,
        "queue": oldHook["queue"] if oldHook else [],
    }
    actions = hook["queue"]  # if oldHook else []

    for action in actions:
        hook["state"] = action(hook["state"]) if callable(action) else action

    hook["queue"].clear()

    def _setState(action):
        global __wipRoot, __currentRoot, __nextUnitOfWork, __deletions
        hook["queue"].append(action)
        __wipRoot = {
            "dom": __currentRoot["dom"],
            "props": __currentRoot["props"],
            "alternate": __currentRoot,
        }
        __deletions = []
        return __wipRoot

    def _setStateWrapper(action):
        __nextUnitOfWork.append(lambda: _setState(action))

    __wipFiber["hooks"].append(hook)
    __hookIndex += 1
    return (hook["state"], _setStateWrapper)


def _hasChangedDeps(prevDeps, nextDeps):
    return (
        prevDeps == None
        or nextDeps == None
        or len(prevDeps) != len(nextDeps)
        or any([prevDeps[i] != nextDeps[i] for i in range(len(prevDeps))])
    )


def useEffect(effect, deps):
    global __hookIndex, __wipFiber
    oldHook = (
        __wipFiber["alternate"]
        and __wipFiber["alternate"]["hooks"]
        and __wipFiber["alternate"]["hooks"][__hookIndex]
    )

    hasChanged = _hasChangedDeps(oldHook["deps"] if oldHook else None, deps)

    hook = {
        "tag": "effect",
        "effect": effect if hasChanged else None,
        "cancel": oldHook and oldHook["cancel"],
        "deps": deps,
    }

    __wipFiber["hooks"].append(hook)
    __hookIndex += 1


def _updateHostComponent(fiber):
    if not fiber["dom"]:
        fiber["dom"] = _createDom(fiber)

    _reconcileChildren(fiber, flatten(fiber["props"]["children"]))


def _reconcileChildren(wipFiber, elements):
    global __deletions

    oldFiber = (
        wipFiber["alternate"]
        and "child" in wipFiber["alternate"]
        and wipFiber["alternate"]["child"]
    )

    # All elements might not have "key" so first I'll compair
    # elements with keys and then other without keys.

    oldElementsHashMap = dict()  # create a hashmap with "key" as key
    tempOldFiber = oldFiber  # temp reference to iterate
    while tempOldFiber:
        if tempOldFiber["key"] != None:
            oldElementsHashMap[tempOldFiber["key"]] = tempOldFiber

        tempOldFiber = "sibling" in tempOldFiber and tempOldFiber["sibling"]

    index = 0
    prevSibling = None
    domRearrage = False

    while index < len(elements) or oldFiber:
        element = index < len(elements) and elements[index]
        newFiber = None

        hasOldKey = element and element["key"] in oldElementsHashMap
        sameElem = (
            oldFiber
            and element
            and element["type"] == oldFiber["type"]
            and element["key"] == oldFiber["key"]
        )

        if sameElem or hasOldKey:
            if not sameElem:
                domRearrage = True
            _oldFiberFromKey = oldElementsHashMap.pop(element["key"], oldFiber)
            newFiber = {
                "type": _oldFiberFromKey["type"],
                "key": _oldFiberFromKey["key"],
                "props": element["props"],
                "dom": _oldFiberFromKey["dom"],
                "parent": wipFiber,
                "alternate": _oldFiberFromKey,
                "effectTag": "UPDATE",
            }

        # mark for delete if no same level match and has no key on oldFiber
        if not sameElem and oldFiber and oldFiber["key"] == None:
            oldFiber["effectTag"] = "DELETION"
            __deletions.append(oldFiber)

        if element and not (sameElem or hasOldKey):
            # placement has to trigger rearrangement
            # cause we are just appending new child
            # when PLACEMENT tag is assigned, and
            # not always it's supposed to be appended
            # so doing this would require rearrangement.
            # and this is not required for first render
            # only in updates
            if element["key"] != None and oldFiber:
                domRearrage = True
            newFiber = {
                "type": element["type"],
                "key": element["key"],
                "props": element["props"],
                "dom": None,
                "parent": wipFiber,
                "alternate": None,
                "effectTag": "PLACEMENT",
            }

        if oldFiber:
            oldFiber = "sibling" in oldFiber and oldFiber["sibling"]

        if index == 0:
            wipFiber["child"] = newFiber
        elif element:
            prevSibling["sibling"] = newFiber

        prevSibling = newFiber
        index += 1

    # rearrange dom
    if domRearrage:
        wipFiber["effectTag"] = "RE_ARRANGE"

    # all oldFibers left in oldElementsHashMap are to be deleted
    for _oldFiber in oldElementsHashMap.values():
        _oldFiber["effectTag"] = "DELETION"
        __deletions.append(_oldFiber)


def p(item):
    """
    For Debug purposes
    """
    if not item:
        return item
    return {
        "type": "type" in item and item["type"],
        "key": "key" in item and item["key"],
        "props": "props" in item and item["props"],
        "dom": "dom" in item and item["dom"] and True,
    }
