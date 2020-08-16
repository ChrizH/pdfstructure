from unittest import TestCase

# import unittest.mock
import mock

from pdfstructure.style_analyser import TextSize, LinearSizeMapper
from pdfstructure.style_analyser import count_sizes, StyleDistribution


# from unittest.mock import Mock, patch, PropertyMock


class TestSizeMapper(TestCase):
    scaler = LinearSizeMapper()
    
    def test_mapping(self):
        size_range = (1, 5, 6, 10, 20, 100)
        lmin, lmax = min(size_range), max(size_range)
        self.assertEqual(TextSize.xsmall, self.scaler.translate(-10, lmin, lmax, ))
        self.assertEqual(TextSize.xsmall, self.scaler.translate(0, lmin, lmax, ))
        self.assertEqual(TextSize.xsmall, self.scaler.translate(1, lmin, lmax, ))
        self.assertEqual(TextSize.small, self.scaler.translate(6, lmin, lmax, ))
        self.assertEqual(TextSize.small, self.scaler.translate(10, lmin, lmax, ))
        self.assertEqual(TextSize.middle, self.scaler.translate(50, lmin, lmax, ))
        self.assertEqual(TextSize.large, self.scaler.translate(70, lmin, lmax, ))
        self.assertEqual(TextSize.xlarge, self.scaler.translate(90, lmin, lmax, ))
        self.assertEqual(TextSize.xlarge, self.scaler.translate(100, lmin, lmax, ))
        self.assertEqual(TextSize.xlarge, self.scaler.translate(120, lmin, lmax, ))


class TestStyleAnalyser(TestCase):
    test_path_1 = "/home/christian/work/private/data-recovery/namefinder/samples/sub/interview_cheatsheet.pdf"
    test_path_2 = "/home/christian/work/private/data-recovery/namefinder/samples/IE00BM67HT60-ATB-FS-DE-2020-2-28.pdf"
    test_ppt = "/home/christian/work/private/data-recovery/namefinder/samples/samplepptx.pdf"
    
    test_same_size = "/home/christian/Documents/data_recovery_katharina/pdf/20524.pdf"
    test_doc_one_h = "/home/christian/Documents/data_recovery_katharina/pdf/5650.pdf"
    
    
    def test_title_size_ppt(self):
        distribution = count_sizes(self.test_ppt)
        self.assertFalse(distribution.is_empty)
        self.assertAlmostEqual(43.5, distribution.title_min_size, delta=0.1)
        self.assertAlmostEqual(32, distribution.body_size, delta=0.1)
        self.assertAlmostEqual(44, distribution.title_size, delta=0.1)
        self.assertEqual(8, distribution.amount)
    
    @mock.patch("pdfstructure.style_analyser.StyleDistribution.title_min_size", new_callable=mock.PropertyMock)
    @mock.patch("pdfstructure.style_analyser.StyleDistribution.title_size", new_callable=mock.PropertyMock)
    @mock.patch("pdfstructure.style_analyser.StyleDistribution.body_size", new_callable=mock.PropertyMock)
    def test_title_extraction_ppt(self, title_min_size, title_size, body_size):
        title_min_size.return_value = 43.5
        title_size.return_value = 44
        body_size.return_value = 32
        
        style_distribution = StyleDistribution()
        # mock values
        title = extract_title(self.test_ppt, style_distribution)
        self.assertEqual('ANNOUNCEMENT__TSiege___The_Technical_Interview_Cheat_Sheet.md', title)
    
    def test_title_size_1(self):
        distribution = count_sizes(self.test_path_1)
        self.assertFalse(distribution.is_empty)
        self.assertAlmostEqual(8.5, distribution.body_size, delta=0.1)
        self.assertAlmostEqual(9.6, distribution.title_min_size, delta=0.1)
        self.assertAlmostEqual(12.8, distribution.title_size, delta=0.1)
        self.assertEqual(8, distribution.amount)
    
    # @patch("style_info.title_min_size", new_callable=PropertyMock())
    @mock.patch("pdfstructure.style_analyser.StyleDistribution.title_min_size", new_callable=mock.PropertyMock)
    @mock.patch("pdfstructure.style_analyser.StyleDistribution.title_size", new_callable=mock.PropertyMock)
    @mock.patch("pdfstructure.style_analyser.StyleDistribution.body_size", new_callable=mock.PropertyMock)
    def test_title_extraction_1(self, title_min_size, title_size, body_size):
        title_min_size.return_value = 9.6
        title_size.return_value = 12.8
        body_size.return_value = 8.5
        
        style_distribution = StyleDistribution()
        # mock values
        title = extract_title(self.test_path_1, style_distribution)
        self.assertEqual('ANNOUNCEMENT__TSiege___The_Technical_Interview_Cheat_Sheet.md', title)
    
    def test_title_size_2(self):
        distribution = count_sizes(self.test_path_2)
        self.assertFalse(distribution.is_empty)
        self.assertAlmostEqual(6, distribution.body_size, delta=0.1)
        self.assertAlmostEqual(7, distribution.title_min_size, delta=0.1)
        self.assertAlmostEqual(18, distribution.title_size, delta=0.1)
        self.assertEqual(18, distribution.amount)
    
    # @patch("style_info.title_min_size", new_callable=PropertyMock())
    @mock.patch("pdfstructure.style_analyser.StyleDistribution.title_min_size", new_callable=mock.PropertyMock)
    @mock.patch("pdfstructure.style_analyser.StyleDistribution.title_size", new_callable=mock.PropertyMock)
    @mock.patch("pdfstructure.style_analyser.StyleDistribution.body_size", new_callable=mock.PropertyMock)
    def test_title_extraction_2(self, title_min_size, title_size, body_size):
        title_min_size.return_value = 7
        title_size.return_value = 18
        body_size.return_value = 6
        
        style_distribution = StyleDistribution()
        # mock values
        title = extract_title(self.test_path_2, style_distribution)
        self.assertEqual('Xtrackers_MSCI_World_Information_Technology_UCITS___MARKETING_MATERIAL', title)
