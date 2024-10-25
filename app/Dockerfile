FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y build-essential libssl-dev zlib1g-dev \
                       libncurses5-dev libgdbm-dev libnss3-dev \
                       libsqlite3-dev libreadline-dev libffi-dev \
                       curl libbz2-dev && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y xz-utils liblzma-dev

RUN curl -O https://www.python.org/ftp/python/3.12.5/Python-3.12.5.tgz && \
    tar -xzf Python-3.12.5.tgz && \
    cd Python-3.12.5 && \
    ./configure --enable-optimizations && \
    make altinstall && \
    cd .. && \
    rm -rf Python-3.12.5.tgz Python-3.12.5

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*


RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

ENV PATH="/root/.cargo/bin:${PATH}"

RUN apt update
RUN apt install -y git

RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash && \
    apt-get install -y git-lfs && \
    git lfs install

WORKDIR /app

COPY ../requirements.txt requirements.txt
RUN python3.12 -m pip install --no-cache-dir --upgrade -r requirements.txt

COPY .. .
COPY .env app/

EXPOSE 8000

ENV PYTHONPATH=/app

RUN git lfs clone https://huggingface.co/deepvk/USER-bge-m3