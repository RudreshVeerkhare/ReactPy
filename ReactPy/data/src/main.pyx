import ReactPy
from browser import document
from browser.timer import set_interval, clear_interval

def Timer(props):
    seconds, setSeconds = ReactPy.useState(0)


    def _tick():
        setSeconds(lambda s: s + 1)

    def __effect():
        __interval = set_interval(lambda: _tick(), 1000)
        return lambda: clear_interval(__interval)

    ReactPy.useEffect(__effect, [])

    return <div>Seconds : {seconds}</div>



def LiveInput(props):
    value, setValue = ReactPy.useState("")

    def __effect():
        print("Input Effect Called!")
        return lambda: print("Input Effect Cancelled!") 
    
    ReactPy.useEffect(__effect, [value])

    return  <div>
                <input value={value} onInput={lambda e: setValue(e.target.value)}/>
                <p>{value}</p>
            </div>

def Counter(props):
    count, setCount = ReactPy.useState(1)

    def __effect():
        print("Effect Called!")

    ReactPy.useEffect(__effect, [count])

    return  <h1 
                onClick={lambda e: setCount(lambda c: c + 1)} 
                className="hello-world" 
                style={{
                    "userSelect": "none",
                    "color": "red"
                }}
            >
               Count :{count}     
            </h1>


def App(props):
    visible, setVisible = ReactPy.useState(True)

    return  <div>
                <LiveInput/>
                <Timer/>
                <button onClick={lambda e: setVisible(True)}>Show</button>
                <button onClick={lambda e: setVisible(False)}>Hide</button>
                {<Counter/> if visible else <span/>}
            </div>


element = <App/>
print(element)
ReactPy.render(element, document.getElementById("root"))