from pathlib import Path
from unittest import TestCase

from pdfstructure.hierarchy.parser import HierarchyParser
from pdfstructure.hierarchy.traversal import traverse_in_order, traverse_level_order, get_document_depth, \
    traverse_inorder_sections_with_content
from pdfstructure.model.document import DanglingTextSection
from pdfstructure.source import FileSource


class TestDocumentTraversal(TestCase):
    straight_forward_doc = str(Path("resources/interview_cheatsheet.pdf").absolute())
    same_style_doc = str(Path("resources/SameStyleOnly.pdf").absolute())
    test_doc = None
    test_doc_same_style = None

    @classmethod
    def setUpClass(cls) -> None:
        parser = HierarchyParser()
        cls.test_doc_same_style = parser.parse_pdf(FileSource(cls.same_style_doc))

        cls.test_doc = parser.parse_pdf(FileSource(cls.straight_forward_doc))

    def test_get_height(self):
        h = get_document_depth(self.test_doc)
        self.assertEqual(4, h)

    def test_traverse_in_order(self):
        elements = [element for element in traverse_in_order(self.test_doc)]
        self.assertEqual(251, len(elements))
        self.assertEqual("Data Structure Basics", elements[19].heading.text)
        self.assertEqual("Array", elements[20].heading.text)
        self.assertEqual("Definition:", elements[21].heading.text)

    def test_traverse_level_order(self):
        elements = [element for element in traverse_level_order(self.test_doc)]

        self.assertEqual(251, len(elements))

        self.assertEqual("Data Structure Basics", elements[5].heading.text)
        self.assertEqual("Search Basics", elements[6].heading.text)
        self.assertEqual("Efficient Sorting Basics", elements[7].heading.text)
        self.assertEqual("Basic Types of Algorithms", elements[8].heading.text)

        self.assertEqual("https://gist.github.com/TSiege/"
                         "cbb0507082bb18ff7e4b#ﬁle-the-technical-interview-cheat-sheet-md", elements[-2].heading.text)
        self.assertEqual("6/18", elements[-1].heading.text)

    def test_traverse_level_order_max_depth(self):
        mid_level = get_document_depth(self.test_doc) / 2

        level_iterator = traverse_level_order(self.test_doc, max_depth=mid_level)
        elements = [element for element in level_iterator]

        self.assertEqual(35, len(elements))

        self.assertEqual("Data Structure Basics", elements[5].heading.text)
        self.assertEqual("Search Basics", elements[6].heading.text)
        self.assertEqual("Efficient Sorting Basics", elements[7].heading.text)
        self.assertEqual("Basic Types of Algorithms", elements[8].heading.text)

        self.assertEqual("Recursive Algorithms", elements[-3].heading.text)
        self.assertEqual("Iterative Algorithms", elements[-2].heading.text)
        self.assertEqual("Greedy Algorithm", elements[-1].heading.text)

    def test_test_level_order_but_flat_structure(self):
        level_iterator = traverse_level_order(self.test_doc_same_style)
        elements = [element for element in level_iterator]
        self.assertEqual(5, len(elements))
        self.assertIsInstance(elements[0], DanglingTextSection)
        self.assertEqual("Lorem Ipsum.", elements[1].heading_text)

    def test_test_in_order_but_flat_structure(self):
        level_iterator = traverse_in_order(self.test_doc_same_style)
        elements = [element for element in level_iterator]
        self.assertEqual(5, len(elements))
        self.assertIsInstance(elements[0], DanglingTextSection)
        self.assertEqual("Lorem Ipsum.", elements[1].heading_text)

    def test_retrieve_sections_with_content(self):
        elements = [element for element in traverse_inorder_sections_with_content(self.test_doc)]
        print(elements)
