#!/usr/bin/env python

from __future__ import print_function
from .ob_pipeline import ob_pipeline_workflow

from nipype import config, logging

import os, sys,glob
import argparse
from itertools import chain

def ob_wf(scans_dir, work_dir, outputdir, subject_ids,
          batch_size,save_logits,model, rs,no_cuda, loc_arc, seg_arc, wfname='ob_pipeline'):
    
    wf = ob_pipeline_workflow(scans_dir, work_dir, outputdir, subject_ids,
                              batch_size,save_logits,model, rs,no_cuda, loc_arc, seg_arc,wfname)
    wf.inputs.inputnode.subject_ids = subject_ids
    
    return wf
    
    
def main():
    """
    Command line wrapper for preprocessing data
    """
    parser = argparse.ArgumentParser(description='Run Olfactory Bulb pipeline on '\
                                     'T2w scans data.',\
                                     epilog='Example-1: {prog} -s '\
                                     '~/data/scans -w '\
                                     '~/data/work -p 2 -t 2 '\
                                     '--subjects subj1 subj2 '\
                                     '\nExample-2: {prog} -s ~/data/scans'\
                                     ' -w ~/data/work'\
                                     ' -o ~/data/output -p 2 -t 2 -g 1 -gp 1'\
                                     '\n\n'
                                     .format(prog=os.path.basename\
                                             (sys.argv[0])),\
                                     formatter_class=argparse.\
                                     RawTextHelpFormatter)

    parser.add_argument('-s', '--scansdir', help='Scans directory where T2w data' \
                        ' is already downloaded for each subject.', required=True)
    
    parser.add_argument('-w', '--workdir', help='Work directory where data' \
                        ' is processed for each subject.', required=True)

    parser.add_argument('-o', '--outputdir', help='Output directory where ' \
                        'results will be stored.', required=True)

    parser.add_argument('--subjects', help='One or more subject IDs'\
                        '(space separated). If omittied, all subjects will be processed.', \
                        default=None, required=False, nargs='+', action='append')

    parser.add_argument('-batch', "--batch_size", type=int,
                        help='Batch size for inference by default is 16', required=False, default=16)
    parser.add_argument('-logits', "--save_logits", action='store_true',
                        help='Save logits', required=False)
    parser.add_argument('-model', "--model", type=int,
                        help='model number', required=False, default=5)
    parser.add_argument('-rs','--rs',action='store_true',help='compute RS statistics',required=False)

    parser.add_argument('-no_cuda', "--no_cuda", action='store_true',\
                        help='Disable CUDA (no GPU usage, inference on CPU)', required=False)

    parser.add_argument('-loc_arc','--loc_arc',help='Localization architecture',required=False,default='FastSurferCNN')
    parser.add_argument('-seg_arc','--seg_arc',help='Segmentation architecture',required=False,default='AttFastSurferCNN')

    parser.add_argument('-b', '--debug', help='debug mode', action='store_true')
    
    parser.add_argument('-p', '--processes', help='overall number of parallel processes', \
                        default=1, type=int)
    parser.add_argument('-g', '--ngpus', help='number of gpus to use (emb-) parallel', \
                        default=1, type=int)
    parser.add_argument('-gp', '--ngpuproc', help='number of processes per gpu', \
                        default=1, type=int)
    parser.add_argument('-n', '--name', help='Pipeline workflow name', 
                        default='ob_pipeline')

    args = parser.parse_args()
    
    
    scans_dir = os.path.abspath(os.path.expandvars(args.scansdir))
    if not os.path.exists(scans_dir):
        raise IOError("Scans directory does not exist.")
        
    
    subject_ids = []
    
    if args.subjects:
        subject_ids = list(chain.from_iterable(args.subjects))
    else:
        subject_ids = glob.glob(scans_dir.rstrip('/') +'/*')
        subject_ids = [os.path.basename(s.rstrip('/')) for s in subject_ids]


    print ("Creating olfactory bulb pipeline workflow...")
    work_dir = os.path.abspath(os.path.expandvars(args.workdir))
    outputdir = os.path.abspath(os.path.expandvars(args.outputdir))
    
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)

    if not os.path.exists(outputdir):
        os.makedirs(outputdir)        
   
    batch_size=args.batch_size
    save_logits=args.save_logits
    model=args.model
    rs=args.rs
    no_cuda=args.no_cuda
    loc_arc=args.loc_arc
    seg_arc=args.seg_arc
     
    config.update_config({
        'logging': {'log_directory': args.workdir, 'log_to_file': True},
        'execution': {'job_finished_timeout' : 15,
                      'poll_sleep_duration' : 15,
                      'hash_method' : 'content',
                      'local_hash_check' : False,
                      'stop_on_first_crash':False,
                      'crashdump_dir': args.workdir,
                      'crashfile_format': 'txt'
                       },
                       })

    #config.enable_debug_mode()
    logging.update_logging(config)


    obwf = ob_wf(scans_dir, work_dir, outputdir, subject_ids,
                                   batch_size,save_logits,model, rs,no_cuda, loc_arc, seg_arc, wfname=args.name)
        
    # Visualize workflow
    if args.debug:
        obwf.write_graph(graph2use='colored', simple_form=True)

    
    obwf.run(
                            plugin='MultiProc', 
                            plugin_args={'n_procs' : args.processes,'n_gpus': args.ngpus, 'ngpuproc': args.ngpuproc}
                           )
    

    print('Done olfactory bulb segmentation pipeline!!!')

    
if __name__ == '__main__':
    sys.exit(main())
