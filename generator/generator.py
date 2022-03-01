# -*- coding: utf-8 -*-

"""
Script for generating full page text images
"""

import itertools
import os
import random
import sys
from multiprocessing import Pool
from typing import Tuple, List

import tqdm
from PIL import Image, ImageChops
from tqdm.contrib.concurrent import process_map

from data.glyph import GlyphLoader
from data.text import TextLoader

MAX_WORKERS = 8
GLOBAL_CW_HEIGHT = 35  # character height and width
GLOBAL_CW_WIDTH = 35
# GLOBAL_CW_HEIGHT = 20  # for smaller characters
# GLOBAL_CW_WIDTH = 20
GLOBAL_MARGIN_HEIGHT = 100
GLOBAL_MARGIN_WIDTH = 100
GLOBAL_WIDTH = 1000
GLOBAL_HEIGHT = 1000
GLOBAL_MAX_ROTATION = 10
GLOBAL_LINE_HEIGHT = 30
SPECIAL_CHARACTERS = ['.', ',', '?', ';', '!', '"', '\'', '/', '\'', '~', '@', '#', '%', '^', '&', '*', '(', ')', '-',
                      '+', '>', '<', '[', ']', '{', '}', '₩']

OUTPUT_DIR = "/Users/itsnamgyu/code/calligram/output/generator_test"


def generate_page_data(gl: GlyphLoader, text, variant, output_path=None, character_per_page=2000) -> Tuple[
    Image.Image, str]:
    """
    :param gl:
    :param text: text to print out on the page
    :param output_path: path to save the generated image data if specified.
    :param variant: glyph variant
    :return: Image, text (with linebreaks)
    """
    y = 0
    CHARACTERS_PER_LINE = int((GLOBAL_WIDTH / GLOBAL_CW_WIDTH)) - 1
    page = Image.new('RGB', (GLOBAL_WIDTH + 2 * GLOBAL_MARGIN_WIDTH, GLOBAL_HEIGHT + 2 * GLOBAL_MARGIN_HEIGHT), "WHITE")
    dst = Image.new('RGB', (GLOBAL_WIDTH, GLOBAL_MARGIN_HEIGHT), "WHITE")
    left = (character_per_page - len(text)) / CHARACTERS_PER_LINE

    lines = []
    for i in range(0, len(text), CHARACTERS_PER_LINE):
        lines.append(text[i:i + CHARACTERS_PER_LINE])

    for line in lines:
        im = generate_single_line(gl, line, 0, y, CHARACTERS_PER_LINE, variant)
        dst = get_concat_v_resize(dst, im)
        y = y + GLOBAL_CW_HEIGHT

    """
    dst = get_concat_v_resize(dst, Image.new('RGB', (GLOBAL_WIDTH, GLOBAL_MARGIN_HEIGHT), "WHITE"), True, True)
    if GLOBAL_HEIGHT - y > 0:
        dst = get_concat_v_resize(dst, Image.new('RGB', (GLOBAL_WIDTH, GLOBAL_HEIGHT - y), "WHITE"), True, True)
    """
    page.paste(dst, (GLOBAL_MARGIN_WIDTH, GLOBAL_MARGIN_HEIGHT))
    if output_path:
        page.save(output_path)

    text = "\n".join(lines)

    return page, text


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
    else:
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


def _generate_data(item):
    i, (variant, data, characters_per_page, gl) = item
    key, string = data
    if len(string) > characters_per_page:
        # For strings that may be longer than characters_per_page
        offset = random.randint(0, len(string) - characters_per_page)
        offset = 0
        string = string[offset: offset + characters_per_page]
    else:
        offset = 0
    output_image_path = os.path.join(OUTPUT_DIR, "text{:04d}_{}_{:04d}_{:06d}.jpg".format(i, key, variant, offset))
    output_text_path = os.path.join(OUTPUT_DIR, "text{:04d}_{}_{:04d}_{:06d}.txt".format(i, key, variant, offset))
    image, text = generate_page_data(gl, string, variant, output_image_path, characters_per_page)
    with open(output_text_path, "w") as f:
        f.write(text)


