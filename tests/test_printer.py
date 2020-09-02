import json
from pathlib import Path
from unittest import TestCase

from pdfstructure.hierarchy.parser import HierarchyParser
from pdfstructure.model.document import StructuredPdfDocument
from pdfstructure.printer import PrettyStringFilePrinter, PrettyStringPrinter, JsonFilePrinter, JsonStringPrinter
from pdfstructure.source import FileSource


class TestPrettyStringPrinter(TestCase):
    straight_forward_doc = str(Path("resources/interview_cheatsheet.pdf").absolute())
    column_doc = str(Path("resources/IE00BM67HT60-ATB-FS-DE-2020-2-28.pdf").absolute())
    correctFormattedText = "[Data Structure Basics]\n\n\t[Array]\n\n\t\t[Definition:]\n\t\t\tStores data elements" \
                           " based on an sequential, most commonly 0 based, index."

    testDocument = None

    @classmethod
    def setUpClass(cls) -> None:
        parser = HierarchyParser()
        cls.testDocument = parser.parse_pdf(FileSource(cls.straight_forward_doc))

    def test_print_pretty_string(self):
        printer = PrettyStringPrinter()
        printed = printer.print(self.testDocument)
        self.assertTrue(self.correctFormattedText in printed)

    def test_print_pretty_file(self):
        printer = PrettyStringFilePrinter()

        file_path = Path("resources/parsed/interview_cheatsheet_pretty.txt")
        printed_file = printer.print(self.testDocument, file_path=str(file_path.absolute()))

        with open(printed_file, "r") as file:
            printed = "".join(file.readlines())
            self.assertTrue(self.correctFormattedText in printed)

    def test_print_json_string(self):
        printer = JsonStringPrinter()

        jsonString = printer.print(self.testDocument)

        decoded_document = StructuredPdfDocument.from_json(json.loads(jsonString))

        self.assertEqual(self.testDocument.elements[1].heading.text,
                         decoded_document.elements[1].heading.text)
        self.assertEqual(self.testDocument.elements[-1].heading.text,
                         decoded_document.elements[-1].heading.text)

        self.assertEqual("Array", decoded_document.elements[5].children[0].heading.text)
        self.assertEqual("Time Complexity:", decoded_document.elements[5].children[0].children[2].heading.text)

    def test_print_json_file(self):
        printer = JsonFilePrinter()

        file_path = Path("resources/parsed/interview_cheatsheet.json")
        printer.print(self.testDocument, file_path=str(file_path.absolute()))

        with open(file_path, "r") as file:
            decoded_document = StructuredPdfDocument.from_json(json.load(file))

            self.assertEqual(self.testDocument.elements[1].heading.text,
                             decoded_document.elements[1].heading.text)
            self.assertEqual(self.testDocument.elements[-1].heading.text,
                             decoded_document.elements[-1].heading.text)

            self.assertEqual("Array", decoded_document.elements[5].children[0].heading.text)
            self.assertEqual("Time Complexity:", decoded_document.elements[5].children[0].children[2].heading.text)
