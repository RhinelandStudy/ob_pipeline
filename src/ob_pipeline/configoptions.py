#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 15:18:10 2017

@author: shahidm
"""

from os.path import realpath, join, abspath, dirname


# defaults
SCRIPT_PATH = dirname(realpath(__file__))

MODELS_DIR = abspath(join(SCRIPT_PATH, 'models'))

seg_dir = join(MODELS_DIR, 'rs_ob_models','SegModels')
loc_dir = join(MODELS_DIR, 'rs_ob_models','LocModels')

