# ============================================================
# Stage 1: Builder — cài dependencies
# ============================================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Cài build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy metadata trước (tận dụng Docker layer cache)
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Cài vào /install (không phải system Python)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install .

# ============================================================
# Stage 2: Runtime — image gọn, non-root
# ============================================================
FROM python:3.12-slim AS runtime

# Tạo non-root user
RUN groupadd --gid 1000 mcp && \
    useradd --uid 1000 --gid mcp --shell /bin/bash --create-home mcp

WORKDIR /app

# Copy site-packages từ builder
COPY --from=builder /install /usr/local

# Copy source code
COPY --chown=mcp:mcp src/ ./src/
COPY --chown=mcp:mcp pyproject.toml README.md ./

# Cài lại package (editable) cho user mcp
RUN pip install --no-cache-dir -e .

# Chuyển sang non-root
USER mcp

# Biến môi trường
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from mcp_rag.config import settings; print('OK')" || exit 1

# Chạy MCP server
ENTRYPOINT ["python", "-m", "mcp_rag"]
