from pdfminer.layout import LTTextContainer


class Style:
    def __init__(self, bold, italic, fontname, fontsize):
        self.bold = bold
        self.italic = italic
        self.font_name = fontname
        self.font_size = fontsize


class Element:
    def __init__(self, data: LTTextContainer, style: Style, level=0):
        self.data = data
        self.style = style
        self.level = None
        self.prefix = None
        self.set_level(level)

    def set_level(self, level):
        self.level = level
        self.prefix = "".join(["\t" for i in range(self.level)])

    def __str__(self):
        return self.prefix + self.data.get_text().strip()


class ParentElement:
    def __init__(self, element: Element, level=0):
        self.heading = element
        self.content = []
        self.children = []
        self.prefix = None
        self.level = None
        self.set_level(level)
    
    def set_level(self, level):
        self.level = level
        self.prefix = "".join(["\t" for i in range(self.level)])

    def get_children_content(self):
        return " ".join(str(e) for e in self.children)

    def get_content(self):
        return "\n".join(str(e) for e in self.content)

    def get_title(self):
        return "{}[{}]".format(self.prefix,
                               self.heading.data.get_text().strip().replace("\n", "{}\n".format(self.prefix)))

    # todo, implement tree.search(title)
    # todo, implement flatten to get whole structure
    def traverse(self):
        # traverse through tree to extract structure as json // or find all titles etc
        pass

    def __str__(self):
        """ todo, define printer interface, pretty string // json"""
        return "{}\n{}\n{}".format(self.get_title(),
                                   self.get_content(),
                                   self.get_children_content())
