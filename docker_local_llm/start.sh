#!/bin/bash
# Qwen3-30B-A3B-Q4 本地启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_FILE="$SCRIPT_DIR/models/Qwen3-30B-A3B-Q4_K_M.gguf"
LLAMA_SERVER="$SCRIPT_DIR/llama-server"

echo "=========================================="
echo "  Qwen3-30B-A3B-Q4 启动脚本"
echo "=========================================="

# 检查模型文件
if [ ! -f "$MODEL_FILE" ]; then
    echo "✗ 错误: 模型文件不存在"
    echo "  路径: $MODEL_FILE"
    echo ""
    echo "请先下载模型:"
    echo "  modelscope download --model Qwen/Qwen3-30B-A3B-GGUF Qwen3-30B-A3B-Q4_K_M.gguf --local_dir ./models"
    exit 1
fi

# 检查模型文件大小（正常约 18-19GB）
FILE_SIZE=$(stat -c%s "$MODEL_FILE" 2>/dev/null || stat -f%z "$MODEL_FILE" 2>/dev/null)
FILE_SIZE_GB=$((FILE_SIZE / 1024 / 1024 / 1024))

echo "模型文件: $MODEL_FILE"
echo "文件大小: ${FILE_SIZE_GB} GB"

if [ "$FILE_SIZE_GB" -lt 17 ] || [ "$FILE_SIZE_GB" -gt 20 ]; then
    echo ""
    echo "⚠️ 警告: 模型文件大小异常!"
    echo "  预期大小: 17-20 GB"
    echo "  实际大小: ${FILE_SIZE_GB} GB"
    echo ""
    echo "可能原因:"
    echo "  1. 下载未完成"
    echo "  2. 文件损坏"
    echo "  3. 多进程同时写入导致文件混乱"
    echo ""
    echo "建议: 删除后重新下载"
    echo "  rm $MODEL_FILE"
    echo "  modelscope download --model Qwen/Qwen3-30B-A3B-GGUF Qwen3-30B-A3B-Q4_K_M.gguf --local_dir ./models"
    exit 1
fi

echo "✓ 模型文件大小正常"

# 检查 llama-server
if [ ! -f "$LLAMA_SERVER" ]; then
    if [ -f "/tmp/llama-cpp-local/build/bin/llama-server" ]; then
        cp "/tmp/llama-cpp-local/build/bin/llama-server" "$LLAMA_SERVER"
        chmod +x "$LLAMA_SERVER"
    else
        echo "✗ llama-server 不存在"
        exit 1
    fi
fi
echo "✓ llama-server: $LLAMA_SERVER"

# 检查 GPU
if command -v nvidia-smi &> /dev/null; then
    echo ""
    echo "GPU 信息:"
    nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader | head -1 | sed 's/^/  /'
fi

echo ""
echo "=========================================="
echo "  启动 llama.cpp server..."
echo "=========================================="

# 配置参数
N_GPU_LAYERS=49          # GPU 层数
CTX_SIZE=4096            # 上下文长度
BATCH_SIZE=512           # 批处理大小
N_THREADS=8              # CPU 线程数

# 如果显存不足，自动调整
GPU_MEM=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
if [ -n "$GPU_MEM" ] && [ "$GPU_MEM" -lt 20000 ]; then
    echo "⚠️  检测到显存不足 ${GPU_MEM}MB，调整参数..."
    N_GPU_LAYERS=25
    CTX_SIZE=2048
fi

echo "  GPU 层数: $N_GPU_LAYERS"
echo "  上下文: $CTX_SIZE tokens"
echo "  服务地址: http://0.0.0.0:8080"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 启动服务（使用保守参数）
exec "$LLAMA_SERVER" \
    --model "$MODEL_FILE" \
    --host 0.0.0.0 \
    --port 8080 \
    --n-gpu-layers "$N_GPU_LAYERS" \
    --ctx-size "$CTX_SIZE" \
    --threads "$N_THREADS" \
    --batch-size "$BATCH_SIZE" \
    --ubatch-size "$BATCH_SIZE" \
    --flash-attn off \
    --no-warmup \
    --mlock \
    "$@"
