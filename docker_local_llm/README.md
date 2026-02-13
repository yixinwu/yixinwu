# Qwen3-30B-A3B-Q4 Docker GPU 部署

使用 llama.cpp 在 Docker 中部署 Qwen3-30B-A3B-Q4 量化模型，充分利用 NVIDIA GPU 加速推理。

## 模型信息

| 属性 | 值 |
|------|-----|
| 模型 | Qwen3-30B-A3B |
| 类型 | MoE (Mixture of Experts) |
| 总参数 | 30.5B |
| 激活参数 | 3.3B |
| 量化 | Q4_K_M (4-bit) |
| 文件大小 | ~18 GB |

## 系统要求

- **GPU**: NVIDIA GPU，显存 ≥ 12GB (推荐 16GB+)
- **Docker**: 已安装并配置 NVIDIA Container Toolkit
- **内存**: ≥ 32GB RAM
- **存储**: ≥ 25GB 可用空间
- **网络**: 访问 modelscope.cn (国内镜像源)

## 快速开始

### 1. 环境检查

```bash
# 检查 GPU
nvidia-smi

# 检查 Docker
./check-env.sh
```

### 2. 配置 Docker 国内镜像源 (推荐)

```bash
sudo mkdir -p /etc/docker

sudo tee /etc/docker/daemon.json > /dev/null << 'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com",
    "https://dockerproxy.com"
  ],
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": { "max-size": "100m" },
  "storage-driver": "overlay2"
}
EOF

sudo systemctl restart docker
```

### 3. 下载模型 (国内镜像源)

**方式一：使用 modelscope 命令行 (推荐)**

```bash
# 安装 modelscope
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple modelscope

# 下载模型 (约 18GB，需要时间)
modelscope download --model Qwen/Qwen3-30B-A3B-GGUF Qwen3-30B-A3B-Q4_K_M.gguf --local_dir ./models
```

**方式二：使用提供的脚本**

```bash
./download-model.sh
```

**方式三：手动下载**

- 访问: https://www.modelscope.cn/models/Qwen/Qwen3-30B-A3B-GGUF
- 下载: `Qwen3-30B-A3B-Q4_K_M.gguf` (注意大小写)
- 放置到: `./models/` 目录

### 4. 拉取 Docker 镜像

```bash
# 尝试使用镜像站拉取
./pull-image.sh

# 如果失败，使用 Docker Hub 镜像
# 或者使用本地构建 (需要本地安装 CUDA)
```

### 5. 启动服务

```bash
docker-compose up -d
```

### 6. 检查状态

```bash
# 查看日志
docker-compose logs -f

# 检查 GPU 使用情况
watch -n 1 nvidia-smi
```

## API 使用

服务启动后，可以通过以下方式访问：

### OpenAI 兼容 API

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-30b-a3b-q4",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "你好，请介绍一下自己"}
    ],
    "temperature": 0.7,
    "max_tokens": 2048
  }'
```

### 流式响应

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-30b-a3b-q4",
    "messages": [{"role": "user", "content": "你好"}],
    "stream": true
  }'
```

### Python 示例

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="qwen3-30b-a3b-q4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你好，请介绍一下自己"}
    ],
    temperature=0.7,
    max_tokens=2048
)

print(response.choices[0].message.content)
```

## 配置调整

编辑 `docker-compose.yml` 可调整以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--n-gpu-layers` | GPU 加载层数 | 999 (全部) |
| `--ctx-size` | 上下文长度 | 32768 |
| `--threads` | CPU 线程数 | 8 |
| `--batch-size` | 批处理大小 | 512 |
| `--flash-attn` | Flash Attention | 启用 |

### 显存不足时的调整

如果 GPU 显存不足，可减少 GPU 层数：

```yaml
# 在 entrypoint.sh 中修改参数
--n-gpu-layers 25    # 减少 GPU 层数
--ctx-size 8192      # 减少上下文
```

## 常用命令

```bash
# 启动
docker-compose up -d

# 停止
docker-compose down

# 查看日志
docker-compose logs -f

# 重启
docker-compose restart

# 进入容器
docker-compose exec llm-qwen3 bash

# 完全删除（包括容器）
docker-compose down -v
```

## 故障排除

### 1. Docker 镜像拉取失败

```bash
# 使用镜像站
./pull-image.sh

# 或者手动下载后构建
# 1. 从 https://github.com/ggml-org/llama.cpp/releases 下载 llama-server-linux-cuda-cu12.2-x64
# 2. 重命名为 llama-server 并放置到项目目录
# 3. ./pull-image.sh 会自动使用本地文件构建
```

### 2. 模型下载失败

```bash
# 使用 aria2 多线程下载
sudo apt-get install -y aria2

aria2c -c -x 16 -s 16 \
  "https://www.modelscope.cn/models/Qwen/Qwen3-30B-A3B-GGUF/resolve/master/Qwen3-30B-A3B-Q4_K_M.gguf" \
  -o models/Qwen3-30B-A3B-Q4_K_M.gguf
```

### 3. GPU 未被使用

```bash
# 检查 nvidia-docker
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi

# 检查日志中的 GPU 信息
docker-compose logs | grep -i gpu
```

### 4. 内存不足 (OOM)

- 减少 `--ctx-size` 到 8192 或 4096
- 减少 `--n-gpu-layers` 让部分层在 CPU 运行

### 5. 端口冲突

编辑 `docker-compose.yml` 修改端口映射：

```yaml
ports:
  - "8081:8080"  # 改为 8081 端口
```

## 性能参考

在 NVIDIA RTX 3090 Ti (24GB) 上的性能：

| 量化 | GPU 层数 | 上下文 | 预填充速度 | 生成速度 |
|------|----------|--------|------------|----------|
| Q4_K_M | 999 | 32K | ~500 t/s | ~35 t/s |

## 文件说明

```
.
├── docker-compose.yml    # Docker 配置
├── entrypoint.sh         # 容器启动脚本
├── download-model.sh     # 模型下载脚本
├── pull-image.sh         # Docker 镜像拉取脚本
├── models/               # 模型文件存放目录
│   └── Qwen3-30B-A3B-Q4_K_M.gguf
└── README.md            # 本文件
```

## 参考链接

- [魔搭社区 - Qwen3-30B-A3B-GGUF](https://www.modelscope.cn/models/Qwen/Qwen3-30B-A3B-GGUF)
- [llama.cpp](https://github.com/ggml-org/llama.cpp)
- [Qwen3 官方文档](https://qwen.readthedocs.io/)
