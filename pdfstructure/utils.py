import itertools
import math
import os
from pathlib import Path

from pdfminer.high_level import extract_pages


def element_generator(file_path: str):
    """
    yields flat list of paragraphs within a document.
    :param file_path:
    :return:
    """
    pNumber = 0
    for page_layout in extract_pages(file_path):
        pNumber += 1
        for element in page_layout:
            element.meta = {"page": pNumber}
            yield element


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
