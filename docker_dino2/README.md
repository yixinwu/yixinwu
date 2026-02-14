# DINOv2 Docker 配置

基于宿主机 PyTorch 环境的 DINOv2 Docker 配置。

## 🎯 特点

- **轻量快速**：利用宿主机 PyTorch + CUDA，镜像体积小
- **环境共享**：容器直接使用宿主机的 PyTorch 2.7.0 + CUDA 12.8
- **即开即用**：无需重复下载大文件

## 📋 前置要求

- Docker 20.10+
- NVIDIA Docker Runtime
- 宿主机已安装 Anaconda3 + PyTorch 2.7.0 + CUDA 12.8
- Python 3.11

## 🚀 快速开始

### 1. 生成测试图片（10张几何形状）

```bash
cd /home/ubuntu2204/kimi_prj/docker_dino2
python3 data/test_images/generate_images.py
```

### 2. 运行 DINOv2 识别测试

**方式1: 直接在宿主机运行（推荐）**
```bash
python3 tests/test_dinov2_images.py
```

**方式2: 使用 Docker**
```bash
# 构建并启动容器
docker-compose up -d

# 进入容器运行测试
docker-compose exec dinov2 bash
python3 tests/test_dinov2_images.py
```

### 3. 查看测试结果

测试完成后会输出：
- 每张图片的特征向量（384维）
- 图片间的相似度矩阵
- 相似图片分组
- 最不相似的图片对
- 性能统计（处理速度等）

结果文件保存在 `output/` 目录：
```bash
ls output/
# features.npy  similarity_matrix.npy  results.json
```

## 🧪 测试

```bash
# 进入容器
docker-compose exec dinov2 bash

# 运行测试
cd /workspace/tests
python3 test_dinov2.py
```

## 📁 目录结构

```
.
├── Dockerfile              # 轻量级镜像定义
├── docker-compose.yml      # 容器配置
├── README.md              # 项目文档
├── data/
│   └── test_images/       # 10张测试图片
│       ├── generate_images.py    # 图片生成脚本
│       ├── categories.json       # 类别映射
│       ├── 01_red_square.jpg
│       ├── 02_green_circle.jpg
│       ├── ...
│       └── 10_teal_cross.jpg
├── tests/
│   ├── test_dinov2.py    # 基础测试套件
│   ├── test_dinov2_images.py  # 10张图片识别测试
│   └── quick_test.sh     # 快速验证脚本
├── examples/
│   └── extract_features.py  # 特征提取示例
└── output/                # 测试结果输出
    ├── features.npy
    ├── similarity_matrix.npy
    └── results.json
```

## 🔧 工作原理

通过 `volumes` 将宿主机的 PyTorch 挂载到容器：

```yaml
volumes:
  - /usr/local/lib/python3.10/dist-packages:/usr/local/lib/python3.10/dist-packages:ro
  - /usr/local/cuda:/usr/local/cuda:ro
```

这样容器可以直接使用宿主机的：
- PyTorch 2.7.0
- TorchVision 0.22.0
- CUDA 12.8

## 🧪 测试示例：10张图片识别

本项目包含完整的测试流程，使用10张几何形状图片验证DINOv2的识别能力。

### 测试图片示例

生成的10张测试图片（400x400像素）：

| 编号 | 文件名 | 类别 |
|------|--------|------|
| 01 | red_square | 红色方块 |
| 02 | green_circle | 绿色圆形 |
| 03 | blue_triangle | 蓝色三角形 |
| 04 | yellow_star | 黄色星形 |
| 05 | purple_diamond | 紫色菱形 |
| 06 | orange_ellipse | 橙色椭圆 |
| 07 | cyan_rectangle | 青色矩形 |
| 08 | magenta_pentagon | 品红色五边形 |
| 09 | lime_hexagon | 酸橙六边形 |
| 10 | teal_cross | 青色十字 |

### 运行测试

```bash
# 方式1: 在宿主机直接运行
cd /home/ubuntu2204/kimi_prj/docker_dino2
python3 tests/test_dinov2_images.py

# 方式2: 在Docker容器内运行
docker-compose up -d
docker-compose exec dinov2 bash
cd /workspace && python3 tests/test_dinov2_images.py
```

### 测试结果示例

```
============================================================
DINOv2 图像识别测试
============================================================

✓ 模型加载成功
✓ 模型类型: DINOv2 ViT-S/14
✓ 参数量: 22,056,576
✓ 特征维度: 384

正在提取特征...
  1. 01_red_square.jpg         -> 红色方块
  2. 02_green_circle.jpg       -> 绿色圆形
  ...
  10. 10_teal_cross.jpg        -> 青色十字

✓ 特征提取完成，耗时: 0.23秒

【相似度分析】

查询图片                 类别              最相似              相似度
--------------------------------------------------------------------------------
01_red_square            红色方块          07_cyan_rectangle   0.9059
02_green_circle          绿色圆形          06_orange_ellipse   0.9164
03_blue_triangle         蓝色三角形        08_magenta_pentagon 0.8252
04_yellow_star           黄色星形          08_magenta_pentagon 0.7890
05_purple_diamond        紫色菱形          08_magenta_pentagon 0.9439
...

【相似图片分组】(相似度 > 0.8)
  分组 1: 红色方块, 紫色菱形, 青色矩形, 品红色五边形
  分组 2: 绿色圆形, 橙色椭圆
  分组 3: 蓝色三角形, 酸橙六边形
```

### 输出文件

测试完成后会生成以下文件：
- `output/features.npy` - 10张图片的特征向量 (10x384)
- `output/similarity_matrix.npy` - 相似度矩阵 (10x10)
- `output/results.json` - 完整的测试结果JSON

## 📝 使用示例

```python
# 在容器内运行
import torch
import torchvision.transforms as transforms
from PIL import Image

# 加载 DINOv2 模型
model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vits14')
model = model.cuda()
model.eval()

# 图像预处理
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                        std=[0.229, 0.224, 0.225])
])

# 提取特征
image = Image.open('your_image.jpg')
input_tensor = transform(image).unsqueeze(0).cuda()

with torch.no_grad():
    features = model(input_tensor)

print(f"特征维度: {features.shape}")
```

## ⚠️ 注意事项

1. **Python 版本**：确保容器和宿主机 Python 版本一致（3.10）
2. **CUDA 版本**：宿主机 CUDA 版本需要与 PyTorch 兼容
3. **权限问题**：如果遇到权限错误，检查挂载目录权限

## 🔧 故障排除

### 问题：找不到 PyTorch

检查宿主机 PyTorch 路径：
```bash
python3 -c "import torch; print(torch.__file__)"
```

然后更新 docker-compose.yml 中的挂载路径。

### 问题：CUDA 不可用

确保 NVIDIA Docker Runtime 已安装：
```bash
# 检查
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

## 📄 许可证

MIT License
