#!/bin/bash
# 环境检查脚本

echo "=========================================="
echo "  Qwen3-30B-A3B-Q4 部署环境检查"
echo "=========================================="
echo ""

# 检查 Docker
echo "[1/5] 检查 Docker..."
if command -v docker &> /dev/null; then
    docker --version
    echo "✓ Docker 已安装"
else
    echo "✗ Docker 未安装"
    echo "  请访问: https://docs.docker.com/engine/install/"
    exit 1
fi
echo ""

# 检查 Docker Compose
echo "[2/5] 检查 Docker Compose..."
if docker-compose --version &> /dev/null || docker compose version &> /dev/null; then
    docker-compose --version 2>/dev/null || docker compose version
    echo "✓ Docker Compose 已安装"
else
    echo "✗ Docker Compose 未安装"
    exit 1
fi
echo ""

# 检查 NVIDIA GPU
echo "[3/5] 检查 NVIDIA GPU..."
if command -v nvidia-smi &> /dev/null; then
    echo "✓ NVIDIA 驱动已安装"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
else
    echo "✗ nvidia-smi 未找到，请安装 NVIDIA 驱动"
    exit 1
fi
echo ""

# 检查 nvidia-docker
echo "[4/5] 检查 NVIDIA Docker 运行时..."
if docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi &> /dev/null; then
    echo "✓ nvidia-docker2 正常工作"
else
    echo "✗ nvidia-docker2 未安装或配置错误"
    echo ""
    echo "请安装 NVIDIA Container Toolkit:"
    echo "  Ubuntu/Debian:"
    echo "    sudo apt-get update"
    echo "    sudo apt-get install -y nvidia-container-toolkit"
    echo "    sudo systemctl restart docker"
    echo ""
    echo "  其他系统请参考:"
    echo "    https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
    exit 1
fi
echo ""

# 检查模型目录
echo "[5/5] 检查模型目录..."
mkdir -p models
if [ -f "models/Qwen3-30B-A3B-Q4_K_M.gguf" ]; then
    echo "✓ 模型文件已存在"
    ls -lh models/Qwen3-30B-A3B-Q4_K_M.gguf
else
    echo "○ 模型文件未下载"
    echo "  请运行: ./download-model.sh"
fi
echo ""

# 磁盘空间检查
echo "[额外] 检查磁盘空间..."
AVAILABLE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$AVAILABLE" -ge 25 ]; then
    echo "✓ 磁盘空间充足: ${AVAILABLE}GB 可用"
else
    echo "⚠ 磁盘空间可能不足: ${AVAILABLE}GB 可用 (建议 ≥ 25GB)"
fi
echo ""

echo "=========================================="
echo "  环境检查完成"
echo "=========================================="
