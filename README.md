# olfactory bulb segmentation pipeline
Olfactory bulb segmentation pipeline for T2 weighted images

## Build docker image

```bash

nvidia-docker build -t ob_pipeline -f docker/Dockerfile .


```

## Or pull from docker hub

```bash
docker pull dznerheinlandstudie/rheinlandstudie:ob_pipeline
```

## Run pipeline:

### Using docker
The pipeline can be run with docker by running the container as follows:


```bash

 nvidia-docker run --rm -v /path/to/input_scans:/input \
                 -v /path/to/work_folder:/work \
                 -v /path/to/output:/output \
        dznerheinlandstudie/rheinlandstudie:ob_pipeline \
        run_ob_pipeline \
        -s /input \
        --subjects test_subject_01 \
        -w /work \
        -o /output \ 
        -p 4 -t 2

```

The command line options are described briefly if the pipeline is started with only ```-h``` option.

### Using Singulraity

The pipeline can be run with Singularity by running the singularity image as follows:

```bash

export SINGULARITY_DOCKER_USERNAME=username
export SINGULARITY_DOCKER_PASSWORD=password

singularity build ob_pipeline.sif docker://dznerheinlandstudie/rheinlandstudie:ob_pipeline
```

When the singularit image is created, then it can be run as follows:

```bash

singularity run --nv -B /path/to/inputdata:/input \
                     -B /path/to/work:/work \
                     -B /path/to/output:/output \
            ob_pipeline.sif "export TFNUM_THREADS=2;export GOTO_NUM_THREADS=2;\
            run_ob_pipeline \ 
                      -s /input \
                      -w /work \
                      -o /output \ 
                      -p 4 -t 2 -g 1 -gp 1"
```



