from unittest import TestCase

from pdfminer.layout import LTChar, LTTextBoxHorizontal, LTTextLineHorizontal

from pdfstructure.hierarchy.headercompare import condition_h2_extends_h1, condition_h1_enum_h2_not
from pdfstructure.model.document import TextElement, Section
from pdfstructure.model.style import Style, TextSize


class TestSubHeaderConditions(TestCase):
    style_middle_bold = Style(bold=True, italic=True, font_name="test-font",
                              mapped_font_size=TextSize.middle,
                              mean_size=10, max_size=15)

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
                               style=self.style_middle_bold)

        element2 = TextElement(text_container=self.create_container("1.1.2 This is a subheader of 1.1"),
                               style=self.style_middle_bold)

        self.assertTrue(condition_h2_extends_h1(Section(element1), Section(element2)))

    def test_condition_enumeration__elements_with_same_style(self):
        h1 = TextElement(text_container=self.create_container("1.1 This is a test header"),
                         style=self.style_middle_bold)

        subheader = TextElement(text_container=self.create_container("This is a subheader of 1.1"),
                                style=self.style_middle_bold)

        neighbor_element = TextElement(text_container=self.create_container("1.2 this is NOT a subheader of 1.1"),
                                       style=self.style_middle_bold)

        self.assertTrue(condition_h1_enum_h2_not(Section(h1), Section(subheader)))
        self.assertFalse(condition_h1_enum_h2_not(Section(h1), Section(neighbor_element)))
