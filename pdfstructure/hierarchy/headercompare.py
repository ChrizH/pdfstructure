import re

from pdfstructure.model.document import Section
from pdfstructure.utils import word_generator

numeration_pattern = re.compile("^(?=.*\d+)((?=.*\.)|(?=.*:)).*$")
white_space_pattern = re.compile("\\s+")


class SubHeaderPredicate:
    """
    Compares two paragraphs that are classified as headers, but have the same mapped FontSize.
    - Its possible that those headers are actually not on the same level, based on some conditions like H1 is enumerated & bold, H2 not.
    """

    def __init__(self):
        self._conditions = []

    def add_condition(self, condition):
        self._conditions.append(condition)

    def test(self, h1, h2):
        return any(condition(h1, h2) for condition in self._conditions)


def get_default_sub_header_conditions():
    _isSubHeader = SubHeaderPredicate()
    _isSubHeader.add_condition(condition_boldness)
    _isSubHeader.add_condition(condition_h1_enum_h2_not)
    _isSubHeader.add_condition(condition_h2_extends_h1)
    _isSubHeader.add_condition(condition_h1_slightly_bigger_h2)
    return _isSubHeader


def condition_boldness(h1: Section, h2: Section):
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


def condition_h2_extends_h1(h1: Section, h2: Section):
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


def condition_h1_enum_h2_not(h1: Section, h2: Section):
    """
    e.g.    h1  -> 1.1 some header title
            h2  -> some other header title
    -> applies only if both headers are of same style type

    """
    if h2.heading.style.bold and not h1.heading.style.bold:
        return False
    # if h2.heading.style.font_name != h1.heading.style.font_name:
    #    return False

    h1start = next(word_generator(h1.heading._data))
    h2start = next(word_generator(h2.heading._data))
    return numeration_pattern.match(h1start) and not numeration_pattern.match(h2start)


def condition_h1_slightly_bigger_h2(h1: Section, h2: Section):
    """s
    Style analysis maps found sizes to a predefined enum (xsmall, small, large, xlarge).
    but sometimes it makes sense to look deeper.
    @param h1:
    @param h2:
    @return:
    """
    return h1.heading.style.mapped_font_size == h2.heading.style.mapped_font_size \
           and h1.heading.style.max_size - h2.heading.style.max_size > 1.0
