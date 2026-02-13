# Qwen3-30B-A3B-Q4 部署状态

## 当前状态

| 项目 | 状态 | 进度 |
|------|------|------|
| Docker 安装 | ✅ 完成 | 29.2.1 |
| NVIDIA 驱动 | ✅ 完成 | 580.126.09 |
| NVIDIA Container Toolkit | ✅ 完成 | 已安装 |
| GPU 检测 | ✅ 完成 | RTX 3090 Ti 24GB |
| 模型下载 | ⏳ 进行中 | ~2.5GB / 18GB |
| Docker 镜像 | ⏳ 等待中 | 依赖模型下载完成 |
| 服务启动 | ⏳ 等待中 | 依赖上述完成 |

## 已完成的配置

### 1. Docker 镜像源配置

已配置以下国内镜像源:
- https://docker.mirrors.ustc.edu.cn
- https://hub-mirror.c.163.com
- https://mirror.baidubce.com
- https://dockerproxy.com

### 2. 模型下载源配置

使用魔搭社区 (ModelScope) 作为国内镜像源:
- 主地址: https://www.modelscope.cn/models/Qwen/Qwen3-30B-A3B-GGUF
- 文件名: Qwen3-30B-A3B-Q4_K_M.gguf (注意大小写)

### 3. 脚本更新

所有脚本已更新使用国内镜像源:
- `download-model.sh` - 使用魔搭社区下载
- `entrypoint.sh` - 使用国内镜像下载
- `pull-image.sh` - 使用镜像站拉取 Docker 镜像

## 监控下载进度

```bash
# 查看模型下载进度
ls -lh models/._____temp/

# 查看后台任务
ps aux | grep modelscope

# 查看下载日志
tail -f /tmp/model-download.log
```

## 下一步操作

当模型下载完成后，执行:

```bash
# 1. 等待模型下载完成 (约需 30-60 分钟)
# 完成后文件会自动移动到 models/Qwen3-30B-A3B-Q4_K_M.gguf

# 2. 拉取 Docker 镜像
./pull-image.sh

# 3. 启动服务
docker-compose up -d

# 4. 检查状态
docker-compose logs -f
```

## 常见问题

### Q: 模型下载太慢怎么办？

A: 可以使用 aria2 多线程下载:
```bash
sudo apt-get install -y aria2
aria2c -c -x 16 -s 16 \
  "https://www.modelscope.cn/models/Qwen/Qwen3-30B-A3B-GGUF/resolve/master/Qwen3-30B-A3B-Q4_K_M.gguf" \
  -o models/Qwen3-30B-A3B-Q4_K_M.gguf
```

### Q: Docker 镜像拉取失败怎么办？

A: 使用本地构建方案:
```bash
# 1. 手动下载 llama-server
wget https://github.com/ggml-org/llama.cpp/releases/download/b4600/llama-server-linux-cuda-cu12.2-x64 -O llama-server
chmod +x llama-server

# 2. 使用本地构建
./pull-image.sh
```

### Q: 如何确认服务正常运行？

```bash
# 测试 API
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen3", "messages": [{"role": "user", "content": "你好"}]}'

# 检查 GPU 使用
nvidia-smi
```

## 预计完成时间

- 模型下载: ~30-60 分钟 (取决于网速)
- Docker 镜像: ~5-10 分钟
- 服务启动: ~1-2 分钟

**总预计时间: 40-75 分钟**

## 资源监控

```bash
# 实时监控 GPU
watch -n 1 nvidia-smi

# 监控容器日志
docker-compose logs -f --tail=100

# 监控磁盘使用
df -h
```
