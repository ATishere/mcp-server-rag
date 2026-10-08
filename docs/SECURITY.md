
Security
Threat Model
Threat	Mitigation
Identity spoofing	JWT with HMAC signature
Privilege escalation	RBAC with 3 roles
Malformed input	Pydantic validation
Prompt injection	20+ regex patterns
DoS	Rate limiting
Data leak	Sensitive data censoring in logs
6-Layer Defense
JWT Authentication

Stateless, HMAC-signed tokens

Claims: sub, role, scopes, exp, iat

Verify signature, expiry, issuer, audience

RBAC

Roles: admin, editor, viewer

Permissions: read, write, delete, admin

require_permission(role, permission) raises if denied

Input Validation

Pydantic v2 models with strict rules

Max length, min length, regex patterns

Custom validators for business logic

Prompt Injection Detection

20+ regex patterns

Categories: instruction override, role change,
system prompt leak, delimiter injection, SQL injection

detect_injection(text) returns bool

Rate Limiting

Sliding window per user

Config: 60 req/min (default)

Backed by Redis (planned)

Audit Logging

Structured JSON logs

Context vars: request_id, user_id, workspace_id

Sensitive data auto-censored
