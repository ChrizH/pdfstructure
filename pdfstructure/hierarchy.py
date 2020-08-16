from collections import Counter

from pdfstructure.style_analyser import TextSize
from pdfstructure.title_finder import ProcessUnit


def header_detector(data):
    stats = Counter()
    terms = data["obj"]
    style = data["style"]
    # data tuple per line, element from pdfminer, annotated style info for whole line
    # todo, compute ratios over whole line // or paragraph :O
    if style.bold or style.italic or style.font_size > TextSize.middle:
        return True
    else:
        return False


class Element():
    def __init__(self, element, style):
        self.data = element
        self.style = style


class NestedElement(Element):
    def __init__(self, element, style):
        super().__init__(element, style)
        self.content = []
        self.children = []
    
    def get_content(self):
        return "\n".join(e.data.get_text() for e in self.content)
    
    def get_title(self):
        return self.data.get_text()
    
    # todo, implement flatten to get whole structure
    def traverse(self):
        # traverse through tree to extract structure as json // or find all titles etc
        pass


class HierarchyLineParser(ProcessUnit):
    
    def __push_to_stack(self, child, stack, output):
        if stack:
            stack[-1].children.append(child)
        else:
            output.append(child)
        stack.append(child)
    
    def __pop_stack_until_match(self, stack, headerSize, header):
        # if top level is smaller than current header to test, pop it
        # repeat until top level is bigger or same
        
        topIsLower = lambda s: s[-1].style.font_size <= header.style.font_size
        
        while (topIsLower(stack)):
            poped = stack.pop()
            
            if poped.style.font_size == headerSize:
                print("do additional analysis!!")
    
    def process(self, line_gen):
        
        structured = []
        levelStack = []
        first_tuple = next(line_gen)
        first = NestedElement(first_tuple["obj"], first_tuple["style"])
        
        levelStack.append(first)
        structured.append(first)
        
        for data in line_gen:
            # if line is header
            line = data["obj"]
            style = data["style"]
            if header_detector(data):
                print("found header: {}".format(data["obj"]))
                child = NestedElement(line, style)
                headerSize = style.font_size
                stackPeekSize = levelStack[-1].style.font_size
                
                if stackPeekSize > headerSize:
                    # append child
                    self.__push_to_stack(child, levelStack, structured)
                
                else:
                    # go up in hierarchy
                    self.__pop_stack_until_match(levelStack, headerSize, child)
                    self.__push_to_stack(child, levelStack, structured)
            
            else:
                # merge content to last paragraph
                levelStack[-1].content.append(Element(line, style))
        return structured
