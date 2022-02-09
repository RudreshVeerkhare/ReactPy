# This is a parser responsible for converting .pyx to .py format
# Basically .pyx is .jsx, just with python
# Still this is a simple parser, this will just match based on defined grammer
# if matched then replace with appropriate syntax else it'll keep that code as
# it is without throwing any Syntax errors, those error will come in converted.py file.

# This parser is a modifed version of https://github.com/michaeljones/packed


from lib2to3.pgen2 import grammar
from operator import rshift
from string import whitespace
from pypeg2 import (
    List,
    Symbol,
    compose,
    ignore,
    maybe_some,
    optional,
    parse,
    attr,
    name,
)
import sys
import re


WHITESPACE = re.compile(r"\s+")
EXP1 = re.compile(r"(?m)(\W)(\s+)(\W)")
EXP2 = re.compile(r"(?m)[\r\n]+")  # to remove all new lines
CREATE_METHOD = "ReactPy.createElement"


def replace_whitespaces(text):

    whitespace_re = re.compile(r"\s")
    non_alpha_re = re.compile(r"\W")
    alpha_re = re.compile(r"\w")

    def _skip(_i, _text):
        while _i < len(_text) and whitespace_re.match(_text[_i]):
            _i += 1
        return _i

    if len(text) < 2:
        return text

    result = ""
    i = j = 0

    text_len = len(text)

    while j < text_len - 1:
        i = _skip(i, text)
        j = _skip(i + 1, text)

        result += text[i]
        # exclude data in strings
        if text[i] == '"' or text[i] == "'":
            # reset j
            j = i + 1
            # this will throw error if quotes are not properly used
            while text[i] != text[j]:
                result += text[j]
                j += 1

            # to avoid eating space after ending quote
            # ex. $$className="hello-world" name="something"$$ --> $$className="hello-world"name="something"$$
            result += text[j]
            _j = _skip(j + 1, text)
            if _j != j + 1 and not non_alpha_re.match(text[_j]):
                result += " "
            i = _j
            continue

        if j == i + 1 or (non_alpha_re.match(text[i]) and non_alpha_re.match(text[j])):
            pass
        else:
            result += " "
        i = j

    return result


# OLD REPLACE WHITESPACES --> Wanted to exclude string from parsing so wrote a new function
def _replace_whitespaces(text):
    """
    Replaces multiple whitespace or newlines or tabs (\s+) with only single
    whitespace if alpha-numeric character surround that group of whitespace
    Ex ->
    Before:: link = <a href = {lambda   x:  get_link()}   >
                        Click{"    "}Here
                    </a>
    After :: link =<a href ={lambda x: get_link()}> Click Here</a>
    """
    # Replace all whitespaces in PYX to single whitespace and then parse it
    t2 = None
    t = text
    _i = 0

    # Sometimes applying all three expressions once is not replacing all spaces
    # even though pattern is correct, therefore while loop will run till text
    # doesn't change.
    # Just for safety while loop will break after running 10 times.
    while t2 != t and _i < 10:
        t2 = t
        _i += 1
        t = re.sub(EXP1, r"\1\3", t)
        t = re.sub(EXP2, "", t)

    # Space was remaning at the start
    text = t.strip()

    return text


def string_difference_transform(text, t_prev, t_next):
    """
    As we are replacing all whitespaces with single, it's affecting parser
    to keep parser going properly we must transform resulting text again in
    indented form

    Parameters::
        text: original text
        t_prev: processed text before parsing
        t: text after parsing

    """

    rw = re.compile(r"\s")

    def _skip(_i, _text):
        while _i < len(_text) and rw.match(_text[_i]):
            _i += 1
        return _i

    # it's basically a string matching while ignoring whitespaces and newlines
    t_start = t_prev[: len(t_prev) - len(t_next)]
    i = j = 0

    while i < len(t_start) and j < len(text):
        i = _skip(i, t_start)
        j = _skip(j, text)

        if t_start[i] == text[j]:
            i += 1
            j += 1

    return text[j:]


class SingleQuoteString(str):
    grammar = "'", re.compile(r"[^']*"), "'"


class DoubleQuoteString(str):
    grammar = '"', re.compile(r"[^\"]*"), '"'


