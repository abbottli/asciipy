from enum import Enum


def escape(value):
    return f'\033[{value}m'


class Colors(Enum):
    END = escape(0)
    BLACK = escape(30)
    RED = escape(31)
    GREEN = escape(32)
    YELLOW = escape(33)
    BLUE = escape(34)
    MAGENTA = escape(35)
    CYAN = escape(36)
    WHITE = escape(37)
    BRIGHT_BLACK = escape(90)
    BRIGHT_RED = escape(91)
    BRIGHT_GREEN = escape(92)
    BRIGHT_YELLOW = escape(93)
    BRIGHT_BLUE = escape(94)
    BRIGHT_MAGENTA = escape(95)
    BRIGHT_CYAN = escape(96)
    BRIGHT_WHITE = escape(97)


RGB = {
    (12, 12, 12): Colors.BLACK,
    (197, 15, 31): Colors.RED,
    (19, 161, 14): Colors.GREEN,
    (193, 156, 0): Colors.YELLOW,
    (0, 55, 218): Colors.BLUE,
    (136, 23, 152): Colors.MAGENTA,
    (58, 150, 221): Colors.CYAN,
    # (204, 204, 204): Colors.WHITE,
    # (129, 131, 131): Colors.BRIGHT_BLACK,
    (252, 57, 31): Colors.BRIGHT_RED,
    (49, 231, 34): Colors.BRIGHT_GREEN,
    (234, 236, 35): Colors.BRIGHT_YELLOW,
    (88, 51, 255): Colors.BRIGHT_BLUE,
    (249, 53, 248): Colors.BRIGHT_MAGENTA,
    (20, 240, 240): Colors.BRIGHT_CYAN,
    (233, 235, 235): Colors.BRIGHT_WHITE
}
