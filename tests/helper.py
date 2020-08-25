from pdfstructure.analysis.annotate import StyleAnnotator
from pdfstructure.analysis.sizemapper import PivotLogMapper
from pdfstructure.analysis.styledistribution import count_sizes
from pdfstructure.utils import element_generator


def generate_annotated_lines(file_path):
    """
    yields paragraph detected by pdfminer annotated with detected & mapped style information
    """
    element_gen = element_generator(file_path)
    distribution = count_sizes(element_gen)
    sizeMapper = PivotLogMapper(distribution)
    style_annotator = StyleAnnotator(sizemapper=sizeMapper, style_info=distribution)

    elements = element_generator(file_path)
    with_style = style_annotator.process(elements)

    yield from with_style
