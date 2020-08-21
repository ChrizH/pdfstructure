import re
from collections import Counter

from pdfstructure.model import Element, ParentElement, StructuredPdfDocument
from pdfstructure.style_analyser import TextSize
from pdfstructure.title_finder import ProcessUnit
from pdfstructure.utils import word_generator

numeration_pattern = re.compile("[\\d+.?]+")
white_space_pattern = re.compile("\\s+")


def condition_boldness(h1: ParentElement, h2: ParentElement):
    """
    h2 is subheader if:if h1 is bold
    - h1 is bold & h2 is not bold
    - but skip if h2 is enumerated and h1 is not
    @param h1:
    @param h2:
    @return:
    """
    h1start = next(word_generator(h1.heading.data))
    h2start = next(word_generator(h2.heading.data))
    if numeration_pattern.match(h2start) and not numeration_pattern.match(h1start):
        return False
    
    return h1.heading.style.bold and not h2.heading.style.bold


def condition_h2_extends_h1(h1: ParentElement, h2: ParentElement):
    """
    e.g.:   h1  ->  1.1 some header
            h2  ->  1.1.2   some sub header
    @param h1:
    @param h2:
    @return:
    """
    h1start = next(word_generator(h1.heading.data))
    h2start = next(word_generator(h2.heading.data))
    return len(h2start) > len(h1start) and h1start in h2start


def condition_h1_enum_h2_not(h1: ParentElement, h2: ParentElement):
    """
    e.g.    h1  -> 1.1 some header title
            h2  -> some other header title
    """
    h1start = next(word_generator(h1.heading.data))
    h2start = next(word_generator(h2.heading.data))
    return numeration_pattern.match(h1start) and not numeration_pattern.match(h2start)


def condition_h1_slightly_bigger_h2(h1: ParentElement, h2: ParentElement):
    """
    Style analysis maps found sizes to a predefined enum (xsmall, small, large, xlarge).
    but sometimes it makes sense to look deeper.
    @param h1:
    @param h2:
    @return:
    """
    return h2.heading.style.mean_size < h1.heading.style.mean_size


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

    if len(terms._objs) <= 2:
        return False

    # data tuple per line, element from pdfminer, annotated style info for whole line
    # todo, compute ratios over whole line // or paragraph :O
    if style.bold or style.italic or style.font_size > TextSize.middle:
        return check_valid_header_tokens(terms)
    else:
        return False


def check_valid_header_tokens(element):
    """
    fr a paragraph to be treated as a header, it has to contain at least 2 letters.
    @param element:
    @return:
    """
    alpha_count = 0
    numeric_count = 0
    for word in word_generator(element):
        for c in word:
            if c.isalpha():
                alpha_count += 1
            if c.isnumeric():
                numeric_count += 1
            
            if alpha_count >= 2:
                return True
    return False


class HierarchyLineParser(ProcessUnit):
    
    def __init__(self):
        self._isSubHeader = SubHeaderPredicate()
        self._isSubHeader.add_condition(condition_boldness)
        self._isSubHeader.add_condition(condition_h1_enum_h2_not)
        self._isSubHeader.add_condition(condition_h2_extends_h1)
        self._isSubHeader.add_condition(condition_h1_slightly_bigger_h2)
    
    def __push_to_stack(self, child, stack, output):
        if stack:
            child.set_level(len(stack))
            stack[-1].children.append(child)
        else:
            # append as highest order element
            output.append(child)
        stack.append(child)
    
    def __should_pop_higher_level(self, stack: [ParentElement], header_to_test: ParentElement):
        """
        @type header_to_test: object
        
        """
        if not stack:
            return False
        return stack[-1].heading.style.font_size <= header_to_test.heading.style.font_size
    
    def __top_has_no_header(self, stack: [ParentElement]):
        if not stack:
            return False
        return len(stack[-1].heading.data) == 0
    
    def __pop_stack_until_match(self, stack, headerSize, header):
        # if top level is smaller than current header to test, pop it
        # repeat until top level is bigger or same
        
        while self.__top_has_no_header(stack) or self.__should_pop_higher_level(stack, header):
            poped = stack.pop()
            # todo, add break condition, pops and adds same element all the time!!
            # header on higher level in stack has sime FontSize
            # -> check additional sub-header conditions like regexes, enumeration etc.
            if poped.heading.style.font_size == headerSize:
                # check if header_to_check is sub-header of poped element within stack
                if self._isSubHeader.test(poped, header):
                    stack.append(poped)
                    return

    def process(self, element_gen) -> StructuredPdfDocument:
        flat = []
        structured = []
        levelStack = []
        element = next(element_gen)
        first = ParentElement(element)
    
        levelStack.append(first)
        structured.append(first)
    
        for element in element_gen:
            # if line is header

            flat.append(element)
            data = element.data
            style = element.style
            if header_detector(element):
                child = ParentElement(element)
                headerSize = style.font_size
                stackPeekSize = levelStack[-1].heading.style.font_size
                
                if stackPeekSize > headerSize:
                    # append child
                    self.__push_to_stack(child, levelStack, structured)

                else:
                    # go up in hierarchy
                    self.__pop_stack_until_match(levelStack, headerSize, child)
                    self.__push_to_stack(child, levelStack, structured)

            else:
                # merge content to last paragraph
                levelStack[-1].content.append(Element(data, style, level=len(levelStack)))
    
        return StructuredPdfDocument(elements=structured), flat
