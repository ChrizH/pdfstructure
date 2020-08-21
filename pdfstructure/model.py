from collections import defaultdict
from typing import List

from pdfminer.layout import LTTextContainer


class Style:
    def __init__(self, bold, italic, fontname, fontsize, mean_size):
        self.bold = bold
        self.italic = italic
        self.font_name = fontname
        self.font_size = fontsize
        self.mean_size = mean_size


class Element:
    def __init__(self, data: LTTextContainer, style: Style, level=0):
        self.data = data  # todo, persist text only --> get rid of pdf metadata
        self.style = style
        self.level = None
        self.set_level(level)

    def set_level(self, level):
        self.level = level

    def __str__(self):
        return self.data.get_text().strip()


class ParentElement:
    def __init__(self, element: Element, level=0):
        self.heading = element
        self.content = []
        self.children = []
        self.level = None
        self.set_level(level)

    def set_level(self, level):
        self.level = level

    # todo, implement tree.search(title)
    # todo, implement flatten to get whole structure
    def traverse(self):
        # traverse through tree to extract structure as json // or find all titles etc
        pass

    def __str__(self):
        return "{}\n{}".format(self.heading.data.get_text().strip(),
                               " ".join([str(e) for e in self.content]))


class StructuredPdfDocument:
    elements: List[ParentElement]
    
    def __init__(self, elements: [ParentElement]):
        self.metadata = defaultdict(str)
        self.elements = elements
    
    def update_metadata(self, key, value):
        self.metadata[key] = value
    
    @property
    def title(self):
        return self.metadata["title"]
