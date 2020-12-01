"""
Script for generating full page text images
"""

import argparse
import json
import os
import random
from PIL import Image, ImageChops
from data.glyph import GlyphLoader
from data.text import TextLoader
import time

GLOBAL_CW_HEIGHT = 50  # character height and width
GLOBAL_CW_WIDTH = 50
GLOBAL_MARGIN_HEIGHT = 100
GLOBAL_MARGIN_WIDTH = 100
GLOBAL_WIDTH = 1000
GLOBAL_HEIGHT = 1000
GLOBAL_ROT = 10
GLOBAL_LINE_GAP = 30
LETTER_PER_LINE = 50
special_characters = ['.', ',', '?', ';', '!', '"', '\'', '/', '\'', '~','@', '#', '%','^','&','*','(',')','-','+', '>', '<', '[', ']', '{', '}', '₩']
def generate_page_data(gl: GlyphLoader, text, variant=None, output_path=None, character_per_page=2000) -> Image:
    """
    :param gl:
    :param text: text to print out on the page
    :param output_path: path to save the generated image data if specified.
    :param variant: glyph variant
    :return: Image
    """
    y = 0
    dst = Image.new('RGB', (GLOBAL_WIDTH, GLOBAL_MARGIN_HEIGHT), "WHITE")
    left = (character_per_page  - len(text)) / LETTER_PER_LINE

    for i in range(0, len(text), LETTER_PER_LINE):
        im = generate_single_line(gl, text[i:i + LETTER_PER_LINE], 0, y, LETTER_PER_LINE, variant)
        dst = get_concat_v_resize(dst, im)
        y = y + GLOBAL_CW_HEIGHT

    dst = get_concat_v_resize(dst, Image.new('RGB', (GLOBAL_WIDTH, GLOBAL_MARGIN_HEIGHT), "WHITE"),True,True)
    if GLOBAL_HEIGHT-y > 0 :
        dst = get_concat_v_resize(dst, Image.new('RGB', (GLOBAL_WIDTH, GLOBAL_HEIGHT-y), "WHITE"),True,True)

    if output_path:
        dst.save(output_path)
    return dst


def generate_single_line(gl: GlyphLoader, text, start_x, start_y, size, variant=None):
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
            img = Image.new("RGB", (GLOBAL_CW_WIDTH, GLOBAL_CW_HEIGHT),"white")
            dst = get_concat_h_resize(dst, img,True,False)
        elif c in special_characters : 
            img = gl.load_glyph(c, variant).convert("RGB")
            dst = get_concat_h_resize(dst, img,True,True)
        else :
            img = trim(gl.load_glyph(c, variant)).convert("RGB")
            dst = get_concat_h_resize(dst, img,True,True)
        previous_x, previous_y, previous_rotation = calculate_next_position(previous_x, previous_y, previous_rotation)
        i = i + 1
    dst = get_concat_h_resize(dst, Image.new("RGB", (GLOBAL_MARGIN_WIDTH, GLOBAL_CW_HEIGHT),"white"),True,False)
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
    if rotate_image  : 
        ro = GLOBAL_ROT * random.uniform(-1, 1)
        im2 = im2.rotate(ro, fillcolor='WHITE', expand=True)
    if resize_big_image :
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

    if not isEmpty : 
        GAP = int(GLOBAL_LINE_GAP * random.uniform(0.3,1))
        dst = Image.new("RGB", (_im1.width, _im1.height + _im2.height + GAP))
        dst.paste(_im1, (0, 0))
        dst.paste(Image.new("RGB", (_im1.width, GAP),"white"), (0, _im1.height ))
        dst.paste(_im2, (0, _im1.height  + GAP))
    else :
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
    # generate_page_data(gl,"안녕하세요 제 이름이 뭐냐고요? 그건 말이죵~ 안알려줌 그래 안녕하세요 제 이름이 뭐냐고요? 그건 말이죵~ 안알려줌 그래 안녕하세요 제 이름이 뭐냐고요? 그건 말이죵~ 안알려줌 그래 안녕하세요 제 이름이 뭐냐고요? 그건 말이죵~ 안알려줌 그래 안녕하세요 제 이름이 뭐냐고요? 그건 말이죵~ 안알려줌 그래 안녕하세요 제 이름이 뭐냐고요? 그건 말이죵~ 안알려줌 그래 안녕하세요 제 이름이 뭐냐고요? 그건 말이죵~ 안알려줌 그래 ", 1, "/home/itsnamgyu/calligram/output/test.png")
   
    i = 0
    character_per_page = int(( GLOBAL_HEIGHT/(GLOBAL_CW_HEIGHT+ GLOBAL_LINE_GAP)))* LETTER_PER_LINE * 2
    print(character_per_page)
    for data in all_data : 
        i = i + 1
        j = 0 
        x = all_data[data]
        strings = [x[k: k + character_per_page] for k in range(0, len(x), character_per_page)]
        for string in strings : 
            j = j + 1
            for m in range(0, gl.variants) :
                start = time.time()
                generate_page_data(gl,string, m, "/home/itsnamgyu/calligram/output/text{}_{}_{}.jpg".format(i,j,m),character_per_page)
                end = time.time()
                print("f/home/itsnamgyu/calligram/output/text{}_{}_{}.jpg".format(i,j,m,end-start) )

 

if __name__ == "__main__":
    main()

"""    

loader = TextLoader(character_set)
loaded_data = loader.load_data('/home/itsnamgyu/calligram/input/text/kaist_corpus')
i = 0
print("finished loaded text...")
for key in loaded_data:    
    generate_page_data(gl, loaded_data[key],"/home/itsnamgyu/calligram/output/{}.jpg".format(i))
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
