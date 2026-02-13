#!/bin/bash
# Qwen3-30B-A3B-Q4 Docker GPU 部署脚本 - 国内镜像版
# 本脚本处理网络限制，使用多种方式获取所需资源

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODELS_DIR="$SCRIPT_DIR/models"
LLAMA_CPP_DIR="/tmp/llama-cpp-local"
MODEL_FILE="$MODELS_DIR/Qwen3-30B-A3B-Q4_K_M.gguf"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查网络连接
check_network() {
    log_info "检查网络连接..."
    
    # 检查多个站点
    local sites=(
        "https://www.modelscope.cn"
        "https://github.com"
        "https://docker.io"
    )
    
    for site in "${sites[@]}"; do
        if curl -s --max-time 5 "$site" > /dev/null 2>&1; then
            log_info "  ✓ 可访问: $site"
        else
            log_warn "  ✗ 无法访问: $site"
        fi
    done
}

# 检查系统要求
check_prerequisites() {
    log_info "检查系统要求..."
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        log_info "请运行 ./install-docker.sh 安装 Docker"
        exit 1
    fi
    log_info "  ✓ Docker 已安装: $(docker --version)"
    
    # 检查 NVIDIA GPU
    if command -v nvidia-smi &> /dev/null; then
        log_info "  ✓ NVIDIA GPU 已检测到:"
        nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | sed 's/^/     /'
    else
        log_warn "  ✗ 未检测到 nvidia-smi，GPU 支持可能不可用"
    fi
    
    # 检查 NVIDIA Container Toolkit
    if command -v nvidia-container-runtime &> /dev/null; then
        log_info "  ✓ NVIDIA Container Toolkit 已安装"
    else
        log_warn "  ✗ NVIDIA Container Toolkit 未安装"
        log_info "    请运行 ./install-docker.sh 安装"
    fi
    
    # 创建模型目录
    mkdir -p "$MODELS_DIR"
}

# 下载 llama.cpp 源码
download_llama_cpp() {
    log_info "获取 llama.cpp..."
    
    if [ -d "$LLAMA_CPP_DIR" ]; then
        log_info "  llama.cpp 已存在"
        return 0
    fi
    
    local urls=(
        "https://ghproxy.com/https://github.com/ggml-org/llama.cpp/archive/refs/heads/master.tar.gz"
        "https://gh.api.99988866.xyz/https://github.com/ggml-org/llama.cpp/archive/refs/heads/master.tar.gz"
        "https://github.com/ggml-org/llama.cpp/archive/refs/heads/master.tar.gz"
    )
    
    for url in "${urls[@]}"; do
        log_info "  尝试下载: $url"
        if wget --timeout=120 -q --show-progress -O /tmp/llama.tar.gz "$url" 2>&1; then
            log_info "  ✓ 下载成功"
            tar xzf /tmp/llama.tar.gz -C /tmp/
            mv /tmp/llama.cpp-master "$LLAMA_CPP_DIR"
            rm -f /tmp/llama.tar.gz
            log_info "  ✓ llama.cpp 解压完成"
            return 0
        fi
    done
    
    log_error "无法下载 llama.cpp 源码"
    return 1
}

# 编译 llama.cpp
build_llama_cpp() {
    log_info "编译 llama.cpp (CUDA 版本)..."
    
    cd "$LLAMA_CPP_DIR"
    
    if [ -f "build/bin/llama-server" ]; then
        log_info "  ✓ llama-server 已编译"
        return 0
    fi
    
    # 检查 CUDA
    if ! command -v nvcc &> /dev/null; then
        log_error "CUDA 未安装，无法编译 GPU 版本"
        log_info "将使用 CPU 版本 (性能较低)"
        cmake -B build -DCMAKE_BUILD_TYPE=Release
    else
        log_info "  使用 CUDA: $(nvcc --version | grep release)"
        cmake -B build \
            -DLLAMA_CUDA=ON \
            -DLLAMA_CUDA_F16=ON \
            -DCMAKE_BUILD_TYPE=Release \
            -DCMAKE_CUDA_ARCHITECTURES="70;75;80;86;89"
    fi
    
    log_info "  开始编译 (这可能需要几分钟)..."
    if cmake --build build --config Release -j$(nproc) --target llama-server; then
        log_info "  ✓ 编译完成"
        return 0
    else
        log_error "编译失败"
        return 1
    fi
}

# 安装 modelscope
install_modelscope() {
    log_info "检查 modelscope..."
    
    if python3 -c "import modelscope" 2>/dev/null; then
        log_info "  ✓ modelscope 已安装"
        return 0
    fi
    
    log_info "  安装 modelscope (使用清华镜像)..."
    pip3 install -q -i https://pypi.tuna.tsinghua.edu.cn/simple modelscope
    log_info "  ✓ modelscope 安装完成"
}

