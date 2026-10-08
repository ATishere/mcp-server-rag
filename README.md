# MCP Server for RAG

> Production-grade MCP server exposing RAG capabilities to LLM applications (Claude Desktop, Cursor, etc.)

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![MCP](https://img.shields.io/badge/MCP-1.0-purple.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-101%20passed-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-84%25-green.svg)]()
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

---

## Overview

A production-grade Model Context Protocol (MCP) server that exposes Retrieval-Augmented Generation (RAG) capabilities to any MCP-compatible client (Claude Desktop, Cursor, etc.).

Think of it as a "USB-C for AI" — a standardized protocol that lets LLMs access your private knowledge base with built-in security, observability, and production safeguards.

### Why this project?

| Problem | Solution |
|---------|----------|
| LLMs don't know your private data | RAG pipeline fetches relevant documents |
| LLMs can't connect to your databases | MCP provides standardized interface |
| No security / access control | 6-layer security stack |
| No observability | Structured logging + metrics |
| Hallucinations from bad retrieval | CRAG (Corrective RAG) — planned |

---

## Features

### Core Capabilities
- **MCP Protocol** — Tools, Resources, Prompts
- **Hybrid Search** — BM25 + Vector similarity with RRF fusion
- **Reranking** — Cross-encoder for improved relevance
- **JWT Authentication** — Stateless auth with role-based claims
- **RBAC** — 3 roles: admin, editor, viewer

### Security (6 layers)
- **JWT Authentication** — Verify identity
- **RBAC** — Check permissions (admin/editor/viewer)
- **Input Validation** — Pydantic models with strict rules
- **Prompt Injection Detection** — 20+ regex patterns
- **Rate Limiting** — Sliding window per user
- **Audit Logging** — Structured JSON logs with context vars

### Observability
- **Structured Logging** — JSON format, context-aware
- **Sensitive Data Censoring** — Auto-mask tokens/passwords
- **Request Tracing** — request_id, user_id propagated

### DevOps
- **Docker** — Multi-stage build, non-root user
- **Docker Compose** — Postgres + Redis + Server
- **CI/CD** — GitHub Actions (lint, type-check, test, coverage)
- **Makefile** — Common commands (make test, make run)

---

## Architecture

### 5-Tier Design
+---------------------------------------------------+
| TIER 1: MCP CLIENT |
| Claude Desktop, Cursor, Cline |
+-----------------------+---------------------------+
| MCP Protocol (stdio/HTTP)
v
+---------------------------------------------------+
| TIER 2: MCP SERVER FOR RAG |
| Tools | Resources | Prompts |
+-----------------------+---------------------------+
v
+---------------------------------------------------+
| TIER 3: SECURITY LAYER (6 layers) |
| JWT | RBAC | Validation |
| Injection Detection | Rate Limit | Audit |
+-----------------------+---------------------------+
v
+---------------------------------------------------+
| TIER 4: RAG ENGINE |
| Embedding | Vector Search | Rerank | Generation |
+-----------------------+---------------------------+
v
+---------------------------------------------------+
| TIER 5: STORAGE |
| PostgreSQL + pgvector | Redis | S3 |
+---------------------------------------------------+

text

### Data Flow
User asks: "What is Kubernetes?"

MCP Client -> MCP Server: call_tool(search_documents)

Security: verify JWT + RBAC + injection check

RAG Engine: embed query -> vector

Storage: hybrid search (top 10 chunks)

RAG Engine: rerank -> top 5 chunks

MCP Server -> MCP Client: formatted chunks

User receives answer with citations

text

---

## Quick Start

### Prerequisites
- Python 3.12+
- (Optional) Docker + Docker Compose
- (Optional) PostgreSQL 16 + pgvector, Redis

### Installation

```bash
# Clone repository
git clone https://github.com/ATishere/mcp-server-rag.git
cd mcp-server-rag

# Create virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
# source .venv/bin/activate    # Linux/Mac

# Install dependencies
pip install -e ".[dev]"

# Setup environment
cp .env.example .env
# Edit .env with your JWT_SECRET
Run server
bash
# Run MCP server (stdio transport)
python -m mcp_rag

# Or via Makefile
make run
Test with Claude Desktop
Add to claude_desktop_config.json:

json
{
  "mcpServers": {
    "rag": {
      "command": "python",
      "args": ["-m", "mcp_rag"],
      "env": {
        "JWT_SECRET": "your-secret-key-here",
        "DATABASE_URL": "postgresql+asyncpg://..."
      }
    }
  }
}
Tools
Tool	Description	Permission
search_documents	Hybrid search (BM25 + vector) with reranking	read
retrieve_chunk	Fetch full content of a chunk by ID	read
generate_answer	LLM-generated answer with citations	read
cite_sources	Retrieve citations for a generated answer	read
Example: search_documents
Request:

json
{
  "query": "What is Kubernetes?",
  "top_k": 5,
  "filters": {"source": "k8s.md"},
  "token": "<JWT>"
}
Response:

text
Found 3 relevant chunks for query: 'What is Kubernetes?'

**1. [doc-1]** (score: 0.950)
   chunk_id: chunk-1
   Kubernetes is a container orchestration platform...

**2. [doc-2]** (score: 0.850)
   ...
Performance Metrics
Metric	Target	Actual	Status
Test count	>50	101	✅
Test coverage	>80%	84%	✅
Test duration	<10s	1.36s	✅
Security layers	>=4	6	✅
p95 latency	<200ms	TBD	⏳
Error rate	<0.1%	TBD	⏳
Security
6-Layer Defense
#	Layer	Protects against
1	JWT Authentication	Identity spoofing
2	RBAC	Privilege escalation
3	Input Validation	Malformed / oversized inputs
4	Prompt Injection Detection	LLM manipulation (20+ patterns)
5	Rate Limiting	DoS / abuse
6	Audit Logging	Forensics / compliance
Example: Injection detection
python
from mcp_rag.security.injection import detect_injection

detect_injection("What is Kubernetes?")                 # False
detect_injection("Ignore all previous instructions")    # True
detect_injection("DROP TABLE users")                    # True
Failure Analysis
Real failure modes discovered during development:

Issue #1: MCP SDK version mismatch
Symptom: AttributeError: 'Server' object has no attribute 'list_tools'

Root cause: MCP SDK 2.x removed decorator API

Fix: Pin to mcp>=1.0.0,<2.0.0

Lesson: Always pin SDK versions in pyproject.toml

Issue #2: Logging polluted stdout
Symptom: Failed to parse JSONRPC message from server

Root cause: Logging written to stdout, conflicting with MCP protocol

Fix: Redirect logging to stderr (stream=sys.stderr)

Lesson: MCP protocol owns stdout; use stderr for diagnostics

Issue #3: UnicodeEncodeError on Windows
Symptom: 'charmap' codec can't encode character '\u2705'

Root cause: Windows console defaults to cp1252

Fix: Remove emoji from test output, or set PYTHONIOENCODING=utf-8

Lesson: Windows console is not UTF-8 by default

Issue #4: SQL injection regex missed
Symptom: DROP TABLE users was not detected

Root cause: Pattern required ; before drop table

Fix: Use \bdrop\s+table\b without requiring semicolon

Lesson: Test regex patterns with multiple variants

Issue #5: Validation vs Auth order
Symptom: Invalid token test failed because token was too short

Root cause: Validation runs BEFORE auth — good for fail-fast

Fix: Use token >= 10 chars for auth-specific tests

Lesson: Test isolation — each test should test one layer

What I Would Do Differently
If I rebuilt this project, I would:

Add semantic caching — Cache by embedding similarity, not exact query hash. Expected: 40% cost reduction.

Implement CRAG (Corrective RAG) — Evaluate retrieval relevance with LLM, retry on low relevance. Expected: hallucination rate from 15% to 5%.

Add multi-hop retrieval — Decompose complex queries into sub-queries. Example: "Compare 2023 and 2024 policies" → fetch both, then combine.

Shard vector DB by workspace — For 10M+ documents, single index is too slow. Shard by workspace_id for 10x faster search.

Add read replicas — For read-heavy workloads, route reads to replicas.

Async ingestion pipeline — Upload 10K docs without blocking. Use queue + workers.

Build eval harness from day one — Use RAGAS metrics (faithfulness, answer relevancy, context recall) with golden dataset.

Testing
bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=mcp_rag --cov-report=html --cov-report=term-missing

# Via Makefile
make test
make test-cov
Test structure
text
tests/
├── conftest.py            # Shared fixtures
├── test_auth.py           # JWT + RBAC (22 tests)
├── test_config.py         # Settings (12 tests)
├── test_logging.py        # Logging (22 tests)
├── test_security.py       # Validation + injection (27 tests)
├── test_server.py         # Server setup (4 tests)
└── test_tools.py          # 4 tools (14 tests)
Docker
bash
# Build image
docker build -t mcp-server-rag:latest .

# Run with dependencies
docker-compose up -d

# View logs
docker-compose logs -f mcp-server
Services:

mcp-server — Our MCP server (non-root user)

postgres — PostgreSQL 16 + pgvector

redis — Redis 7 (cache)

Documentation
Architecture — 5-tier design

API Reference — All tools/resources

Security — Threat model

Deployment — Docker, K8s

Tech Stack
Layer	Technology
Protocol	MCP (Model Context Protocol)
Language	Python 3.12
Package manager	pip + pyproject.toml
Validation	Pydantic v2
Auth	PyJWT
Database	PostgreSQL 16 + pgvector
Cache	Redis 7
Logging	structlog
Testing	pytest + pytest-asyncio + pytest-cov
Linting	ruff
Type checking	mypy
CI/CD	GitHub Actions
Container	Docker + docker-compose
License
MIT License — see LICENSE for details.

Author
Pham Anh Tuan

Email: tech.anhpham@gmail.com

GitHub: @ATishere

⭐ If you find this project useful, please give it a star!
