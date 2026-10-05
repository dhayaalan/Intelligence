# Environment Configuration

Sential uses separate environment configurations for backend and frontend.

## Backend Variables (`backend/.env`)

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `APP_ENV` | `development` | Deployment environment mode |
| `SECRET_KEY` | *(Secret)* | 256-bit symmetric key for signing JWTs |
| `DATABASE_URL` | `sqlite:///./sential.db` | Primary transactional database URI |
| `REDIS_URL` | `redis://localhost:6379/0` | Async cache and job queue connection |
| `SEARCH_JOB_TIMEOUT_SECONDS` | `30` | Timeout before an isolated module job is cancelled |
| `PROVIDER_TIMEOUT_SECONDS` | `10` | Timeout for individual network provider requests |
| `SHODAN_API_KEY` | `""` | Optional Shodan API enrichment key |
| `SPIDERFOOT_URL` | `http://localhost:5001` | Optional SpiderFoot server URL |
| `ZAP_API_ENDPOINT` | `http://localhost:8080` | Optional OWASP ZAP scanner daemon |

## Frontend Variables (`frontend/.env`)

Only safe public variables with the `VITE_` prefix are permitted:

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `VITE_API_URL` | `http://localhost:8000/api/v1` | Public API endpoint for client requests |
