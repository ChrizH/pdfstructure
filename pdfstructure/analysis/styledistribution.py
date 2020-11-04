import itertools
from collections import Counter, defaultdict

from pdfminer.layout import LTTextContainer, LTTextLine, LTChar
from sortedcontainers import SortedDict

from pdfstructure.utils import truncate, closest_key


class StyleDistribution:
    """
    Represents style information for one analysed element stream (typically one stream per document).
    """

    def __init__(self, data=None, line_margin=0.5):
        """
        
        :type data: Counter
        :param data:
        """
        if data:
            self._data = data
            self._body_size = data.most_common(1)[0][0]
            self._min_found_size, self._max_found_size = min(data.keys()), max(data.keys())
            if self._min_found_size == self._max_found_size:
                self._min_found_size /= 2
                self._max_found_size *= 2
        self._line_margin = line_margin

    @property
    def line_margin(self):
        return self._line_margin

    def norm_data_binned(self, bins=50):
        amount_items = self.amount_values
        step = 1.0 / bins
        keys = [step * i for i in range(bins)]
        normalised = SortedDict({key: 0.0 for key in keys})
        for size in self.data:
            norm_key = truncate(size / self.max_found_size, 2)
            k = closest_key(normalised, norm_key)
            normalised[k] += float(self.data[size]) / amount_items

        return normalised

    @property
    def norm_data(self):
        # normalise counts with total amount of collected values
        # normalise each key value against max found key value (size)
        # normalise X & Y
        normalised = defaultdict(int)
        amount_items = self.amount_values
        for size in self.data:
            normalised[truncate(size / self.max_found_size, 2)] += float(self.data[size]) / amount_items

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


class SizeAnalyser:
    def __init__(self):
        self.sizeDistribution = Counter()

    def consume(self, node: LTTextContainer):
        sizes = list(itertools.islice(
            [c.size for c in node if isinstance(c, LTChar)], 10))
        # get max size, check that it occurred at least twice
        maxSize = max(sizes)
        if sizes.count(maxSize) > 2:
            self.sizeDistribution.update([truncate(maxSize, 2)])

    def process_result(self):
        pass


class LineMarginAnalyer:
    _previousNode: LTTextContainer

    def __init__(self):
        self._distanceCounter = defaultdict(int)
        self._headingTrailingCounter = defaultdict(int)
        self._previousNode = None
        self._y = None
        self._previousBoxHeight = None

    def consume(self, node: LTTextContainer):
        if self._previousNode:
            diff = truncate(abs(self._previousNode.y0 - node.y1), 2)
            if self._previousNode.height == node.height:
                self._distanceCounter[(diff, node.height)] += 1
            else:
                self._headingTrailingCounter[(diff, self._previousNode.height, node.height)] += 1

        self._previousNode = node

    def process_result(self):
        """
        Find relative line margin threshold that will be used in pdfminers paragraphs algorithm.
        lines that are vertically closer than margin * height are considered to belong to the same paragraph.
        @return:
        """
        (abs_margin, line_height), count = max(self._distanceCounter.items(), key=lambda item: item[1])
        body_line_margin = min(0.5, 1.75 * abs_margin / line_height)
        # todo, find next largest value from title_trailing --> margin should be smaller than that
        # sorted(self._headingTrailingCounter.keys(), key=lambda keys: keys[1])
        # print("line margin: {}".format(line_margin))
        return body_line_margin


def count_sizes(element_gen) -> StyleDistribution:
    """
    analyse used fonts, character sizes, paragraph margins etc.
    :param element_gen:
    :return:
    """
    sizeAnalyser = SizeAnalyser()
    lineMarginAnalyser = LineMarginAnalyer()

    for element in element_gen:
        if isinstance(element, LTTextContainer):
            for node in element:
                if not isinstance(node, LTTextLine) or node.is_empty() \
                        or len(node._objs) == 0:
                    continue

                sizeAnalyser.consume(node)
                lineMarginAnalyser.consume(node)

    if not sizeAnalyser.sizeDistribution:
        raise TypeError("document does not contain text")

    return StyleDistribution(sizeAnalyser.sizeDistribution, line_margin=lineMarginAnalyser.process_result())