# 下载模型
download_model() {
    log_info "检查模型文件..."
    
    if [ -f "$MODEL_FILE" ]; then
        log_info "  ✓ 模型文件已存在: $MODEL_FILE"
        ls -lh "$MODEL_FILE"
        return 0
    fi
    
    # 尝试使用 modelscope 下载
    install_modelscope
    
    log_info "  使用魔搭社区 (ModelScope) 下载模型..."
    
    python3 << EOF
from modelscope import snapshot_download
import sys

try:
    model_dir = snapshot_download(
        "Qwen/Qwen3-30B-A3B-GGUF",
        allow_file_pattern=["qwen3-30b-a3b-q4_k_m.gguf"],
        local_dir="$MODELS_DIR",
        local_dir_use_symlinks=False
    )
    print(f"模型下载成功: {model_dir}")
    sys.exit(0)
except Exception as e:
    print(f"下载失败: {e}")
    sys.exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        # 重命名文件
        if [ -f "$MODELS_DIR/qwen3-30b-a3b-q4_k_m.gguf" ]; then
            mv "$MODELS_DIR/qwen3-30b-a3b-q4_k_m.gguf" "$MODEL_FILE"
        fi
        log_info "  ✓ 模型下载完成"
        ls -lh "$MODEL_FILE"
        return 0
    fi
    
    # 备用: 直接下载
    log_warn "  modelscope 下载失败，尝试直接下载..."
    
    local urls=(
        "https://www.modelscope.cn/models/Qwen/Qwen3-30B-A3B-GGUF/resolve/master/qwen3-30b-a3b-q4_k_m.gguf"
        "https://hf-mirror.com/Qwen/Qwen3-30B-A3B-GGUF/resolve/main/qwen3-30b-a3b-q4_k_m.gguf"
    )
    
    for url in "${urls[@]}"; do
        log_info "  尝试: $url"
        if wget --timeout=300 --show-progress -O "$MODEL_FILE" "$url" 2>&1; then
            log_info "  ✓ 模型下载完成"
            return 0
        fi
    done
    
    log_error "模型下载失败"
    return 1
}

# 创建 Docker 镜像
create_docker_image() {
    log_info "创建 Docker 镜像..."
    
    # 创建 Dockerfile
    cat > "$SCRIPT_DIR/Dockerfile.local" << 'EOF'
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

# 安装依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

# 复制 llama-server
COPY llama-server /server
RUN chmod +x /server

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1
ENTRYPOINT ["/server"]
EOF
    
    # 复制编译好的二进制文件
    cp "$LLAMA_CPP_DIR/build/bin/llama-server" "$SCRIPT_DIR/"
    
    # 构建镜像
    cd "$SCRIPT_DIR"
    if docker build -f Dockerfile.local -t llama-cpp-qwen3:local . 2>&1; then
        log_info "  ✓ Docker 镜像创建成功"
        return 0
    else
        log_error "Docker 镜像创建失败"
        return 1
    fi
}

# 更新 docker-compose.yml
update_docker_compose() {
    log_info "更新 docker-compose 配置..."
    
    cat > "$SCRIPT_DIR/docker-compose.yml" << EOF
version: '3.8'

services:
  llm-qwen3:
    image: llama-cpp-qwen3:local
    container_name: qwen3-30b-a3b-q4
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - CUDA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
    ports:
      - "8080:8080"
    volumes:
      - ./models:/models:rw
      - ./entrypoint.sh:/entrypoint.sh:ro
    working_dir: /models
    entrypoint: ["/bin/bash", "/entrypoint.sh"]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 120s
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
EOF
    
    log_info "  ✓ docker-compose.yml 已更新"
}

# 创建启动脚本
create_launch_script() {
    log_info "创建启动脚本..."
    
    cat > "$SCRIPT_DIR/start-local.sh" << EOF
#!/bin/bash
# 本地启动 Qwen3-30B-A3B-Q4 (不使用 Docker)

MODEL_FILE="$MODEL_FILE"
LLAMA_SERVER="$LLAMA_CPP_DIR/build/bin/llama-server"

if [ ! -f "\$MODEL_FILE" ]; then
    echo "错误: 模型文件不存在"
    echo "请运行: ./deploy.sh"
    exit 1
fi

echo "启动 llama.cpp server (本地模式)..."
echo "  模型: \$MODEL_FILE"
echo "  GPU: 启用"
echo "  服务地址: http://0.0.0.0:8080"

exec "\$LLAMA_SERVER" \\
    --model "\$MODEL_FILE" \\
    --host 0.0.0.0 \\
    --port 8080 \\
    --n-gpu-layers 999 \\
    --ctx-size 32768 \\
    --threads 8 \\
    --batch-size 512 \\
    --flash-attn \\
    --mlock
EOF
    
    chmod +x "$SCRIPT_DIR/start-local.sh"
    log_info "  ✓ 本地启动脚本: ./start-local.sh"
}

# 主函数
main() {
    echo "=========================================="
    echo "  Qwen3-30B-A3B-Q4 Docker GPU 部署"
    echo "=========================================="
    echo ""
    
    # 检查网络
    check_network
    
    # 检查系统要求
    check_prerequisites
    
    # 下载并编译 llama.cpp
    if ! download_llama_cpp; then
        log_error "无法获取 llama.cpp 源码"
        log_info "请手动下载: https://github.com/ggml-org/llama.cpp"
        exit 1
    fi
    
    if ! build_llama_cpp; then
        log_error "编译失败"
        exit 1
    fi
    
    # 下载模型
    if ! download_model; then
        log_error "无法下载模型"
        log_info "请手动下载:"
        log_info "  访问: https://www.modelscope.cn/models/Qwen/Qwen3-30B-A3B-GGUF"
        log_info "  下载: qwen3-30b-a3b-q4_k_m.gguf"
        log_info "  放置到: $MODELS_DIR/"
        exit 1
    fi
    
    # 创建 Docker 镜像
    create_docker_image
    
    # 更新配置
    update_docker_compose
    
    # 创建本地启动脚本
    create_launch_script
    
    echo ""
    echo "=========================================="
    echo "  部署完成!"
    echo "=========================================="
    echo ""
    log_info "启动方式:"
    echo "  1. Docker 方式: docker-compose up -d"
    echo "  2. 本地方式:   ./start-local.sh"
    echo ""
    log_info "测试 API:"
    echo "  curl http://localhost:8080/v1/chat/completions \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"model\": \"qwen3\", \"messages\": [{\"role\": \"user\", \"content\": \"你好\"}]}'"
    echo ""
}

# 运行
main "$@"
