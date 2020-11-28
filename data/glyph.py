"""
Glossary
character: string characters like "가", "나", "다"
glyph: image of a character
"""
import glob
import os
import re
import warnings
from collections import defaultdict
from typing import Set
import random
from PIL import Image


class GlyphLoader:
    def __init__(self, dataset_dir, ext="tif"):
        """
        :param dataset_dir:
        """
        self.dataset_dir = dataset_dir
        self.ext = ext

        paths = glob.glob(os.path.join(dataset_dir, "*/*.{}".format(ext)), recursive=True)
        re_path = re.compile(".*/([^/]*)/([0-9A-Fa-f]{4})." + ext)

        if len(paths) == 0:
            raise ValueError("No .{} files found in dataset_dir {}".format(ext, dataset_dir))

        pids = set()
        d = defaultdict(set) # { pid: [ chars ], ... }
        for path in paths:
            match = re_path.match(path)
            if not match:
                raise ValueError("Invalid file found in dataset_dir {}: {}".format(dataset_dir, path))
            pid, char = match.groups()
            pids.add(pid)
            d[pid].add(char)
        pids = sorted(list(pids))

        character_set = d[pids[0]]
        for pid in pids:
            assert(character_set == d[pid])

        self.character_set = character_set
        self.pids = pids
        self.variants = len(pids)

    def load_glyph(self, character, variant_index=None, path_only=False):
        """
        :param character: "가", "나", "다", etc.
        :param variant_index: Whose handwriting? Range: [0, len(self.variants)) (random if None)
        :param path_only: Whether to return path of image file (else, PIL Image)
        :return:
        """
        if not 0 <= variant_index < len(self.pids):
            warnings.warn("Varient index {} is out of bounds [{}, {})".format(variant_index, 0, len(self.pids)))
            variant = None
        if variant_index is None:
            variant_index = random.randint(0, len(self.pids))
        pid = self.pids[variant_index]
        hex = "{:04x}".format(ord(character))
        path = os.path.join(self.dataset_dir, pid, "{}.{}".format(hex, self.ext))

        if path_only:
            return path
        else:
            return Image.open(path)
