from bs4 import BeautifulSoup as BS
import sys


def link_css_file(html_content, css_filepaths):
    soup = BS(html_content, "html.parser")

    # create a link tag and append them to head
    for css_filepath in css_filepaths:
        tag = soup.new_tag("link", rel="stylesheet", href=css_filepath)
        soup.head.append(tag)

    return soup.prettify()


def add_brython_modules(html_content, filename):
    soup = BS(html_content, "html.parser")

    brython_tag = soup.head.find_all("script", attrs={"src": "brython.js"})[0]
    brython_tag.insert_after(
        soup.new_tag("script", src=filename, type="text/javascript")
    )

    return soup.prettify()


if __name__ == "__main__":
    filename = sys.argv[1]
    with open(filename, "r") as f:
        input_code = f.read()
        soup = BS(input_code)
        print("hello")
