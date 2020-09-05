from pathlib import Path
from unittest import TestCase

from pdfstructure.hierarchy.parser import HierarchyParser
from pdfstructure.model.document import DanglingTextSection
from pdfstructure.source import FileSource
from tests import helper


class TestHierarchy(TestCase):
    doc_with_columns = str(Path("resources/IE00BM67HT60-ATB-FS-DE-2020-2-28.pdf").absolute())
    straight_forward_doc = str(Path("resources/interview_cheatsheet.pdf").absolute())
    nested_doc_bold_title = str(Path("resources/5648.pdf").absolute())

    same_style_doc = str(Path("resources/SameStyleOnly.pdf").absolute())
    same_size_bold_header = str(Path("resources/SameSize_BoldTitle.pdf").absolute())
    same_size_enum_header = str(Path("resources/SameSize_EnumeratedTitle.pdf").absolute())

    def test_no_hierarchy_detected(self):
        parser = HierarchyParser()
        pdf = parser.parse_pdf(FileSource(self.same_style_doc))
        self.assertEqual(4, len(pdf.elements[0].children))

        self.assertIsInstance(pdf.elements[0], DanglingTextSection)

    def test_hierarchy_bold_title(self):
        parser = HierarchyParser()
        pdf = parser.parse_pdf(FileSource(self.same_size_bold_header))
        self.assertEqual(2, len(pdf.elements))
        self.assertEqual("Lorem Ipsum.", pdf.elements[0].heading.text)
        self.assertEqual("Appendix", pdf.elements[1].heading.text)

    def test_hierarchy_pdf_parser(self):
        path = self.straight_forward_doc
        parser = HierarchyParser()
        source = FileSource(path)
        pdf = parser.parse_pdf(source)
        self.assertEqual(9, len(pdf.elements))
        self.assertEqual("Data Structure Basics", pdf.elements[5].heading.text)

    def test_grouping(self):
        test_doc = self.nested_doc_bold_title
        parser = HierarchyParser()
        lines_gen = helper.generate_annotated_lines(test_doc)
        structured = parser.create_hierarchy(lines_gen)
        self.assertEqual(1, structured.__len__())
        self.assertEqual(12, structured[0].children.__len__())
        self.assertEqual("Outdoorpädagogik", structured[0].heading.text)
        self.assertEqual("„Fange den Stock“", structured[0].children[0].heading.text)

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
