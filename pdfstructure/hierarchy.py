from collections import Counter

from pdfstructure.model import Element, NestedElement
from pdfstructure.style_analyser import TextSize
from pdfstructure.title_finder import ProcessUnit


def bold_distinction(h1, h2):
    return h1.style.bold and not h2.style.bold


def is_sub_header(h1, h2):
    # todo, test it !!
    conditions = [bold_distinction]
    return any(condition(h1, h2) for condition in conditions)


def header_detector(element):
    stats = Counter()
    terms = element.data
    style = element.style
    # data tuple per line, element from pdfminer, annotated style info for whole line
    # todo, compute ratios over whole line // or paragraph :O
    if style.bold or style.italic or style.font_size > TextSize.middle:
        return True
    else:
        return False


class HierarchyLineParser(ProcessUnit):
    
    def __push_to_stack(self, child, stack, output):
        if stack:
            stack[-1].children.append(child)
        else:
            output.append(child)
        stack.append(child)
    
    def __should_pop_higher_level(self, stack, header_to_test):
        """
        @type header_to_test: object
        
        """
        if not stack:
            return False
        return stack[-1].style.font_size <= header_to_test.style.font_size
    
    def __pop_stack_until_match(self, stack, headerSize, header):
        # if top level is smaller than current header to test, pop it
        # repeat until top level is bigger or same
        
        while self.__should_pop_higher_level(stack, header):
            poped = stack.pop()
            
            if poped.style.font_size == headerSize:
                print("do additional analysis!!")
    
    def process(self, element_gen):
        
        structured = []
        levelStack = []
        element = next(element_gen)
        first = NestedElement(element.data, element.style)
        
        levelStack.append(first)
        structured.append(first)
        
        for element in element_gen:
            # if line is header
            data = element.data
            style = element.style
            if header_detector(element):
                print("found header: {}".format(data))
                child = NestedElement(data, style)
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
                levelStack[-1].content.append(Element(data, style))
        return structured
