from unittest import TestCase

from pdfstructure.hierarchy import HierarchyLineParser
from tests.test_style_mapper import TestUtils


class TestHierarchy(TestCase):
    base_path = "/home/christian/Documents/data_recovery_katharina/pdf/"
    
    def test_grouping(self):
        test_doc = self.base_path + "5648.pdf"
        parser = HierarchyLineParser()
        lines_gen = TestUtils.generate_annotated_lines(test_doc)
        structured = parser.process(lines_gen)
        self.assertEqual(13, structured[0].children.__len__())
        
        
