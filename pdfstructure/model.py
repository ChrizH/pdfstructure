class Element():
    def __init__(self, data, style):
        self.data = data
        self.style = style


class NestedElement(Element):
    def __init__(self, element, style):
        super().__init__(element, style)
        self.content = []
        self.children = []
    
    def get_content(self):
        return " ".join(e.data.get_text() for e in self.content)
    
    def get_title(self):
        return self.data.get_text()
    
    # todo, implement flatten to get whole structure
    def traverse(self):
        # traverse through tree to extract structure as json // or find all titles etc
        pass
    
    def __str__(self):
        return "{}\n{}".format(self.get_title(), self.get_content())
