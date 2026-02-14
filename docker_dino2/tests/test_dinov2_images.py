#!/usr/bin/env python3
"""
DINOv2 图像识别测试脚本
使用10张测试图片进行特征提取和相似度分析
"""

import os
import sys
import time
import json
import torch
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
from pathlib import Path

# 设置设备
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"使用设备: {device}")
if device == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# 图像预处理
transform = transforms.Compose(
    [
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


def load_model():
    """加载 DINOv2 模型"""
    print("\n" + "=" * 60)
    print("加载 DINOv2 模型...")
    print("=" * 60)

    model = torch.hub.load("facebookresearch/dinov2", "dinov2_vits14")
    model = model.to(device)
    model.eval()

    print(f"✓ 模型加载成功")
    print(f"✓ 模型类型: DINOv2 ViT-S/14")
    print(f"✓ 参数量: {sum(p.numel() for p in model.parameters()):,}")
    print(f"✓ 特征维度: 384")

    return model


def extract_features(model, image_path):
    """提取单张图片的特征"""
    image = Image.open(image_path).convert("RGB")
    input_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        features = model(input_tensor)

    return features.cpu().numpy().flatten()


def compute_similarity(features1, features2):
    """计算余弦相似度"""
    norm1 = np.linalg.norm(features1)
    norm2 = np.linalg.norm(features2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return np.dot(features1, features2) / (norm1 * norm2)


def find_most_similar(query_features, all_features, all_names, top_k=3):
    """找出最相似的图片"""
    similarities = []
    for i, features in enumerate(all_features):
        sim = compute_similarity(query_features, features)
        similarities.append((all_names[i], sim, i))

    # 排序并返回前K个
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]


def test_all_images(model, test_dir):
    """测试所有图片"""
    print("\n" + "=" * 60)
    print("开始测试10张图片")
    print("=" * 60)

    # 加载类别映射
    with open(os.path.join(test_dir, "categories.json"), "r", encoding="utf-8") as f:
        categories = json.load(f)

    # 获取所有测试图片
    image_files = sorted([f for f in os.listdir(test_dir) if f.endswith(".jpg")])

    print(f"\n找到 {len(image_files)} 张测试图片:\n")

    # 存储所有特征和名称
    all_features = []
    all_names = []
    all_categories = []

    # 提取所有图片的特征
    print("正在提取特征...")
    start_time = time.time()

    for i, img_file in enumerate(image_files, 1):
        img_path = os.path.join(test_dir, img_file)
        base_name = img_file.replace(".jpg", "")
        category = categories.get(base_name, base_name)

        features = extract_features(model, img_path)
        all_features.append(features)
        all_names.append(base_name)
        all_categories.append(category)

        print(f"  {i}. {img_file:25s} -> {category}")

    elapsed = time.time() - start_time
    print(f"\n✓ 特征提取完成，耗时: {elapsed:.2f}秒")
    print(f"✓ 平均每张图片: {elapsed / len(image_files):.3f}秒")

    # 分析结果
    print("\n" + "=" * 60)
    print("识别结果分析")
    print("=" * 60)

    # 1. 显示特征统计
    print("\n【特征统计】")
    features_array = np.array(all_features)
    print(f"  特征矩阵形状: {features_array.shape}")
    print(f"  特征均值: {features_array.mean():.4f}")
    print(f"  特征标准差: {features_array.std():.4f}")
    print(f"  特征最小值: {features_array.min():.4f}")
    print(f"  特征最大值: {features_array.max():.4f}")

    # 2. 计算相似度矩阵
    print("\n【相似度分析】")
    similarity_matrix = np.zeros((len(image_files), len(image_files)))

    for i in range(len(image_files)):
        for j in range(len(image_files)):
            similarity_matrix[i][j] = compute_similarity(
                all_features[i], all_features[j]
            )

    # 3. 为每张图片找出最相似的图片
    print("\n【每张图片的最相似匹配】")
    print("-" * 80)
    print(f"{'查询图片':<20} {'类别':<15} {'最相似':<20} {'相似度':>10}")
    print("-" * 80)

    for i in range(len(image_files)):
        # 排除自身，找最相似的
        similarities = []
        for j in range(len(image_files)):
            if i != j:
                similarities.append((j, similarity_matrix[i][j]))

        similarities.sort(key=lambda x: x[1], reverse=True)
        most_similar_idx, max_sim = similarities[0]

        query_name = all_names[i]
        query_cat = all_categories[i]
        similar_name = all_names[most_similar_idx]
        similar_cat = all_categories[most_similar_idx]

        print(f"{query_name:<20} {query_cat:<15} {similar_name:<20} {max_sim:>10.4f}")

    # 4. 相似度矩阵可视化
    print("\n【相似度矩阵】")
    print("-" * 100)

    # 打印表头
    header = "查询图片           |"
    for i in range(len(image_files)):
        header += f" {i + 1:>6}"
    print(header)
    print("-" * 100)

    # 打印每一行
    for i in range(len(image_files)):
        row = f"{all_names[i]:<18} |"
        for j in range(len(image_files)):
            if i == j:
                row += f" {'---':>6}"
            else:
                row += f" {similarity_matrix[i][j]:>6.3f}"
        print(row)
    print("-" * 100)
    print("注: 数值越高表示越相似 (范围: -1 到 1)")

    # 5. 聚类分析 - 将相似的图片分组
    print("\n【相似图片分组】(相似度 > 0.8)")
    threshold = 0.8
    groups = []
    used = set()

    for i in range(len(image_files)):
        if i in used:
            continue

        group = [i]
        used.add(i)

        for j in range(i + 1, len(image_files)):
            if j not in used and similarity_matrix[i][j] > threshold:
                group.append(j)
                used.add(j)

        if len(group) > 1:
            groups.append(group)

    if groups:
        for idx, group in enumerate(groups, 1):
            print(f"\n  分组 {idx}:")
            for i in group:
                print(f"    - {all_names[i]} ({all_categories[i]})")
    else:
        print("\n  没有相似度超过0.8的图片组")

    # 6. 最不相似的图片对
    print("\n【最不相似的图片对】(差异最大)")
    min_sim = float("inf")
    min_pair = (0, 0)

    for i in range(len(image_files)):
        for j in range(i + 1, len(image_files)):
            if similarity_matrix[i][j] < min_sim:
                min_sim = similarity_matrix[i][j]
                min_pair = (i, j)

    i, j = min_pair
    print(f"  {all_names[i]} ({all_categories[i]})")
    print(f"  vs")
    print(f"  {all_names[j]} ({all_categories[j]})")
    print(f"  相似度: {min_sim:.4f}")

    # 7. 性能统计
    print("\n【性能统计】")
    print(f"  总处理时间: {elapsed:.2f}秒")
    print(f"  图片数量: {len(image_files)}张")
    print(f"  平均时间: {elapsed / len(image_files) * 1000:.2f}ms/张")
    print(f"  吞吐量: {len(image_files) / elapsed:.2f}张/秒")

    return all_features, all_names, all_categories, similarity_matrix


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("DINOv2 图像识别测试")
    print("=" * 60)
    print("\n本测试将:")
    print("1. 加载 DINOv2 预训练模型")
    print("2. 处理10张测试图片")
    print("3. 提取每张图片的特征向量")
    print("4. 分析图片之间的相似度")
    print("5. 输出详细的识别结果")

    # 加载模型
    model = load_model()

    # 测试图片目录
    test_dir = "/home/ubuntu2204/kimi_prj/docker_dino2/data/test_images"

    if not os.path.exists(test_dir):
        print(f"\n错误: 测试图片目录不存在: {test_dir}")
        print("请先运行: python3 data/test_images/generate_images.py")
        sys.exit(1)

    # 运行测试
    features, names, categories, sim_matrix = test_all_images(model, test_dir)

    # 保存结果
    output_dir = "/home/ubuntu2204/kimi_prj/docker_dino2/output"
    os.makedirs(output_dir, exist_ok=True)

    # 保存特征
    np.save(os.path.join(output_dir, "features.npy"), np.array(features))

    # 保存相似度矩阵
    np.save(os.path.join(output_dir, "similarity_matrix.npy"), sim_matrix)

    # 保存结果摘要
    results = {
        "num_images": len(names),
        "image_names": names,
        "categories": categories,
        "feature_dimension": 384,
        "similarity_matrix": sim_matrix.tolist(),
    }

    with open(os.path.join(output_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("测试结果已保存")
    print("=" * 60)
    print(f"  特征文件: output/features.npy")
    print(f"  相似度矩阵: output/similarity_matrix.npy")
    print(f"  结果摘要: output/results.json")

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