def main():
    gl = GlyphLoader("/Users/itsnamgyu/code/calligram/input/glyph/hicau_mod0/", ext="tif")
    s = str(gl.character_set)[:1000]
    character_set = [' ']
    i = 0
    for character in gl.character_set:
        character_set.append(chr(int(character, 16)))
        i = i + 1
    character_set = ['제', '억', '럼', '했', '워', '노', '밤', '책', '름', '언', '프', '오', '난', '남', '란', '로', '어', '다', '런', '까',
                     '직', '에', '벌', '봄', '차', '엇', '디', '국', '녀', '겨', '루', '멀', '별', '써', '위', '레', '릴', '운', '슴', '퍼',
                     '덤', '입', '기', '것', '외', '의', '파', '으', '북', '거', '득', '린', '무', '춘', '닭', '헤', '아', '소', '람', '비',
                     '이', '하', '스', '고', '러', '힌', '흙', '습', '말', '절', '일', '신', '패', '풀', '성', '슬', '인', '애', '랑', '는',
                     '헬', '끄', '교', '간', '십', '부', '덕', '계', '었', '네', '마', '버', '침', '봅', '사', '상', '묻', '딴', '던', '듯',
                     '집', '같', '.', '걱', '할', '도', '있', '속', '학', '라', '씩', '강', '을', '면', '지', '동', '들', '웃', '못', '끼',
                     '된', '잔', '빛', '님', '쉬', '너', '합', '함', '많', '요', '우', '그', '청', '와', '처', '토', '않', '늘', '덮', '가',
                     '보', '둘', '옥', '머', '은', '한', '잠', '울', '내', '니', '자', '정', ',', '새', '시', '불', '케', '경', '당', '피',
                     '를', '리', '나', '쓸', '없', '과', '때', '추']
    loader = TextLoader(character_set)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    characters_per_line = int((GLOBAL_WIDTH / GLOBAL_CW_WIDTH)) - 1
    characters_per_page = int((GLOBAL_HEIGHT / (GLOBAL_CW_HEIGHT + GLOBAL_LINE_HEIGHT))) * characters_per_line
    print("Characters per page:", characters_per_page)

    all_data = {}

    """
    # Use random string
    print("Loading random strings")
    for i in tqdm.tqdm(range(0, 180)):
        all_data[i] = loader.generate_random_text(max_length=int(characters_per_page * random.uniform(0.9, 1)))
    """

    # Use poem data
    print("Using poem data")
    poem = "계절이 지나가는 하늘에는 가을로 가득 차 있습니다. 나는 아무 걱정도 없이 가을 속의 별들을 다 헬 듯합니다. 가슴 속에 하나 둘 새겨지는 별을 이제 다 못 헤는 것은 쉬이 아침이 오는 까닭이요, 내일 밤이 남은 까닭이요, 아직 나의 청춘이 다하지 않은 까닭입니다. 별 하나에 추억과 별 하나에 사랑과 별 하나에 쓸쓸함과 별 하나에 동경과 별 하나에 시와 별 하나에 어머니, 어머니, 어머님, 나는 별 하나에 아름다운 말 한마디씩 불러 봅니다. 소학교 때 책상을 같이 했던 아이들의 이름과, 패, 경, 옥, 이런 이국 소녀들의 이름과, 벌써 아기 어머니 된 계집애들의 이름과, 가난한 이웃 사람들의 이름과, 비둘기, 강아지, 토끼, 노새, 노루, 프랑시스 잠, 라이너 마리아 릴케 이런 시인의 이름을 불러 봅니다. 이네들은 너무나 멀리 있습니다. 별이 아스라이 멀듯이. 어머님, 그리고 당신은 멀리 북간도에 계십니다. 나는 무엇인지 그리워 이 많은 별빛이 내린 언덕 위에 내 이름자를 써 보고 흙으로 덮어 버리었습니다. 딴은 밤을 새워 우는 벌레는 부끄러운 이름을 슬퍼하는 까닭입니다. 그러나 겨울이 지나고 나의 별에도 봄이 오면 무덤 위에 파란 잔디가 피어나듯이 내 이름자 묻힌 언덕 위에도 자랑처럼 풀이 무성할 거외다."
    import random
    l = poem.split()
    random.shuffle(l)
    poem = ' '.join(l)
    all_data[0] = poem

    items = itertools.product(range(0, gl.variants), all_data.items(), [characters_per_page], [gl])
    total = gl.variants * len(all_data)

    MAX_WORKERS = 8
    print("Generating pages for {} variants for {} strings using up to {} workers".format(gl.variants, len(all_data), MAX_WORKERS))

    process_map(_generate_data, enumerate(items), max_workers=MAX_WORKERS, total=total)
    p = Pool(MAX_WORKERS)
    p.map(_generate_data, enumerate(items))
    """
    for i, (variant, data) in tqdm.tqdm(, total=total):
        key, string = data
        if len(string) > characters_per_page:
            # For strings that may be longer than characters_per_page
            offset = random.randint(0, len(string) - characters_per_page)
            string = string[offset: offset + characters_per_page]
        else:
            offset = 0

        output_image_path = os.path.join(output_dir, "text{:04d}_{}_{:04d}_{:06d}.jpg".format(i, key, variant, offset))
        output_text_path = os.path.join(output_dir, "text{:04d}_{}_{:04d}_{:06d}.txt".format(i, key, variant, offset))
        image, text = generate_page_data(gl, string, variant, output_image_path, characters_per_page)
        with open(output_text_path, "w") as f:
            f.write(text)
    """


