from pathlib import Path
from unittest import TestCase

from pdfminer.layout import LTTextLineHorizontal, LTChar, LTTextBoxHorizontal
from pdfstructure.hierarchy.headercompare import condition_h2_extends_h1
from pdfstructure.hierarchy.parser import HierarchyParser
from pdfstructure.model import TextElement, Style, Section, TextSize
from pdfstructure.source import FileSource
from tests import helper


class TestHierarchy(TestCase):
    base_path = "/home/christian/Documents/data_recovery_katharina/pdf/"
    doc_with_columns = str(Path("resources/IE00BM67HT60-ATB-FS-DE-2020-2-28.pdf").absolute())
    straight_forward_doc = str(Path("resources/interview_cheatsheet.pdf").absolute())

    def test_hierarchy_pdf_parser(self):
        path = self.straight_forward_doc
        parser = HierarchyParser()
        source = FileSource(path)
        pdf = parser.parse_pdf(source)
        self.assertTrue(pdf.elements)

        ## check that all header & sub headers are detected
        headers = []
        for header in pdf.traverse():
            headers.append(header.heading.text)
        self.assertEqual(78, len(headers))

    def test_grouping(self):
        test_doc = self.base_path + "5648.pdf"
        parser = HierarchyParser()
        lines_gen = helper.generate_annotated_lines(test_doc)
        structured = parser.create_hierarchy(lines_gen)
        self.assertEqual(13, structured[0].children.__len__())

    def test_grouping_bold_key_and_size(self):
        parser = HierarchyParser()
        elements_gen = helper.generate_annotated_lines(self.straight_forward_doc)
        elements = parser.create_hierarchy(elements_gen)
        self.assertEqual(len(elements), 9)

    def test_grouping_bold_columns(self):
        parser = HierarchyParser()
        elements_gen = helper.generate_annotated_lines(self.doc_with_columns)
        elements = parser.create_hierarchy(elements_gen)
        self.assertEqual("Xtrackers MSCI World Information Technology UCITS ETF 1C", elements[1].heading.text)
        self.assertEqual(7, elements[1].children.__len__())


class TestSubHeaderConditions(TestCase):
    class TestFont:
        fontname = "Test"

        def is_vertical(self):
            return True

    def create_char(self, text):
        return LTChar((1, 2, 3, 4, 5, 6), TestSubHeaderConditions.TestFont(), 10, 10, 10, text, 10, (1, 1), 10, "")

    def create_container(self, text):
        box = LTTextBoxHorizontal()
        line = LTTextLineHorizontal(0)
        for c in text:
            line.add(self.create_char(c))
        box.add(line)
        return box

    def test_condition_h2_extends_h1(self):
        element1 = TextElement(text_container=self.create_container("1.1 This is a test header"),
                               style=Style(bold=True, italic=True, font_name="test-font",
                                           mapped_font_size=TextSize.middle,
                                           mean_size=10))

        element2 = TextElement(text_container=self.create_container("1.1.2 This is a subheader of 1.1"),
                               style=Style(bold=True, italic=True, font_name="test-font",
                                           mapped_font_size=TextSize.middle,
                                           mean_size=10))

        self.assertTrue(condition_h2_extends_h1(Section(element1), Section(element2)))
