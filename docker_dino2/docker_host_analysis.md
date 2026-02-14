# Docker 容器与宿主机 PyTorch 环境分析

## 问题背景

用户在宿主机执行 `docker image ls` 看不到相关容器/镜像，但测试报告中提到 "通过 volumes 将宿主机的 PyTorch 挂载到容器"。本文详细解释这两者的差别。

---

## 一、核心概念澄清

### 1.1 Docker Image vs Container

| 概念 | 说明 | 查看命令 |
|------|------|----------|
| **Image (镜像)** | 只读模板，包含运行应用所需的所有内容 | `docker image ls` |
| **Container (容器)** | 镜像的运行实例，可读写 | `docker ps -a` |

> ⚠️ **常见误区**：用户说"看不到创建的容器"，但使用的是 `docker image ls`（查看镜像）。如果要查看运行中的容器，应该用 `docker ps` 或 `docker ps -a`。

---

## 二、两种运行方式的对比

### 方式一：常规 Docker 运行（自包含）

```dockerfile
# 常规 Dockerfile - 在镜像内安装所有依赖
FROM pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime

# 在镜像构建时安装 PyTorch（镜像体积大）
RUN pip install torch torchvision torchaudio
```

**特点：**
- ✅ 镜像自包含，可在任何机器运行
- ✅ 环境隔离，不受宿主机影响
- ❌ 镜像体积大（数 GB）
- ❌ 构建时间长
- ❌ 每次启动都要加载大镜像

**查看方式：**
```bash
# 能看到镜像
docker image ls | grep pytorch

# 能看到容器
docker ps -a | grep my_container
```

---

### 方式二：挂载宿主机 PyTorch（本项目采用）

```dockerfile
# Dockerfile - 轻量版，不安装 PyTorch
FROM ubuntu:22.04

# 只安装基础依赖，不安装 PyTorch
RUN pip install numpy pillow opencv-python

# 注：PyTorch 通过 volume 挂载从宿主机获取
```

```yaml
# docker-compose.yml - volumes 挂载
docker-compose.yml 关键配置：
volumes:
  # 挂载宿主机 Anaconda Python 库
  - /home/ubuntu2204/anaconda3/lib/python3.11/site-packages:/opt/conda/lib/python3.11/site-packages:ro
  # 挂载 CUDA 库
  - /usr/local/cuda:/usr/local/cuda:ro
```

**特点：**
- ✅ 镜像体积小（几百 MB 而非数 GB）
- ✅ 构建速度快
- ✅ 容器直接使用宿主机的 PyTorch 2.7.0 + CUDA 12.8
- ✅ 无需重复下载大文件
- ❌ 依赖宿主机环境，换机器需要重新配置路径
- ❌ 如果宿主机没有 PyTorch，容器也无法运行

**查看方式：**
```bash
# 镜像存在但很小（因为没装 PyTorch）
docker image ls | grep dinov2
# REPOSITORY   TAG       SIZE
# dinov2       latest    850MB  (而非 5GB+)

# 容器运行中但依赖宿主机
docker ps | grep dinov2
# CONTAINER ID   IMAGE          STATUS
dinov2_container   dinov2:latest   Up 2 hours

# 进入容器查看 PyTorch（实际使用的是宿主机的）
docker-compose exec dinov2 bash
python3 -c "import torch; print(torch.__file__)"
# 输出: /opt/conda/lib/python3.11/site-packages/torch/__init__.py
# （这是挂载的宿主机路径）
```

---

## 三、为什么用户可能看不到

### 情况 1：从未构建过镜像

如果用户从未执行过：
```bash
docker-compose build
# 或
docker-compose up -d
```

那么本地确实没有这个镜像：
```bash
docker image ls | grep dinov2
# 无输出（镜像不存在）
```

### 情况 2：镜像名不匹配

docker-compose.yml 中定义的镜像名：
```yaml
services:
  dinov2:
    image: dinov2:latest
```

用户可能用错误的关键词搜索：
```bash
# 错误 - 搜不到
docker image ls | grep docker_dino2

# 正确 - 能搜到
docker image ls | grep dinov2
```

### 情况 3：在宿主机直接运行（根本没用到 Docker）

查看 README.md 中的说明：
```markdown
**方式1: 直接在宿主机运行（推荐）**
```bash
python3 tests/test_dinov2_images.py
```

**方式2: 使用 Docker**
```bash
docker-compose up -d
```
```

**很多测试实际上是在宿主机直接运行的！** 用户如果在宿主机运行测试，根本不会创建 Docker 容器。

### 情况 4：容器已停止/删除

```bash
# 只查看运行中的容器（默认）
docker ps
# 可能为空

# 查看所有容器（包括停止的）
docker ps -a

# 查看已删除的容器历史（需要日志系统）
```

---

## 四、验证当前环境状态

### 检查 1：Docker 镜像是否存在

```bash
docker image ls
```

预期输出（如果有）：
```
REPOSITORY   TAG       IMAGE ID       CREATED        SIZE
dinov2       latest    abc123def456   2 days ago     850MB
```

### 检查 2：Docker 容器状态

```bash
# 查看运行中的容器
docker ps

# 查看所有容器（包括停止的）
docker ps -a
```

### 检查 3：宿主机 PyTorch 环境

```bash
python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.version.cuda}'); print(f'路径: {torch.__file__}')"
```

预期输出：
```
PyTorch: 2.7.0+cu128
CUDA: 12.8
路径: /home/ubuntu2204/anaconda3/lib/python3.11/site-packages/torch/__init__.py
```

### 检查 4：挂载路径是否存在

