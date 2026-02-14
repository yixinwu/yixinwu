#!/usr/bin/env python3
"""
DINOv2 Docker 测试脚本
包含基础功能测试、特征提取测试、图像分类测试等
"""

import os
import sys
import time
import torch
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
import cv2

# 测试配置
TEST_CONFIG = {
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "test_image_size": (224, 224),
    "batch_size": 4,
    "num_features": 768,  # DINOv2 small 模型的特征维度
}


def test_environment():
    """测试环境配置"""
    print("=" * 60)
    print("测试1: 环境配置检查")
    print("=" * 60)

    results = []

    # 检查 PyTorch
    try:
        print(f"✓ PyTorch 版本: {torch.__version__}")
        results.append(True)
    except Exception as e:
        print(f"✗ PyTorch 检查失败: {e}")
        results.append(False)

    # 检查 CUDA
    try:
        if torch.cuda.is_available():
            print(f"✓ CUDA 可用")
            print(f"✓ CUDA 版本: {torch.version.cuda}")
            print(f"✓ GPU 数量: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"  - GPU {i}: {torch.cuda.get_device_name(i)}")
        else:
            print("⚠ CUDA 不可用，使用 CPU 模式")
        results.append(True)
    except Exception as e:
        print(f"✗ CUDA 检查失败: {e}")
        results.append(False)

    # 检查 DINOv2 模块
    try:
        import dinov2

        print(f"✓ DINOv2 模块已安装")
        results.append(True)
    except ImportError:
        print("✗ DINOv2 模块未安装")
        results.append(False)

    print(f"\n环境检查通过率: {sum(results)}/{len(results)}\n")
    return all(results)


def test_model_loading():
    """测试模型加载"""
    print("=" * 60)
    print("测试2: 模型加载测试")
    print("=" * 60)

    results = []

    try:
        # 加载预训练模型 (使用 torch hub)
        print("正在加载 DINOv2 small 模型...")
        model = torch.hub.load("facebookresearch/dinov2", "dinov2_vits14")
        model = model.to(TEST_CONFIG["device"])
        model.eval()

        print(f"✓ 模型加载成功")
        print(f"✓ 模型参数数量: {sum(p.numel() for p in model.parameters()):,}")
        results.append(True)

        return model, results
    except Exception as e:
        print(f"✗ 模型加载失败: {e}")
        results.append(False)
        return None, results


def test_feature_extraction(model):
    """测试特征提取功能"""
    print("=" * 60)
    print("测试3: 特征提取测试")
    print("=" * 60)

    results = []

    try:
        # 创建测试图像
        print("创建测试图像...")
        test_image = Image.new("RGB", TEST_CONFIG["test_image_size"], color="red")

        # 图像预处理
        transform = transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

        input_tensor = transform(test_image).unsqueeze(0).to(TEST_CONFIG["device"])
        print(f"✓ 输入张量形状: {input_tensor.shape}")

        # 特征提取
        with torch.no_grad():
            features = model(input_tensor)

        print(f"✓ 特征提取成功")
        print(f"✓ 输出特征形状: {features.shape}")
        print(f"✓ 特征维度: {features.shape[-1]}")

        # 验证特征维度
        assert features.shape[-1] == TEST_CONFIG["num_features"], "特征维度不匹配"
        print(f"✓ 特征维度验证通过")

        results.append(True)

    except Exception as e:
        print(f"✗ 特征提取失败: {e}")
        results.append(False)

    print()
    return results


def test_batch_processing(model):
    """测试批量处理"""
    print("=" * 60)
    print("测试4: 批量处理测试")
    print("=" * 60)

    results = []

    try:
        # 创建批量测试数据
        print(f"创建 {TEST_CONFIG['batch_size']} 张测试图像...")
        transform = transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

        batch_tensors = []
        for i in range(TEST_CONFIG["batch_size"]):
            # 创建不同颜色的测试图像
            color = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)][i]
            img = Image.new("RGB", TEST_CONFIG["test_image_size"], color=color)
            tensor = transform(img)
            batch_tensors.append(tensor)

        batch = torch.stack(batch_tensors).to(TEST_CONFIG["device"])
        print(f"✓ 批输入形状: {batch.shape}")

        # 批量特征提取
        start_time = time.time()
        with torch.no_grad():
            features = model(batch)
        end_time = time.time()

        print(f"✓ 批量特征提取成功")
        print(f"✓ 输出特征形状: {features.shape}")
        print(f"✓ 处理时间: {(end_time - start_time) * 1000:.2f}ms")
        print(
            f"✓ 单张平均时间: {(end_time - start_time) / TEST_CONFIG['batch_size'] * 1000:.2f}ms"
        )

        results.append(True)

    except Exception as e:
        print(f"✗ 批量处理失败: {e}")
        results.append(False)

    print()
    return results


