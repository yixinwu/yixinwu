#!/usr/bin/env python3
"""
DINOv2 真实照片识别测试
识别 data/test_photo 目录中的照片并分析
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
    print(f"✓ 特征维度: 384")

    return model


def extract_features(model, image_path):
    """提取单张图片的特征"""
    try:
        # 处理 webp 格式
        image = Image.open(image_path).convert("RGB")
        input_tensor = transform(image).unsqueeze(0).to(device)

        with torch.no_grad():
            features = model(input_tensor)

        return features.cpu().numpy().flatten(), image.size
    except Exception as e:
        print(f"✗ 处理 {os.path.basename(image_path)} 失败: {e}")
        return None, None


def compute_similarity(features1, features2):
    """计算余弦相似度"""
    norm1 = np.linalg.norm(features1)
    norm2 = np.linalg.norm(features2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return np.dot(features1, features2) / (norm1 * norm2)


def analyze_photo(model, image_path):
    """分析单张照片"""
    features, image_size = extract_features(model, image_path)
    if features is None:
        return None

    # 计算特征统计
    feature_stats = {
        "mean": float(np.mean(features)),
        "std": float(np.std(features)),
        "min": float(np.min(features)),
        "max": float(np.max(features)),
        "norm": float(np.linalg.norm(features)),
    }

    return {"features": features, "image_size": image_size, "stats": feature_stats}


def classify_by_similarity(all_results, all_names):
    """根据相似度对照片进行分类"""
    n = len(all_results)
    similarity_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            similarity_matrix[i][j] = compute_similarity(
                all_results[i]["features"], all_results[j]["features"]
            )

    # 为每张照片找到最相似的其他照片
    similarities_info = []
    for i in range(n):
        # 排除自身，找最相似的
        sims = []
        for j in range(n):
            if i != j:
                sims.append(
                    {
                        "index": j,
                        "name": all_names[j],
                        "similarity": float(similarity_matrix[i][j]),
                    }
                )

        sims.sort(key=lambda x: x["similarity"], reverse=True)
        similarities_info.append(sims)

    return similarity_matrix, similarities_info


def detect_photo_category(filename, features):
    """
    基于特征尝试推测照片类别
    注意：DINOv2 是特征提取模型，不是分类器
    这里仅基于启发式规则给出可能的类别提示
    """
    filename_lower = filename.lower()

    # 基于文件名的启发式
    categories = []
    if any(
        word in filename_lower for word in ["attraction", "landmark", "world", "travel"]
    ):
        categories.append("可能为: 地标/旅游景点")
    if any(word in filename_lower for word in ["nature", "animal", "bird", "wildlife"]):
        categories.append("可能为: 自然/动物")
    if any(word in filename_lower for word in ["people", "person", "portrait"]):
        categories.append("可能为: 人物/肖像")
    if any(word in filename_lower for word in ["city", "urban", "building"]):
        categories.append("可能为: 城市/建筑")

    if not categories:
        categories.append("类别未知 (需要更多上下文)")

    return categories


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("DINOv2 真实照片识别")
    print("=" * 60)

    # 照片目录
    photo_dir = "/home/ubuntu2204/kimi_prj/docker_dino2/data/test_photo"

    if not os.path.exists(photo_dir):
        print(f"\n错误: 照片目录不存在: {photo_dir}")
        sys.exit(1)

    # 获取所有照片文件
    photo_files = []
    for ext in ["*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp"]:
        photo_files.extend(Path(photo_dir).glob(ext))

    photo_files = sorted([str(f) for f in photo_files])

    if not photo_files:
        print(f"\n错误: 未找到照片文件 (支持: jpg, jpeg, png, webp, bmp)")
        sys.exit(1)

    print(f"\n找到 {len(photo_files)} 张照片:")
    for i, photo in enumerate(photo_files, 1):
        size = os.path.getsize(photo) / 1024  # KB
        print(f"  {i}. {os.path.basename(photo)} ({size:.1f} KB)")

    # 加载模型
    model = load_model()

    # 分析所有照片
    print("\n" + "=" * 60)
    print("开始分析照片...")
    print("=" * 60)

    all_results = []
    all_names = []

    start_time = time.time()

    for i, photo_path in enumerate(photo_files, 1):
        print(f"\n[{i}/{len(photo_files)}] 分析: {os.path.basename(photo_path)}")

        result = analyze_photo(model, photo_path)
        if result:
            all_results.append(result)
            all_names.append(os.path.basename(photo_path))

            # 显示基本信息
            width, height = result["image_size"]
            stats = result["stats"]

            print(f"  图片尺寸: {width} x {height}")
            print(f"  特征维度: 384")
            print(f"  特征均值: {stats['mean']:.4f}")
            print(f"  特征标准差: {stats['std']:.4f}")
            print(f"  特征范数: {stats['norm']:.4f}")

            # 基于文件名推测类别
            categories = detect_photo_category(
                os.path.basename(photo_path), result["features"]
            )
            print(f"  类别推测: {', '.join(categories)}")

    elapsed = time.time() - start_time

    if len(all_results) < 2:
        print("\n✗ 需要至少2张照片进行相似度分析")
        sys.exit(1)

    # 相似度分析
    print("\n" + "=" * 60)
    print("相似度分析")
    print("=" * 60)

    similarity_matrix, similarities_info = classify_by_similarity(
        all_results, all_names
    )

    # 1. 显示相似度矩阵
    print("\n【相似度矩阵】(值越接近1表示越相似)")
    print("-" * 80)

    # 表头
    header = "照片名称                    |"
    for i in range(len(all_names)):
        header += f" {i + 1:>6}"
    print(header)
    print("-" * 80)

    # 每一行
    for i in range(len(all_names)):
        name = all_names[i][:25].ljust(25)
        row = f"{name} |"
        for j in range(len(all_names)):
            if i == j:
                row += f" {'---':>6}"
            else:
                row += f" {similarity_matrix[i][j]:>6.3f}"
        print(row)
    print("-" * 80)

    # 2. 每张照片的最相似匹配
    print("\n【每张照片的最相似匹配】")
    print("-" * 80)
    print(f"{'查询照片':<30} {'最相似照片':<30} {'相似度':>10}")
    print("-" * 80)

    for i in range(len(all_names)):
        if similarities_info[i]:
            most_sim = similarities_info[i][0]
            print(
                f"{all_names[i]:<30} {most_sim['name']:<30} {most_sim['similarity']:>10.4f}"
            )

    # 3. 相似照片分组
    print("\n【相似照片分组】(相似度 > 0.85)")
    threshold = 0.85
    groups = []
    used = set()

    for i in range(len(all_names)):
        if i in used:
            continue

        group = [i]
        used.add(i)

        for j in range(i + 1, len(all_names)):
            if j not in used and similarity_matrix[i][j] > threshold:
                group.append(j)
                used.add(j)

        if len(group) > 1:
            groups.append(group)

    if groups:
        for idx, group in enumerate(groups, 1):
            print(f"\n  分组 {idx} (可能为相似场景/主题):")
            for i in group:
                print(f"    - {all_names[i]}")
    else:
        print("\n  没有相似度超过0.85的照片组")
        print("  (这些照片内容差异较大)")

    # 4. 最不相似的照片对
    print("\n【最不相似的照片对】(内容差异最大)")
    min_sim = float("inf")
    min_pair = (0, 0)

    for i in range(len(all_names)):
        for j in range(i + 1, len(all_names)):
            if similarity_matrix[i][j] < min_sim:
                min_sim = similarity_matrix[i][j]
                min_pair = (i, j)

    i, j = min_pair
    print(f"  {all_names[i]}")
    print(f"  vs")
    print(f"  {all_names[j]}")
    print(f"  相似度: {min_sim:.4f}")
    print(f"  说明: 这两张照片内容差异最大")

    # 5. 整体分析结论
    print("\n" + "=" * 60)
    print("识别结果总结")
    print("=" * 60)

    # 计算平均相似度
    avg_sims = []
    for i in range(len(all_names)):
        for j in range(i + 1, len(all_names)):
            avg_sims.append(similarity_matrix[i][j])

    avg_similarity = np.mean(avg_sims)

    print(f"\n处理统计:")
    print(f"  照片总数: {len(all_names)}张")
    print(f"  总处理时间: {elapsed:.2f}秒")
    print(f"  平均每张: {elapsed / len(all_names) * 1000:.2f}ms")

    print(f"\n相似度统计:")
    print(f"  平均相似度: {avg_similarity:.4f}")
    print(f"  最高相似度: {np.max(avg_sims):.4f}")
    print(f"  最低相似度: {np.min(avg_sims):.4f}")

    if avg_similarity > 0.8:
        print(f"\n结论: 这些照片内容高度相似，可能是同一场景的不同角度/时间拍摄")
    elif avg_similarity > 0.6:
        print(f"\n结论: 这些照片有一定相似性，可能属于同一类别或主题")
    else:
        print(f"\n结论: 这些照片内容差异较大，属于不同场景或主题")

    # 保存结果
    output_dir = "/home/ubuntu2204/kimi_prj/docker_dino2/output"
    os.makedirs(output_dir, exist_ok=True)

    # 保存特征
    features_array = np.array([r["features"] for r in all_results])
    np.save(os.path.join(output_dir, "photo_features.npy"), features_array)
    np.save(os.path.join(output_dir, "photo_similarity_matrix.npy"), similarity_matrix)

    # 保存详细结果
    results = {
        "num_photos": len(all_names),
        "photo_names": all_names,
        "photo_info": [
            {
                "name": all_names[i],
                "size": all_results[i]["image_size"],
                "stats": all_results[i]["stats"],
                "most_similar": similarities_info[i][0]
                if similarities_info[i]
                else None,
            }
            for i in range(len(all_names))
        ],
        "similarity_matrix": similarity_matrix.tolist(),
        "processing_time": elapsed,
        "average_similarity": float(avg_similarity),
    }

    with open(
        os.path.join(output_dir, "photo_results.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到 output/ 目录:")
    print(f"  - photo_features.npy")
    print(f"  - photo_similarity_matrix.npy")
    print(f"  - photo_results.json")

    print("\n" + "=" * 60)
    print("照片识别完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
