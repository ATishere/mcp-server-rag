
Deployment
Local Development
bash
python -m venv .venv
source .venv/Scripts/activate
pip install -e ".[dev]"
cp .env.example .env
# Edit .env
python -m mcp_rag
Docker
bash
# Build
docker build -t mcp-server-rag:latest .

# Run with dependencies
docker-compose up -d

# Logs
docker-compose logs -f mcp-server

# Stop
docker-compose down
Production Checklist
□ Set ENVIRONMENT=production in .env
□ Generate strong JWT_SECRET (32+ chars)
□ Use PostgreSQL with pgvector
□ Use Redis for cache + rate limiting
□ Enable HTTPS (if using HTTP transport)
□ Set up log aggregation (ELK, Loki, Datadog)
□ Set up metrics (Prometheus + Grafana)
□ Configure alerts for error rate > 0.1%
