#!/usr/bin/python

import math
import sys

from PIL import Image

from util import Helper, ImageHelper
from util.CharType import CharType, maps as char_maps
from util.ImageType import ImageType

BRAILLE_BASE = int('0x2800', 16)
BRAILLE_MASK_LEN = 8


def convert(pixel, char_type=CharType.ASCII):
    return char_maps[char_type][pixel // (256 // len(char_maps[char_type]))]


def to_braille_unicode(braille_mask, use_dot_spacing=False):
    unicode_offset = sum(braille_mask[i] << i for i in range(BRAILLE_MASK_LEN))
    # for i in range(BRAILLE_MASK_LEN):
    #     unicode_offset += braille_mask[i] << i

    if use_dot_spacing and unicode_offset == 0:
        unicode_offset = 4  # blank braille char has kerning issues for some fonts
    return chr(BRAILLE_BASE + unicode_offset)


# convert sets of 2x4 pixels into their braille equivalent
def convert_to_braille(image, threshold=128):
    width, height = image.size
    text = [[0] * math.ceil(width / 2) for _ in range(math.ceil(height / 4))]
    braille_mask = [0] * BRAILLE_MASK_LEN
    data = image.load()
    cache = {}

    # convert every 2x4 area in its braille equivalent
    for y in range(0, height, 4):
        for x in range(0, width, 2):
            bitmask = 0
            for i in range(2):
                for j in range(4):
                    if x + i < width and y + j < height:
                        bitmask += (data[x + i, y + j] <= threshold) << ((i * 4) + j)
                        # braille_mask[(i * 4) + j] = (data[x + i, y + j] <= threshold)
            if bitmask in cache:
                braille_unicode = cache[bitmask]
            else:
                braille_unicode = chr(BRAILLE_BASE + bitmask)
                cache[bitmask] = braille_unicode
            text[y // 4][x // 2] = braille_unicode

    return text


def convert_to_text(image, char_type=CharType.ASCII):
    if char_type == CharType.BRAILLE:
        return convert_to_braille(image)

    text = []
    data = image.load()
    for y in range(image.height):
        text.append([])
        for x in range(image.width):
            text[y].append(convert(data[x, y], char_type))

    return text


def setup_text_image(text):
    image = ''
    for i in range(len(text)):
        image += ''.join(text[i]) + '\n'
    return image


def store_text(text, input_filename):
    with open(ImageHelper.resource_folder(f'output/{input_filename}.txt'), 'w', encoding='utf-8') as output_file:
        output_file.write(text)


def gray_scale_image():
    image = Image.new('L', [255, 255])
    data = image.load()

    for x in range(image.width):
        for y in range(image.height):
            data[x, y] = x

    return image


def to_ascii_from_image(image, name='image', invert=True, char_type=CharType.BRAILLE, image_type=ImageType.DITHER):
    image = Helper.fit_image_to_terminal(image, char_type == CharType.BRAILLE)
    if invert:
        image = ImageHelper.invert(image)

    image = ImageHelper.convert_image(image, image_type)

    text_array = convert_to_text(image, char_type)

    ascii_text = setup_text_image(text_array)
    if ImageHelper.DEBUG:
        store_text(ascii_text, name)

    return ascii_text


def to_ascii(input_filename):
    return to_ascii_from_image(Image.open(input_filename).convert('RGB'), input_filename)


def main():
    if len(sys.argv) < 2:
        raise RuntimeError('Usage: this_script.py <input file>')
    input_filename = sys.argv[1]

    text = to_ascii(input_filename)
    print(text)

    # Helper.clear()


if __name__ == '__main__':
    main()
    # input('Press enter to exit')
