from pathlib import Path
from unittest import TestCase

from pdfminer.layout import LTTextLineHorizontal, LTChar, LTTextBoxHorizontal

from pdfstructure.hierarchy import HierarchyLineParser, condition_h2_extends_h1
from pdfstructure.model import PdfElement, Style, ParentPdfElement
from pdfstructure.style_analyser import TextSize
from tests.test_title_finder import TestUtils


class TestHierarchy(TestCase):
    base_path = "/home/christian/Documents/data_recovery_katharina/pdf/"
    doc_with_columns = str(Path("resources/IE00BM67HT60-ATB-FS-DE-2020-2-28.pdf").absolute())
    straight_forward_doc = str(Path("resources/interview_cheatsheet.pdf").absolute())

    def test_grouping(self):
        test_doc = self.base_path + "5648.pdf"
        parser = HierarchyLineParser()
        lines_gen = TestUtils.generate_annotated_lines(test_doc)
        structured = parser.process(lines_gen)
        self.assertEqual(13, structured.elements[0].children.__len__())

    def test_grouping_bold_key_and_size(self):
        parser = HierarchyLineParser()
        elements_gen = TestUtils.generate_annotated_lines(self.straight_forward_doc)
        document = parser.process(elements_gen)
        self.assertEqual(len(document.elements), 9)

    def test_grouping_bold_columns(self):
        parser = HierarchyLineParser()
        elements_gen = TestUtils.generate_annotated_lines(self.doc_with_columns)
        document = parser.process(elements_gen)
        self.assertTrue(document)


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
        element1 = PdfElement(data=self.create_container("1.1 This is a test header"),
                              style=Style(bold=True, italic=True, font_name="test-font",
                                          mapped_font_size=TextSize.middle,
                                          mean_size=10))
    
        element2 = PdfElement(data=self.create_container("1.1.2 This is a subheader of 1.1"),
                              style=Style(bold=True, italic=True, font_name="test-font",
                                          mapped_font_size=TextSize.middle,
                                          mean_size=10))
    
        self.assertTrue(condition_h2_extends_h1(ParentPdfElement(element1), ParentPdfElement(element2)))
