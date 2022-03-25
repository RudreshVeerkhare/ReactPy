import ReactPy
from ReactPy import useState, useEffect
from ReactPy.utils import lmap
from .todoform import TodoForm
from .todo import Todo

def TodoList(props):
    todos, setTodos = useState([])

    def add_todo(todo):
        if not todo["text"].strip():
            return
        
        new_todos = [*todos, todo]

        setTodos(new_todos)
    
    def update_todo(todo_id, new_value):
        if not new_value["text"].strip():
            return

        setTodos(lambda prev: lmap(
            lambda item: new_value if item["id"] == todo_id else item
        , todos))
    
    def remove_todo(id):
        removed_todos = list(filter(
            lambda todo: todo["id"] != id, todos
        ))

        setTodos(removed_todos)

    def complete_todo(id):
        def __update(todo):
            print(todo)
            if todo["id"] == id:
                todo["is_complete"] = not todo["is_complete"]
            return todo

        updated_todos = lmap(
            __update, todos
        )

        setTodos(updated_todos)

    return  ReactPy.createElement("div", {'className': 'todo-app'}, ReactPy.createElement("h1", {}, "What\'s the Plan for Today?", ), ReactPy.createElement(TodoForm, {'onSubmit': add_todo}), ReactPy.createElement(Todo, {'todos': todos, 'complete_todo': complete_todo, 'remove_todo': remove_todo, 'update_todo': update_todo}), )

