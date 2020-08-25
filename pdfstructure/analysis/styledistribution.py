import itertools
from collections import Counter, defaultdict

from pdfminer.layout import LTTextContainer, LTTextLine, LTChar
from sortedcontainers import SortedDict

from pdfstructure.utils import truncate, closest_key


class StyleDistribution:
    """
    Represents style information for one analysed element stream (typically one stream per document).
    """

    def __init__(self, data=None):
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


def count_sizes(element_gen) -> StyleDistribution:
    """
    count all character sizes within observed element stream.
    :param element_gen:
    :return:
    """
    distribution = Counter()
    # checkout each character within
    for element in element_gen:

        if isinstance(element, LTTextContainer):
            for node in element:
                # grep first character and take size
                if not isinstance(node, LTTextLine) or node.is_empty() \
                        or len(node._objs) == 0:
                    continue

                sizes = list(itertools.islice(
                    [c.size for c in node if isinstance(c, LTChar)], 10))
                # get max size, check that it occurred at least twice
                maxSize = max(sizes)
                if sizes.count(maxSize) > 2:
                    distribution.update([truncate(maxSize, 2)])

    if not distribution:
        raise TypeError("document does not contain text")
    return StyleDistribution(distribution)
