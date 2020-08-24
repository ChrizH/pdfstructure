from pdfstructure.model import ParentPdfElement, StructuredPdfDocument, PdfElement, Style
from pdfstructure.utils import dict_subset


class Printer:
    def print(self, document: StructuredPdfDocument, *args, **kwargs):
        pass


class PrettyStringPrinter(Printer):
    """
    pretty prints nested document structure with \t prefixes per level.
    """
    
    @staticmethod
    def get_prefix_for_level(level):
        return "".join(["\t" for i in range(level)])
    
    def print_content(self, element: PdfElement):
        """
        print all contents of given element with appropriate level prefix.
        a content element has no children.
        @param element: content element within document structure.
        @return:
        """
        return " ".join((self.get_prefix_for_level(element.level), element.text))
    
    def print_nested(self, parent: ParentPdfElement):
        """
        prints nested parental element with its title, content and childrens content,
        with its level prefix respectively.
        @param parent: parent node within document structure
        @return:
        """
        
        def str_title(p: ParentPdfElement):
            prefix = self.get_prefix_for_level(p.level)
            return "{}[{}]".format(prefix, p.heading.text)
        
        def str_content(p: ParentPdfElement):
            return "\n".join(self.print_content(e) for e in p.content)
        
        def str_children_content(p: ParentPdfElement):
            return " ".join(self.print_nested(e) for e in p.children)
        
        return "{}\n{}\n{}".format(str_title(parent),
                                   str_content(parent),
                                   str_children_content(parent))
    
    @staticmethod
    def str_document_title(document):
        return "[[{}]]\n\n".format(document.title)
    
    def print(self, document: StructuredPdfDocument, *args, **kwargs):
        data = [self.print_nested(e) for e in document.elements]
        
        if document.title:
            data.insert(0, self.str_document_title(document))
        
        return "\n".join(data)


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
            if document.title:
                file.write(self.str_document_title(document))
    
            [file.write(self.print_nested(e)) for e in document.elements]
        return output_file


import json


class ElementTextEncoder(json.JSONEncoder):
    def default(self, e):
        if isinstance(e, PdfElement):
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
    if isinstance(obj, PdfElement):
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
