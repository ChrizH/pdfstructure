import itertools
import re
from collections import Generator, Iterator
from enum import IntEnum, auto

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar, LTTextBoxHorizontal, LTTextContainer

from pdfstructure.style_analyser import StyleDistribution, TextSize, SizeMapper, PivotLinearMapper, count_sizes, \
    PivotLogMapper


def head_char(container: LTTextBoxHorizontal) -> LTChar:
    """
    :rtype LTChar
    :param container:
    :return:
    """
    return container._objs[0]._objs[0]


def clean_title(text: str, amount: int = 100) -> str:
    """
    clean and strip text to title string
    :param text:
    :return:
    """
    text = re.sub("\\s+|/", "_", text)
    text = re.sub("_+", "_", text)
    return text[:amount]


class Style:
    def __init__(self, bold, italic, fontname, fontsize):
        self.bold = bold
        self.italic = italic
        self.font_name = fontname
        self.font_size = fontsize


class ProcessUnit:
    def process(self, *args, **kwargs):
        pass


class StyleDistributionMode(IntEnum):
    title_from_size = auto()
    body_text_biggest = auto()
    only_one_size = auto()


class HeaderSelector(ProcessUnit):
    
    def __init__(self, style_info: StyleDistribution):
        self.style_info = style_info
        if style_info.amount_sizes == 1:
            self.mode = StyleDistributionMode.only_one_size
        elif style_info.body_size == style_info.max_found_size:
            self.mode = StyleDistributionMode.body_text_biggest
        else:
            self.mode = StyleDistributionMode.title_from_size
    
    def merge_headers(self, headers, n=4):
        return "__".join(itertools.islice(headers, n))
    
    def yield_forward_text_as_title(self, element_gen):
        for data in element_gen:
            if "obj" in data and len(data["obj"]._objs) > 2:
                element = data["obj"]
                header = element.get_text().strip()
                header = clean_title(header)
                
                yield header
    
    def yield_title_from_size(self, element_gen, threshold=TextSize.large):
        for data in element_gen:
            if "obj" in data and "style" in data:
                element = data["obj"]
                
                if not len(data["obj"]._objs) > 2:
                    continue
                
                if data["style"].font_size >= threshold:
                    header = element.get_text().strip()
                    header = clean_title(header)
                    yield header
            else:
                print("unpredicted element {}".format(data))
    
    def process(self, element_gen):
        if self.mode == StyleDistributionMode.title_from_size:
            yield from self.yield_title_from_size(element_gen, threshold=TextSize.large)
        elif self.mode == StyleDistributionMode.body_text_biggest:
            yield from self.yield_title_from_size(element_gen, threshold=TextSize.middle)
        elif self.mode == StyleDistributionMode.only_one_size:
            yield from self.yield_forward_text_as_title(element_gen)
        else:
            raise Exception("not implemented")


class StyleAnnotator(ProcessUnit):
    def __init__(self, sizemapper: SizeMapper, style_info: StyleDistribution):
        self._sizeMapper = sizemapper
        self._styleInfo = style_info
    
    def process(self, element_gen):  # element: LTTextContainer):
        """"
        annotate each element with fontsize
        """
        for element in element_gen:
            if isinstance(element, LTTextBoxHorizontal):
                # todo, capture pdfminers paragraph dedection logic
                for line in element:
                    # get average size of all characters
                    sizes = [sub_char.size for sub_char in line
                             if hasattr(sub_char, "size")]
                    # mostCommonSize = statistics.mean(sizes)
                    fontName = head_char(element).fontname
                    mapped_size = self._sizeMapper.translate(target_enum=TextSize,
                                                             value=max(sizes))
                    s = Style(bold="bold" in str(fontName.lower()),
                              italic="italic" in fontName.lower(),
                              fontname=fontName, fontsize=mapped_size)
                    
                    yield {"obj": line, "style": s}


class DocumentTitleExtractor(ProcessUnit):
    
    def process(self, distribution: StyleDistribution, elements):
        sizeMapper = PivotLogMapper(distribution)
        header_selector = HeaderSelector(distribution)
        style_annotator = StyleAnnotator(sizemapper=sizeMapper, style_info=distribution)
        
        with_style = style_annotator.process(elements)
        grep_header = header_selector.process(with_style)
        return header_selector.merge_headers(grep_header, n=4)


class HierarchyProcessor(ProcessUnit):
    def __init__(self):
        pass
    
    def process(self, doc_path):
        root = []
        
        level = []
        
        def find_level(element):
            while level and level[-1].style.font_size >= element.style.font_size:
                level.pop()
            return level[-1]
        
        # count styles
        distribution = count_sizes(doc_path)
        page_processor = StyleAnnotator(sizemapper=PivotLinearMapper(distribution))
        last = None
        for page in extract_pages(doc_path):
            for element in page_processor.process(page, distribution):
                element.children = []
                # todo!!!!!
                if not root:
                    root.append(element)
                
                if not last:
                    level.append(element)
                    last = element
                else:
                    
                    higher = find_level(element)
                    
                    if element.style.font_size == higher.style.font_size:
                        level.pop()
                        level.append(element)
                    elif element.style.font_size < higher.style.font_size:
                        # add element as children
                        higher.children.append(element)
                        level.append(element)
        
        print(page)


def element_generator(file_path: str):
    pNumber = 0
    for page_layout in extract_pages(file_path):
        pNumber += 1
        for element in page_layout:
            element.meta = {"page": pNumber}
            yield element
