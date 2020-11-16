#!/usr/bin/env python3
"""
    Script for generating full page text image 

"""
import argparse
import json
import os 
"""
global variables for page generation
"""
GLOBAL_CW_HEIGHT = 5 # character height and width 
GLOBAL_CW_WIDTH = 5
GLOBAL_MARGIN_HEIGHT = 10
GLOBAL_MARGIN_WIDTH = 10

def generate_page_data(text, output_path) :
    """
    convert string text to a full page data 
        :param 
            text : text to print out on the page
            output_path : path to save the generated image data
    """
    raise NotImplementedError()

def generate_single_line(text, start_x, start_y, end_x, end_y) : 
    """
    print out a single line of images 
        :param : 
            text : text to be printed 
            start_x, start_y : position of the starting character 
            end_x, end_y : position of the last character 
    """
    raise NotImplementedError()

def calculate_next_position(previous_x, previous_y, previous_rotation) : 
    """
     Returns the x,y position of the next character to be printed.

        :param previous_x, previous_y: the position of previous character. 
               previous_rotation : the rotation of previous character 
        :return:
    """
    raise NotImplementedError()