FROM nvidia/cuda:10.0-base-centos7

#----------------------------
# Install common dependencies
#----------------------------
RUN yum install -y epel-release bzip2 ca-certificates curl git unzip gcc gcc-c++ libx11-6 postgresql-devel opencl-headers clinfo openblas openblas-devel \
    && yum clean packages \
    && rm -rf /var/cache/yum/* /tmp/* /var/tmp/*


ENV LANG=C.UTF-8 \
    CONDA_AUTO_UPDATE_CONDA=false \
    PATH=/opt:/opt/miniconda/bin:/opt/miniconda/envs/default/bin:/usr/local/cuda/bin:/usr/local/nvidia:/usr/local/nvidia/bin:$PATH \
    LC_ALL=en_US.UTF-8 \
    LD_LIBRARY_PATH=/usr/local/nvidia:/usr/local/nvidia/lib64:/usr/local/cuda/lib64:/lib:/.singularity.d/libs:/lib64:$LD_LIBRARY_PATH \
    MPLCONFIGDIR=~/.config/matplotlib \
    STARTUP="/opt/startup.sh"

COPY ./src /opt/

RUN echo "Downloading and installing Miniconda3 installer and setting up python 3 environment ..." \
    && curl -sSL -o /opt/miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-4.7.12.1-Linux-x86_64.sh \
    && chmod +x /opt/miniconda.sh \
    && bash /opt/miniconda.sh -b -p /opt/miniconda \
    && rm -f /opt/miniconda.sh \
    && /opt/miniconda/bin/conda config --add channels pytorch \
    && /opt/miniconda/bin/conda config --append channels conda-forge \
    && /opt/miniconda/bin/conda create -n default -y python==3.6.9 \
    && source /opt/miniconda/bin/activate default \
    && pip install --upgrade pip \
    && conda clean -y --all \
    && conda install -y -c pytorch cudatoolkit=10.0 pytorch=1.4.0 \
    && cd /opt \
    && pip install -r requirements.txt \
    && pip install -e .


RUN echo "Updating settings for pipeline..." \
    && source /opt/miniconda/bin/activate default \
    && cp -f  /opt/ob_pipeline/multiproc.py /opt/miniconda/envs/default/lib/python3.6/site-packages/nipype/pipeline/plugins/multiproc.py \
    && mkdir -p ~/.config/matplotlib \
    && echo 'backend: Agg' > ~/.config/matplotlib/matplotlibrc \
    && sed -i 's/backend      : TkAgg/backend      : Agg/' /opt/miniconda/envs/default/lib/python3.6/site-packages/matplotlib/mpl-data/matplotlibrc \
    && if [ ! -f "$STARTUP" ]; then \
       echo '#!/usr/bin/env bash' >> $STARTUP; \
       echo 'source  /docker_environment' >> $STARTUP; \
       echo 'export LD_LIBRARY_PATH=/.singularity.d/libs:/lib64:$LD_LIBRARY_PATH' >> $STARTUP; \
       echo 'source /opt/miniconda/bin/activate default' >> $STARTUP; \
       echo 'IFS=";" read -ra COMMANDS <<< "$@"' >> $STARTUP; \
       echo 'for command in "${COMMANDS[@]}";do' >> $STARTUP; \
       echo 'echo "`date` : executing ${command}";' >> $STARTUP; \
       echo '${command}' >> $STARTUP; \
       echo 'done' >> $STARTUP; \
       fi \
    && chmod 755 $STARTUP

ENTRYPOINT ["/opt/startup.sh"]
