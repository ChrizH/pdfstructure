from pathlib import Path
from unittest import TestCase

from pdfminer.layout import LTTextLineHorizontal, LTChar, LTTextBoxHorizontal

from pdfstructure.hierarchy import HierarchyLineParser, condition_h2_extends_h1
from pdfstructure.model import Element, Style
from pdfstructure.style_analyser import TextSize
from tests.test_title_finder import TestUtils


class TestHierarchy(TestCase):
    base_path = "/home/christian/Documents/data_recovery_katharina/pdf/"
    
    def test_grouping(self):
        test_doc = self.base_path + "5648.pdf"
        parser = HierarchyLineParser()
        lines_gen = TestUtils.generate_annotated_lines(test_doc)
        structured = parser.process(lines_gen)
        self.assertEqual(13, structured[0].children.__len__())
    
    def test_nested_bold_key(self):
        test_doc = str(Path("resources/interview_cheatsheet.pdf").absolute())
        parser = HierarchyLineParser()
        elements_gen = TestUtils.generate_annotated_lines(test_doc)
        structured, flat = parser.process(elements_gen)
        t = "\n".join([str(e) for e in structured])
        self.assertEqual(len(structured), 9)


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
        h1 = Element(data=self.create_container("1.1 This is a test header"),
                     style=Style(bold=True, italic=True, fontname="test-font", fontsize=TextSize.middle))
        
        h2 = Element(data=self.create_container("1.1.2 This is a subheader of 1.1"),
                     style=Style(bold=True, italic=True, fontname="test-font", fontsize=TextSize.middle))
        
        self.assertTrue(condition_h2_extends_h1(h1, h2))
