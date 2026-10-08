# Architecture

## 5-Tier Design

### Tier 1: MCP Client
- Claude Desktop, Cursor, Cline, Continue
- User interacts here
- Communicates via MCP protocol (stdio / HTTP)

### Tier 2: MCP Server
- Receives requests from clients
- Routes to appropriate tool
- Returns results
- Components: Tools, Resources, Prompts

### Tier 3: Security Layer (6 layers)
1. JWT Authentication — Verify identity
2. RBAC — Check permissions
3. Input Validation — Pydantic models
4. Prompt Injection Detection — 20+ regex patterns
5. Rate Limiting — Sliding window
6. Audit Logging — Structured JSON

### Tier 4: RAG Engine
- Embedding — Text → Vector
- Vector Search — Hybrid (BM25 + vector)
- Reranking — Cross-encoder
- Generation — LLM (Claude)
- CRAG — Corrective RAG (planned)

### Tier 5: Storage
- PostgreSQL + pgvector — Documents, chunks, embeddings
- Redis — Cache, rate limiting
- S3 — Raw documents

## Data Flow
User Query
↓
MCP Client
↓ (MCP protocol)
MCP Server
↓
Security Layer (JWT → RBAC → Validation → Injection)
↓
RAG Engine (Embed → Search → Rerank → Generate)
↓
Storage (Postgres → Redis → S3)
↓
Response back to User

text
