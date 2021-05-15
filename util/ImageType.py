from enum import Enum


class ImageType(Enum):
    BLACK_WHITE = 0
    DITHER = 1
    HALFTONE = 2
    GRAY = 3
    SILHOUETTE = 4
    COLOR = 5
    COLOR_DITHER = 6
