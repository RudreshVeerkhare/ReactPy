import ReactPy
from browser import document
from components import TodoList


def App(props):
    return  ReactPy.createElement("div", {}, ReactPy.createElement(TodoList, {}), )


element = ReactPy.createElement(App, {})
print(element)
ReactPy.render(element, document.getElementById("root"))


