# Security Architecture & Guardrails

## 1. Authentication & Hashing
* Passwords hashed using bcrypt via `passlib.context.CryptContext`.
* Access tokens signed using symmetric HMAC-SHA256 with 24-hour expiration.

## 2. Secrets Management & Redaction
* Structured logger sanitizes keys matching `password`, `secret`, `token`, `api_key`, `authorization`.
* Frontend environment variables are restricted strictly to `VITE_` public identifiers.

## 3. Tool Execution Sandboxing
* Intelligence probes run within isolated timeouts and restricted network operations.
* Arbitrary shell commands are completely prohibited; only strictly validated parameters reach provider adapters.
* Input queries are validated by `TargetClassifier` to prevent command injection and SSRF.
