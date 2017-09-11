FROM ubuntu:14.04

ENV LANG C.UTF-8

# Install basics
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      ca-certificates \
      curl \
      dstat \
      git \
 && rm -rf /var/lib/apt/lists/*

# Install conda
ENV PATH /opt/miniconda/bin:$PATH
RUN curl -sfL https://repo.continuum.io/miniconda/Miniconda3-4.3.21-Linux-x86_64.sh >miniconda.sh \
 && bash miniconda.sh -p /opt/miniconda -b \
 && rm -f miniconda.sh \
 && conda update --quiet --yes conda \
 && conda install --quiet --yes pip \
 && conda clean --tarballs --packages

# Install conda packages
COPY conda-requirements.txt .
RUN conda install -y --file conda-requirements.txt

# Install pip packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install app
COPY . .
