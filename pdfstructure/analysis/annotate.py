import statistics

from pdfminer.layout import LTTextBoxHorizontal

from pdfstructure.analysis.sizemapper import SizeMapper
from pdfstructure.analysis.styledistribution import StyleDistribution
from pdfstructure.model import TextSize, Style, PdfElement
from pdfstructure.utils import head_char_line, truncate


class StyleAnnotator:
    """
    creates a PdfElements from incoming pdf-paragraphs (raw LTTextContainer from pdfminer.six).
    - annotates paragraph with @Style(italic, bold, fontname, mapped_size, mean_size).
    - mapped_font_size: captures most dominant character size within paragraph & maps it to TextSize Enum.
      mapped Size is leveraged by the hierarchy detection algorithm.
    """

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
                    fontName = head_char_line(line).fontname
                    mapped_size = self._sizeMapper.translate(target_enum=TextSize,
                                                             value=max(sizes))
                    mean_size = truncate(statistics.mean(sizes), 1)
                    s = Style(bold="bold" in str(fontName.lower()),
                              italic="italic" in fontName.lower(),
                              font_name=fontName,
                              mapped_font_size=mapped_size,
                              mean_size=mean_size)
                    metadata = {"page": element.page} if hasattr(element, "page") else None
                    yield PdfElement(text_container=line, style=s, metadata=metadata)
