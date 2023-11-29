#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: Automated segmentation pipeline for Olfactory bulb in high resolutional T2 images
__author__ = 'santiago estrada'
__contact__ = 'estradae@dzne.de'
__copyright__ = ''
__license__ = ''
__date__ = '2021-04'
__version__ = '1.0'


# Copyright 2021 Population Health Sciences and Image Analysis, German Center for Neurodegenerative Diseases(DZNE)
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

from __future__ import division

import nipype.pipeline.engine as pe
from nipype import SelectFiles
import nipype.interfaces.utility as util
from nipype import IdentityInterface, DataSink

from ob_pipeline.configoptions import seg_dir,loc_dir
from ob_pipeline.utils import misc

import sys

import numpy as np
import os
import argparse
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


def read_config(path):
    import yaml
    print("Given configuration file: ", path)
    with open(path, 'r') as file:
        configStruct = yaml.load(file,Loader=yaml.FullLoader)
    return configStruct

def get_full_paths(weights_dict,root_dir):

    new_dict={}
    for key,value in weights_dict.items():
        path = misc.locate_file(value,root_dir)

        if os.path.isfile(path[0]):
            new_dict[key]=path[0]
        else:
            raise ValueError('File for model {} doesnt exist : {}'.format(key,value))

    return  new_dict


def ob_segment(sub_id, in_img, batch_size, rs, model,no_cuda,save_logits, flags):

    import os
    import time
    import nibabel as nib
    from ob_pipeline.utils import conform as conform
    from ob_pipeline.models.OBNet import OBNet
    from ob_pipeline.utils import stats
    from ob_pipeline.utils import visualization
    from ob_pipeline.utils import misc
    from collections import namedtuple
    import glob

    args = namedtuple('ArgNamespace', ['sub_id','in_img', 'batch_size', 'model','rs','no_cuda','save_logits'])

    #args.sub_id=sub_id
    args.sub_id = 'subid'
    args.in_img=in_img
    args.batch_size=batch_size
    args.model=model
    args.rs=rs
    args.no_cuda=no_cuda
    args.save_logits=save_logits

    save_dir=os.getcwd() #args.output_dir
    #misc.create_exp_directory(save_dir)
    logger = misc.setup_logger("log.txt")

    start = time.time()


    if os.path.isfile(args.in_img):

        logger.info('Reading file {}'.format(in_img))
        #load t2 image
        t2_orig_img=nib.load(args.in_img)
        t2_img=conform.conform(t2_orig_img,flags,logger)


        #Prediction
        pipeline= OBNet(args,flags,logger)

        pred_img,t2_crop, logits,coords,cm_logits= pipeline.eval(t2_img,save_dir)

        misc.create_exp_directory(os.path.join(save_dir, 'stats'))

        if coords:
            #calculate stats

            misc.create_exp_directory(os.path.join(save_dir,'QC'))

            visualization.plot_qc_images(save_dir=save_dir,image=t2_crop,prediction=pred_img)


            stats.calculate_stats(args,save_dir,image=t2_crop,prediction=pred_img,logits=logits,cm=coords,cm_logits=cm_logits,logger=logger)

            end = time.time() - start

            logger.info("Total computation time :  %0.4f seconds." % end)
        else:
            stats.calculate_stats_no_loc(args, save_dir)


        stats.obstats2tableRS(args, save_dir)

    else:
        logger.info('ERROR: file {} not found'.format(args.in_img))

    mri_files  =[os.path.abspath(f) for f in glob.glob('mri/*')]
    qc_files   =[os.path.abspath(f) for f in glob.glob('QC/*')]
    stats_files =[os.path.abspath(f) for f in glob.glob('stats/*')]

    return mri_files,qc_files,stats_files 

"""
def option_parse():
    parser = argparse.ArgumentParser(
        description='',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-in_img", "--in_img", help="T2 image path", required=True)

    parser.add_argument("-out_dir", "--output_dir", help="Main output directory where models results are going to be store", required=True)

    parser.add_argument("-sid", "--sub_id", type=str, help="subject id", required=True,
                        default='subid')

    parser.add_argument('-batch', "--batch_size", type=int,
                        help='Batch size for inference by default is 16', required=False, default=16)

    parser.add_argument('-gpu_id', "--gpu_id", type=int,
                        help='GPU device name to run model', required=False, default=0)
    parser.add_argument('-no_cuda', "--no_cuda", action='store_true',
                        help='Disable CUDA (no GPU usage, inference on CPU)', required=False)
    parser.add_argument('-logits', "--save_logits", action='store_true',
                        help='Save logits', required=False)

    parser.add_argument('-model', "--model", type=int,
                        help='model number', required=False, default=5)

    parser.add_argument('-rs','--rs',action='store_true',help='compute RS statistics',required=False)

    parser.add_argument('-loc_dir','--loc_dir',help='Localization weights directory',required=False,default='../LocModels')
    parser.add_argument('-loc_arc','--loc_arc',help='Localization architecture',required=False,default='UNet')

    parser.add_argument('-seg_dir','--seg_dir',help='Segmentation weights directory',required=False,default='../SegModels')
    parser.add_argument('-seg_arc','--seg_arc',help='Segmentation architecture',required=False,default='AttFastSurferCNN')


    args = parser.parse_args()

    FLAGS=set_up_model(seg_dir=args.seg_dir,seg_arc=args.seg_arc,loc_dir=args.loc_dir,loc_arc=args.loc_arc,model=args.model)

    FLAGS.update({'batch_size':args.batch_size})
    FLAGS.update({'loc_arc':args.loc_arc})
    FLAGS.update({'seg_arc':args.seg_arc})

    return args,FLAGS
"""

