# llama.cpp CUDA 服务器镜像 - 使用预编译二进制
FROM ubuntu:22.04

# 使用阿里云 Ubuntu 镜像源
RUN rm -f /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/ubuntu/ jammy main restricted universe multiverse" > /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/ubuntu/ jammy-updates main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/ubuntu/ jammy-backports main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/ubuntu/ jammy-security main restricted universe multiverse" >> /etc/apt/sources.list && \
    apt-get update

# 安装依赖
RUN apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    wget \
    libc6 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 下载 llama.cpp 最新 release 的 Linux 二进制文件
# 使用 GitHub 代理加速
RUN cd /tmp && \
    echo "下载 llama.cpp 服务器二进制文件..." && \
    (wget --timeout=60 -q -O llama-server https://ghproxy.com/https://github.com/ggml-org/llama.cpp/releases/download/b4600/llama-server-linux-cuda-cu12.2-x64 2>/dev/null || \
     wget --timeout=60 -q -O llama-server https://github.com/ggml-org/llama.cpp/releases/download/b4600/llama-server-linux-cuda-cu12.2-x64 2>/dev/null || \
     wget --timeout=60 -q -O llama-server https://gh.api.99988866.xyz/https://github.com/ggml-org/llama.cpp/releases/download/b4600/llama-server-linux-cuda-cu12.2-x64) && \
    chmod +x llama-server && \
    mv llama-server /server && \
    echo "llama-server 下载完成"

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["/server"]
