import ReactPy
from browser import document

createElement = ReactPy.createElement

def Counter(props):
    count, setCount = ReactPy.useState(1)

    def __effect():
        print("Effect Called!")
        return lambda: print("Effect Cancelled!")

    ReactPy.useEffect(__effect, [count])

    return  <h1 
                onClick={lambda e: setCount(lambda c: c + 1)} 
                className="hello-world" 
                style={{
                    "userSelect": "none",
                    "color": "red"
                }}
            >
               Count {count}     
            </h1>


def App(props):
    visible, setVisible = ReactPy.useState(True)

    return  <div>
                <button onClick={lambda e: setVisible(True)}>Show</button>
                <button onClick={lambda e: setVisible(False)}>Hide</button>
                {<Counter/> if visible else None}
            </div>


element = <App/>
print(element)
ReactPy.render(element, document.getElementById("root"))