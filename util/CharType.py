from enum import Enum


class CharType(Enum):
    ASCII = 0
    MATRIX = 1
    MATRIX_KATA = 2
    BRAILLE = 3


# map 256 grayscale to 16 chars
maps = {
    # ascii gradient from black to white
    CharType.ASCII:  ['@', 'M', 'N', 'm', 'd', 'h', 'y', 's', 'o', '+', '/', ':', '-', '.', '`', ' '],
    # matrix code gradient from black to white using hiragana/katakana
    CharType.MATRIX: ['あ', 'せ', 'ホ', 'オ', 'ネ', 'じ', 'ワ', 'ク', 'ナ', 'い', 'し', 'ツ', 'ノ', '゛', '、', '\u3000'],
    CharType.MATRIX_KATA: ['ヰ', 'サ', 'ホ', 'オ', 'ネ', 'じ', 'ワ', 'ク', 'ナ', 'キ', 'ト', 'ツ', 'ノ', '゛', '、', '\u3000']
}
