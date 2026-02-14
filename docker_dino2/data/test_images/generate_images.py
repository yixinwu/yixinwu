#!/usr/bin/env python3
"""
生成测试图片用于 DINOv2 测试
生成10张不同类别的测试图片
"""

import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# 创建测试图片目录
os.makedirs("/home/ubuntu2204/kimi_prj/docker_dino2/data/test_images", exist_ok=True)

# 定义10个测试类别和对应的颜色
test_categories = [
    ("red_square", (255, 0, 0), "红色方块"),
    ("green_circle", (0, 255, 0), "绿色圆形"),
    ("blue_triangle", (0, 0, 255), "蓝色三角形"),
    ("yellow_star", (255, 255, 0), "黄色星形"),
    ("purple_diamond", (128, 0, 128), "紫色菱形"),
    ("orange_ellipse", (255, 165, 0), "橙色椭圆"),
    ("cyan_rectangle", (0, 255, 255), "青色矩形"),
    ("magenta_pentagon", (255, 0, 255), "品红色五边形"),
    ("lime_hexagon", (50, 205, 50), "酸橙六边形"),
    ("teal_cross", (0, 128, 128), "青色十字"),
]


def create_square(draw, color, size=400):
    """创建方块"""
    margin = 50
    draw.rectangle([margin, margin, size - margin, size - margin], fill=color)


def create_circle(draw, color, size=400):
    """创建圆形"""
    margin = 50
    draw.ellipse([margin, margin, size - margin, size - margin], fill=color)


def create_triangle(draw, color, size=400):
    """创建三角形"""
    margin = 50
    points = [
        (size // 2, margin),
        (margin, size - margin),
        (size - margin, size - margin),
    ]
    draw.polygon(points, fill=color)


def create_star(draw, color, size=400):
    """创建星形"""
    cx, cy = size // 2, size // 2
    outer_r = 150
    inner_r = 60
    points = []
    for i in range(10):
        angle = np.pi / 2 + i * np.pi / 5
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + r * np.cos(angle)
        y = cy - r * np.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=color)


def create_diamond(draw, color, size=400):
    """创建菱形"""
    cx, cy = size // 2, size // 2
    points = [(cx, 50), (350, cy), (cx, 350), (50, cy)]
    draw.polygon(points, fill=color)


def create_ellipse(draw, color, size=400):
    """创建椭圆"""
    draw.ellipse([50, 100, 350, 300], fill=color)


def create_rectangle(draw, color, size=400):
    """创建矩形"""
    draw.rectangle([50, 100, 350, 300], fill=color)


def create_pentagon(draw, color, size=400):
    """创建五边形"""
    cx, cy = size // 2, size // 2
    r = 150
    points = []
    for i in range(5):
        angle = np.pi / 2 + i * 2 * np.pi / 5
        x = cx + r * np.cos(angle)
        y = cy - r * np.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=color)


def create_hexagon(draw, color, size=400):
    """创建六边形"""
    cx, cy = size // 2, size // 2
    r = 150
    points = []
    for i in range(6):
        angle = i * np.pi / 3
        x = cx + r * np.cos(angle)
        y = cy + r * np.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=color)


def create_cross(draw, color, size=400):
    """创建十字"""
    # 横条
    draw.rectangle([50, 170, 350, 230], fill=color)
    # 竖条
    draw.rectangle([170, 50, 230, 350], fill=color)


# 形状函数映射
shape_functions = {
    "square": create_square,
    "circle": create_circle,
    "triangle": create_triangle,
    "star": create_star,
    "diamond": create_diamond,
    "ellipse": create_ellipse,
    "rectangle": create_rectangle,
    "pentagon": create_pentagon,
    "hexagon": create_hexagon,
    "cross": create_cross,
}

# 生成测试图片
print("正在生成10张测试图片...")
image_paths = []

for i, (name, color, chinese_name) in enumerate(test_categories):
    # 创建白色背景图像
    img = Image.new("RGB", (400, 400), color="white")
    draw = ImageDraw.Draw(img)

    # 获取形状类型
    shape_type = name.split("_")[1]

    # 绘制形状
    if shape_type in shape_functions:
        shape_functions[shape_type](draw, color)

    # 保存图片
    filename = f"{i + 1:02d}_{name}.jpg"
    filepath = f"/home/ubuntu2204/kimi_prj/docker_dino2/data/test_images/{filename}"
    img.save(filepath, "JPEG", quality=95)
    image_paths.append(filepath)

    print(f"  ✓ 生成: {filename} - {chinese_name}")

print(f"\n完成！共生成 {len(image_paths)} 张测试图片")
print(f"保存位置: /home/ubuntu2204/kimi_prj/docker_dino2/data/test_images/")

# 创建类别映射文件
import json

category_map = {
    f"{i + 1:02d}_{name}": chinese_name
    for i, (name, _, chinese_name) in enumerate(test_categories)
}
with open(
    "/home/ubuntu2204/kimi_prj/docker_dino2/data/test_images/categories.json",
    "w",
    encoding="utf-8",
) as f:
    json.dump(category_map, f, ensure_ascii=False, indent=2)

print("类别映射已保存到 categories.json")
