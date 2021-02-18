from pathlib import Path
from typing import List, Generator

from pdfminer.layout import LTTextContainer, LAParams

from pdfstructure.analysis.annotate import StyleAnnotator
from pdfstructure.analysis.sizemapper import PivotLogMapper
from pdfstructure.analysis.styledistribution import count_sizes, StyleDistribution
from pdfstructure.hierarchy.detectheader import header_detector
from pdfstructure.hierarchy.headercompare import get_default_sub_header_conditions
from pdfstructure.model.document import TextElement, Section, StructuredPdfDocument, DanglingTextSection
from pdfstructure.source import Source


class HierarchyParser:

    def __init__(self, sub_header_conditions=get_default_sub_header_conditions()):
        self._isSubHeader = sub_header_conditions

    def parse_pdf(self, source: Source) -> StructuredPdfDocument:
        """
        Analysises and parses a PDF document from a given @Source containing its natural hierarchy.
        @param source:
        @return:
        """
        # 1. iterate once through PDF and analyse style distribution
        distribution = count_sizes(source.read())
        size_mapper = PivotLogMapper(distribution)
        style_annotator = StyleAnnotator(sizemapper=size_mapper, style_info=distribution)

        # 2. iterate second time trough pdf
        # - annotate each paragraph with mapped Style
        elements_with_style = style_annotator.process(source.read(
            override_la_params=LAParams(line_margin=distribution.line_margin)))

        # - create nested document structure on the fly
        structured_elements = self.create_hierarchy(elements_with_style, distribution)

        # 3. create wrapped document and capture some metadata
        pdf_document = StructuredPdfDocument(elements=structured_elements, style_info=distribution)
        enrich_metadata(pdf_document, source)
        return pdf_document

    def create_hierarchy(self, element_gen: Generator[TextElement, LTTextContainer, None],
                         style_distribution: StyleDistribution) -> List[Section]:
        """
        Takes incoming flat list of paragraphs and creates nested natural order hierarchy.

        Example Structure:
        ==================
        Document.pdf
        <<
            1.  H1 Chapter Header
            content
                1.2     H2 Section Header
                content
                1.3     H2 Section Header
                content
                    1.3.1   H3 Subsection Header
                    content
            2.  H1 Chapter Header
            content
        >>

        @param element_gen:
        @return:
        """
        structured = []
        level_stack = []

        for element in element_gen:
            # if line is header
            style = element.style
            if header_detector(element, style_distribution):
                child = Section(element)
                header_size = style.mapped_font_size

                # initial state - push and continue with next element
                if not level_stack:
                    self.__push_to_stack(child, level_stack, structured)
                    continue

                stack_peek_size = level_stack[-1].heading.style.mapped_font_size

                if stack_peek_size > header_size:
                    # append element as children
                    self.__push_to_stack(child, level_stack, structured)

                else:
                    # go up in hierarchy and insert element (as children) on its level
                    self.__pop_stack_until_match(level_stack, header_size, child)
                    self.__push_to_stack(child, level_stack, structured)

            else:
                # no header found, add paragraph as a content element to previous node
                # - content is on same level as its corresponding header
                content_node = Section(element, level=len(level_stack))
                if level_stack:
                    level_stack[-1].append_children(content_node)
                else:
                    # if last element in output structure has also no header, merge
                    if structured and isinstance(structured[-1], DanglingTextSection):
                        structured[-1].append_children(content_node)
                    else:
                        # # add dangling content as section
                        dangling_content = DanglingTextSection()
                        dangling_content.append_children(content_node)
                        dangling_content.set_level(len(level_stack))
                        structured.append(dangling_content)

        return structured

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

    @staticmethod
    def __push_to_stack(child, stack, output):
        """
        insert incoming paragraph (child) in level(hierarchy) stack.
        @param child: next incoming paragraph
        @param stack: hierarchy-detect helper stack
        @param output: exporting list of elements (contains complete structure in the end)
        @return:
        """
        if stack:
            child.set_level(len(stack))
            stack[-1].children.append(child)
        else:
            # append as highest order element
            output.append(child)
        stack.append(child)

    @staticmethod
    def __should_pop_higher_level(stack: [Section], header_to_test: Section):
        """
        helper method for __pop_stack_until_match: check if last element in stack is smaller then new header-paragraph.
        @type header_to_test: object

        """
        if not stack:
            return False
        return stack[-1].heading.style.mapped_font_size <= header_to_test.heading.style.mapped_font_size

    @staticmethod
    def __top_has_no_header(stack: [Section]):
        """
        helper method for @__pop_stack_until_match
        @param stack:
        @return:
        """
        if not stack:
            return False
        return len(stack[-1].heading._data) == 0


def enrich_metadata(pdf: StructuredPdfDocument, source: Source):
    """
    add some metadata to parsed PDF if possible
        # add filename
        # todo create document summary
        # todo extract document-title from best titles
    @return:
    """
    # try to capture filename
    try:
        filename = Path(source.uri).name
        pdf.update_metadata("filename", filename)
    except Exception as e:
        pass
