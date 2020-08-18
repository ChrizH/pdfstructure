from pdfminer.layout import LTTextContainer


class Style:
    def __init__(self, bold, italic, fontname, fontsize):
        self.bold = bold
        self.italic = italic
        self.font_name = fontname
        self.font_size = fontsize


class Element:
    def __init__(self, data: LTTextContainer, style: Style):
        self.data = data
        self.style = style
    
    def __str__(self):
        return self.data.get_text()


class NestedElement(Element):
    def __init__(self, element, style):
        super().__init__(element, style)
        self.content = []
        self.children = []
    
    def get_children_content(self):
        return " ".join(e.data.get_text() for e in self.children)
    
    def get_content(self):
        return " ".join(e.data.get_text() for e in self.content)
    
    def get_title(self):
        return self.data.get_text()
    
    # todo, implement flatten to get whole structure
    def traverse(self):
        # traverse through tree to extract structure as json // or find all titles etc
        pass
    
    def __str__(self):
        return "{}\n{}\n{}".format(self.get_title(), self.get_content(), self.get_children_content())
