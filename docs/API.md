# API Reference

## Tools

### search_documents

Search documents using hybrid search (BM25 + vector).

**Input:**
```json
{
  "query": "string (1-500 chars)",
  "top_k": "integer (1-50, default 10)",
  "filters": "object (optional)",
  "token": "string (JWT)"
}
Output: Formatted list of relevant chunks with scores.

Permission: read

retrieve_chunk
Fetch full content of a specific chunk.

Input:

json
{
  "chunk_id": "string (alphanumeric + -_)",
  "token": "string (JWT)"
}
Permission: read

generate_answer
Generate a natural language answer with citations.

Input:

json
{
  "query": "string (1-500 chars)",
  "context": "array of strings (1-20 items)",
  "token": "string (JWT)"
}
Permission: read

cite_sources
Retrieve citations for a previously generated answer.

Input:

json
{
  "answer_id": "string",
  "token": "string (JWT)"
}
Permission: read
