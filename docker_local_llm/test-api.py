#!/usr/bin/env python3
"""
Qwen3-30B-A3B-Q4 API 测试脚本
"""

import sys
import requests
import json

BASE_URL = "http://localhost:8080"


def check_health():
    """检查服务健康状态"""
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        if resp.status_code == 200:
            print("✓ 服务运行正常")
            return True
    except Exception as e:
        print(f"✗ 服务未就绪: {e}")
    return False


def list_models():
    """列出可用模型"""
    try:
        resp = requests.get(f"{BASE_URL}/v1/models", timeout=5)
        data = resp.json()
        print("\n可用模型:")
        for model in data.get("data", []):
            print(f"  - {model.get('id')}")
    except Exception as e:
        print(f"获取模型列表失败: {e}")


def test_chat():
    """测试对话接口"""
    print("\n测试对话接口...")
    
    messages = [
        {"role": "system", "content": "你是一个 helpful 的 AI 助手。"},
        {"role": "user", "content": "你好，请用一句话介绍自己。"}
    ]
    
    payload = {
        "model": "qwen3-30b-a3b-q4",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 512,
        "stream": False
    }
    
    try:
        resp = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=60
        )
        data = resp.json()
        
        if "choices" in data:
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            
            print("\n=== 模型回复 ===")
            print(content)
            print("\n=== Token 使用情况 ===")
            print(f"  输入: {usage.get('prompt_tokens', 'N/A')}")
            print(f"  输出: {usage.get('completion_tokens', 'N/A')}")
            print(f"  总计: {usage.get('total_tokens', 'N/A')}")
            return True
        else:
            print(f"错误: {data}")
            return False
            
    except Exception as e:
        print(f"请求失败: {e}")
        return False


def test_stream():
    """测试流式响应"""
    print("\n测试流式响应...")
    
    payload = {
        "model": "qwen3-30b-a3b-q4",
        "messages": [{"role": "user", "content": "你好"}],
        "stream": True,
        "max_tokens": 100
    }
    
    try:
        resp = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            stream=True,
            timeout=60
        )
        
        print("\n=== 流式输出 ===")
        for line in resp.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0]["delta"]
                        if "content" in delta:
                            print(delta["content"], end='', flush=True)
                    except:
                        pass
        print("\n")
        return True
        
    except Exception as e:
        print(f"流式请求失败: {e}")
        return False


def main():
    print("=" * 50)
    print("Qwen3-30B-A3B-Q4 API 测试")
    print("=" * 50)
    
    # 检查服务
    if not check_health():
        print("\n请确保服务已启动: make up")
        sys.exit(1)
    
    # 列出模型
    list_models()
    
    # 测试对话
    if not test_chat():
        sys.exit(1)
    
    # 测试流式（可选）
    if len(sys.argv) > 1 and sys.argv[1] == "--stream":
        test_stream()
    
    print("\n" + "=" * 50)
    print("✓ 所有测试通过!")
    print("=" * 50)


if __name__ == "__main__":
    main()
