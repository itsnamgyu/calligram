# calligram
Calligram

## Setup

1. Make sure to have Python 3.7 (SEVEN) or over!
2. Set up a virtual environment to be safe
3. Run `python setup.py develop`. If you don't, you might break your keyboard.

## Modules

- data: load glyph (character image) and text (plain string) data

## Dataset Preparation 
Download modified KAIST corpus dataset and move to directory:  
`input/text/kaist_corpus`  

**Changes:**  
* Moved all txt files into a single folder/directory named kaist_corpus.  
* Folder contains all the txt files renamed into format: `kaistcorpus_written_raw_or_(subdirectories)_(unique_id).txt`  
* Removed all tags from the txt files to contain only the main contents.  
