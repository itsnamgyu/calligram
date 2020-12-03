"""
Script for generating full page text images
"""

import itertools
import os
import random

import tqdm
from PIL import Image, ImageChops
from data.glyph import GlyphLoader
from data.text import TextLoader

GLOBAL_CW_HEIGHT = 35  # character height and width
GLOBAL_CW_WIDTH = 35
#GLOBAL_CW_HEIGHT = 20  # for smaller characters 
# GLOBAL_CW_WIDTH = 20
GLOBAL_MARGIN_HEIGHT = 100
GLOBAL_MARGIN_WIDTH = 100
GLOBAL_WIDTH = 1000
GLOBAL_HEIGHT = 1000
GLOBAL_MAX_ROTATION = 10
GLOBAL_LINE_HEIGHT = 30
SPECIAL_CHARACTERS = ['.', ',', '?', ';', '!', '"', '\'', '/', '\'', '~', '@', '#', '%', '^', '&', '*', '(', ')', '-',
                      '+', '>', '<', '[', ']', '{', '}', '₩']


def generate_page_data(gl: GlyphLoader, text, variant, output_path=None, character_per_page=2000) -> Image:
    """
    :param gl:
    :param text: text to print out on the page
    :param output_path: path to save the generated image data if specified.
    :param variant: glyph variant
    :return: Image
    """
    y = 0
    CHARACTERS_PER_LINE = int((GLOBAL_WIDTH / GLOBAL_CW_WIDTH)) - 1 
    page = Image.new('RGB', (GLOBAL_WIDTH + 2 * GLOBAL_MARGIN_WIDTH, GLOBAL_HEIGHT + 2*  GLOBAL_MARGIN_HEIGHT), "WHITE")
    dst = Image.new('RGB', (GLOBAL_WIDTH, GLOBAL_MARGIN_HEIGHT), "WHITE")
    left = (character_per_page - len(text)) / CHARACTERS_PER_LINE

    for i in range(0, len(text), CHARACTERS_PER_LINE):
        im = generate_single_line(gl, text[i:i + CHARACTERS_PER_LINE], 0, y, CHARACTERS_PER_LINE, variant)
        dst = get_concat_v_resize(dst, im)
        y = y + GLOBAL_CW_HEIGHT

    """
    dst = get_concat_v_resize(dst, Image.new('RGB', (GLOBAL_WIDTH, GLOBAL_MARGIN_HEIGHT), "WHITE"), True, True)
    if GLOBAL_HEIGHT - y > 0:
        dst = get_concat_v_resize(dst, Image.new('RGB', (GLOBAL_WIDTH, GLOBAL_HEIGHT - y), "WHITE"), True, True)
    """
    page.paste(dst,(GLOBAL_MARGIN_WIDTH,GLOBAL_MARGIN_HEIGHT))
    if output_path:
        page.save(output_path)
    return page


def generate_single_line(gl: GlyphLoader, text, start_x, start_y, size, variant):
    """
    print out a single line of images 
        :param : 
            text : text to be printed 
            start_x, start_y : position of the starting character 
            end_x, end_y : position of the last character
            variant : glyph variant
    """
    previous_x = start_x + GLOBAL_MARGIN_WIDTH
    previous_y = start_y + GLOBAL_MARGIN_HEIGHT
    previous_rotation = 0
    i = 0
    dst = Image.new("RGB", (GLOBAL_MARGIN_WIDTH, GLOBAL_CW_HEIGHT), "white")
    text = text.lstrip()
    text += ' ' * (size - len(text))
    for c in text:
        if c.isspace():
            img = Image.new("RGB", (GLOBAL_CW_WIDTH, GLOBAL_CW_HEIGHT), "white")
            dst = get_concat_h_resize(dst, img, True, False)
        elif c in SPECIAL_CHARACTERS:
            img = gl.load_glyph(c, variant).convert("RGB")
            img.resize((GLOBAL_CW_WIDTH, GLOBAL_CW_HEIGHT), Image.ANTIALIAS)
            dst = get_concat_h_resize(dst, img, True, True)
        else:
            img = trim(gl.load_glyph(c, variant)).convert("RGB")
            img.resize((GLOBAL_CW_WIDTH, GLOBAL_CW_HEIGHT), Image.ANTIALIAS)
            dst = get_concat_h_resize(dst, img, True, True)
        previous_x, previous_y, previous_rotation = calculate_next_position(previous_x, previous_y, previous_rotation)
        i = i + 1
    dst = get_concat_h_resize(dst, Image.new("RGB", (GLOBAL_MARGIN_WIDTH, GLOBAL_CW_HEIGHT), "white"), True, False)
    return dst


def calculate_next_position(previous_x, previous_y, previous_rotation):
    """
     Returns the x,y position of the next character to be printed.

        :param previous_x, previous_y: the position of previous character. 
               previous_rotation : the rotation of previous character 
        :return:
    """
    previous_x = previous_x + GLOBAL_CW_WIDTH * random.uniform(0, 1)
    previous_y = previous_y
    previous_rotation = previous_rotation + -10 * random.uniform(-1, 1)
    return int(previous_x), int(previous_y), int(previous_rotation)


