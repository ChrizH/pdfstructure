from pathlib import Path
from unittest import TestCase

from pdfstructure.hierarchy.parser import HierarchyParser
from pdfstructure.hierarchy.traversal import traverse_in_order, traverse_level_order, get_document_depth
from pdfstructure.source import FileSource


class TestDocumentTraversal(TestCase):
    straight_forward_doc = str(Path("resources/interview_cheatsheet.pdf").absolute())
    test_doc = None

    @classmethod
    def setUpClass(cls) -> None:
        path = cls.straight_forward_doc
        parser = HierarchyParser()
        source = FileSource(path)
        cls.test_doc = parser.parse_pdf(source)

    def test_get_height(self):
        h = get_document_depth(self.test_doc)
        self.assertEqual(4, h)

    def test_traverse_in_order(self):
        elements = [element for element in traverse_in_order(self.test_doc)]
        self.assertEqual(78, len(elements))
        self.assertEqual("Data Structure Basics", elements[7].heading.text)
        self.assertEqual("Array", elements[8].heading.text)
        self.assertEqual("Definition:", elements[9].heading.text)

    def test_traverse_level_order(self):
        elements = [element for element in traverse_level_order(self.test_doc)]

        self.assertEqual(78, len(elements))

        self.assertEqual("Data Structure Basics", elements[5].heading.text)
        self.assertEqual("Search Basics", elements[6].heading.text)
        self.assertEqual("Efficient Sorting Basics", elements[7].heading.text)
        self.assertEqual("Basic Types of Algorithms", elements[8].heading.text)

        self.assertEqual("Owner", elements[-2].heading.text)
        self.assertEqual("TSiege commented on 2 May 2014", elements[-1].heading.text)

    def test_traverse_level_order_max_depth(self):
        mid_level = get_document_depth(self.test_doc) / 2

        level_iterator = traverse_level_order(self.test_doc, max_depth=mid_level)
        elements = [element for element in level_iterator]

        self.assertEqual(23, len(elements))

        self.assertEqual("Data Structure Basics", elements[5].heading.text)
        self.assertEqual("Search Basics", elements[6].heading.text)
        self.assertEqual("Efficient Sorting Basics", elements[7].heading.text)
        self.assertEqual("Basic Types of Algorithms", elements[8].heading.text)

        self.assertEqual("Recursive Algorithms", elements[-3].heading.text)
        self.assertEqual("Iterative Algorithms", elements[-2].heading.text)
        self.assertEqual("Greedy Algorithm", elements[-1].heading.text)
