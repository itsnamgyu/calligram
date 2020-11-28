# calligram
Calligram

## Setup

1. Make sure to have Python 3.7 (SEVEN) or over!
2. Set up a virtual environment to be safe
3. Run `python setup.py develop`. If you don't, you might break your keyboard.

## Modules

### `data/text`

Load strings from text corpora

### `data/glyph`

Load glyph images.

Usage
```python
from data.glyph import GlyphLoader
import matplotlib.pyplot as plt

gl = GlyphLoader("<dataset_absolute_path>", ext="tif")
img = gl.load_glyph("가", 0)
plt.imshow(img))
```

## Data Preparation

Data files are saved in the `Dataset Modified` folder in our Google Drive.

### [Text] Kaist Corbus

Download modified KAIST corpus dataset and move to directory:
> `input/text/kaist_corpus`  

#### Changes

* Moved all txt files into a single folder/directory named kaist_corpus.  
* Folder contains all the txt files renamed into format: `kaistcorpus_written_raw_or_(subdirectories)_(unique_id).txt`  
* Removed all tags from the txt files to contain only the main contents.  

### [Glyph] HICAU

*Data from Human Interface Lab at CAU*

Download modified HICAU dataset and move to directory
> `input/glyph/hicau_mod0`  

#### Changes 

Modifications are defined in `notebooks/Glyph Processing.ipynb`. Currently (version `_mod0`), we only consider
complete sets that contain all 2447 characters. Note that this only leaves us with 51 out of 576 HW variants.