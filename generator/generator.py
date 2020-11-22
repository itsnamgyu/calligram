#!/usr/bin/env python3
"""
    Script for generating full page text image 

"""
import argparse
import json
import os
import random
from PIL import Image
 
"""
global variables for page generation
"""
GLOBAL_CW_HEIGHT = 200 # character height and width 
GLOBAL_CW_WIDTH = 300
GLOBAL_MARGIN_HEIGHT = 100
GLOBAL_MARGIN_WIDTH = 100
GLOBAL_WIDTH = 1000
GLOBAL_HEIGHT = 1000 

verticals = []
images = ['../set/char_data/AC4B/HIL_006_0001_1371_AC4B_KO_001_091028.tif', 
'../set/char_data/D3E3/HIL_006_0001_1998_D3E3_KO_001_091028.tif',
'../set/char_data/AC4B/HIL_006_0001_1371_AC4B_KO_001_091028.tif',
'../set/char_data/AC4B/HIL_006_0001_1371_AC4B_KO_001_091028.tif', 
'../set/char_data/D3E3/HIL_006_0001_1998_D3E3_KO_001_091028.tif'
]

def generate_page_data(text, output_path) :
    """
    convert string text to a full page data 
        :param 
            text : text to print out on the page
            output_path : path to save the generated image data
    """

    y = 0
    dst = Image.new('RGB', (GLOBAL_WIDTH, GLOBAL_MARGIN_HEIGHT),"WHITE")
    for i in range(0,10) : 
        im = generate_single_line("hello my name is",0,y)
        dst = get_concat_v_resize(dst,im) 
        y = y + GLOBAL_CW_HEIGHT 

    dst = get_concat_v_resize(dst,Image.new('RGB', (GLOBAL_WIDTH, GLOBAL_MARGIN_HEIGHT),"WHITE"))
    dst.save(output_path) 

def generate_single_line(text, start_x, start_y) : 
    """
    print out a single line of images 
        :param : 
            text : text to be printed 
            start_x, start_y : position of the starting character 
            end_x, end_y : position of the last character 
    """
    previous_x = start_x + GLOBAL_MARGIN_WIDTH
    previous_y = start_y + GLOBAL_MARGIN_HEIGHT
    previous_rotation = 0
    i = 0
    dst = Image.new('RGB', (GLOBAL_MARGIN_WIDTH, GLOBAL_CW_HEIGHT),"WHITE")

    for c in text :
        dst = get_concat_h_resize(dst,Image.open(images[i%5]))
        previous_x, previous_y, previous_rotation = calculate_next_position(previous_x, previous_y, previous_rotation)
        i = i + 1 
        
    dst = get_concat_h_resize(dst,Image.new('RGB', (GLOBAL_MARGIN_WIDTH, GLOBAL_CW_HEIGHT),"WHITE"))
    return dst 
def calculate_next_position(previous_x, previous_y, previous_rotation) : 
    """
     Returns the x,y position of the next character to be printed.

        :param previous_x, previous_y: the position of previous character. 
               previous_rotation : the rotation of previous character 
        :return:
    """
    previous_x = previous_x + GLOBAL_CW_WIDTH*random.uniform(0, 1) 
    previous_y = previous_y 
    previous_rotation = previous_rotation + -10 *random.uniform(-1, 1) 
    return int(previous_x), int(previous_y), int(previous_rotation) 

def get_concat_h_resize(im1, im2, resample=Image.BICUBIC, resize_big_image=True):
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
    dst = Image.new('RGB', (_im1.width + _im2.width, _im1.height),"WHITE")
    dst.paste(_im1, (0, 0))
    ro = 30*random.uniform(-1,1)
    _im2 = _im2.rotate(ro, expand=1, fillcolor = "white")
    dst.paste(_im2, (_im1.width, 0))
    return dst

def get_concat_v_resize(im1, im2, resample=Image.BICUBIC, resize_big_image=True):
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
    dst = Image.new('RGB', (_im1.width, _im1.height + _im2.height),"WHITE")
    dst.paste(_im1, (0, 0))
    dst.paste(_im2, (0, _im1.height - 30 ))
    return dst

generate_page_data("temperate string", "output.jpg")