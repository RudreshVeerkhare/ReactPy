import ReactPy
from browser import document
import "index.css"
import "app.css"

def App(props):

    return  <div className="App">
                <header className="App-header">
                    <div className="frame">
                        <img src="react-rings-gradient.svg" className="App-logo" alt="logo" />
                    </div>
                        <p>
                            Edit <code>{" src/main.pyx "}</code> and save to reload.
                        </p>
                    <a
                        className="App-link"
                        href="https://github.com/RudreshVeerkhare/ReactPy"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Explore ReactPy
                    </a>
                </header>
            </div>


element = <App/>
print(element)
ReactPy.render(element, document.getElementById("root"))