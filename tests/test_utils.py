from pathlib import Path
from unittest import TestCase

from pdfstructure.utils import element_generator, word_generator


class Test(TestCase):
    test_path_1 = str(Path("resources/interview_cheatsheet.pdf").absolute())
    
    def test_word_generator(self):
        elements = element_generator(self.test_path_1)
        
        # 1st text container
        element = next(elements)
        words = list(word_generator(element))
        self.assertEqual(1, len(words))
        self.assertEqual('31/10/2019', " ".join(words))
        
        # 2nd text container
        element = next(elements)
        words = list(word_generator(element))
        self.assertEqual(31, len(words))
        self.assertEqual("This is my technical interview cheat sheet.", " ".join(words[:7]))
