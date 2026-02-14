#!/bin/bash

# DINOv2 Docker 快速测试脚本
# 用于快速验证 Docker 容器功能

echo "=========================================="
echo "DINOv2 Docker 快速测试"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试函数
test_python() {
    echo -e "\n[1/4] 测试 Python 环境..."
    if python3 --version > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Python 版本: $(python3 --version)"
        return 0
    else
        echo -e "${RED}✗${NC} Python 未找到"
        return 1
    fi
}

test_pytorch() {
    echo -e "\n[2/4] 测试 PyTorch..."
    python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA可用: {torch.cuda.is_available()}')"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} PyTorch 安装正常"
        return 0
    else
        echo -e "${RED}✗${NC} PyTorch 测试失败"
        return 1
    fi
}

test_dinov2() {
    echo -e "\n[3/4] 测试 DINOv2 模块..."
    python3 -c "import dinov2; print('DINOv2 模块已安装')"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} DINOv2 模块安装正常"
        return 0
    else
        echo -e "${RED}✗${NC} DINOv2 模块测试失败"
        return 1
    fi
}

test_model_download() {
    echo -e "\n[4/4] 测试模型下载..."
    python3 << 'EOF'
import torch
print("正在下载 DINOv2 预训练模型（首次运行需要）...")
try:
    model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vits14', pretrained=True)
    print("✓ 模型下载成功")
except Exception as e:
    print(f"✗ 模型下载失败: {e}")
    exit(1)
EOF
    if [ $? -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

# 运行测试
passed=0
failed=0

test_python && ((passed++)) || ((failed++))
test_pytorch && ((passed++)) || ((failed++))
test_dinov2 && ((passed++)) || ((failed++))
test_model_download && ((passed++)) || ((failed++))

# 结果总结
echo -e "\n=========================================="
echo "测试完成"
echo "=========================================="
echo -e "通过: ${GREEN}${passed}${NC}, 失败: ${RED}${failed}${NC}"

if [ $failed -eq 0 ]; then
    echo -e "\n${GREEN}所有测试通过！${NC}"
    exit 0
else
    echo -e "\n${RED}部分测试失败${NC}"
    exit 1
fi
