#!/bin/bash
# 使用国内镜像代理拉取 Docker 镜像

set -e

echo "=========================================="
echo "  拉取 llama.cpp CUDA 镜像"
echo "=========================================="
echo ""

# 方法1: 使用 DaoCloud 镜像站
echo "[方法1] 尝试从 DaoCloud 镜像站拉取..."
if docker pull docker.m.daocloud.io/ghcr.io/ggml-org/llama.cpp:server-cuda 2>/dev/null; then
    docker tag docker.m.daocloud.io/ghcr.io/ggml-org/llama.cpp:server-cuda ghcr.io/ggml-org/llama.cpp:server-cuda
    docker rmi docker.m.daocloud.io/ghcr.io/ggml-org/llama.cpp:server-cuda
    echo "✓ 拉取成功 (DaoCloud)"
    exit 0
fi

# 方法2: 使用阿里云镜像站
echo "[方法2] 尝试配置阿里云镜像..."
# 阿里云镜像需要配置镜像源，已经在 install-docker.sh 中配置

# 方法3: 直接拉取 (如果已配置镜像源)
echo "[方法3] 尝试直接拉取 (使用已配置的镜像源)..."
if docker pull ghcr.io/ggml-org/llama.cpp:server-cuda; then
    echo "✓ 拉取成功"
    exit 0
fi

# 方法4: 使用本地构建
echo ""
echo "=========================================="
echo "  远程拉取失败，使用本地构建方案"
echo "=========================================="
echo ""

# 检查本地是否有编译好的 llama-server
if [ -f "./llama-server" ]; then
    echo "✓ 找到本地 llama-server"
else
    echo "× 未找到本地 llama-server"
    echo ""
    echo "请选择以下方式之一:"
    echo ""
    echo "  方式1 - 手动下载二进制文件:"
    echo "     访问: https://github.com/ggml-org/llama.cpp/releases"
    echo "     下载: llama-server-linux-cuda-cu12.2-x64"
    echo "     放置到: ./llama-server"
    echo ""
    echo "  方式2 - 本地编译:"
    echo "     git clone https://github.com/ggml-org/llama.cpp"
    echo "     cd llama.cpp && cmake -B build -DLLAMA_CUDA=ON && cmake --build build"
    echo "     cp build/bin/llama-server /path/to/project/"
    echo ""
    exit 1
fi

# 使用本地 Dockerfile 构建
echo "使用本地 Dockerfile 构建镜像..."

# 创建临时 Dockerfile
cat > Dockerfile.ghcr << 'EOF'
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl && rm -rf /var/lib/apt/lists/*

COPY llama-server /server
RUN chmod +x /server

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1
ENTRYPOINT ["/server"]
EOF

# 构建镜像
docker build -f Dockerfile.ghcr -t ghcr.io/ggml-org/llama.cpp:server-cuda .
rm -f Dockerfile.ghcr

echo ""
echo "✓ 本地镜像构建完成"
