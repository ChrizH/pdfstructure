from pathlib import Path
from unittest import TestCase

from pdfstructure.hierarchy.parser import HierarchyParser
from pdfstructure.hierarchy.traversal import traverse_in_order
from pdfstructure.model.document import Section
from pdfstructure.printer import PrettyStringPrinter
from pdfstructure.source import FileSource


class TestExamples(TestCase):
    parser = HierarchyParser()

    def extract_contents(self, document):
        """
        retrieve all sections in order with their respective title & section content.
        @param document:
        @return:
        """
        for section in filter(lambda sec: len(sec.children) > 0, traverse_in_order(document)):
            children: Section
            tokens = []
            for children in section.children:
                if children.children:
                    continue
                tokens.extend(children.heading_text.split())
            yield section.level, section.heading_text, tokens

    def test_count_paragraph_words(self):
        test_file = str(Path("resources/lorem.pdf"))
        document = self.parser.parse_pdf(FileSource(file_path=test_file))
        for count, (level, header, tokens) in enumerate(self.extract_contents(document)):
            prefix = PrettyStringPrinter.get_title_prefix(level)
            print("{}{}; words: {}".format(prefix, header, len(tokens)))

    def test_load_book(self):
        book_path = Path("resources/interview_cheatsheet.pdf")
        document = self.parser.parse_pdf(FileSource(file_path=str(book_path)))

        for count, (level, header, tokens) in enumerate(self.extract_contents(document)):
            prefix = PrettyStringPrinter.get_title_prefix(level)
            print("{}{}; words: {}".format(prefix, header, len(tokens)))
