from collections import defaultdict
from enum import IntEnum, auto
from typing import List

from pdfminer.layout import LTTextContainer


class Style:
    def __init__(self, bold, italic, font_name, mapped_font_size, mean_size):
        self.bold = bold
        self.italic = italic
        self.font_name = font_name
        self.mapped_font_size = mapped_font_size
        self.mean_size = mean_size

    @classmethod
    def from_json(cls, data: dict):
        mapped_size = TextSize[data["mapped_font_size"]]
        data["mapped_font_size"] = mapped_size
        return cls(**data)


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
        return TextElement(text_container=None, style=Style.from_json(data["style"]),
                           text=data["text"])

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

    @classmethod
    def from_json(cls, data: dict):
        content = list(map(TextElement.from_json, data.get("content")))
        children = list(map(Section.from_json, data.get("children")))
        heading = TextElement.from_json(data.get("heading"))
        element = cls(heading, data["level"])
        element.children = children
        element.content = content
        return element

    def __str__(self):
        return "{}\n{}".format(self.heading.text,
                               " ".join([str(e) for e in self.content]))


class StructuredPdfDocument:
    """
    PDF document containing its natural order hierarchy, as detected by the HierarchyParser.
    """
    elements: List[Section]

    def __init__(self, elements: [Section], style_info=None):
        self.metadata = defaultdict(str)
        self.elements = elements
        self.metadata["style_info"] = style_info

    def update_metadata(self, key, value):
        self.metadata[key] = value

    @property
    def title(self):
        return self.metadata["title"]

    @classmethod
    def from_json(cls, data: dict):
        elements = list(map(Section.from_json, data["elements"]))
        pdf = cls(elements)
        pdf.metadata.update(data.get("metadata"))
        return pdf

    @staticmethod
    def __traverse__in_order__(element: Section):
        child: Section
        for child in element.children:
            yield child
            yield from StructuredPdfDocument.__traverse__in_order__(child)

    def traverse(self):
        """
        Traverse through hierarchy and yield element by element in-order.
        @return:
        """
        for element in self.elements:
            yield element
            yield from self.__traverse__in_order__(element)


class TextSize(IntEnum):
    xsmall = auto()
    small = auto()
    middle = auto()
    large = auto()
    xlarge = auto()

    @classmethod
    def from_range(cls, borders: tuple, value: int):
        if value < borders[0]:
            return cls.xsmall
        elif value >= borders[0] and value < borders[1]:
            return cls.small
        elif value >= borders[1] and value < borders[2]:
            return cls.middle
        elif value >= borders[2] and value < borders[3]:
            return cls.large
        elif value >= borders[3]:
            return cls.xlarge
