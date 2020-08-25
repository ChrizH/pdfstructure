from collections import defaultdict
from typing import List

from pdfminer.layout import LTTextContainer

from pdfstructure.style_analyser import TextSize


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


class PdfElement:
    """
    """

    def __init__(self, text_container: LTTextContainer, style: Style, level=0, text=None):
        self._data = text_container
        self._text = text
        self.style = style
        self.level = None
        self.set_level(level)

    def set_level(self, level):
        self.level = level

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
        return PdfElement(data=None, style=Style.from_json(data["style"]), level=data["level"], text=data["text"])

    def __str__(self):
        return self.text


class ParentPdfElement:

    def __init__(self, element: PdfElement, level=0):
        self.heading = element
        self.content = []  # PdfElements
        self.children = []  # ParentPdfElements
        self.level = None
        self.set_level(level)

    def set_level(self, level):
        self.level = level

    # todo, implement tree.search(title)
    # todo, implement flatten to get whole structure
    def traverse(self):
        # traverse through tree to extract structure as json // or find all titles etc
        pass

    @classmethod
    def from_json(cls, data: dict):
        content = list(map(PdfElement.from_json, data.get("content")))
        children = list(map(ParentPdfElement.from_json, data.get("children")))
        heading = PdfElement.from_json(data.get("heading"))
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
    elements: List[ParentPdfElement]

    def __init__(self, elements: [ParentPdfElement]):
        self.metadata = defaultdict(str)
        self.elements = elements

    def update_metadata(self, key, value):
        self.metadata[key] = value

    @property
    def title(self):
        return self.metadata["title"]

    @classmethod
    def from_json(cls, data: dict):
        elements = list(map(ParentPdfElement.from_json, data["elements"]))
        pdf = cls(elements)
        pdf.metadata.update(data.get("metadata"))
        return pdf

    @staticmethod
    def __traverse__in_order__(element: ParentPdfElement):
        child: ParentPdfElement
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
