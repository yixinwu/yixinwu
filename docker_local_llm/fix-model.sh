#!/bin/bash
# 修复模型文件 - 重新下载

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_FILE="$SCRIPT_DIR/models/Qwen3-30B-A3B-Q4_K_M.gguf"

echo "=========================================="
echo "  修复模型文件"
echo "=========================================="
echo ""

# 检查当前文件
if [ -f "$MODEL_FILE" ]; then
    FILE_SIZE=$(stat -c%s "$MODEL_FILE" 2>/dev/null || stat -f%z "$MODEL_FILE" 2>/dev/null)
    FILE_SIZE_GB=$((FILE_SIZE / 1024 / 1024 / 1024))
    echo "当前文件大小: ${FILE_SIZE_GB} GB"
    
    if [ "$FILE_SIZE_GB" -ge 17 ] && [ "$FILE_SIZE_GB" -le 20 ]; then
        echo "✓ 文件大小正常，无需修复"
        exit 0
    fi
    
    echo ""
    echo "⚠️ 文件大小异常，需要重新下载"
    echo ""
    read -p "是否删除并重新下载? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 0
    fi
    
    echo "删除旧文件..."
    rm -f "$MODEL_FILE"
fi

# 停止任何正在运行的下载
pkill -f "modelscope download" 2>/dev/null || true

# 安装 aria2（如果可用）
if ! command -v aria2c &> /dev/null; then
    echo "安装 aria2..."
    sudo apt-get update && sudo apt-get install -y aria2 2>/dev/null || echo "无法安装 aria2，使用 wget"
fi

echo ""
echo "开始下载模型..."
echo "来源: 魔搭社区 (ModelScope)"
echo "文件: Qwen3-30B-A3B-Q4_K_M.gguf"
echo "大小: 约 18 GB"
echo ""

MODEL_URL="https://www.modelscope.cn/models/Qwen/Qwen3-30B-A3B-GGUF/resolve/master/Qwen3-30B-A3B-Q4_K_M.gguf"

if command -v aria2c &> /dev/null; then
    echo "使用 aria2 多线程下载..."
    aria2c -c -x 16 -s 16 -k 1M \
        --console-log-level=warn --summary-interval=10 \
        -o "models/Qwen3-30B-A3B-Q4_K_M.gguf" \
        "$MODEL_URL"
elif command -v wget &> /dev/null; then
    echo "使用 wget 下载..."
    wget --show-progress --timeout=600 --continue \
        -O "$MODEL_FILE" \
        "$MODEL_URL"
else
    echo "使用 modelscope 下载..."
    pip install -q modelscope
    modelscope download --model Qwen/Qwen3-30B-A3B-GGUF Qwen3-30B-A3B-Q4_K_M.gguf --local_dir ./models
fi

echo ""
echo "=========================================="
echo "  下载完成!"
echo "=========================================="
ls -lh "$MODEL_FILE"
