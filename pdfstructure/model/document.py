from collections import defaultdict
from typing import List

from pdfminer.layout import LTTextContainer

from pdfstructure.analysis.styledistribution import StyleDistribution
from pdfstructure.model.style import Style


class TextElement:
    """
    Represents one single TextContainer like a line of words.
    """

    def __init__(self, text_container: LTTextContainer, style: Style, text=None, page=None):
        self._data = text_container
        self._text = text
        self.style = style
        self.page = page

    @property
    def text(self):
        if not self._data:
            return self._text
        else:
            return self._data.get_text().strip()

    @classmethod
    def from_json(cls, data: dict):
        """

        @param data:
        @return:
        """
        if data:
            return TextElement(text_container=None, style=Style.from_json(data["style"]),
                               text=data["text"])
        return None

    def __str__(self):
        return self.text


class Section:
    """
    Represents a section with title, contents and children
    """

    def __init__(self, element: TextElement, level=0):
        self.heading = element
        self.content = []  # PdfElements
        self.children = []  # ParentPdfElements
        self.level = None
        self.set_level(level)

    def set_level(self, level):
        self.level = level

    def append_content(self, paragraph: TextElement):
        self.content.append(paragraph)

    def append_children(self, section):
        self.children.append(section)

    @classmethod
    def from_json(cls, data: dict):
        content = list(map(TextElement.from_json, data.get("content")))
        children = list(map(Section.from_json, data.get("children")))
        heading = TextElement.from_json(data.get("heading"))
        element = cls(heading, data["level"])
        element.children = children
        element.content = content
        return element

    @property
    def heading_text(self):
        if self.heading and self.heading.text:
            return self.heading.text
        else:
            return ""

    def __str__(self):
        return "{}\n{}".format(self.heading.text,
                               " ".join([str(e) for e in self.content]))


class DanglingTextSection(Section):
    def __init__(self):
        super().__init__(element=None)

    def __str__(self):
        return "{}".format(" ".join([str(e) for e in self.content]))


class StructuredPdfDocument:
    """
    PDF document containing its natural order hierarchy, as detected by the HierarchyParser.
    """
    elements: List[Section]

    def __init__(self, elements: [Section], style_info=None):
        self.metadata = defaultdict(str)
        self.elements = elements
        self.metadata["style_distribution"] = style_info

    def update_metadata(self, key, value):
        self.metadata[key] = value

    @property
    def title(self):
        return self.metadata.get("title")

    @property
    def style_distribution(self) -> StyleDistribution:
        return self.metadata.get("style_distribution")

    @classmethod
    def from_json(cls, data: dict):
        elements = list(map(Section.from_json, data["elements"]))
        pdf = cls(elements)
        pdf.metadata.update(data.get("metadata"))
        return pdf