String = [SingleQuoteString, DoubleQuoteString]


class EscapeString:
    """
    it's intermidiate form of inline code that to be stored so that
    it shouldn't be interpreted as string
    """

    def __init__(self, content):
        self.content = content

    def __repr__(self) -> str:
        return f"{self.content.strip()}"


class DictEntry:
    """This is for each key-value entry in a dictionary"""

    grammar = (
        attr("key", String),
        ":",
        attr(
            "value",
            [String, re.compile(r"[^,}]+")],
        ),
        optional(","),
    )


class Dictionary(List):
    """
    Grammer to recognize Dictionary
    """

    grammar = "{", maybe_some(DictEntry), "}"

    def to_dict(self):
        res = dict()
        for entry in self:
            if isinstance(entry.value, SingleQuoteString) or isinstance(
                entry.value, DoubleQuoteString
            ):
                res[entry.key] = entry.value
            else:
                res[entry.key] = EscapeString(entry.value)
        return res


class InlineCode:
    """
    To represent Inline code in PYX syntax
    """

    grammar = "{", attr("code", [Dictionary, re.compile(r"[^}]*")]), "}"

    def to_code(self):
        if isinstance(self.code, Dictionary):
            return self.code.to_dict()
        if isinstance(self.code, TagChildren):
            return self.code.compose()
        return EscapeString(self.code)

    def compose(self):
        return f"{self.to_code()}"


class Attribute:
    """Matches attribute passed to tag in format key="value" or key={value} or key={{key: val, ...}}"""

    grammar = (
        name(),
        ignore(optional(WHITESPACE)),
        "=",
        attr("value", [String, InlineCode]),
    )

    def to_dict(self):
        res = dict()
        key = self.name.name

        if isinstance(self.value, str):
            res[key] = self.value
            return res

        if isinstance(self.value, InlineCode):
            res[key] = self.value.to_code()
            return res


class Attributes(List):
    """Matches zero or more Attribute"""

    grammar = optional(
        ignore(WHITESPACE), Attribute, maybe_some(ignore(WHITESPACE), Attribute)
    )

    def to_dict(self):
        res = dict()
        for attribute in self:
            res.update(attribute.to_dict())
        return res


class Text(object):
    """Matches text between tags and/or inline code sections."""

    grammar = attr("value", re.compile(r"[^<{]+"))

    def compose(self):
        return f'"{self.value.strip()}"'


class PairedTag:
    """
    This are tags which have children elements
    Ex. -> <h1>Hello, World</h1>
    """

    @staticmethod
    def parse(parser, text, pos):

        # Replace all whitespaces in PYX to single whitespace and then parse it
        text_org = text
        text = replace_whitespaces(text)
        t_prev = text
        result = PairedTag()
        try:
            text, _ = parser.parse(text, "<")
            text, tag = parser.parse(text, Symbol)
            result.tag = tag
            text, attributes = parser.parse(text, Attributes)
            result.attributes = attributes
            text, _ = parser.parse(text, ">")
            text, children = parser.parse(text, TagChildren)
            result.children = children
            text, _ = parser.parse(text, optional(WHITESPACE))
            text, _ = parser.parse(text, "</")
            text, _ = parser.parse(text, result.tag)
            text, _ = parser.parse(text, ">")
        except SyntaxError as e:
            return text_org, e

        # we have replaced whitespaces, but parser is not aware so we have to transform it back
        text = string_difference_transform(text_org, t_prev, text)

        return text, result

    def compose(self):
        tag = f'"{self.tag}"'
        if self.tag[0].isupper():
            tag = self.tag
        return f"{CREATE_METHOD}({tag}, {self.attributes.to_dict()}, {self.children.compose()})"


class SelfClosingTag:
    """
    This tags are self closing.
    Ex. -> <Counter />
    """

    grammar = (
        "<",
        attr("tag", Symbol),
        attr("attributes", Attributes),
        # ignore(WHITESPACE),
        "/>",
    )

    @staticmethod
    def parse(parser, text, pos):
        # Replace all whitespaces in PYX to single whitespace and then parse it
        t = replace_whitespaces(text)
        t_prev = t
        t, r = parser._parse(t, SelfClosingTag.grammar, pos)

        if type(r) == SyntaxError:
            return text, r

        # we have replaced whitespaces, but parser is not aware so we have to transform it back
        text = string_difference_transform(text, t_prev, t)

        obj = SelfClosingTag()
        for _r in r:
            setattr(obj, _r.name, _r.thing)
        return text, obj

    def compose(self):
        # Component name has to be first char capital
        tag = f'"{self.tag}"'
        if self.tag[0].isupper():
            tag = self.tag

        return f"{CREATE_METHOD}({tag}, {self.attributes.to_dict()})"


