import itertools
import re
from enum import IntEnum, auto

from pdfminer.layout import LTChar, LTTextBoxHorizontal

from pdfstructure.model import Element, Style
from pdfstructure.style_analyser import StyleDistribution, TextSize, SizeMapper, PivotLogMapper


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
        for element in element_gen:
            if isinstance(element, Element) and len(element.data._objs) > 2:
                header = element.data.get_text().strip()
                header = clean_title(header)
                
                yield header
    
    def yield_title_from_size(self, element_gen, threshold=TextSize.large):
        for element in element_gen:
            if not isinstance(element, Element):
                print("unpredicted element {}".format(element))
                continue
            
            if not len(element.data._objs) > 2:
                continue
            
            if element.style.font_size >= threshold:
                header = element.data.get_text().strip()
                header = clean_title(header)
                yield header
    
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
                    
                    yield Element(data=line, style=s)


class DocumentTitleExtractor(ProcessUnit):
    
    def process(self, distribution: StyleDistribution, elements):
        sizeMapper = PivotLogMapper(distribution)
        header_selector = HeaderSelector(distribution)
        style_annotator = StyleAnnotator(sizemapper=sizeMapper, style_info=distribution)
        
        with_style = style_annotator.process(elements)
        grep_header = header_selector.process(with_style)
        return header_selector.merge_headers(grep_header, n=4)