"""
def main():
    gl = GlyphLoader("/Users/itsnamgyu/code/calligram/input/glyph/hicau_mod0/", ext="tif")
    s = str(gl.character_set)[:1000]
    character_set = [' ']
    i = 0
    for character in gl.character_set:
        character_set.append(chr(int(character, 16)))
        i = i + 1
    character_set = ['제', '억', '럼', '했', '워', '노', '밤', '책', '름', '언', '프', '오', '난', '남', '란', '로', '어', '다', '런', '까', '직', '에', '벌', '봄', '차', '엇', '디', '국', '녀', '겨', '루', '멀', '별', '써', '위', '레', '릴', '운', '슴', '퍼', '덤', '입', '기', '것', '외', '의', '파', '으', '북', '거', '득', '린', '무', '춘', '닭', '헤', '아', '소', '람', '비', '이', '하', '스', '고', '러', '힌', '흙', '습', '말', '절', '일', '신', '패', '풀', '성', '슬', '인', '애', '랑', '는', '헬', '끄', '교', '간', '십', '부', '덕', '계', '었', '네', '마', '버', '침', '봅', '사', '상', '묻', '딴', '던', '듯', '집', '같', '.', '걱', '할', '도', '있', '속', '학', '라', '씩', '강', '을', '면', '지', '동', '들', '웃', '못', '끼', '된', '잔', '빛', '님', '쉬', '너', '합', '함', '많', '요', '우', '그', '청', '와', '처', '토', '않', '늘', '덮', '가', '보', '둘', '옥', '머', '은', '한', '잠', '울', '내', '니', '자', '정', ',', '새', '시', '불', '케', '경', '당', '피', '를', '리', '나', '쓸', '없', '과', '때', ' ', '추']
    loader = TextLoader(character_set)
    all_data = loader.load_data("/Users/itsnamgyu/code/calligram/input/text/kaist_corpus", verbose=True)
    output_dir = "/Users/itsnamgyu/code/calligram/output/generator_test"
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
"""

if __name__ == "__main__":
    main()
