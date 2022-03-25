import ReactPy
from browser import document
from components import TodoList
import "style.css"

def App(props):
    return  <div>
                <TodoList/>
            </div>


element = <App/>
print(element)
ReactPy.render(element, document.getElementById("root"))


