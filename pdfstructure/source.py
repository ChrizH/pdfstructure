from typing import Generator, Any

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LAParams


class Source:
    """
    Abstract interface to read a PDF from somewhere.
    """

    def __init__(self, uri=None):
        """

        @param uri: points to pdf that should be read
        """
        self.uri = uri

    def config(self):
        """
        get source configuration
        @return:
        """
        pass

    def read(self) -> Generator[LTTextContainer, Any, None]:
        """
        yields flat list of paragraphs within a document.
        @param args:
        @param kwargs:
        @return:
        """
        pass


class FileSource(Source):
    def __init__(self, file_path: str, page_numbers=None, la_params=LAParams(boxes_flow=None, detect_vertical=False)):
        super().__init__(uri=file_path)
        self.page_numbers = page_numbers
        self.la_params = la_params

    def config(self):
        return self.__dict__

    def read(self) -> Generator[LTTextContainer, Any, None]:
        pNumber = 0
        # disable boxes_flow, style based hierarchy detection is based on purely flat list of paragraphs
        # params = LAParams(boxes_flow=None, detect_vertical=False)  # setting for easy doc
        # params = LAParams(boxes_flow=0.5, detect_vertical=True) # setting for column doc
        # todo, do pre-analysis in count_sizes --> are there many boxes within same line
        # todo, understand LAParams, for columns, NONE works better, for vertical only layout LAParams(boxes_flow=None, detect_vertical=False) works better!! :O
        #   do some sort of layout analyis, if there are many boxes vertically next to each other, use layout analysis
        #   - column type
        #   - straight forward document
        for page_layout in extract_pages(self.uri, laparams=self.la_params, page_numbers=self.page_numbers):
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    element.page = pNumber
                    yield element
            pNumber += 1
