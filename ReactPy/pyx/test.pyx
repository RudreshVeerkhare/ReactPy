import ReactPy
from ReactPy import useState, useState
from ReactPy.utils import lmap
from time import time

def TodoForm(props):
    input, setInput = useState(props["edit"]["value"] if props["edit"] else "")

    def handle_change(e):
        setInput(e.target.value)

    def handle_submit(e):
        e.preventDefault()

        props["onSubmit"]({
            "id": time() * 1000,
            "text": input
        })

        setInput("")
    
    return  <form onSubmit={handle_submit} className="todo-form">
                <input
                    placeholder='Update your item'
                    value={input}
                    onChange={handle_change}
                    name='text'
                    className={'todo-input edit' if props["edit"] else "todo-input"}
                />
                <button onClick={handleSubmit} className={'todo-button edit' if props["edit"] else "todo-button"}>
                    {"Update" if props["edit"] else "Add Todo"}
                </button>
            </form>

