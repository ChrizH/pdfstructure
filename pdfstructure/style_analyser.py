# class SizeDistro:
import itertools
from collections import Counter

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextLine, LTChar


class StyleDistribution:
    
    def __init__(self, data=None):
        """
        
        :type data: Counter
        :param data:
        """
        if data:
            self._data = data
            self._body_size = data.most_common(1)[0][0]
            self._title_size = max(self._data.keys())
            self._title_min_size = self.get_min_size(data, self._body_size, self._title_size)
            self._min_found_size, self._max_found_size = min(data.keys()), max(data.keys())
    
    def norm_data(self):
        # normalise counts with total amount of collected values
        # normalise each key value against max found key value (size)
        # normalise X & Y
        normalised = {}
        amount_items =  self.amount_values
        amount_sizes = self.amount_sizes
        
        for size in self.data:
            normalised[size / amount_sizes] = self.data[size] / amount_items
        
        return normalised
    
    @property
    def min_found_size(self):
        return self._min_found_size
    
    @property
    def max_found_size(self):
        return self._max_found_size
    
    @staticmethod
    def get_min_size(data: Counter, body_size, title_size):
        if len(data) > 2:
            tmin = sorted(data.keys(), reverse=True)[:3][-1]
            return tmin if tmin > body_size else title_size - 0.5
        else:
            return title_size - 0.5
    
    @property
    def body_size(self):
        return self._body_size
    
    @property
    def title_min_size(self):
        return self._title_min_size
    
    @property
    def title_size(self):
        return self._title_size
    
    @property
    def is_empty(self):
        return not self._data
    
    @property
    def amount_values(self):
        return sum(self._data.values(), 0.0)
    
    @property
    def amount_sizes(self):
        """
        amount of found sizes
        :return:
        """
        return len(self._data)
    
    @property
    def data(self) -> Counter:
        return self._data.copy()


import math
from enum import auto, IntEnum, Enum


class TextSize(IntEnum):
    xsmall = auto()
    small = auto()
    middle = auto()
    large = auto()
    xlarge = auto()
    
    @classmethod
    def from_range(cls, borders: tuple, value: int):
        if value < borders[0]:
            return cls.xsmall
        elif value >= borders[0] and value < borders[1]:
            return cls.small
        elif value >= borders[1] and value < borders[2]:
            return cls.middle
        elif value >= borders[2] and value < borders[3]:
            return cls.large
        elif value >= borders[3]:
            return cls.xlarge


class SizeMapper:
    
    def translate(self, target_enum: Enum, style_info: StyleDistribution, value) -> Enum:
        pivot = style_info.data.most_common(1)


class PivotLogMapper(SizeMapper):
    def __init__(self, style_info: StyleDistribution, bins=5):
        self.bins = bins
        self.borders = []
        # find pivot
        # diff pivot to max & min
        pivot = style_info.data.most_common()[0][0]
        # if style_info.min_found_size <= pivot <= style_info.max_found_size:
        right_span = style_info.max_found_size - pivot
        left_span = pivot - style_info.min_found_size
        
        if right_span > pivot:
            right_span = pivot
        if right_span == 0:
            right_span = 5
        if left_span == 0:
            left_span = 5
        
        targetSteps = bins / 2.
        alpha = 0.2
        thRunner = pivot
        mem = 0
        for i in range(1, int((bins / 2) + 1)):
            scaledStep = left_span / targetSteps * self.weight(i) + mem * alpha
            thRunner -= scaledStep
            mem = scaledStep
            self.borders.insert(0, thRunner)
        thRunner = pivot
        mem = 0
        for i in range(1, int((bins / 2) + 1)):
            scaledStep = right_span / targetSteps * self.weight(i) + mem * alpha
            thRunner += scaledStep
            mem = scaledStep
            self.borders.append(thRunner)
    
    @staticmethod
    def weight(n):
        return 1.0 - 1. / math.exp(n - 0.5)
    
    def translate(self, target_enum: TextSize, style_info: StyleDistribution, value) -> Enum:
        return TextSize.from_range(self.borders, value)


class PivotLinearMapper(SizeMapper):
    
    def __init__(self, style_info: StyleDistribution):
        # find pivot
        # diff pivot to max & min
        pivot = style_info.data.most_common()[0][0]
        # if style_info.min_found_size <= pivot <= style_info.max_found_size:
        right_span = style_info.max_found_size - pivot
        left_span = pivot - style_info.min_found_size
        # else:
        #   print("error?")
        
        right_step = (right_span / 2.) * 0.5
        left_step = (left_span / 2.) * 0.5
        
        b0, b1 = style_info.min_found_size + left_step, style_info.min_found_size + left_step * 2
        b2, b3 = pivot + right_step, pivot + right_step * 2
        self.borders = (b0, b1, b2, b3)
    
    def translate(self, target_enum: TextSize, style_info: StyleDistribution, value) -> Enum:
        return TextSize.from_range(self.borders, value)
        
        # divide left & right span to bins, map


class LinearSizeMapper(SizeMapper):
    
    def translate(self, target_enum: Enum, style_info: StyleDistribution, value) -> Enum:
        # Figure out how 'wide' each range is
        leftSpan = style_info.max_found_size - style_info.min_found_size
        rightSpan = target_enum.xlarge.value - target_enum.xsmall.value
        
        # Convert the left range into a 0-1 range (float)
        scaled = float(value - style_info.min_found_size) / float(leftSpan)
        if scaled > 1.0:
            return target_enum.xlarge
        elif scaled < 0:
            return target_enum.xsmall
        
        else:
            # Convert the 0-1 range into a value in the right range.
            return TextSize(int(target_enum.xsmall.value + (scaled * rightSpan)))


def truncate(number, decimals=0):
    """
    Returns a value truncated to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)
    
    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor


def count_sizes(file_path: str) -> StyleDistribution:
    distribution = Counter()
    for page_layout in extract_pages(file_path):
        # checkout each character within
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for node in element:
                    # grep first character and take size
                    if not isinstance(node, LTTextLine) or node.is_empty() \
                            or not node.get_text():
                        continue
                    
                    sizes = list(itertools.islice(
                        [c.size for c in node if isinstance(c, LTChar)], 10))
                    # get max size, check that it occurred at least twice
                    maxSize = max(sizes)
                    if sizes.count(maxSize) > 2:
                        distribution.update([truncate(maxSize, 2)])
    
    if not distribution:
        raise TypeError("{} document does not contain text".format(file_path))
    return StyleDistribution(distribution)
