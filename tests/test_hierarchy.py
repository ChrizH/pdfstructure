from pathlib import Path
from unittest import TestCase

from pdfminer.high_level import extract_text

from pdfstructure.hierarchy.parser import HierarchyParser
from pdfstructure.model.document import DanglingTextSection
from pdfstructure.printer import PrettyStringPrinter
from pdfstructure.source import FileSource


class TestHierarchy(TestCase):
    doc_with_columns = str(Path("resources/IE00BM67HT60-ATB-FS-DE-2020-2-28.pdf").absolute())
    straight_forward_doc = str(Path("resources/interview_cheatsheet.pdf").absolute())
    nested_doc_bold_title = str(Path("resources/5648.pdf").absolute())

    same_style_doc = str(Path("resources/SameStyleOnly.pdf").absolute())
    same_size_bold_header = str(Path("resources/SameSize_BoldTitle.pdf").absolute())
    same_size_enum_header = str(Path("resources/SameSize_EnumeratedTitle.pdf").absolute())
    paper = str(Path("resources/paper.pdf").absolute())
    parser = HierarchyParser()

    def test_no_hierarchy_detected(self):
        pdf = self.parser.parse_pdf(FileSource(self.same_style_doc))
        self.assertEqual(4, len(pdf.elements[0].children))

        self.assertIsInstance(pdf.elements[0], DanglingTextSection)

    def test_reading_order_paper_format(self):
        pdf = self.parser.parse_pdf(FileSource(self.paper))
        self.assertEqual(1, len(pdf.elements))
        self.assertEqual("5 Experiments: Passage Retrieval",pdf.elements[0].children[-2].heading_text)
        self.assertEqual("6 Experiments: Question Answering",pdf.elements[0].children[-1].heading_text)

    def test_hierarchy_bold_title(self):
        pdf = self.parser.parse_pdf(FileSource(self.same_size_bold_header))
        self.assertEqual(2, len(pdf.elements))
        self.assertEqual("Lorem Ipsum.", pdf.elements[0].heading.text)
        self.assertEqual("Appendix", pdf.elements[1].heading.text)

    def test_hierarchy_pdf_parser(self):
        path = self.straight_forward_doc
        source = FileSource(path)
        pdf = self.parser.parse_pdf(source)
        self.assertEqual(9, len(pdf.elements))
        self.assertEqual("Data Structure Basics", pdf.elements[5].heading.text)
        self.assertEqual("Basic Types of Algorithms", pdf.elements[8].heading.text)
        self.assertEqual(4, pdf.elements[8].heading.page)

    def test_grouping(self):
        test_doc = self.nested_doc_bold_title
        doc = self.parser.parse_pdf(FileSource(test_doc))
        self.assertEqual(1, doc.elements.__len__())
        self.assertEqual(13, doc.elements[0].children.__len__())
        self.assertEqual("Outdoorpädagogik", doc.elements[0].heading.text)
        self.assertEqual("„Fange den Stock“", doc.elements[0].children[0].heading.text)

    def test_grouping_bold_key_and_size(self):
        doc = self.parser.parse_pdf(FileSource(self.straight_forward_doc))
        self.assertEqual(len(doc.elements), 9)

    def skip_test_grouping_bold_columns(self):
        doc = self.parser.parse_pdf(FileSource(self.doc_with_columns))
        self.assertEqual("Xtrackers MSCI World Information Technology UCITS ETF 1C", doc.elements[1].heading.text)


class TestComapreFrameworks(TestCase):
    def skip_test_pdftotext(self):
        path = TestHierarchy.straight_forward_doc

        with open(path, "rb") as f:
            pdf = pdftotext.PDF(f)

        print("\n\n".join(pdf))

    def skip_test_pdfminer_high_level(self):
        text = extract_text(TestHierarchy.straight_forward_doc, laparams=None)
        print(text)

    def skip_test_pdfminer(self):
        from io import StringIO

        from pdfminer.converter import TextConverter
        from pdfminer.layout import LAParams
        from pdfminer.pdfdocument import PDFDocument
        from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
        from pdfminer.pdfpage import PDFPage
        from pdfminer.pdfparser import PDFParser

        output_string = StringIO()
        with open(TestHierarchy.straight_forward_doc, 'rb') as in_file:
            parser = PDFParser(in_file)
            doc = PDFDocument(parser)
            rsrcmgr = PDFResourceManager()
            device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            for page in PDFPage.create_pages(doc):
                interpreter.process_page(page)

        print(output_string.getvalue())

    def skip_test_pdfstructure(self):
        path = TestHierarchy.straight_forward_doc
        parser = HierarchyParser()
        source = FileSource(path)
        pdf = parser.parse_pdf(source)
        print(PrettyStringPrinter().print(pdf))
