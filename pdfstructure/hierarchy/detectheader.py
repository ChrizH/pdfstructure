from collections import Counter

from pdfstructure.model import TextSize, TextElement
from pdfstructure.utils import word_generator


def header_detector(element: TextElement):
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
