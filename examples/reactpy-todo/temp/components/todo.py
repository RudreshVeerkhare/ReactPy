import ReactPy
from ReactPy import useState, useState
from ReactPy.utils import lmap
from .todoform import TodoForm

def Todo(props):
    todos = props["todos"]
    complete_todo = props["complete_todo"]
    remove_todo = props["remove_todo"]
    update_todo = props["update_todo"]

    edit, setEdit = useState({
        "id": None,
        "value": ""
    })

    def submit_update(value):
        update_todo(edit["id"], value)
        setEdit({
            "id": None,
            "value": ""
        })

    def on_edit_click(todo):
        setEdit({"id": todo["id"], "value": todo["text"]})
    
    if edit["id"]:
        return ReactPy.createElement(TodoForm, {'edit': edit, 'onSubmit': submit_update})
    
    def map_todo(index, todo):
        return  ReactPy.createElement("div", {'className': "todo-row complete" if todo["is_complete"] else "todo-row"}, ReactPy.createElement("div", {'key': todo["id"], 'onClick': lambda e: complete_todo(todo["id"])},  todo["text"]   , ), ReactPy.createElement("div", {'className': 'icons'}, ReactPy.createElement("i", {'className': 'fa-regular fa-trash-can delete-icon', 'onClick': lambda e: remove_todo(todo["id"])}, ), ReactPy.createElement("i", {'className': 'fa-regular fa-pen-to-square edit-icon', 'onClick': lambda e: on_edit_click(todo)}, ), ), )

    return ReactPy.createElement("div", {},  lmap( lambda x: map_todo(x[0], x[1]), enumerate(todos))   , )

