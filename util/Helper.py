import os
from util import ImageHelper
from PIL import Image

DEFAULT_COLUMNS = 317
DEFAULT_LINES = 76


def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def fit_image_to_terminal(image, is_braille, scale_type=Image.BICUBIC):
    # attempt to get terminal window size
    try:
        columns, lines = os.get_terminal_size()
        # print(f'using columns={columns}, lines={lines}')
    except Exception:
        # print(f'unable to determine terminal size, using default: columns={DEFAULT_COLUMNS}, lines={DEFAULT_LINES}')
        columns = DEFAULT_COLUMNS
        lines = DEFAULT_LINES

    if is_braille:
        columns *= 2
        lines *= 4

    return ImageHelper.resize_image(image, columns, lines, scale_type)
