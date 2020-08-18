import re
from collections import Counter

from pdfstructure.model import Element, NestedElement
from pdfstructure.style_analyser import TextSize
from pdfstructure.title_finder import ProcessUnit
from pdfstructure.utils import word_generator

numeration_pattern = re.compile("[\\d+.?]+")
white_space_pattern = re.compile("\\s+")


def condition_boldness(h1: Element, h2: Element):
    """
    h2 is subheader if:if h1 is bold
    - h1 is bold & h2 is not bold
    - but skip if h2 is enumerated and h1 is not
    @param h1:
    @param h2:
    @return:
    """
    h1start = next(word_generator(h1.data))
    h2start = next(word_generator(h2.data))
    if numeration_pattern.match(h2start) and not numeration_pattern.match(h1start):
        return False
    
    return h1.style.bold and not h2.style.bold


def condition_h2_extends_h1(h1: Element, h2: Element):
    """
    e.g.:   h1  ->  1.1 some header
            h2  ->  1.1.2   some sub header
    @param h1:
    @param h2:
    @return:
    """
    h1start = next(word_generator(h1.data))
    h2start = next(word_generator(h2.data))
    return len(h2start) > len(h1start) and h1start in h2start


def condition_h1_enum_h2_not(h1, h2):
    """
    e.g.    h1  -> 1.1 some header title
            h2  -> some other header title
    """
    h1start = next(word_generator(h1.data))
    h2start = next(word_generator(h2.data))
    return numeration_pattern.match(h1start) and not numeration_pattern.match(h2start)


class SubHeaderPredicate:
    def __init__(self):
        self._conditions = []
    
    def add_condition(self, condition):
        self._conditions.append(condition)
    
    def test(self, h1, h2):
        return any(condition(h1, h2) for condition in self._conditions)


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
    
    def __init__(self):
        self._isSubHeader = SubHeaderPredicate()
        self._isSubHeader.add_condition(condition_boldness)
        self._isSubHeader.add_condition(condition_h1_enum_h2_not)
        self._isSubHeader.add_condition(condition_h2_extends_h1)
    
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
    
    def __top_has_no_header(self, stack):
        if not stack:
            return False
        return len(stack[-1].data) == 0
    
    def __pop_stack_until_match(self, stack, headerSize, header):
        # if top level is smaller than current header to test, pop it
        # repeat until top level is bigger or same
        
        while self.__top_has_no_header(stack) or self.__should_pop_higher_level(stack, header):
            poped = stack.pop()
            
            # header on higher level in stack has sime FontSize
            # -> check additional sub-header conditions like regexes, enumeration etc.
            if poped.style.font_size == headerSize:
                # check if header_to_check is sub-header of poped element within stack
                if self._isSubHeader.test(poped, header):
                    stack.append(poped)
    
    def process(self, element_gen):
        flat = []
        structured = []
        levelStack = []
        element = next(element_gen)
        first = NestedElement(element.data, element.style)
        
        levelStack.append(first)
        structured.append(first)
        
        for element in element_gen:
            # if line is header
            flat.append(element)
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
        return structured, flat
