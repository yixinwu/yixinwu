# DINOv2 Docker Image (轻量版)
# 利用宿主机 PyTorch 环境

FROM ubuntu:22.04

LABEL maintainer="DINOv2 Docker"
LABEL description="DINOv2 Self-Supervised Learning Framework"

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV TORCH_HOME=/root/.cache/torch
ENV HF_HOME=/root/.cache/huggingface

# 安装 Python 3.11 和系统依赖
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa -y \
    && apt-get update \
    && apt-get install -y \
    python3.11 \
    python3.11-distutils \
    python3-pip \
    git \
    wget \
    curl \
    vim \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 创建 PyTorch 挂载目录
RUN mkdir -p /opt/conda/lib/python3.11/site-packages

# 设置 Python 3.11 为默认
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# 升级 pip
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# 安装 DINOv2 所需的 Python 包 (不安装 PyTorch，将挂载宿主机环境)
RUN python3 -m pip install --no-cache-dir \
    numpy \
    scipy \
    pillow \
    opencv-python \
    matplotlib \
    scikit-learn \
    timm \
    transformers \
    einops \
    submitit \
    omegaconf

# 克隆 DINOv2 官方仓库
WORKDIR /workspace
RUN git clone --depth 1 https://github.com/facebookresearch/dinov2.git

# 安装 DINOv2 (不包含 torch 依赖)
WORKDIR /workspace/dinov2
RUN python3 -m pip install --no-cache-dir --no-deps -e .

# 创建模型缓存目录
RUN mkdir -p /root/.cache/torch/hub/checkpoints

# 设置 Python 路径
ENV PYTHONPATH=/opt/conda/lib/python3.11/site-packages:/workspace/dinov2

# 工作目录
WORKDIR /workspace

# 默认命令
CMD ["/bin/bash"]
