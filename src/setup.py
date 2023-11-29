#!/usr/bin/env python

"""
#Rhineland Study MRI Post-processing pipelines
#rs_olfbulb_pipeline: Pipeline for segmentation of Olfactory Bulb using python/nipype
"""
import os
import sys
from glob import glob
if os.path.exists('MANIFEST'): os.remove('MANIFEST')

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('ob_pipeline/models/rs_ob_models')


def main(**extra_args):
    from setuptools import setup
    setup(name='ob_pipeline',
          version='1.0.0',
          description='RhinelandStudy Olfactory Bulb Pipeline',
          long_description="""RhinelandStudy processing for olfactory bulb segmentation using T2 scans """, 
          author= 'estradae',
          author_email='estradae@dzne.de',
          url='http://www.dzne.de/',
          packages = ['ob_pipeline',
                      'ob_pipeline.utils','ob_pipeline.models'],
          entry_points={
            'console_scripts': [
                             "run_ob_pipeline=ob_pipeline.run_ob_pipeline:main"
                              ]
                       },
          license='DZNE License',
          classifiers = [c.strip() for c in """\
            Development Status :: 1.0 (2021)
            Intended Audience :: Developers
            Intended Audience :: Science/Research
            Operating System :: OS Independent
            Programming Language :: Python
            Topic :: Software Development
            """.splitlines() if len(c.split()) > 0],    
          maintainer = 'RheinlandStudy MRI/MRI-IT group, DZNE',
          maintainer_email = 'mohammad.shahid@dzne.de',
          package_data = {'ob_pipeline': extra_files},
          install_requires=["nipype","nibabel"],
          **extra_args
         )

if __name__ == "__main__":
    main()

