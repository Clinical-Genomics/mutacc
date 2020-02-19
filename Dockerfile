FROM ubuntu:xenial

SHELL ["/bin/bash", "-c"]

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PATH /opt/conda/bin:${PATH}

COPY . /source/mutacc

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

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-4.7.10-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    source /opt/conda/etc/profile.d/conda.sh && \
    conda clean -tipsy

RUN conda config --add channels defaults && \
    conda config --add channels conda-forge && \
    conda config --add channels bioconda && \
    conda install --yes python=3.6 cython=0.29 numpy=1.17 picard=2.18 seqkit=0.11 && \
    conda clean -tipsy

RUN pip install source/mutacc
