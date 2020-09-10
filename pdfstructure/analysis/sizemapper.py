import math
from enum import Enum
from typing import Type

from pdfstructure.analysis.styledistribution import StyleDistribution
from pdfstructure.model.style import TextSize


class SizeMapper:

    def __init__(self):
        self._borders = None

    @property
    def borders(self):
        return self._borders

    def translate(self, target_enum: Type[TextSize], value) -> Enum:
        return TextSize.from_range(self.borders, value)


class PivotLogMapper(SizeMapper):
    def __init__(self, style_info: StyleDistribution, bins=5):
        super().__init__()
        self.bins = bins
        borders = []
        # find pivot
        # diff pivot to max & min
        pivot = style_info.body_size
        # if style_info.min_found_size <= pivot <= style_info.max_found_size:
        right_span = style_info.max_found_size - pivot
        left_span = pivot - style_info.min_found_size

        if right_span > pivot * 2:
            right_span = pivot * 2
        if right_span == 0:
            right_span = 5
        if left_span == 0:
            left_span = 5

        targetSteps = bins / 2.
        alpha = 0.5
        thRunner = pivot
        mem = 0
        for i in range(1, int((bins / 2) + 1)):
            scaledStep = left_span / targetSteps * self.weight(i) + mem * alpha
            thRunner -= scaledStep
            mem = scaledStep
            borders.insert(0, thRunner)
        thRunner = pivot
        mem = 0
        for i in range(1, int((bins / 2) + 1)):
            scaledStep = right_span / targetSteps * self.weight(i) + mem * alpha
            thRunner += scaledStep
            mem = scaledStep
            borders.append(thRunner)

        self._borders = tuple(borders)

    @staticmethod
    def weight(n):
        """
        used in sizemapper, walking in N steps from pivot point towards max & min found size.
        first step is weighted more (to have a more narrow pivot), the further towards edge values, the further the step.
        @param n:
        @return:
        """
        return 1.0 - 1. / math.exp(n - 0.2)


class PivotLinearMapper(SizeMapper):

    def __init__(self, style_info: StyleDistribution):
        # find pivot
        # diff pivot to max & min
        super().__init__()
        pivot = style_info.body_size
        # if style_info.min_found_size <= pivot <= style_info.max_found_size:
        right_span = style_info.max_found_size - pivot
        left_span = pivot - style_info.min_found_size
        # else:
        #   print("error?")

        right_step = (right_span / 2.) * 0.5
        left_step = (left_span / 2.) * 0.5

        b0, b1 = style_info.min_found_size + left_step, style_info.min_found_size + left_step * 2
        b2, b3 = pivot + right_step, pivot + right_step * 2
        self._borders = (b0, b1, b2, b3)


class LinearSizeMapper(SizeMapper):

    def __init__(self, style_info: StyleDistribution):
        super().__init__()
        self.style_info = style_info

    def translate(self, target_enum, value) -> Enum:
        # Figure out how 'wide' each range is
        leftSpan = self.style_info.max_found_size - self.style_info.min_found_size
        rightSpan = target_enum.xlarge.value - target_enum.xsmall.value

        # Convert the left range into a 0-1 range (float)
        scaled = float(value - self.style_info.min_found_size) / float(leftSpan)
        if scaled > 1.0:
            return target_enum.xlarge
        elif scaled < 0:
            return target_enum.xsmall

        else:
            # Convert the 0-1 range into a value in the right range.
            return TextSize(int(target_enum.xsmall.value + (scaled * rightSpan)))
