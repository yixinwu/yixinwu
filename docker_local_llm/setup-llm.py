#!/usr/bin/env python3
"""
Qwen3-30B-A3B-Q4 部署脚本 - 国内镜像版
使用魔搭社区 (ModelScope) 下载模型
"""

import os
import sys
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

# 配置
MODELS_DIR = Path("./models")
MODEL_FILE = MODELS_DIR / "Qwen3-30B-A3B-Q4_K_M.gguf"
LLAMA_SERVER = Path("/tmp/llama-server")

# 国内镜像源
MODEL_URLS = [
    "https://www.modelscope.cn/models/Qwen/Qwen3-30B-A3B-GGUF/resolve/master/qwen3-30b-a3b-q4_k_m.gguf",
    "https://hf-mirror.com/Qwen/Qwen3-30B-A3B-GGUF/resolve/main/qwen3-30b-a3b-q4_k_m.gguf",
]

LLAMA_SERVER_URLS = [
    "https://ghproxy.com/https://github.com/ggml-org/llama.cpp/releases/download/b4600/llama-server-linux-cuda-cu12.2-x64",
    "https://github.com/ggml-org/llama.cpp/releases/download/b4600/llama-server-linux-cuda-cu12.2-x64",
]

def run_cmd(cmd, cwd=None):
    """运行命令"""
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
        return False
    return True

def download_file(url, output_path, desc="文件"):
    """下载文件"""
    print(f"\n下载 {desc}...")
    print(f"  URL: {url}")
    print(f"  保存到: {output_path}")
    
    try:
        # 设置超时和 header
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        
        # 下载
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with urllib.request.urlopen(req, timeout=300) as response:
            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                while True:
                    chunk = response.read(block_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r  进度: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='', flush=True)
        
        print(f"\n✓ {desc} 下载完成!")
        return True
        
    except Exception as e:
        print(f"\n✗ 下载失败: {e}")
        if output_path.exists():
            output_path.unlink()
        return False

def download_with_wget(url, output_path):
    """使用 wget 下载"""
    cmd = ["wget", "--timeout=300", "-t", "3", "--show-progress", "-O", str(output_path), url]
    return run_cmd(cmd)

