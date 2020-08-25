import re
from collections import Counter

from pdfstructure.model import PdfElement, ParentPdfElement, StructuredPdfDocument
from pdfstructure.style_analyser import TextSize
from pdfstructure.title_finder import ProcessUnit
from pdfstructure.utils import word_generator

numeration_pattern = re.compile("[\\d+.?]+")
white_space_pattern = re.compile("\\s+")


def condition_boldness(h1: ParentPdfElement, h2: ParentPdfElement):
    """
    h2 is subheader if:if h1 is bold
    - h1 is bold & h2 is not bold
    - but skip if h2 is enumerated and h1 is not
    @param h1:
    @param h2:
    @return:
    """
    h1start = next(word_generator(h1.heading._data))
    h2start = next(word_generator(h2.heading._data))
    if numeration_pattern.match(h2start) and not numeration_pattern.match(h1start):
        return False
    
    return h1.heading.style.bold and not h2.heading.style.bold


def condition_h2_extends_h1(h1: ParentPdfElement, h2: ParentPdfElement):
    """
    e.g.:   h1  ->  1.1 some header
            h2  ->  1.1.2   some sub header
    @param h1:
    @param h2:
    @return:
    """
    h1start = next(word_generator(h1.heading._data))
    h2start = next(word_generator(h2.heading._data))
    return len(h2start) > len(h1start) and h1start in h2start


def condition_h1_enum_h2_not(h1: ParentPdfElement, h2: ParentPdfElement):
    """
    e.g.    h1  -> 1.1 some header title
            h2  -> some other header title
    """
    h1start = next(word_generator(h1.heading._data))
    h2start = next(word_generator(h2.heading._data))
    return numeration_pattern.match(h1start) and not numeration_pattern.match(h2start)


def condition_h1_slightly_bigger_h2(h1: ParentPdfElement, h2: ParentPdfElement):
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
    terms = element._data
    style = element.style
    
    if len(terms._objs) <= 2:
        return False
    
    # data tuple per line, element from pdfminer, annotated style info for whole line
    # todo, compute ratios over whole line // or paragraph :O
    if style.bold or style.italic or style.mapped_font_size > TextSize.middle:
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
        # self._isSubHeader.add_condition(condition_h1_slightly_bigger_h2)

    def __push_to_stack(self, child, stack, output):
        if stack:
            child.set_level(len(stack))
            stack[-1].children.append(child)
        else:
            # append as highest order element
            output.append(child)
        stack.append(child)

    def __should_pop_higher_level(self, stack: [ParentPdfElement], header_to_test: ParentPdfElement):
        """
        @type header_to_test: object
        
        """
        if not stack:
            return False
        return stack[-1].heading.style.mapped_font_size <= header_to_test.heading.style.mapped_font_size

    def __top_has_no_header(self, stack: [ParentPdfElement]):
        if not stack:
            return False
        return len(stack[-1].heading._data) == 0

    def __pop_stack_until_match(self, stack, headerSize, header):
        # if top level is smaller than current header to test, pop it
        # repeat until top level is bigger or same

        while self.__top_has_no_header(stack) or self.__should_pop_higher_level(stack, header):
            poped = stack.pop()
            # header on higher level in stack has sime FontSize
            # -> check additional sub-header conditions like regexes, enumeration etc.
            if poped.heading.style.mapped_font_size == headerSize:
                # check if header_to_check is sub-header of poped element within stack
                if self._isSubHeader.test(poped, header):
                    stack.append(poped)
                    return

    def process(self, element_gen) -> StructuredPdfDocument:
        flat = []
        structured = []
        levelStack = []
        element = next(element_gen)
        first = ParentPdfElement(element)

        levelStack.append(first)
        structured.append(first)

        for element in element_gen:
            # if line is header
            flat.append(element)
            data = element._data
            style = element.style
            if header_detector(element):
                child = ParentPdfElement(element)
                headerSize = style.mapped_font_size
                stackPeekSize = levelStack[-1].heading.style.mapped_font_size

                if stackPeekSize > headerSize:
                    # append element as children
                    self.__push_to_stack(child, levelStack, structured)

                else:
                    # go up in hierarchy and insert element (as children) on its level
                    self.__pop_stack_until_match(levelStack, headerSize, child)
                    self.__push_to_stack(child, levelStack, structured)

            else:
                # no header found, add paragraph as a content element to previous node
                # - content is on same level as its corresponding header
                levelStack[-1].content.append(PdfElement(text_container=data, style=style, level=len(levelStack) - 1))

        return StructuredPdfDocument(elements=structured)
