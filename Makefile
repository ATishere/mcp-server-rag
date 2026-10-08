# ============================================================
# MCP Server for RAG — Makefile
# ============================================================
.PHONY: help install install-dev test test-cov lint format type-check \
        run clean docker docker-build docker-up docker-down \
        eval pre-commit

# ----- Help -----
help:  ## Hiển thị help
	@echo "MCP Server for RAG — Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ----- Install -----
install:  ## Cài package (production)
	pip install -e .

install-dev:  ## Cài package + dev tools
	pip install -e ".[dev]"

# ----- Test -----
test:  ## Chạy tất cả tests
	pytest tests/ -v

test-cov:  ## Chạy tests với coverage
	pytest tests/ -v --cov=mcp_rag --cov-report=html --cov-report=term-missing

test-fast:  ## Chạy tests nhanh (bỏ slow)
	pytest tests/ -v -m "not slow"

# ----- Code quality -----
lint:  ## Chạy linter (ruff)
	ruff check src/ tests/

format:  ## Format code (ruff)
	ruff format src/ tests/

type-check:  ## Chạy type checker (mypy)
	mypy src/

check: lint type-check test  ## Chạy tất cả checks

# ----- Run -----
run:  ## Chạy MCP server
	python -m mcp_rag

# ----- Docker -----
docker-build:  ## Build Docker image
	docker build -t mcp-server-rag:latest .

docker-up:  ## Khởi động services (docker-compose up)
	docker-compose up -d

docker-down:  ## Dừng services
	docker-compose down

docker-logs:  ## Xem logs
	docker-compose logs -f mcp-server

# ----- Clean -----
clean:  ## Xóa cache, build artifacts
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf htmlcov/ .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# ----- Eval -----
eval:  ## Chạy RAG evaluation (sẽ thêm sau)
	@echo "Evaluation harness chưa được cài đặt."

# ----- Pre-commit -----
pre-commit:  ## Chạy trước khi commit
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test
