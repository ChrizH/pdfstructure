import tempfile
from pathlib import Path
from unittest import TestCase

from pdfstructure.hierarchy import HierarchyLineParser
from pdfstructure.printer import PrettyStringFilePrinter, PrettyStringPrinter, JsonPrinter
from tests.test_title_finder import TestUtils


class TestPrettyStringPrinter(TestCase):
    straight_forward_doc = str(Path("resources/interview_cheatsheet.pdf").absolute())
    correctFormattedText = "[Data Structure Basics]\n\n\t[Array]\n\n\t\t[Definition:]\n\t\t\tStores data elements" \
                           " based on an sequential, most commonly 0 based, index."
    testDocument = None
    
    @classmethod
    def setUpClass(cls) -> None:
        parser = HierarchyLineParser()
        elements_gen = TestUtils.generate_annotated_lines(cls.straight_forward_doc)
        cls.testDocument, _ = parser.process(elements_gen)
    
    def test_print_string(self):
        printer = PrettyStringPrinter()
        printed = printer.print(self.testDocument)
        self.assertTrue(self.correctFormattedText in printed)
    
    def test_print_to_file(self):
        printer = PrettyStringFilePrinter()
        
        with tempfile.TemporaryDirectory() as tmp:
            print('created temporary directory', tmp)
            
            file_path = Path(tmp, "document-pretty.txt")
            printed_file = printer.print(self.testDocument, file_path=str(file_path.absolute()))
            
            with open(printed_file, "r") as file:
                printed = "".join(file.readlines())
                self.assertTrue(self.correctFormattedText in printed)
    
    def skipped_print_to_json(self):
        printer = JsonPrinter()
        # todo, abstract hierarchy extraction step to text only models!!
        
        with tempfile.TemporaryDirectory() as tmp:
            print('created temporary directory', tmp)
            
            file_path = Path(tmp, "document-pretty.json")
            printed_file = printer.print(self.testDocument, file_path=str(file_path.absolute()))
            
            with open(printed_file, "r") as file:
                printed = "".join(file.readlines())
                self.assertTrue(self.correctFormattedText in printed)
