from pdfstructure.model import ParentElement, StructuredPdfDocument, Element


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
    
    def print_content(self, element: Element):
        """
        print all contents of given element with appropriate level prefix.
        a content element has no children.
        @param element: content element within document structure.
        @return:
        """
        return self.get_prefix_for_level(element.level) \
               + element.data.get_text().strip()
    
    def print_nested(self, parent: ParentElement):
        """
        prints nested parental element with its title, content and childrens content,
        with its level prefix respectively.
        @param parent: parent node within document structure
        @return:
        """
        
        def str_title(p: ParentElement):
            prefix = self.get_prefix_for_level(p.level)
            return "{}[{}]".format(prefix,
                                   p.heading.data.get_text().strip())
        
        def str_content(p: ParentElement):
            return "\n".join(self.print_content(e) for e in p.content)
        
        def str_children_content(p: ParentElement):
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


class JsonPrinter(Printer):
    def print(self, document: StructuredPdfDocument, *args, **kwargs):
        """
        @param document:
        @param args:
        @param kwargs:
            Keyword Args:
                file_path (str): path to output file
        @return:
        """
        with open(kwargs.get("file_path"), "w") as fp:
            json.dump(document, fp=fp, default=lambda o: o.__dict__, indent=4)
