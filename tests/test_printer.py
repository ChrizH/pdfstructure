import json
import tempfile
from pathlib import Path
from unittest import TestCase

from pdfstructure.hierarchy import HierarchyLineParser
from pdfstructure.model import StructuredPdfDocument, ParentPdfElement
from pdfstructure.printer import PrettyStringFilePrinter, PrettyStringPrinter, JsonFilePrinter, JsonStringPrinter
from tests.test_title_finder import TestUtils


class TestPrettyStringPrinter(TestCase):
    straight_forward_doc = str(Path("resources/interview_cheatsheet.pdf").absolute())
    correctFormattedText = "[Data Structure Basics]\n\t[Array]\n\t\t[Definition:]\n\t\t\tStores data elements" \
                           " based on an sequential, most commonly 0 based, index."
    
    testDocument = None
    
    @classmethod
    def setUpClass(cls) -> None:
        parser = HierarchyLineParser()
        elements_gen = TestUtils.generate_annotated_lines(cls.straight_forward_doc)
        cls.testDocument = parser.process(elements_gen)
    
    def test_print_traverse(self):
        header: ParentPdfElement
        for header in self.testDocument.traverse():
            prefix = "".join(["\t" for i in range(header.level)])
            print(prefix + header.heading.text)
            [print(prefix + "  " + c.text) for c in header.content]
    
    def test_print_pretty_string(self):
        printer = PrettyStringPrinter()
        printed = printer.print(self.testDocument)
        self.assertTrue(self.correctFormattedText in printed)
    
    def test_print_pretty_file(self):
        printer = PrettyStringFilePrinter()
        
        with tempfile.TemporaryDirectory() as tmp:
            print('created temporary directory', tmp)
            
            file_path = Path(tmp, "document-pretty.txt")
            printed_file = printer.print(self.testDocument, file_path=str(file_path.absolute()))
            
            with open(printed_file, "r") as file:
                printed = "".join(file.readlines())
                self.assertTrue(self.correctFormattedText in printed)
    
    def test_print_json_string(self):
        printer = JsonStringPrinter()
        
        jsonString = printer.print(self.testDocument)
        
        decoded_document = StructuredPdfDocument.from_json(json.loads(jsonString))
        
        self.assertEqual(self.testDocument.elements[0].heading.text,
                         decoded_document.elements[0].heading.text)
        self.assertEqual(self.testDocument.elements[-1].heading.text,
                         decoded_document.elements[-1].heading.text)
    
    def test_print_json_file(self):
        printer = JsonFilePrinter()
        
        with tempfile.TemporaryDirectory() as tmp:
            print('created temporary directory', tmp)
            
            file_path = Path(tmp, "document-pretty.json")
            printer.print(self.testDocument, file_path=str(file_path.absolute()))
            
            with open(file_path, "r") as file:
                jsonData = json.load(file)
                
                decoded_document = StructuredPdfDocument.from_json(jsonData)
                
                self.assertEqual(self.testDocument.elements[0].heading.text,
                                 decoded_document.elements[0].heading.text)
                self.assertEqual(self.testDocument.elements[-1].heading.text,
                                 decoded_document.elements[-1].heading.text)
