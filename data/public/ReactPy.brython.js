__BRYTHON__.use_VFS = true;
var scripts = {"$timestamp": 1642486935849, "ReactPy.react": [".py", "from browser import document,window\nfrom .utils import lmap,flatten,transform_attr\n\n\n__nextUnitOfWork=None\n__currentRoot=None\n__wipRoot=None\n__deletions=None\n__wipFiber=None\n__hookIndex=None\n\n\ndef createElement(type,props,*children):\n return {\n \"type\":type,\n \"props\":{\n **props,\n \"children\":lmap(\n lambda child:child\n if isinstance(child,dict)\n else _createTextElement(child),\n flatten(children),\n ),\n },\n }\n \n \ndef _createTextElement(text):\n return {\"type\":\"TEXT_ELEMENT\",\"props\":{\"textContent\":text,\"children\":[]}}\n \n \ndef _createDom(fiber):\n dom=(\n document.createTextNode(\"\")\n if fiber[\"type\"]==\"TEXT_ELEMENT\"\n else document.createElement(fiber[\"type\"])\n )\n \n _updateDom(dom,{},fiber[\"props\"])\n \n return dom\n \n \n \n \ndef isEvent(key):return key.startswith(\"on\")\ndef isProperty(key):return key !=\"children\"and not isEvent(key)\n\n\ndef isNew(prev,next):return lambda key:not (\nkey in prev and key in next and prev[key]==next[key]\n)\ndef isGone(prev,next):return lambda key:not (key in next)\n\n\ndef _updateDom(dom,prevProps,nextProps):\n\n lmap(\n lambda name:dom.unbind(name.lower()[2:],prevProps[name]),\n filter(\n lambda key:not (key in nextProps)or isNew(\n prevProps,nextProps)(key),\n filter(isEvent,prevProps.keys()),\n ),\n )\n \n \n def __reset(name):\n  dom.attrs[name]=\"\"\n  \n lmap(\n __reset,\n filter(isGone(prevProps,nextProps),\n filter(isProperty,prevProps.keys())),\n )\n \n \n def __set_prop(name):\n  if name ==\"style\":\n  \n   _transformDomStyle(dom,nextProps[\"style\"])\n  elif name ==\"className\":\n  \n   if \"className\"in prevProps:\n    dom.classList.remove(*prevProps[\"className\"].split())\n   dom.classList.add(*nextProps[\"className\"].split())\n  elif name ==\"textContent\":\n  \n   dom.textContent=nextProps[\"textContent\"]\n  else :\n   dom.attrs[name]=nextProps[name]\n   \n lmap(\n __set_prop,\n filter(isNew(prevProps,nextProps),filter(\n isProperty,nextProps.keys())),\n )\n \n \n \n lmap(\n lambda name:dom.bind(name.lower()[2:],nextProps[name]),\n filter(isNew(prevProps,nextProps),filter(isEvent,nextProps.keys())),\n )\n \n \ndef _transformDomStyle(dom,style):\n\n dom.style={transform_attr(k):v for k,v in style.items()}\n \n \ndef _commitRoot():\n global __wipRoot,__deletions,__currentRoot\n lmap(_commitWork,__deletions)\n _commitWork(\"child\"in __wipRoot and __wipRoot[\"child\"])\n __currentRoot=__wipRoot\n __wipRoot=None\n \n \ndef _commitWork(fiber):\n if not fiber:\n  return\n  \n domParentFiber=fiber[\"parent\"]\n while not domParentFiber[\"dom\"]:\n  domParentFiber=domParentFiber[\"parent\"]\n domParent=domParentFiber[\"dom\"]\n \n if fiber[\"effectTag\"]==\"PLACEMENT\":\n  if fiber[\"dom\"]:\n   domParent.appendChild(fiber[\"dom\"])\n  _runEffects(fiber)\n elif fiber[\"effectTag\"]==\"UPDATE\":\n  _cancelEffects(fiber)\n  if fiber[\"dom\"]:\n   _updateDom(fiber[\"dom\"],fiber[\"alternate\"]\n   [\"props\"],fiber[\"props\"])\n  _runEffects(fiber)\n elif fiber[\"effectTag\"]==\"DELETION\":\n  _cancelEffects(fiber)\n  _commitDeletion(fiber,domParent)\n  return\n  \n _commitWork(\"child\"in fiber and fiber[\"child\"])\n _commitWork(\"sibling\"in fiber and fiber[\"sibling\"])\n \n \ndef _commitDeletion(fiber,domParent):\n if fiber[\"dom\"]:\n  domParent.removeChild(fiber[\"dom\"])\n else :\n  _commitDeletion(fiber[\"child\"],domParent)\n  \n  \ndef _cancelEffects(fiber):\n if \"hooks\"in fiber and fiber[\"hooks\"]:\n  lmap(\n  lambda effectHook:effectHook[\"cancel\"](),\n  filter(\n  lambda hook:\"tag\"in hook\n  and hook[\"tag\"]==\"effect\"\n  and hook[\"cancel\"]!=None and callable(hook[\"cancel\"]),\n  fiber[\"hooks\"],\n  ),\n  )\n  \n  \ndef _runEffects(fiber):\n if \"hooks\"in fiber and fiber[\"hooks\"]:\n \n  def __apply_effect(effectHook):\n   if \"effect\"in effectHook and callable(effectHook[\"effect\"]):\n    effectHook[\"cancel\"]=effectHook[\"effect\"]()\n    \n  lmap(\n  __apply_effect,\n  filter(\n  lambda hook:\"tag\"in hook\n  and hook[\"tag\"]==\"effect\"\n  and hook[\"effect\"],\n  fiber[\"hooks\"],\n  ),\n  )\n  \n  \ndef render(element,container):\n global __wipRoot,__deletions,__nextUnitOfWork\n __wipRoot={\n \"dom\":container,\n \"props\":{\"children\":[element]},\n \"alternate\":__currentRoot,\n }\n \n __deletions=[]\n __nextUnitOfWork=__wipRoot\n \n \ndef _workLoop(deadline):\n global __nextUnitOfWork,__wipRoot\n \n shouldYield=False\n while __nextUnitOfWork and not shouldYield:\n  __nextUnitOfWork=_performUnitOfWork(__nextUnitOfWork)\n  shouldYield=deadline.timeRemaining()<1\n  \n  \n if not __nextUnitOfWork and __wipRoot:\n  _commitRoot()\n  \n  \n window.requestIdleCallback(_workLoop)\n \n \n \nwindow.requestIdleCallback(_workLoop)\n\n\ndef _performUnitOfWork(fiber):\n ''\n\n\n \n isFunctionalComponent=\"type\"in fiber and callable(fiber[\"type\"])\n \n if isFunctionalComponent:\n  _updateFunctionComponent(fiber)\n else :\n  _updateHostComponent(fiber)\n  \n if \"child\"in fiber and fiber[\"child\"]:\n  return fiber[\"child\"]\n  \n nextFiber=fiber\n while nextFiber:\n  if \"sibling\"in nextFiber and nextFiber[\"sibling\"]:\n   return nextFiber[\"sibling\"]\n   \n  nextFiber=\"parent\"in nextFiber and nextFiber[\"parent\"]\n  \n  \ndef _updateFunctionComponent(fiber):\n global __wipFiber,__hookIndex\n \n __wipFiber=fiber\n __hookIndex=0\n __wipFiber[\"hooks\"]=[]\n children=[fiber[\"type\"](fiber[\"props\"])]\n _reconcileChildren(fiber,children)\n \n \ndef useState(initial):\n global __wipFiber,__hookIndex,__currentRoot\n \n oldHook=(\n __wipFiber[\"alternate\"]\n and __wipFiber[\"alternate\"][\"hooks\"]\n and __wipFiber[\"alternate\"][\"hooks\"][__hookIndex]\n )\n \n hook={\"state\":oldHook[\"state\"]if oldHook else initial,\"queue\":[]}\n \n actions=oldHook[\"queue\"]if oldHook else []\n \n for action in actions:\n  hook[\"state\"]=action(hook[\"state\"])if callable(action)else action\n  \n def _setState(action):\n  global __wipRoot,__currentRoot,__nextUnitOfWork,__deletions\n  hook[\"queue\"].append(action)\n  __wipRoot={\n  \"dom\":__currentRoot[\"dom\"],\n  \"props\":__currentRoot[\"props\"],\n  \"alternate\":__currentRoot,\n  }\n  __nextUnitOfWork=__wipRoot\n  __deletions=[]\n  \n __wipFiber[\"hooks\"].append(hook)\n __hookIndex +=1\n return (hook[\"state\"],_setState)\n \n \ndef _hasChangedDeps(prevDeps,nextDeps):\n return (\n not prevDeps\n or not nextDeps\n or len(prevDeps)!=len(nextDeps)\n or any([prevDeps[i]!=nextDeps[i]for i in range(len(prevDeps))])\n )\n \n \ndef useEffect(effect,deps):\n global __hookIndex,__wipFiber\n oldHook=(\n __wipFiber[\"alternate\"]\n and __wipFiber[\"alternate\"][\"hooks\"]\n and __wipFiber[\"alternate\"][\"hooks\"][__hookIndex]\n )\n \n hasChanged=_hasChangedDeps(oldHook[\"deps\"]if oldHook else None ,deps)\n \n hook={\n \"tag\":\"effect\",\n \"effect\":effect if hasChanged else None ,\n \"cancel\":hasChanged and oldHook and oldHook[\"cancel\"],\n \"deps\":deps,\n }\n \n __wipFiber[\"hooks\"].append(hook)\n __hookIndex +=1\n \n \ndef _updateHostComponent(fiber):\n if not fiber[\"dom\"]:\n  fiber[\"dom\"]=_createDom(fiber)\n  \n _reconcileChildren(fiber,flatten(fiber[\"props\"][\"children\"]))\n \n \ndef _reconcileChildren(wipFiber,elements):\n global __deletions\n index=0\n oldFiber=(\n wipFiber[\"alternate\"]\n and \"child\"in wipFiber[\"alternate\"]\n and wipFiber[\"alternate\"][\"child\"]\n )\n prevSibling=None\n \n while index <len(elements)or oldFiber:\n  element=index <len(elements)and elements[index]\n  newFiber=None\n  \n  sameType=oldFiber and element and element[\"type\"]==oldFiber[\"type\"]\n  \n  if sameType:\n   newFiber={\n   \"type\":oldFiber[\"type\"],\n   \"props\":element[\"props\"],\n   \"dom\":oldFiber[\"dom\"],\n   \"parent\":wipFiber,\n   \"alternate\":oldFiber,\n   \"effectTag\":\"UPDATE\",\n   }\n   \n  if element and not sameType:\n  \n   newFiber={\n   \"type\":element[\"type\"],\n   \"props\":element[\"props\"],\n   \"dom\":None ,\n   \"parent\":wipFiber,\n   \"alternate\":None ,\n   \"effectTag\":\"PLACEMENT\",\n   }\n   \n  if oldFiber and not sameType:\n   oldFiber[\"effectTag\"]=\"DELETION\"\n   __deletions.append(oldFiber)\n   \n  if oldFiber:\n   oldFiber=\"sibling\"in oldFiber and oldFiber[\"sibling\"]\n   \n  if index ==0:\n   wipFiber[\"child\"]=newFiber\n  elif element:\n   prevSibling[\"sibling\"]=newFiber\n   \n  prevSibling=newFiber\n  index +=1\n", ["ReactPy.utils", "browser"]], "ReactPy.utils": [".py", "def lmap(func,iterable):\n ''\n\n\n \n return list(map(func,iterable))\n \n \ndef flatten(list_iterable):\n ''\n\n \n res=[]\n for item in list_iterable:\n  if isinstance(item,list):\n   res +=flatten(item)\n  else :\n   res.append(item)\n return res\n \n \ndef transform_attr(name):\n ''\n\n \n res=\"\"\n for ch in name:\n  if ch.isupper():\n   res +=\"-\"+ch.lower()\n  else :\n   res +=ch\n return res\n", []], "ReactPy": [".py", "from .react import createElement,render,useState,useEffect\n", ["ReactPy.react"], 1]}
__BRYTHON__.update_VFS(scripts)
