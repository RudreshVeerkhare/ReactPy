import ReactPy

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