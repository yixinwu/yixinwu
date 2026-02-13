#!/bin/bash
# Docker 和 NVIDIA Container Toolkit 安装脚本

set -e

echo "=========================================="
echo "  Docker 及 GPU 支持安装脚本"
echo "=========================================="
echo ""

# 检测系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
else
    echo "✗ 无法检测操作系统"
    exit 1
fi

echo "检测到的系统: $OS $VERSION"

# 检查是否为 Ubuntu/Debian
if [[ "$OS" != "ubuntu" && "$OS" != "debian" ]]; then
    echo "⚠ 警告: 此脚本主要为 Ubuntu/Debian 系统设计"
    read -p "是否继续? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# ========== 步骤1: 卸载旧版本 ==========
echo ""
echo "[1/6] 卸载旧版本 Docker..."
sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# ========== 步骤2: 安装依赖 ==========
echo ""
echo "[2/6] 安装依赖..."
sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    apt-transport-https

# ========== 步骤3: 添加 Docker 官方 GPG 密钥 ==========
echo ""
echo "[3/6] 添加 Docker 源..."
sudo install -m 0755 -d /etc/apt/keyrings

# 使用国内镜像
if curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg 2>/dev/null; then
    echo "✓ 使用阿里云镜像源"
    DOCKER_MIRROR="aliyun"
else
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo "✓ 使用官方源"
    DOCKER_MIRROR="official"
fi

sudo chmod a+r /etc/apt/keyrings/docker.gpg

# ========== 步骤4: 添加 Docker 软件源 ==========
echo ""
echo "添加 Docker 软件源..."

if [ "$DOCKER_MIRROR" = "aliyun" ]; then
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
else
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
fi

sudo apt-get update

# ========== 步骤5: 安装 Docker ==========
echo ""
echo "[4/6] 安装 Docker..."
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# ========== 配置 Docker 国内镜像源 ==========
echo ""
echo "[4.5/6] 配置 Docker 国内镜像源..."

sudo mkdir -p /etc/docker

sudo tee /etc/docker/daemon.json > /dev/null << 'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com",
    "https://dockerproxy.com",
    "https://docker.m.daocloud.io",
    "https://docker.nju.edu.cn"
  ],
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2"
}
EOF

echo "✓ Docker 镜像源配置完成"
sudo systemctl restart docker

# 添加当前用户到 docker 组
echo ""
echo "将当前用户添加到 docker 组..."
sudo usermod -aG docker $USER

echo "✓ Docker 安装完成"
docker --version

# ========== 步骤6: 安装 NVIDIA Container Toolkit ==========
echo ""
echo "[5/6] 安装 NVIDIA Container Toolkit..."

# 检查 NVIDIA GPU
if command -v nvidia-smi &> /dev/null; then
    echo "✓ 检测到 NVIDIA GPU"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
else
    echo "⚠ 未检测到 nvidia-smi，请确保 NVIDIA 驱动已安装"
    echo "  安装驱动后请重新运行此脚本"
fi

# 添加 NVIDIA Container Toolkit 源
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# 配置 Docker 使用 nvidia-container-runtime
sudo nvidia-ctk runtime configure --runtime=docker

# 重启 Docker
sudo systemctl restart docker

# 测试 GPU 支持
echo ""
echo "[6/6] 测试 GPU 支持..."
if docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi 2>/dev/null; then
    echo "✓ NVIDIA Container Toolkit 安装成功!"
else
    echo "⚠ GPU 测试失败，可能需要重启 Docker 服务或系统"
fi

echo ""
echo "=========================================="
echo "  安装完成!"
echo "=========================================="
echo ""
echo "请执行以下命令使配置生效:"
echo "  newgrp docker    # 刷新用户组"
echo "  或重新登录系统"
echo ""
echo "验证安装:"
echo "  docker run hello-world"
echo "  docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi"
echo ""