def test_image_similarity(model):
    """测试图像相似度计算"""
    print("=" * 60)
    print("测试5: 图像相似度测试")
    print("=" * 60)

    results = []

    try:
        transform = transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

        # 创建测试图像
        img1 = Image.new("RGB", (224, 224), color="red")
        img2 = Image.new("RGB", (224, 224), color="red")  # 相同
        img3 = Image.new("RGB", (224, 224), color="blue")  # 不同

        # 提取特征
        with torch.no_grad():
            feat1 = model(transform(img1).unsqueeze(0).to(TEST_CONFIG["device"]))
            feat2 = model(transform(img2).unsqueeze(0).to(TEST_CONFIG["device"]))
            feat3 = model(transform(img3).unsqueeze(0).to(TEST_CONFIG["device"]))

        # 计算余弦相似度
        cos_sim = torch.nn.CosineSimilarity(dim=1)

        sim_same = cos_sim(feat1, feat2).item()
        sim_diff = cos_sim(feat1, feat3).item()

        print(f"✓ 相同图像相似度: {sim_same:.4f}")
        print(f"✓ 不同图像相似度: {sim_diff:.4f}")
        print(f"✓ 相似度差异: {sim_same - sim_diff:.4f}")

        # 验证: 相同图像应该有更高的相似度
        assert sim_same > sim_diff, "相似度计算异常"
        print(f"✓ 相似度逻辑验证通过")

        results.append(True)

    except Exception as e:
        print(f"✗ 相似度测试失败: {e}")
        results.append(False)

    print()
    return results


def test_performance(model):
    """测试性能基准"""
    print("=" * 60)
    print("测试6: 性能基准测试")
    print("=" * 60)

    results = []

    try:
        transform = transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

        # 预热
        print("预热中...")
        dummy_input = torch.randn(1, 3, 224, 224).to(TEST_CONFIG["device"])
        for _ in range(10):
            with torch.no_grad():
                _ = model(dummy_input)

        if TEST_CONFIG["device"] == "cuda":
            torch.cuda.synchronize()

        # 性能测试
        print("性能测试...")
        num_iterations = 100
        times = []

        for i in range(num_iterations):
            start = time.time()
            with torch.no_grad():
                _ = model(dummy_input)
            if TEST_CONFIG["device"] == "cuda":
                torch.cuda.synchronize()
            end = time.time()
            times.append((end - start) * 1000)  # 转换为毫秒

        avg_time = np.mean(times)
        std_time = np.std(times)

        print(f"✓ 平均推理时间: {avg_time:.2f}ms ± {std_time:.2f}ms")
        print(f"✓ 吞吐量: {1000 / avg_time:.2f} images/sec")

        results.append(True)

    except Exception as e:
        print(f"✗ 性能测试失败: {e}")
        results.append(False)

    print()
    return results


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("DINOv2 Docker 测试套件")
    print("=" * 60 + "\n")

    all_results = []

    # 测试1: 环境配置
    all_results.append(test_environment())

    # 测试2: 模型加载
    model, results = test_model_loading()
    all_results.extend(results)

    if model is None:
        print("模型加载失败，跳过后续测试")
        sys.exit(1)

    # 测试3-6: 功能测试
    all_results.extend(test_feature_extraction(model))
    all_results.extend(test_batch_processing(model))
    all_results.extend(test_image_similarity(model))
    all_results.extend(test_performance(model))

    # 总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    passed = sum(all_results)
    total = len(all_results)
    print(f"通过测试: {passed}/{total}")
    print(f"成功率: {passed / total * 100:.1f}%")

    if passed == total:
        print("\n✓ 所有测试通过！DINOv2 Docker 镜像工作正常。")
        return 0
    else:
        print("\n✗ 部分测试失败，请检查配置。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
