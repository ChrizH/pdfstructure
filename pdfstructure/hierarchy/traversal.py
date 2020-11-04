import sys
from collections import deque
from typing import Generator

from pdfstructure.model.document import StructuredPdfDocument, Section


def get_document_depth(document: StructuredPdfDocument):
    """
    retrieves document depth found within tree structure, + 1 because the levels are 0 notated.
    """
    return max(set([section.level for section in traverse_in_order(document)])) + 1


def traverse_inorder_sections_with_content(document: StructuredPdfDocument) -> Generator[
    tuple, StructuredPdfDocument, None]:
    """
    Traverse section by section in order and group top children as combined content
    @param document:
    @return: yields level, title, content
    """
    for section in filter(lambda sec: len(sec.children) > 0, traverse_in_order(document)):
        children: Section
        content = []
        for children in section.children:
            if children.children:
                continue
            content.append(children.heading_text)
        yield section.level, section.heading_text, "\n".join(content)


def traverse_in_order(document: StructuredPdfDocument) \
        -> Generator[Section, StructuredPdfDocument, None]:
    """
                     5   10
                  /   \    \
                 1     2    3
               / | \        |
              a  b  c       x

    yield order:
    - [5,1,a,b,c,2,10,3,x]
    """

    def __traverse__(section: Section):
        child: Section
        for child in section.children:
            yield child
            yield from __traverse__(child)

    for element in document.elements:
        yield element
        yield from __traverse__(element)


def traverse_level_order(document: StructuredPdfDocument, max_depth=sys.maxsize) \
        -> Generator[Section, StructuredPdfDocument, None]:
    """
                     5   10
                  /   \    \
                 1     2    3
               / | \        |
              a  b  c       x

    yield order:
    - [5,10,1,2,3,a,b,c,x]

    @param document: structured pdf document, each element holds its own dopth information (Section.level)
    @param max_depth: yield elements until max_depth is reached
    """

    element_queue = deque()

    element: Section
    for element in document.elements:
        element_queue.append(element)

    while element_queue:
        element = element_queue.popleft()

        if element.level < max_depth:
            yield element

            # append next layer of elements / children nodes
            for child in element.children:
                element_queue.append(child)
