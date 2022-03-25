import ReactPy
from ReactPy import useState, useState
from ReactPy.utils import lmap
from time import time

def TodoForm(props):
    input, setInput = useState(props["edit"]["value"] if "edit" in props else "")

    def handle_change(e):
        setInput(e.target.value)

    def handle_submit(e):
        e.preventDefault()

        props["onSubmit"]({
            "id": time() * 1000,
            "text": input,
            "is_complete": False
        })

    
    return  ReactPy.createElement("form", {'onSubmit': handle_submit, 'className': 'todo-form'}, ReactPy.createElement("input", {'placeholder': 'Update your item', 'value': input, 'onChange': handle_change, 'name': 'text', 'className': 'todo-input edit' if "edit" in props else "todo-input"}), ReactPy.createElement("button", {'onClick': handle_submit, 'className': 'todo-button edit' if "edit" in props else "todo-button"},  'Update' if "edit" in props else "Add Todo"   , ), )

