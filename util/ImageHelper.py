import os
import math

from PIL import Image, ImageOps

from util.Colors import RGB
from util.ImageType import ImageType

RESOURCE_FOLDER = 'resources'
BLACK = 255
WHITE = 0
DEBUG = True


def resource_folder(file):
    return os.path.join(RESOURCE_FOLDER, file)


def convert_image(image, convert_type=ImageType.DITHER):
    if ImageType.DITHER == convert_type:
        return dither(image)
    elif ImageType.BLACK_WHITE == convert_type:
        return black_white(image)
    elif ImageType.HALFTONE == convert_type:
        return halftone(image)
    elif ImageType.GRAY == convert_type:
        return gray(image)
    elif ImageType.SILHOUETTE == convert_type:
        return silhouette(image)
    elif ImageType.COLOR == convert_type:
        return nearest_color(image, RGB.keys(), is_dither=False)
    elif ImageType.COLOR_DITHER == convert_type:
        return nearest_color(image, RGB.keys(), is_dither=True)


def nearest_color(image, color_map, is_dither=True):
    image = remove_transparent(image)

    if is_dither:
        image = color_dither_image(image)

    image = image.convert('RGB')
    width, height = image.size
    pixels = image.load()
    cache = {}

    for x in range(width):
        for y in range(height):
            color = pixels[x, y]
            if color in cache:
                pixels[x, y] = cache[color]
            else:
                near = find_nearest_color(color_map, color)
                pixels[x, y] = near
                cache[color] = near

    if DEBUG:
        image.save(resource_folder('nearest_color.png'))
    return image


# color closeness approximation from https://www.compuphase.com/cmetric.htm
# formula is a low cost approximation of the red weighted distance
def distance(c1, c2):
    r1, g1, b1 = c1
    r2, g2, b2 = c2
    r_mean = int((r1 + r2) / 2)
    r = r1 - r2
    g = g1 - g2
    b = b1 - b2
    return math.sqrt((((512 + r_mean) * r * r) >> 8) + 4 * g * g + (((767 - r_mean) * b * b) >> 8))


def find_nearest_color(color_map, color):
    return min(color_map, key=lambda c: distance(color, c))


# remove transparent pixels by pasting original image over white background
def remove_transparent(image):
    no_transparent = Image.new("RGB", image.size, "WHITE")
    no_transparent.paste(image, (0, 0), image.convert('RGBA'))
    return no_transparent


def color_dither_image(image):
    image = image.convert('P', dither=Image.FLOYDSTEINBERG)
    if DEBUG:
        image.save(resource_folder('color_dither.png'))
    return image


def gray(image):
    image = image.convert('L')
    if DEBUG:
        image.save(resource_folder('gray.png'))
    return image


def black_white(image, thresh=128):
    image = image.convert('L').point(lambda x: BLACK if x > thresh else WHITE, mode='1')
    if DEBUG:
        image.save(resource_folder('bw.png'))
    return image


def silhouette(image):
    image = image.convert('L').point(lambda x: BLACK if x == BLACK else WHITE, mode='1')
    if DEBUG:
        image.save(resource_folder('silhouette.png'))
    return image


def dither(image):
    image = image.convert('1')
    if DEBUG:
        image.save(resource_folder('dither.png'))
    return image


def halftone(image):
    image = image.convert('L')
    width, height = image.size
    pixels = image.load()

    for x in range(0, width, 2):
        for y in range(0, height, 2):
            here, right, down, diag = (x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)

            if x + 1 >= width:
                right = (0, 0)
                diag = (0, 0)
            if y + 1 >= height:
                down = (0, 0)
                diag = (0, 0)

            saturation = (pixels[here] + pixels[right] + pixels[down] + pixels[diag]) / 4

            if saturation > 223:  # all white
                pixels[here] = 255
                pixels[right] = 255
                pixels[down] = 255
                pixels[diag] = 255
            elif saturation > 159:
                pixels[here] = 255
                pixels[right] = 255
                pixels[down] = 0
                pixels[diag] = 255
            elif saturation > 95:
                pixels[here] = 255
                pixels[right] = 0
                pixels[down] = 0
                pixels[diag] = 255
            elif saturation > 23:
                pixels[here] = 0
                pixels[right] = 0
                pixels[down] = 0
                pixels[diag] = 255
            else:  # all black
                pixels[here] = 0
                pixels[right] = 0
                pixels[down] = 0
                pixels[diag] = 0

    if DEBUG:
        image.save(resource_folder('halftone.png'))
    return image


def resize_image(image, max_width, max_height, scale_type=Image.BICUBIC):
    if image.width > max_width or image.height > max_height:
        # resize image to console window bounds
        scale = min(max_width / image.width, max_height / image.height)

        scaled = tuple([int(x * scale) for x in image.size])
        resized = image.resize(scaled, scale_type)
        if DEBUG:
            resized.save(resource_folder('resized.png'))
        return resized
    return image


def invert(image):
    return ImageOps.invert(image)
