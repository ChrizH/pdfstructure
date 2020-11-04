from pathlib import Path
from unittest import TestCase

from pdfstructure.hierarchy.parser import HierarchyParser
from pdfstructure.hierarchy.traversal import traverse_inorder_sections_with_content
from pdfstructure.printer import PrettyStringPrinter as txtPrinter
from pdfstructure.source import FileSource


class TestExamples(TestCase):
    parser = HierarchyParser()

    def test_count_paragraph_words(self):
        test_file = str(Path("resources/lorem.pdf"))
        document = self.parser.parse_pdf(FileSource(file_path=test_file))
        assert_token_order = [50, 100, 150]
        for level, title, content in traverse_inorder_sections_with_content(document):
            prefix = txtPrinter.get_title_prefix(level)
            tokens = content.split()
            self.assertEqual(assert_token_order.pop(0), len(tokens))
            print("{}{};\twords: {}".format(prefix, title, len(tokens)))

    def test_load_book(self):
        book_path = Path("resources/interview_cheatsheet.pdf")
        document = self.parser.parse_pdf(FileSource(file_path=str(book_path)))

        for level, title, content in traverse_inorder_sections_with_content(document):
            prefix = txtPrinter.get_title_prefix(level)
            print("{}{};\twords: {}".format(prefix, title, len(content.split())))