class TagChildrenInlineCode:
    """
    To represent Inline code in PYX syntax
    """

    grammar = (
        "{",
        attr("pre_tag", optional([SelfClosingTag, PairedTag])),
        attr("code_1", [Dictionary, re.compile(r"[^<}]*")]),
        attr("mid_tag", optional([SelfClosingTag, PairedTag])),
        attr("code_2", [Dictionary, re.compile(r"[^<}]*")]),
        attr("end_tag", optional([SelfClosingTag, PairedTag])),
        "}",
    )

    def compose(self):
        pre_tag = self.pre_tag.compose().strip() if self.pre_tag else ""
        mid_tag = self.mid_tag.compose().strip() if self.mid_tag else ""
        end_tag = self.end_tag.compose().strip() if self.end_tag else ""
        return f"{pre_tag} {self.code_1.to_dict() if isinstance(self.code_1, Dictionary) else self.code_1} {mid_tag} {self.code_2.to_dict() if isinstance(self.code_2, Dictionary) else self.code_2} {end_tag}"


class TagChildren(List):
    """Matches valid tag children which can be other tags, plain text, {values} or a mix of all
    three."""

    grammar = maybe_some([SelfClosingTag, PairedTag] + [TagChildrenInlineCode, Text])

    def compose(self):
        text = []
        for entry in self:
            # Skip pure whitespace
            text.append(entry.compose())
            text.append(", ")

        return "".join(text)


class CSSFilenameSingleQuote(str):
    grammar = "'", re.compile("[^']*\.css"), "'"


class CSSFilenameDoubleQuote(str):
    grammar = '"', re.compile('[^"]*\.css'), '"'


CSSFilename = [CSSFilenameSingleQuote, CSSFilenameDoubleQuote]


class CSSImport:
    """
    This pattern is to detect css file import
    Ex. import '../assets/style.css'
    """

    grammar = (
        "import",
        ignore(WHITESPACE),
        attr("filename", CSSFilename),
    )

    def get_filename(self):
        return self.filename


class PYXBlock(List):
    """
    This is the actual PYX code
    """

    grammar = attr("line_start", re.compile(r"[^#<\n]+")), [SelfClosingTag, PairedTag]

    @staticmethod
    def parse(parser, text, pos):
        # Replace all whitespaces in PYX to single whitespace and then parse it
        t = text  # replace_whitespaces(text)
        t, r = parser._parse(t, PYXBlock.grammar, pos)

        if type(r) == SyntaxError:
            return t, r

        obj = PYXBlock(r[1:])
        setattr(obj, r[0].name, r[0].thing)
        return t, obj

    def compose(self):
        text = [self.line_start]
        for entry in self:
            if isinstance(entry, str):
                text.append(entry)
            else:
                text.append(entry.compose())

        return "".join(text)


class NonPYXLine:
    grammar = attr("content", re.compile(".*")), "\n"

    def compose(self):
        return "%s\n" % self.content


class CodeBlock(List):
    grammar = maybe_some([PYXBlock, CSSImport, NonPYXLine, re.compile(r".+")])
    css_imports = list()

    def compose(self, parser, attr_of=None):
        text = []
        for entry in self:
            if isinstance(entry, str):
                text.append(entry)
            elif isinstance(entry, CSSImport):
                self.css_imports.append(entry.get_filename())
            else:
                text.append(entry.compose())

        return "".join(text)


def transform(input_code):
    """
    Parses given string input and also extracts imported .css files
    """
    result = parse(input_code, CodeBlock, whitespace=None)
    return compose(result), CodeBlock.css_imports


if __name__ == "__main__":
    filename = sys.argv[1]
    with open(filename, "r") as f:
        input_code = f.read()
        print(*transform(input_code))