def set_up_model(model,batch_size,seg_dir,seg_arc,loc_dir,loc_arc):

    from ob_pipeline.ob_pipeline import read_config,get_full_paths
    import os
    import numpy as np

    FLAGS = {}

    FLAGS['base_ornt'] = np.array([[0, -1], [1, 1], [2, 1]])
    FLAGS['spacing'] = [float(0.8), float(0.8), float(0.8)]

    FLAGS['batch_size'] = batch_size
    FLAGS['thickness'] = 1

    FLAGS['num_classes'] = 2

    # Segmenation model
    FLAGS['segmentation'] = {}

    FLAGS['segmentation']['imgSize'] = [96, 96]
    FLAGS['segmentation']['models'] = {}

    FLAGS['localization'] = {}
    FLAGS['localization']['imgSize'] = [192, 192]
    FLAGS['localization']['spacing'] = [1.6, 1.6, 1.6]
    FLAGS['localization']['models'] = {}

    seg_config = os.path.join(seg_dir,seg_arc, seg_arc+'_weights.yml')
    seg_weights = read_config(seg_config)

    if model in [1,2,3,4,5]:
        if model != 5:
            aux_weights={}
            split = 'split_'+ str(model)
            for weight in seg_weights:
                if split in seg_weights[weight]:
                    aux_weights[weight]=seg_weights[weight]
            del seg_weights
            seg_weights = aux_weights.copy()
    else:
        print('Model {} option not available, model option will be change to all models'.format(model))

    seg_weights = get_full_paths(seg_weights, seg_dir)
    FLAGS['segmentation']['models'].update(seg_weights)

    loc_config = os.path.join(loc_dir,loc_arc, loc_arc+'_weights.yml')
    loc_weights = read_config(loc_config)
    loc_weights = get_full_paths(loc_weights, loc_dir)

    FLAGS['localization']['models'].update(loc_weights)

    if '3D' in seg_arc:
        FLAGS.update({'3D': True})
    else:
        FLAGS.update({'3D': False})


    FLAGS.update({'batch_size':batch_size})
    FLAGS.update({'loc_arc':loc_arc})
    FLAGS.update({'seg_arc':seg_arc})

    return FLAGS




def ob_pipeline_workflow(scans_dir, work_dir, outputdir, subject_ids,
                          batch_size,save_logits,model,rs,no_cuda, loc_arc, seg_arc, wfname):


    obwf = pe.Workflow(name=wfname)
    obwf.base_dir=work_dir

    inputnode = pe.Node(interface=IdentityInterface(fields=['subject_ids', 'model', 'outputdir']), name='inputnode')
    inputnode.iterables = [('subject_ids', subject_ids)]
    inputnode.inputs.subject_ids = subject_ids
    inputnode.inputs.model=model
    inputnode.inputs.outputdir = outputdir

    #template for input files
    templates = {"T2": "{subject_id}/T2*.nii.gz"}

    fileselector = pe.Node(SelectFiles(templates), name='fileselect')
    fileselector.inputs.base_directory = scans_dir

    #setup model
    setup_model=pe.Node(interface=util.Function(input_names=['model','batch_size','seg_dir','seg_arc','loc_dir','loc_arc'],
                                                output_names=['flags'],
                                                function=set_up_model),name='setup_model')

    setup_model.inputs.seg_dir=seg_dir
    setup_model.inputs.seg_arc=seg_arc
    setup_model.inputs.loc_dir=loc_dir
    setup_model.inputs.loc_arc=loc_arc
    setup_model.inputs.batch_size=batch_size

    segment_ob = pe.Node(interface=util.Function(input_names=['sub_id', 'in_img', 'batch_size','rs','model','no_cuda', 'save_logits','flags'],
                                                 output_names=['mri_files','qc_files','stats_files'],
                                                 function=ob_segment),name='segment_ob')
    segment_ob.inputs.batch_size=batch_size
    segment_ob.inputs.save_logits=save_logits
    segment_ob.inputs.rs=rs
    segment_ob.inputs.no_cuda=no_cuda


    #%% collect outputs
    datasinkout = pe.Node(interface=DataSink(), name='datasinkout')
    datasinkout.inputs.parameterization=False

    # %% workflow connections

    #step 1
    obwf.connect(inputnode        , 'subject_ids',      fileselector,   'subject_id')
    obwf.connect(inputnode        , 'model',            setup_model,    'model')
    obwf.connect(inputnode        , 'subject_ids',      segment_ob,     'sub_id')
    obwf.connect(inputnode        , 'model',            segment_ob,     'model')
    obwf.connect(fileselector     , 'T2',               segment_ob,     'in_img')
    obwf.connect(setup_model      , 'flags',            segment_ob,     'flags')

    # outputs
    obwf.connect(inputnode        , 'subject_ids',     datasinkout, 'container')
    obwf.connect(inputnode        , 'outputdir',       datasinkout, 'base_directory')
    obwf.connect(segment_ob       , 'mri_files',       datasinkout, 'mri.@mri_files')
    obwf.connect(segment_ob       , 'qc_files',        datasinkout, 'qc.@qc_files')
    obwf.connect(segment_ob       , 'stats_files',     datasinkout, 'stats.@stats_files')


    return obwf

"""
if __name__ == '__main__':

    args,FLAGS= option_parse()

    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID";
    # The GPU id to use, usually either "0" or "1";
    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu_id);

    ob_pipeline(args,FLAGS)


    sys.exit(0)
"""