def get_concat_h_resize(im1, im2, resample=Image.BICUBIC, resize_big_image=True, rotate_image=True):
    if rotate_image:
        ro = GLOBAL_MAX_ROTATION * random.uniform(-1, 1)
        im2 = im2.rotate(ro, fillcolor='WHITE', expand=True)
    if resize_big_image:
        im2.resize((GLOBAL_CW_WIDTH, GLOBAL_CW_HEIGHT), Image.ANTIALIAS)

    if im1.height == im2.height:
        _im1 = im1
        _im2 = im2
    elif (((im1.height > im2.height) and resize_big_image) or
          ((im1.height < im2.height) and not resize_big_image)):
        _im1 = im1.resize((int(im1.width * im2.height / im1.height), im2.height), resample=resample)
        _im2 = im2
    else:
        _im1 = im1
        _im2 = im2.resize((int(im2.width * im1.height / im2.height), im1.height), resample=resample)
    dst = Image.new('RGB', (_im1.width + _im2.width, _im1.height), "WHITE")

    dst.paste(_im1, (0, 0))
    dst.paste(_im2, (_im1.width, 0))

    return dst


def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    else :
        return im 


def get_concat_v_resize(im1, im2, resample=Image.BICUBIC, resize_big_image=True, isEmpty=False):
    if im1.width == im2.width:
        _im1 = im1
        _im2 = im2
    elif (((im1.width > im2.width) and resize_big_image) or
          ((im1.width < im2.width) and not resize_big_image)):
        _im1 = im1.resize((im2.width, int(im1.height * im2.width / im1.width)), resample=resample)
        _im2 = im2
    else:
        _im1 = im1
        _im2 = im2.resize((im1.width, int(im2.height * im1.width / im2.width)), resample=resample)

    if not isEmpty:
        GAP = int(GLOBAL_LINE_HEIGHT * random.uniform(0.3, 1))
        dst = Image.new("RGB", (_im1.width, _im1.height + _im2.height + GAP))
        dst.paste(_im1, (0, 0))
        dst.paste(Image.new("RGB", (_im1.width, GAP), "white"), (0, _im1.height))
        dst.paste(_im2, (0, _im1.height + GAP))
    else:
        dst = Image.new("RGB", (_im1.width, _im1.height + _im2.height))
        dst.paste(_im1, (0, 0))
        dst.paste(_im2, (0, _im1.height))

    return dst


def main():
    gl = GlyphLoader("/home/itsnamgyu/calligram/input/glyph/hicau_mod0/", ext="tif")
    s = str(gl.character_set)[:1000]
    character_set = [' ']
    i = 0
    for character in gl.character_set:
        character_set.append(chr(int(character, 16)))
        i = i + 1
    loader = TextLoader(character_set)
    all_data = loader.load_data("/home/itsnamgyu/calligram/input/text/kaist_corpus", verbose=True)
    # generate_page_data(gl,"안녕하세요 제 이름이 뭐냐고요? 그건 말이죵~ 안알려줌 그래 안녕하세요 제 이름이 뭐냐고요? 그건 말이죵~ 안알려줌 그래 안녕하세요 제 이름이 뭐냐고요? 그건 말이죵~ 안알려줌 그래 안녕하세요 제 이름이 뭐냐고요? 그건 말이죵~ 안알려줌 그래 안녕하세요 제 이름이 뭐냐고요? 그건 말이죵~ 안알려줌 그래 안녕하세요 제 이름이 뭐냐고요? 그건 말이죵~ 안알려줌 그래 안녕하세요 제 이름이 뭐냐고요? 그건 말이죵~ 안알려줌 그래 ", 1, "/Users/itsnamgyu/code/calligram/output/test.png")

    output_dir = "/home/itsnamgyu/calligram/output/generator_test"
    os.makedirs(output_dir, exist_ok=True)
    CHARACTERS_PER_LINE = int((GLOBAL_WIDTH / GLOBAL_CW_WIDTH)) - 1 
    characters_per_page = int((GLOBAL_HEIGHT / (GLOBAL_CW_HEIGHT + GLOBAL_LINE_HEIGHT))) * CHARACTERS_PER_LINE 
    print("Characters per page:", characters_per_page)
    items = itertools.product(range(0, gl.variants), all_data.items())
    total = gl.variants * len(all_data)
    print("Generating pages for {} variants for {} strings".format(gl.variants, len(all_data)))

    for i, (variant, data) in tqdm.tqdm(enumerate(items), total=total):
        key, string = data
        if len(string) > characters_per_page:
            offset = random.randint(0, len(string) - characters_per_page)
            string = string[offset: offset + characters_per_page]
        else:
            offset = 0

        with open(os.path.join(output_dir, "text{:04d}_{}_{:04d}_{:06d}.txt".format(i, key, variant, offset)),
                  "w") as f:
            f.write(string)
        generate_page_data(gl, string, variant,
                           os.path.join(output_dir, "text{:04d}_{}_{:04d}_{:06d}.jpg".format(i, key, variant, offset)),
                           characters_per_page)
        


if __name__ == "__main__":
    main()

"""    

loader = TextLoader(character_set)
loaded_data = loader.load_data('/Users/itsnamgyu/code/calligram/input/text/kaist_corpus')
i = 0
print("finished loaded text...")
for key in loaded_data:    
    generate_page_data(gl, loaded_data[key],"/Users/itsnamgyu/code/calligram/output/{}.jpg".format(i))
    print("created {} data..".format(i))
    exit(0)
    i = i + 1
     s = str(gl.character_set)[:1000]
    character_set = []
    i = 0
    for character in gl.character_set:
        character_set.append(chr(int(character, 16)))
        i = i + 1
"""