```bash
ls -la /home/ubuntu2204/anaconda3/lib/python3.11/site-packages/ | grep torch
ls -la /usr/local/cuda/
```

---

## 五、关键差异总结

| 特性 | 常规 Docker | 本项目（挂载宿主机） |
|------|-------------|----------------------|
| **镜像大小** | 5GB+ | ~850MB |
| **构建时间** | 10-30 分钟 | 2-5 分钟 |
| **PyTorch 来源** | 镜像内部安装 | 宿主机挂载 |
| **可移植性** | 高（任何机器） | 低（需要相同宿主机配置） |
| **启动速度** | 慢 | 快 |
| **磁盘占用** | 大（每个镜像独立） | 小（共享宿主机环境） |
| **版本冲突风险** | 低（完全隔离） | 中（依赖宿主机） |

---

## 六、实际运行流程对比

### 流程 A：宿主机直接运行（推荐）

```
┌─────────────────────────────────────────┐
│           宿主机 (Ubuntu 22.04)          │
│  ┌───────────────────────────────────┐  │
│  │   Python 3.11 (Anaconda3)         │  │
│  │   ├─ PyTorch 2.7.0 (已安装)       │  │
│  │   ├─ CUDA 12.8 (已安装)           │  │
│  │   └─ DINOv2 代码                  │  │
│  │                                   │  │
│  │   $ python3 tests/test_dinov2.py  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
           ↑
       用户执行命令
```

**结果**：`docker image ls` 看不到任何东西（因为根本没用到 Docker）

---

### 流程 B：Docker 容器运行

```
┌─────────────────────────────────────────────────────────────────┐
│                    宿主机 (Ubuntu 22.04)                         │
│  ┌─────────────────────┐    ┌────────────────────────────────┐  │
│  │  Anaconda3          │    │     Docker 容器 (dinov2)       │  │
│  │  ├─ PyTorch 2.7.0   │◄───┼── /opt/conda/... (volume 挂载) │  │
│  │  ├─ CUDA 12.8       │◄───┼── /usr/local/cuda (volume 挂载)│  │
│  │  └─ 其他 Python 包  │◄───┤                                │  │
│  └─────────────────────┘    │  $ python3 tests/test_dinov2.py│  │
│                             └────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**volumes 挂载的本质**：
- 把宿主机的 `/home/ubuntu2204/anaconda3/lib/python3.11/site-packages` 
- 映射到容器的 `/opt/conda/lib/python3.11/site-packages`
- 容器内的 Python import 时，实际读取的是宿主机的 PyTorch

**结果**：
```bash
docker image ls
# 能看到 dinov2 镜像（但很小，因为 PyTorch 不在镜像里）

docker ps
# 能看到运行的 dinov2_container
```

---

## 七、常见疑问解答

### Q1: 为什么镜像这么小？

**A**: 因为 Dockerfile 里没有 `pip install torch`。PyTorch 是通过 `-v` 挂载从宿主机"借用"的，不是镜像的一部分。

### Q2: 这算是"真正的 Docker"吗？

**A**: 是的，但属于**特殊用途配置**：
- 适合：开发环境、单机部署、节省磁盘空间
- 不适合：生产部署、多机分发、CI/CD

### Q3: 如果把容器移到另一台机器？

**A**: 会失败！因为新机器没有 `/home/ubuntu2204/anaconda3/...` 这个路径。需要在新的 docker-compose.yml 中修改 volumes 路径。

### Q4: 宿主机和容器的 Python 版本必须一致吗？

**A**: 是的！这是关键约束：
- 宿主机：Python 3.11
- 容器：Python 3.11（Dockerfile 中明确安装的）
- 如果宿主机是 3.10，挂载后可能会出错

---

## 八、如何确认自己处于哪种模式

### 测试方法 1：检查进程

```bash
# 查看是否有 Docker 进程
ps aux | grep docker

# 查看 Python 进程路径
ps aux | grep python3
# 如果显示 /usr/bin/python3，可能是宿主机运行
# 如果显示 /opt/conda/...，可能是容器内运行
```

### 测试方法 2：检查文件系统

```bash
# 检查是否在容器内
ls -la /.dockerenv 2>/dev/null && echo "在容器内" || echo "在宿主机"

# 检查 hostname
cat /etc/hostname
# 宿主机通常显示实际主机名
# 容器通常显示容器 ID（如 a1b2c3d4e5f6）
```

### 测试方法 3：检查 PyTorch 路径

```bash
python3 -c "import torch; print(torch.__file__)"
# 宿主机: /home/ubuntu2204/anaconda3/lib/python3.11/site-packages/torch/__init__.py
# 容器:   /opt/conda/lib/python3.11/site-packages/torch/__init__.py（挂载点）
```

---

## 九、总结

| 用户可能的情况 | 解释 |
|--------------|------|
| `docker image ls` 为空 | 从未构建过镜像，或镜像名不匹配 |
| `docker ps` 为空 | 容器未运行，或在宿主机直接运行 |
| 测试能运行但看不到容器 | **很可能是在宿主机直接运行的**（推荐方式） |
| 镜像存在但很小 | 这是正常的，因为 PyTorch 是挂载的不是安装的 |

**核心要点**：
1. 本项目支持两种运行方式，**宿主机直接运行是推荐方式**
2. 如果使用 Docker，镜像是轻量级的（通过 volumes 挂载宿主机 PyTorch）
3. `docker image ls` 查看镜像，`docker ps` 查看容器，不要混淆
4. 很多测试报告的结果来自**宿主机直接运行**，而非 Docker 容器内运行
