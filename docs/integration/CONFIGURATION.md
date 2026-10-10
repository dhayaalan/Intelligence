# Configuration Guide: Social Media Intelligence & AI Agents

## 1. Overview

This document specifies all configuration keys, environment variables, feature flags, and deployment prerequisites for the newly integrated social-media intelligence modules and AI agents.

All settings have safe defaults allowing immediate local execution without external paid APIs.

---

## 2. Environment Variables

Add or modify these variables in `backend/.env` (or Kubernetes ConfigMap/Secret):

```bash
# ==============================================================================
# SOCIAL MEDIA INTELLIGENCE SETTINGS
# ==============================================================================
# Master toggle for social media intelligence module
ENABLE_SOCIAL_MEDIA_INTELLIGENCE=true

# Request timeouts for external collectors (in seconds)
SOCIAL_COLLECTOR_TIMEOUT=10.0

# Platform-specific toggles
ENABLE_BLUESKY_COLLECTOR=true
ENABLE_TELEGRAM_COLLECTOR=true
ENABLE_REDDIT_COLLECTOR=true
ENABLE_MASTODON_COLLECTOR=true
ENABLE_YOUTUBE_COLLECTOR=true

# Optional: Custom Mastodon instance URL (default: https://mastodon.social)
MASTODON_INSTANCE_URL=https://mastodon.social

# Optional: Reddit API Credentials (if high-throughput OAuth is required)
# If omitted, polite public JSON search is used
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=Intelligence-OSINT/2.0

# Optional: YouTube Data API Key (if higher quota than oEmbed/timedtext is needed)
YOUTUBE_API_KEY=

# ==============================================================================
# AI AGENTS & LLM SETTINGS
# ==============================================================================
# Master toggle for AI agent orchestration
ENABLE_AI_AGENTS=true

# Default LLM Provider: 'heuristic' | 'openai' | 'anthropic' | 'ollama'
AI_AGENT_PROVIDER=heuristic

# OpenAI Configuration (Optional)
OPENAI_API_KEY=
OPENAI_MODEL_NAME=gpt-4o-mini

# Anthropic Configuration (Optional)
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL_NAME=claude-3-5-sonnet-20241022

# Local Ollama Configuration (Optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_NAME=llama3.2
```

---

## 3. Frontend Configuration

In `frontend/.env`:

```bash
# Backend API Base URL
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 4. Verification Commands

To verify active configuration:

1. **Check Module Manifest & Health**:
   ```bash
   curl -s http://localhost:8000/api/v1/modules | jq .
   ```
   Confirm `social_media_intelligence` is listed under active modules.

2. **Test Social Search Endpoint**:
   ```bash
   curl -s -X POST http://localhost:8000/api/v1/social/search \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <TOKEN>" \
     -d '{"query": "cybersecurity", "platforms": ["bluesky"], "limit": 5}' | jq .
   ```

3. **Test AI Agents Endpoint**:
   ```bash
   curl -s -X POST http://localhost:8000/api/v1/agents/grounded-analysis \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <TOKEN>" \
     -d '{"target": "Test Campaign", "query": "Summarize threats"}' | jq .
   ```