def install_modelscope():
    """安装 modelscope"""
    print("\n安装 modelscope...")
    try:
        import modelscope
        print("✓ modelscope 已安装")
        return True
    except ImportError:
        print("安装 modelscope...")
        cmd = [sys.executable, "-m", "pip", "install", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple", "modelscope"]
        return run_cmd(cmd)

def download_model_with_modelscope():
    """使用 modelscope 下载模型"""
    try:
        from modelscope import snapshot_download
        print("\n使用魔搭社区下载模型...")
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        
        # 下载模型
        model_dir = snapshot_download(
            "Qwen/Qwen3-30B-A3B-GGUF",
            allow_file_pattern=["qwen3-30b-a3b-q4_k_m.gguf"],
            local_dir=str(MODELS_DIR),
            local_dir_use_symlinks=False
        )
        
        # 重命名文件
        src_file = MODELS_DIR / "qwen3-30b-a3b-q4_k_m.gguf"
        if src_file.exists() and not MODEL_FILE.exists():
            src_file.rename(MODEL_FILE)
        
        if MODEL_FILE.exists():
            print(f"✓ 模型下载成功: {MODEL_FILE}")
            print(f"  大小: {MODEL_FILE.stat().st_size / 1024 / 1024 / 1024:.2f} GB")
            return True
        return False
        
    except Exception as e:
        print(f"✗ modelscope 下载失败: {e}")
        return False

def download_llama_server():
    """下载 llama-server 二进制文件"""
    if LLAMA_SERVER.exists():
        print(f"\n✓ llama-server 已存在: {LLAMA_SERVER}")
        return True
    
    print("\n下载 llama-server...")
    
    # 尝试多个 URL
    for url in LLAMA_SERVER_URLS:
        if download_with_wget(url, LLAMA_SERVER):
            # 添加执行权限
            os.chmod(LLAMA_SERVER, 0o755)
            print(f"✓ llama-server 下载完成")
            return True
    
    return False

def download_model():
    """下载模型文件"""
    if MODEL_FILE.exists():
        print(f"\n✓ 模型文件已存在: {MODEL_FILE}")
        print(f"  大小: {MODEL_FILE.stat().st_size / 1024 / 1024 / 1024:.2f} GB")
        return True
    
    # 尝试使用 modelscope
    if install_modelscope():
        if download_model_with_modelscope():
            return True
    
    # 尝试直接下载
    print("\n尝试直接下载模型...")
    for url in MODEL_URLS:
        if download_with_wget(url, MODEL_FILE):
            print(f"✓ 模型下载成功")
            return True
    
    return False

def test_llama_server():
    """测试 llama-server"""
    print("\n测试 llama-server...")
    cmd = [str(LLAMA_SERVER), "--help"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 or "llama-server" in result.stdout.lower():
        print("✓ llama-server 可用")
        return True
    print(f"✗ llama-server 测试失败")
    return False

def create_launch_script():
    """创建启动脚本"""
    script = MODELS_DIR / "run-server.sh"
    content = f'''#!/bin/bash
# Qwen3-30B-A3B-Q4 启动脚本

MODEL_FILE="{MODEL_FILE}"
LLAMA_SERVER="{LLAMA_SERVER}"

if [ ! -f "$MODEL_FILE" ]; then
    echo "错误: 模型文件不存在: $MODEL_FILE"
    echo "请先运行: python3 setup-llm.py --download-model"
    exit 1
fi

echo "启动 llama.cpp server..."
echo "  模型: $MODEL_FILE"
echo "  GPU: 启用 (全部层)"
echo "  上下文: 32768 tokens"
echo "  服务地址: http://0.0.0.0:8080"
echo ""

exec "$LLAMA_SERVER" \\
    --model "$MODEL_FILE" \\
    --host 0.0.0.0 \\
    --port 8080 \\
    --n-gpu-layers 999 \\
    --ctx-size 32768 \\
    --threads 8 \\
    --batch-size 512 \\
    --ubatch-size 512 \\
    --flash-attn \\
    --mlock \\
    "$@"
'''
    script.write_text(content)
    script.chmod(0o755)
    print(f"\n✓ 启动脚本已创建: {script}")
    return script

def main():
    print("=" * 60)
    print("  Qwen3-30B-A3B-Q4 部署脚本")
    print("=" * 60)
    
    # 下载 llama-server
    if not download_llama_server():
        print("\n✗ 无法下载 llama-server")
        print("\n请手动下载:")
        print("  https://github.com/ggml-org/llama.cpp/releases")
        print("  选择: llama-server-linux-cuda-cu12.2-x64")
        print(f"  保存到: {LLAMA_SERVER}")
        return 1
    
    # 测试 llama-server
    if not test_llama_server():
        print("\n警告: llama-server 可能有问题")
    
    # 下载模型
    if "--download-model" in sys.argv or not MODEL_FILE.exists():
        if not download_model():
            print("\n✗ 无法下载模型")
            print("\n请手动下载:")
            print("  访问: https://www.modelscope.cn/models/Qwen/Qwen3-30B-A3B-GGUF")
            print("  下载: qwen3-30b-a3b-q4_k_m.gguf")
            print(f"  保存到: {MODEL_FILE}")
            return 1
    
    # 创建启动脚本
    launch_script = create_launch_script()
    
    print("\n" + "=" * 60)
    print("  部署准备完成!")
    print("=" * 60)
    print(f"\n模型文件: {MODEL_FILE}")
    print(f"启动脚本: {launch_script}")
    print("\n启动服务:")
    print(f"  bash {launch_script}")
    print("\n或使用 Docker:")
    print("  docker-compose up -d")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
