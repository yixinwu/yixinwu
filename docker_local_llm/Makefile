.PHONY: help up down logs download test status clean

help:
	@echo "Qwen3-30B-A3B-Q4 Docker 部署"
	@echo ""
	@echo "可用命令:"
	@echo "  make download  - 下载模型文件"
	@echo "  make up        - 启动服务"
	@echo "  make down      - 停止服务"
	@echo "  make logs      - 查看日志"
	@echo "  make test      - 测试 API"
	@echo "  make status    - 查看状态"
	@echo "  make clean     - 清理容器和卷"
	@echo "  make restart   - 重启服务"

download:
	@./download-model.sh

up:
	@docker-compose up -d
	@echo "服务启动中..."
	@sleep 3
	@docker-compose ps

down:
	@docker-compose down

logs:
	@docker-compose logs -f

test:
	@echo "测试 API..."
	@curl -s http://localhost:8080/health 2>/dev/null || echo "服务未就绪，请稍后再试"
	@echo ""
	@curl -s http://localhost:8080/v1/models 2>/dev/null | head -20 || echo ""

status:
	@echo "=== Docker 状态 ==="
	@docker-compose ps
	@echo ""
	@echo "=== GPU 使用情况 ==="
	@nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv 2>/dev/null || echo "nvidia-smi 不可用"

restart:
	@docker-compose restart
	@echo "服务重启中..."
	@sleep 3
	@docker-compose ps

clean:
	@docker-compose down -v
	@docker rmi ghcr.io/ggml-org/llama.cpp:server-cuda 2>/dev/null || true
	@echo "清理完成"

# 开发调试用
shell:
	@docker-compose exec llm-qwen3 bash
