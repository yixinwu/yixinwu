#!/usr/bin/env python3
"""
DINOv2 特征提取示例
展示如何使用 DINOv2 进行图像特征提取
"""

import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
from pathlib import Path


def extract_features(image_path, model_name="dinov2_vits14", device="cuda"):
    """
    从图像中提取 DINOv2 特征

    参数:
        image_path: 图像路径
        model_name: 模型名称 ('dinov2_vits14', 'dinov2_vitb14', 'dinov2_vitl14', 'dinov2_vitg14')
        device: 计算设备 ('cuda' 或 'cpu')

    返回:
        features: 特征向量 (numpy array)
    """
    # 加载模型
    print(f"加载模型: {model_name}...")
    model = torch.hub.load("facebookresearch/dinov2", model_name)
    model = model.to(device)
    model.eval()

    # 图像预处理
    transform = transforms.Compose(
        [
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    # 加载图像
    image = Image.open(image_path).convert("RGB")
    input_tensor = transform(image).unsqueeze(0).to(device)

    # 提取特征
    print(f"提取特征...")
    with torch.no_grad():
        features = model(input_tensor)

    # 转换为 numpy
    features = features.cpu().numpy()

    print(f"特征维度: {features.shape}")
    print(f"特征范数: {np.linalg.norm(features):.4f}")

    return features


def batch_extract_features(
    image_paths, model_name="dinov2_vits14", batch_size=8, device="cuda"
):
    """
    批量提取图像特征

    参数:
        image_paths: 图像路径列表
        model_name: 模型名称
        batch_size: 批处理大小
        device: 计算设备

    返回:
        features_list: 特征列表
    """
    # 加载模型
    model = torch.hub.load("facebookresearch/dinov2", model_name)
    model = model.to(device)
    model.eval()

    transform = transforms.Compose(
        [
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    all_features = []

    # 分批处理
    for i in range(0, len(image_paths), batch_size):
        batch_paths = image_paths[i : i + batch_size]

        # 加载并预处理图像
        batch_tensors = []
        for path in batch_paths:
            image = Image.open(path).convert("RGB")
            tensor = transform(image)
            batch_tensors.append(tensor)

        # 批处理推理
        batch = torch.stack(batch_tensors).to(device)
        with torch.no_grad():
            features = model(batch)

        all_features.append(features.cpu().numpy())

        if (i // batch_size + 1) % 10 == 0:
            print(
                f"已处理 {min(i + batch_size, len(image_paths))}/{len(image_paths)} 张图像"
            )

    # 合并所有特征
    all_features = np.vstack(all_features)
    print(f"\n总特征数量: {all_features.shape[0]}")
    print(f"特征维度: {all_features.shape[1]}")

    return all_features


def compute_similarity(features1, features2):
    """
    计算两组特征之间的余弦相似度

    参数:
        features1: 第一组特征
        features2: 第二组特征

    返回:
        similarity: 相似度矩阵
    """
    # 归一化特征
    features1_norm = features1 / np.linalg.norm(features1, axis=1, keepdims=True)
    features2_norm = features2 / np.linalg.norm(features2, axis=1, keepdims=True)

    # 计算余弦相似度
    similarity = np.dot(features1_norm, features2_norm.T)

    return similarity


def main():
    """示例主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="DINOv2 特征提取示例")
    parser.add_argument("--image", type=str, help="输入图像路径")
    parser.add_argument(
        "--model",
        type=str,
        default="dinov2_vits14",
        choices=["dinov2_vits14", "dinov2_vitb14", "dinov2_vitl14", "dinov2_vitg14"],
        help="模型名称",
    )
    parser.add_argument(
        "--device", type=str, default="cuda", choices=["cuda", "cpu"], help="计算设备"
    )

    args = parser.parse_args()

    # 检查设备可用性
    if args.device == "cuda" and not torch.cuda.is_available():
        print("警告: CUDA 不可用，切换到 CPU")
        args.device = "cpu"

    if args.image:
        # 单张图像特征提取
        if not Path(args.image).exists():
            print(f"错误: 图像不存在: {args.image}")
            return

        features = extract_features(args.image, args.model, args.device)

        # 保存特征
        output_path = Path(args.image).stem + "_features.npy"
        np.save(output_path, features)
        print(f"\n特征已保存到: {output_path}")

    else:
        # 演示模式
        print("=" * 60)
        print("DINOv2 特征提取演示")
        print("=" * 60)
        print(f"\n可用模型:")
        print("  - dinov2_vits14 (推荐，21M参数)")
        print("  - dinov2_vitb14 (86M参数)")
        print("  - dinov2_vitl14 (300M参数)")
        print("  - dinov2_vitg14 (1.1B参数)")
        print(f"\n使用示例:")
        print(f"  python examples/extract_features.py --image path/to/image.jpg")
        print(
            f"  python examples/extract_features.py --image path/to/image.jpg --model dinov2_vitb14"
        )


if __name__ == "__main__":
    main()
