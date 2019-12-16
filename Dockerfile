FROM ubuntu:xenial

SHELL ["/bin/bash", "-c"]

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PATH /opt/conda/bin:${PATH}

RUN apt-get update --fix-missing && apt-get install -y \
        build-essential \
        coreutils \
        dialog \
        git \
        language-pack-en-base \
        libbz2-dev \
        libcurl4-openssl-dev \
        liblzma-dev \
        libncurses5-dev \
        libncursesw5-dev \
        libreadline-dev \
        libssl-dev \
        unzip \
        wget \
        zlib1g-dev && apt-get clean

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    source /opt/conda/etc/profile.d/conda.sh && \
    conda install -c bioconda cython numpy seqkit picard && \
    conda clean -tipsy

RUN conda config --add channels defaults && \
    conda config --add channels conda-forge && \
    conda config --add channels bioconda && \
    conda install --yes python=3.6 cython numpy picard seqkit && \
    conda clean -tipsy && \
    pip install git+https://github.com/Clinical-Genomics/mutacc

ENV MUTACC_CONFIG_PATH /root/mutacc-config.yaml
COPY docker/mutacc-docker-config.yaml $MUTACC_CONFIG_PATH

ENTRYPOINT ["mutacc", "--config-file", "/root/mutacc-config.yaml"]
