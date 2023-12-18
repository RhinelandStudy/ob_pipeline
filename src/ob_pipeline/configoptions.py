#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2023 Population Health Sciences and AI in Medical Imaging, German Center for Neurodegenerative Diseases (DZNE)
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


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

