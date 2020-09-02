import json
from typing import Iterator

from pdfstructure.hierarchy.traversal import traverse_in_order
from pdfstructure.model.document import Section, StructuredPdfDocument, TextElement
from pdfstructure.model.style import Style
from pdfstructure.utils import dict_subset


class Printer:
    def print(self, document: StructuredPdfDocument, *args, **kwargs):
        pass


class PrettyStringPrinter(Printer):
    """
    pretty prints nested document structure with \t prefixes per level.
    """

    @staticmethod
    def get_title_prefix(level):
        return "".join(["\t" for i in range(level)])

    def make_item_pretty(self, item_gen: Iterator[Section]):
        """
        yield pretty string representation of given element
        - add prefix for each paragraph, corresponding to its level
        - put Title in brackets
        @param item_gen: all elements in order, generator provided by StructuredPdfDocument.traverse()
        """
        for element in item_gen:
            prefix = self.get_title_prefix(element.level)
            formatted_text = element.heading_text.rstrip().replace("\n", "\n{}".format(prefix))
            # if element has children, then its content is a header
            if element.children:
                content = "\n\n{}[{}]".format(prefix, formatted_text)
            else:
                # render as normal content
                content = "\n{}{}".format(prefix, formatted_text)
            yield content

    def print(self, document: StructuredPdfDocument, *args, **kwargs):
        element_iterator = traverse_in_order(document)
        data = [item for item in self.make_item_pretty(element_iterator)]
        return "".join(data)


class PrettyStringFilePrinter(PrettyStringPrinter):
    def print(self, document: StructuredPdfDocument, *args, **kwargs) -> str:
        """
        
        @param **kwargs:
        @param document:
        @param args:
        @param kwargs:
            Keyword Args:
                file_path (str): path to output file
        @return: file_path to outputfile
        """
        output_file = kwargs.get("file_path")
        print("write to file: {}".format(output_file))
        with open(output_file, "w") as file:
            element_iterator = traverse_in_order(document)
            for pretty in self.make_item_pretty(element_iterator):
                file.write(pretty)
        return output_file


class ElementTextEncoder(json.JSONEncoder):
    def default(self, e):
        if isinstance(e, TextElement):
            properties = e.__dict__.copy()
            properties["data"] = e._data.get_text()
            return properties
        else:
            return super().default(e)


def encode_pdf_element(obj):
    """
    customizse pdf element encoding
    - get rid of detailed pdf information retrieved from pdfminer like bounding box coords
    - use mapped fontsize name instead of ordinal value
    @param obj:
    @return:
    """
    if isinstance(obj, TextElement):
        properties = dict_subset(obj.__dict__.copy(), ("_data", "_text"))
        properties["text"] = obj.text
        properties["style"] = encode_pdf_element(obj.style)
        return properties
    elif isinstance(obj, Style):
        properties = obj.__dict__.copy()
        properties["mapped_font_size"] = str(obj.mapped_font_size.name)
        return properties
    else:
        return obj.__dict__


class JsonStringPrinter(Printer):
    def print(self, document: StructuredPdfDocument, *args, **kwargs):
        return json.dumps(document, default=encode_pdf_element, indent=4)


class JsonFilePrinter(Printer):
    def print(self, document: StructuredPdfDocument, *args, **kwargs):
        """
        @param document:
        @param args:
        @param kwargs:
            Keyword Args:
                file_path (str): path to output file
        @return:
        """
        file_path = kwargs.get("file_path")
        with open(file_path, "w") as fp:
            json.dump(document, fp=fp, default=encode_pdf_element, indent=4)
        return file_path
