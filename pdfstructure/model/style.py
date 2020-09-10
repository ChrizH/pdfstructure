from enum import IntEnum, auto


class TextSize(IntEnum):
    """
    Used to annotate extracted paragraphs with a predefined range of possible FontSize.
    Convenient to perform style-based grouping of similar pieces of text.
    """
    xsmall = auto()
    small = auto()
    middle = auto()
    large = auto()
    xlarge = auto()

    @classmethod
    def from_range(cls, borders: tuple, value: int):
        if value < borders[0]:
            return cls.xsmall
        elif borders[0] <= value < borders[1]:
            return cls.small
        elif borders[1] <= value < borders[2]:
            return cls.middle
        elif borders[2] <= value < borders[3]:
            return cls.large
        elif value >= borders[3]:
            return cls.xlarge


class Style:
    """
    Extracted paragraphs get annotated with found font-style information.
    """

    def __init__(self, bold, italic, font_name, mapped_font_size: TextSize, mean_size: float, max_size: float):
        self.bold = bold
        self.italic = italic
        self.font_name = font_name
        self.mapped_font_size = mapped_font_size
        self.mean_size = mean_size
        self.max_size = max_size

    @classmethod
    def from_json(cls, data: dict):
        mapped_size = TextSize[data["mapped_font_size"]]
        data["mapped_font_size"] = mapped_size
        return cls(**data)

    def __gt__(self, other):
        if isinstance(other, Style):
            return self.mapped_font_size > other.mapped_font_size or \
                   self.mapped_font_size == other.mapped_font_size and self.bold and not other.bold
        return False

    def __lt__(self, other):
        if isinstance(other, Style):
            return self.mapped_font_size < other.mapped_font_size or \
                   self.mapped_font_size == other.mapped_font_size and not self.bold and other.bold
        return False

    def __eq__(self, other):
        if isinstance(other, Style):
            return self.mapped_font_size == other.mapped_font_size and \
                   self.bold == other.bold
        else:
            return False
