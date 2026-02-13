#!/bin/bash
set -e

MODEL_FILE="/models/Qwen3-30B-A3B-Q4_K_M.gguf"
MODEL_FILE_ALT="/models/qwen3-30b-a3b-q4_k_m.gguf"

# 使用国内镜像源 - 魔搭社区 (ModelScope)
MODEL_URL="https://www.modelscope.cn/models/Qwen/Qwen3-30B-A3B-GGUF/resolve/master/Qwen3-30B-A3B-Q4_K_M.gguf"
# 备用镜像
HF_MIRROR_URL="https://hf-mirror.com/Qwen/Qwen3-30B-A3B-GGUF/resolve/main/Qwen3-30B-A3B-Q4_K_M.gguf"

echo "=========================================="
echo "  Qwen3-30B-A3B-Q4 Docker Deployment"
echo "=========================================="

# 检查模型文件是否存在 (支持两种命名)
if [ -f "$MODEL_FILE" ]; then
    echo "✓ 模型文件已存在: $MODEL_FILE"
    ls -lh "$MODEL_FILE"
elif [ -f "$MODEL_FILE_ALT" ]; then
    echo "✓ 模型文件已存在: $MODEL_FILE_ALT"
    mv "$MODEL_FILE_ALT" "$MODEL_FILE"
    ls -lh "$MODEL_FILE"
else
    echo "× 模型文件不存在，开始下载..."
    echo "  目标: $MODEL_FILE"
    echo ""
    
    # 创建目录
    mkdir -p /models
    
    # 使用国内镜像下载
    echo "[1/2] 尝试从魔搭社区 (ModelScope) 下载..."
    echo "  URL: $MODEL_URL"
    if wget --timeout=600 --tries=2 --progress=bar:force -O "$MODEL_FILE" "$MODEL_URL" 2>&1; then
        echo "  ✓ 从魔搭社区下载成功"
    else
        echo "  从魔搭社区下载失败，尝试 HF-Mirror..."
        
        echo "[2/2] 尝试从 HF-Mirror 下载..."
        echo "  URL: $HF_MIRROR_URL"
        if ! wget --timeout=600 --tries=2 --progress=bar:force -O "$MODEL_FILE" "$HF_MIRROR_URL" 2>&1; then
            echo ""
            echo "=========================================="
            echo "  下载失败！请手动下载模型文件:"
            echo "=========================================="
            echo ""
            echo "  推荐方式 - 魔搭社区 (国内最快):"
            echo "     浏览器访问:"
            echo "     https://www.modelscope.cn/models/Qwen/Qwen3-30B-A3B-GGUF"
            echo ""
            echo "  或使用命令行 (需安装 modelscope):"
            echo "     pip install modelscope"
            echo "     modelscope download --model Qwen/Qwen3-30B-A3B-GGUF Qwen3-30B-A3B-Q4_K_M.gguf --local_dir ./models"
            echo ""
            echo "  下载后放置到目录: ./models/"
            echo ""
            exit 1
        fi
    fi
    
    echo ""
    echo "✓ 模型下载完成!"
    ls -lh "$MODEL_FILE"
fi

echo ""
echo "=========================================="
echo "  启动 llama.cpp server..."
echo "=========================================="
echo "  模型: $MODEL_FILE"
echo "  GPU加速: 启用 (n_gpu_layers=999)"
echo "  上下文: 32768 tokens"
echo "  服务地址: http://0.0.0.0:8080"
echo "=========================================="
echo ""

# 启动llama-server
exec /server \
    --model "$MODEL_FILE" \
    --host 0.0.0.0 \
    --port 8080 \
    --n-gpu-layers 999 \
    --ctx-size 32768 \
    --threads 8 \
    --batch-size 512 \
    --ubatch-size 512 \
    --flash-attn \
    --mlock \
    "$@"
