import itertools
from unittest import TestCase

import pandas as pd

from pdfstructure.model import Element
from pdfstructure.style_analyser import count_sizes, PivotLogMapper
from pdfstructure.title_finder import StyleAnnotator, DocumentTitleExtractor, \
    clean_title
from pdfstructure.utils import element_generator, find_file, DocTypeFilter


class TestStyleMapping(TestCase):
    base_path = "/home/christian/Documents/data_recovery_katharina/pdf/"
    
    test_doc_path = base_path + "5650.pdf"
    test_doc_path_same_size = base_path + "6772.pdf"
    test_doc_path_two_size = base_path + "6376.pdf"
    test_doc_path_body_biggest = base_path + "21611.pdf"
    test_doc_path_body_biggest_2 = base_path + "6041.pdf"
    test_doc_path_body_biggest_3 = base_path + "6287.pdf"
    
    def test_mapper(self):
        distribution = count_sizes(element_generator(self.test_doc_path))
        sizeMapper = PivotLogMapper(distribution, bins=5)
        self.assertEqual(4, sizeMapper.borders.__len__())
        style_annotator = StyleAnnotator(sizemapper=sizeMapper, style_info=distribution)
        get_elements = element_generator(self.test_doc_path)
        with_style = style_annotator.process(get_elements)
        for data in with_style:
            # for element in style_annotator.process(page, self.distribution):
            self.assertIsInstance(data, Element)
    
    def test_header_selector(self):
        distribution = count_sizes(element_generator(file_path=self.test_doc_path))
        elements = element_generator(file_path=self.test_doc_path)
        
        extractor = DocumentTitleExtractor()
        title = extractor.process(distribution, elements)
        self.assertEqual('Outdoorpädagogik__„Fange_den_Stock“__„Schwebeast“__„Schlange“', title)
    
    def test_header_selector_same_size(self):
        extractor = DocumentTitleExtractor()
        distribution = count_sizes(element_generator(file_path=self.test_doc_path_same_size))
        elements = element_generator(file_path=self.test_doc_path_same_size)
        title = extractor.process(distribution, elements)
        self.assertEqual("Sportunterricht_2._Jhg_18.3.2020__Meine_Lieben!__Ihr_wisst,_dass_Ausdauertraining"
                         "_und_Bewegung_überhaupt_einen_wesentlichen__Beitrag_zur_Schönheit,_Fitness_und_Gesundheit_(Stärkung_des_Immunsystems,",
                         title)
    
    def test_header_selector_two_size(self):
        extractor = DocumentTitleExtractor()
        distribution = count_sizes(element_generator(file_path=self.test_doc_path_two_size))
        elements = element_generator(file_path=self.test_doc_path_two_size)
        title = extractor.process(distribution, elements)
        self.assertEqual("Aktuelle_Fragen_zur_Landwirtschaft", title)
    
    def test_header_selector_body_biggest(self):
        extractor = DocumentTitleExtractor()
        distribution = count_sizes(element_generator(file_path=self.test_doc_path_body_biggest))
        elements = element_generator(file_path=self.test_doc_path_body_biggest)
        title = extractor.process(distribution, elements)
        self.assertEqual('Test_Name___1._Erkenne_folgende_Bäume_an_ihren_Früchten:_4_P__a)_B)_c)_d)'
                         '__2._A)Zeichne_ein_Birkenblatt,_Eichenblatt_auf,_2P', title)
    
    def test_header_selector_body_biggest_2(self):
        extractor = DocumentTitleExtractor()
        distribution = count_sizes(element_generator(file_path=self.test_doc_path_body_biggest_2))
        elements = element_generator(file_path=self.test_doc_path_body_biggest_2)
        title = extractor.process(distribution, elements)
        self.assertEqual("„Liebenswerte_Heimat“__Sensibilisierung_über_die_Herkunft_der_Österr._Grundprodukte", title)
    
    def test_header_selector_body_biggest_3(self):
        extractor = DocumentTitleExtractor()
        distribution = count_sizes(element_generator(file_path=self.test_doc_path_body_biggest_3))
        elements = element_generator(file_path=self.test_doc_path_body_biggest_3)
        
        title = extractor.process(distribution, elements)
        self.assertEqual('Verdammt_lang_her_Andreas_Gabalier', title)
    
    def test_with_images(self):
        # todo, 13100
        extractor = DocumentTitleExtractor()
        distribution = count_sizes(element_generator(file_path=self.base_path + "13100.pdf"))
        elements = element_generator(file_path=self.base_path + "13100.pdf")
        
        title = extractor.process(distribution, elements)
        self.assertEqual('Frage_10_Nenne_und_beschreibe_3_heimische_Nadel_und_3_heimische_Laubbäume.', title)
    
    def test_excel(self):
        # todo, 13100
        extractor = DocumentTitleExtractor()
        distribution = count_sizes(element_generator(file_path=self.base_path + "20542.pdf"))
        elements = element_generator(file_path=self.base_path + "20542.pdf")
        
        title = extractor.process(distribution, elements)
        self.assertEqual('Schneidtechniken__Der_Wiegeschnitt__Konservieren_von_Obst:__Einfrieren', title)


class TestUtils(TestCase):
    
    def test_clean_title(self):
        self.assertEqual("_hello_", clean_title("______hello ___ "))
        longer = "______helllo hello world " \
                 "//// woelda dsfsadfsdfsadfasdfasdfasd" \
                 "fasdfsadfasdfasdfasdfsadfsdafasdfasdfsadfsdf hello world what is going on___ "
        
        self.assertEqual(100, len(clean_title(longer)))
    
    @staticmethod
    def generate_annotated_lines(file_path):
        """
        yields paragraph detected by pdfminer annotated with detected & mapped style information
        """
        element_gen = element_generator(file_path)
        distribution = count_sizes(element_gen)
        sizeMapper = PivotLogMapper(distribution)
        style_annotator = StyleAnnotator(sizemapper=sizeMapper, style_info=distribution)
        
        elements = element_generator(file_path)
        with_style = style_annotator.process(elements)
        
        yield from with_style
    
    def test_fontnames(self):
        fonts = []
        for file in itertools.islice(find_file(TestStyleMapping.base_path, DocTypeFilter(endings=("pdf"))), 30):
            if not file.is_file():
                continue
            file_path = str(file.absolute())
            distribution = count_sizes(element_generator(file_path))
            
            sizeMapper = PivotLogMapper(distribution)
            style_annotator = StyleAnnotator(sizemapper=sizeMapper, style_info=distribution)
            
            elements = element_generator(file_path)
            with_style = style_annotator.process(elements)
            
            for data in with_style:
                fonts.append(data["style"].font_name)
        ds = pd.Series(fonts, name="fonts", dtype=str)
        boldmasked = ds.loc[ds.apply(lambda x: "bold" in x.lower())]
        italic = ds.loc[ds.apply(lambda x: "italic" in x.lower())]
