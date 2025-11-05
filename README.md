# mwebsitepr.com

Modern portfolio site for showcasing MWebsite projects, delivered as a static front end served by nginx with a FastAPI backend that powers contact handling and interactive demos. 

## Project Highlights
- Static HTML/CSS frontend with ScrollMagic-driven animations and Bootstrap assets.
- Python backend exposes contact email workflow plus script-based experiences via WebSockets.
- Fully containerized stack: nginx for static delivery and reverse proxying, FastAPI for dynamic features.

## Directory Layout
- `index.html`, `style.css`, `subworks.css`: main landing page and shared styling.
- `scrollmagic/`, `scrollmagicAnimations.js`: animation helpers and ScrollMagic configuration.
- `assets/`: images, SVGs, and other media referenced by the site.
- `python-backend/app/main.py`: FastAPI application entrypoint; `python-backend/scripts/` contains CLI demos surfaced through the API.
- `nginx/default.conf`: nginx reverse proxy configuration used inside the container images.

## Prerequisites
- Docker 24+ with Compose v2 (`docker compose`).
- Optional: Python 3.11+ and `uvicorn` for local backend-only development.
- SMTP credentials for sending contact emails.

## Getting Started
```bash
# build images locally
docker build -t mwebsite-image:latest .
docker build -t mwebsite-backend:latest python-backend

# run the stack (site on :9005, API on :9006)
docker compose up --build
```
Use `docker compose up -d` to run in the background. During backend development you can run `uvicorn app.main:app --reload --port 8000` from `python-backend/` to enable hot reloads.

## Environment Variables
Configure email delivery via environment variables or a `.env` file consumed by Compose:
- `ALLOWED_ORIGINS`: comma-separated list of origins the API should trust.
- `CONTACT_EMAIL_TO`: destination address list for contact form submissions.
- `CONTACT_EMAIL_FROM`: sender/from address (defaults to username or first recipient).
- `CONTACT_EMAIL_SUBJECT_PREFIX`: optional subject prefix (default `[Portfolio Contact]`).
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`: SMTP connection details.
- `SMTP_USE_TLS` / `SMTP_USE_SSL`: toggle secure transport.

Example `.env` excerpt (never commit secrets):
```
ALLOWED_ORIGINS=https://example.com
CONTACT_EMAIL_TO=owner@example.com
CONTACT_EMAIL_FROM=owner@example.com
SMTP_HOST=smtp.exampl.com
SMTP_PORT=587
SMTP_USERNAME=owner@example.com
SMTP_PASSWORD=change-me
SMTP_USE_TLS=true
```

## Testing
Add `pytest` suites under `python-backend/tests/` following module naming (e.g., `test_main.py`) and run:
```bash
cd python-backend
pytest --cov=app
```
Mock outbound SMTP and subprocess calls so tests remain deterministic and do not trigger external services.


