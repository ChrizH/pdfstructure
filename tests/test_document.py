import json
from pathlib import Path
from unittest import TestCase

from pdfstructure.model.document import StructuredPdfDocument


class TestSection(TestCase):

    def test_full_content(self):
        with open(str(Path("resources/parsed/interview_cheatsheet.json").absolute()), "r") as fp:
            json_string = json.load(fp)
            document = StructuredPdfDocument.from_json(json_string)
            text = document.text

            expected_newline_merged_subsections_excerpt = "Greedy Algorithm\nDefinition:\nAn algorithm that, while"

            self.assertTrue(expected_newline_merged_subsections_excerpt in text)
