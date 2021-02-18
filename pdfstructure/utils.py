import itertools
import math
import os
from pathlib import Path
from typing import Generator

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine, LAParams, LTTextLineHorizontal


def char_generator(text_container: LTTextContainer):
    for container in text_container:
        if isinstance(container, LTChar):
            yield container
        elif isinstance(container, LTTextLine):
            for obj in container:
                if isinstance(obj, LTChar):
                    yield obj


def dict_subset(d, exclude_keys):
    return {k: v for k, v in d.items() if k not in exclude_keys}


def word_generator(text_container: LTTextContainer):
    """
    iterates through container's characters and yields a word as soon as found (trailing whitespace).
    @param text_container:
    @return:
    """
    characters = []

    for obj in char_generator(text_container):
        character = obj.get_text()
        if character != " ":
            characters.append(character)
        else:
            word = "".join(characters).strip()
            # skip if word is just a whitespace on its own
            if len(word) > 0:
                yield word
            characters.clear()
    if characters:
        yield "".join(characters)


def element_generator(file_path: str, page_numbers=None) -> Generator[LTTextContainer, None, None]:
    """
    yields flat list of paragraphs within a document.
    :param file_path:
    :return:
    """
    pNumber = 0
    # disable boxes_flow, style based hierarchy detection is based on purely flat list of paragraphs
    params = LAParams(boxes_flow=None, detect_vertical=False)  # setting for easy doc
    # params = LAParams(boxes_flow=0.5, detect_vertical=True) # setting for column doc
    # todo, do pre-analysis in count_sizes --> are there many boxes within same line
    # todo, understand LAParams, for columns, NONE works better, for vertical only layout LAParams(boxes_flow=None, detect_vertical=False) works better!! :O
    #   do some sort of layout analyis, if there are many boxes vertically next to each other, use layout analysis
    #   - column type
    #   - straight forward document
    for page_layout in extract_pages(file_path, laparams=params, page_numbers=page_numbers):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                element.meta = {"page": pNumber}
                yield element
        pNumber += 1


def truncate(number, decimals=0):
    """
    Returns a value truncated to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor


class DocTypeFilter:

    def __init__(self, endings=("doc", "docx", "ppt", "pptx", "xls", "xlsx", "odt", "rtf")):
        self.endings = endings if isinstance(endings, (list, tuple)) else (endings)

    def test(self, name):
        return name.split(".")[-1].lower() in self.endings


def closest_key(sorted_dict, key):
    "Return closest key in `sorted_dict` to given `key`."
    assert len(sorted_dict) > 0
    keys = list(itertools.islice(sorted_dict.irange(minimum=key), 1))
    keys.extend(itertools.islice(sorted_dict.irange(maximum=key, reverse=True), 1))
    return min(keys, key=lambda k: abs(key - k))


def find_file(root_dir: str, type_filter: DocTypeFilter, print_mod=10) -> iter([Path]):
    processed = 0
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if type_filter.test(file):
                yield Path(root + "/" + file)
                processed += 1
                if print_mod and processed % print_mod == 0:
                    print("\nprocessed {}\n".format(processed))
    print("found {} file-paths".format(processed))


def head_char_line(container: LTTextLineHorizontal) -> LTChar:
    """
    :rtype LTChar
    :param container:
    :return:
    """
    for obj in container:
        if isinstance(obj, LTChar):
            return obj
