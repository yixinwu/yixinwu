#!/bin/bash
# Qwen3-30B-A3B-Q4 模型下载脚本 - 使用国内镜像源

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODELS_DIR="$SCRIPT_DIR/models"
MODEL_FILE="$MODELS_DIR/Qwen3-30B-A3B-Q4_K_M.gguf"

# 魔搭社区 (ModelScope) - 国内首选
# 注意: 文件名是 Qwen3-30B-A3B-Q4_K_M.gguf (大写)
MODELSCOPE_URL="https://www.modelscope.cn/models/Qwen/Qwen3-30B-A3B-GGUF/resolve/master/Qwen3-30B-A3B-Q4_K_M.gguf"

# 备用镜像源
HF_MIRROR_URL="https://hf-mirror.com/Qwen/Qwen3-30B-A3B-GGUF/resolve/main/Qwen3-30B-A3B-Q4_K_M.gguf"

mkdir -p "$MODELS_DIR"

echo "=========================================="
echo "  Qwen3-30B-A3B-Q4 模型下载"
echo "  使用国内镜像源 (魔搭社区)"
echo "=========================================="
echo "  模型文件: Qwen3-30B-A3B-Q4_K_M.gguf"
echo "  保存路径: $MODEL_FILE"
echo "  文件大小: 约 18 GB"
echo "=========================================="
echo ""

# 检查是否已存在
if [ -f "$MODEL_FILE" ]; then
    echo "✓ 模型文件已存在!"
    ls -lh "$MODEL_FILE"
    echo ""
    read -p "是否重新下载? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "跳过下载，使用现有文件。"
        exit 0
    fi
    rm -f "$MODEL_FILE"
fi

# 检查可用下载工具
check_downloader() {
    if command -v aria2c &> /dev/null; then
        echo "aria2c"
    elif command -v wget &> /dev/null; then
        echo "wget"
    elif command -v curl &> /dev/null; then
        echo "curl"
    else
        echo "none"
    fi
}

DOWNLOADER=$(check_downloader)

if [ "$DOWNLOADER" = "none" ]; then
    echo "✗ 错误: 需要安装 aria2c、wget 或 curl"
    echo "  安装命令: sudo apt-get install -y aria2 wget curl"
    exit 1
fi

echo "✓ 使用下载工具: $DOWNLOADER"
echo ""

# 下载函数
download_with_aria2() {
    local url=$1
    local output=$2
    aria2c -c -x 16 -s 16 -k 1M --max-connection-per-server=16 \
        --console-log-level=warn --summary-interval=5 \
        -o "$output" "$url"
}

download_with_wget() {
    local url=$1
    local output=$2
    wget --show-progress --timeout=600 --tries=3 --continue \
        -O "$output" "$url"
}

download_with_curl() {
    local url=$1
    local output=$2
    curl -L --progress-bar --max-time 600 --retry 3 --continue-at - \
        -o "$output" "$url"
}

download_model() {
    local url=$1
    local name=$2
    local output="$MODEL_FILE.tmp"
    
    echo "[尝试] 从 $name 下载..."
    echo "  URL: $url"
    
    case $DOWNLOADER in
        aria2c)
            download_with_aria2 "$url" "$output"
            ;;
        wget)
            download_with_wget "$url" "$output"
            ;;
        curl)
            download_with_curl "$url" "$output"
            ;;
    esac
    
    if [ $? -eq 0 ] && [ -f "$output" ]; then
        mv "$output" "$MODEL_FILE"
        return 0
    fi
    
    rm -f "$output"
    return 1
}

# 优先使用魔搭社区
echo ""
if download_model "$MODELSCOPE_URL" "魔搭社区 (ModelScope)"; then
    echo ""
    echo "✓ 从 魔搭社区 下载成功!"
else
    echo "× 魔搭社区下载失败，尝试备用镜像..."
    echo ""
    
    if download_model "$HF_MIRROR_URL" "HF-Mirror (镜像站)"; then
        echo ""
        echo "✓ 从 HF-Mirror 下载成功!"
    else
        echo ""
        echo "=========================================="
        echo "  自动下载失败!"
        echo "=========================================="
        echo ""
        echo "请尝试以下方式手动下载:"
        echo ""
        echo "  方式一 - 魔搭社区 (推荐):"
        echo "     浏览器访问:"
        echo "     https://www.modelscope.cn/models/Qwen/Qwen3-30B-A3B-GGUF"
        echo ""
        echo "  方式二 - 命令行 (需要安装 modelscope):"
        echo "     pip install modelscope"
        echo "     modelscope download --model Qwen/Qwen3-30B-A3B-GGUF Qwen3-30B-A3B-Q4_K_M.gguf --local_dir ./models"
        echo ""
        echo "  方式三 - 浏览器下载后放置到:"
        echo "     $MODELS_DIR/"
        echo ""
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "  下载完成!"
echo "=========================================="
ls -lh "$MODEL_FILE"
echo ""
echo "✓ 现在可以运行: docker-compose up -d"
