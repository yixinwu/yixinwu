# Qwen3-30B-A3B-Q4 Docker GPU 部署 - 完整设置指南

## 系统环境

- GPU: NVIDIA GeForce RTX 3090 Ti (24GB)
- 驱动: 580.126.09 ✓
- Docker: 29.2.1 ✓

## 需要完成的步骤

### 步骤 1: 配置 Docker 国内镜像源

由于网络原因，需要配置国内镜像源：

```bash
sudo mkdir -p /etc/docker

sudo tee /etc/docker/daemon.json > /dev/null << 'EOF'
{
  "registry-mirrors": [
    "https://dockerproxy.com",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com",
    "https://docker.mirrors.ustc.edu.cn"
  ],
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2"
}
EOF

sudo systemctl restart docker
```

### 步骤 2: 安装 NVIDIA Container Toolkit

这是 GPU 支持必需的：

```bash
# 添加 NVIDIA 软件源
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# 安装
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# 配置 Docker
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# 测试
sudo docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

### 步骤 3: 下载模型（国内镜像源）

```bash
# 使用已配置的脚本（已使用魔搭社区镜像）
./download-model.sh
```

或者手动下载：

```bash
# 安装 modelscope 工具
pip install modelscope

# 从魔搭社区下载
modelscope download --model Qwen/Qwen3-30B-A3B-GGUF qwen3-30b-a3b-q4_k_m.gguf --local_dir ./models
```

或者直接浏览器下载：
- 访问: https://www.modelscope.cn/models/Qwen/Qwen3-30B-A3B-GGUF
- 下载: `qwen3-30b-a3b-q4_k_m.gguf`
- 放置到: `./models/` 目录

### 步骤 4: 启动服务

```bash
# 使用 Makefile
make up

# 或直接使用 docker-compose
docker-compose up -d
```

### 步骤 5: 验证部署

```bash
# 检查容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 测试 API
make test

# 检查 GPU 使用情况
watch -n 1 nvidia-smi
```

## 一键执行脚本

如果你希望一键完成所有设置，可以运行：

```bash
# 给脚本执行权限
chmod +x install-docker.sh

# 执行安装（需要 sudo 密码）
./install-docker.sh
```

**注意**: 脚本需要 sudo 权限，运行时会提示输入密码。

## 手动执行命令汇总

如果脚本执行有问题，可以逐条手动执行：

```bash
# 1. 配置 Docker 镜像源
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://dockerproxy.com",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
EOF
sudo systemctl restart docker

# 2. 安装 nvidia-container-toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# 3. 下载模型
./download-model.sh

# 4. 启动服务
docker-compose up -d
```

## 模型信息

| 属性 | 值 |
|------|-----|
| 模型 | Qwen3-30B-A3B |
| 类型 | MoE (Mixture of Experts) |
| 总参数 | 30.5B |
| 激活参数 | 3.3B |
| 量化 | Q4_K_M (4-bit) |
| 文件大小 | ~18 GB |
| 显存需求 | ~12-16 GB |
| 上下文 | 32K (可扩展至 128K) |

## 下载源对比

| 源 | 地址 | 速度 | 推荐 |
|-----|------|------|------|
| 魔搭社区 | modelscope.cn | ⭐⭐⭐⭐⭐ | ✅ 首选 |
| HF-Mirror | hf-mirror.com | ⭐⭐⭐⭐ | 备选 |
| HuggingFace | huggingface.co | ⭐⭐ | 不推荐(国内) |

## 故障排除

### Docker 镜像拉取超时

```bash
# 检查镜像源配置
cat /etc/docker/daemon.json

# 重启 Docker
sudo systemctl restart docker

# 测试拉取
docker pull hello-world
```

### GPU 无法使用

```bash
# 检查 nvidia-docker
sudo docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi

# 如果失败，重新安装 toolkit
sudo apt-get reinstall nvidia-container-toolkit
sudo systemctl restart docker
```

### 模型下载失败

```bash
# 使用 aria2 多线程下载
sudo apt-get install -y aria2

aria2c -c -x 16 -s 16 \
  "https://www.modelscope.cn/models/Qwen/Qwen3-30B-A3B-GGUF/resolve/master/qwen3-30b-a3b-q4_k_m.gguf" \
  -o models/Qwen3-30B-A3B-Q4_K_M.gguf
```
