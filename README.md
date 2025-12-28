# whatsapp-wrapped

your whatsapp chat, analyzed. spotify wrapped but for your conversations.

## what it does

upload a whatsapp chat export → select members → get stats like:
- who texts the most
- emoji usage
- response times
- night owls & early birds
- conversation starters & killers
- personality tags & roasts
- catchphrases & signature words

## architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   frontend  │────▶│   flask     │────▶│   celery    │
│   next.js   │◀────│   api       │◀────│   worker    │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                   │
                    ┌──────┴──────┐            │
                    ▼             ▼            ▼
              ┌──────────┐  ┌──────────┐  ┌──────────┐
              │  neon    │  │  upstash │  │ cf r2    │
              │ postgres │  │  redis   │  │ storage  │
              └──────────┘  └──────────┘  └──────────┘
```

## flow

```
1. POST /api/upload        → upload file, get participants
                           ← { job_id, participants: [...] }

2. POST /api/analyze       → select members, start analysis
                           ← { job_id, status: "processing" }

3. GET /api/jobs/{id}      → poll for progress
                           ← { progress: 50, step: "analyzing emojis..." }

4. GET /api/jobs/{id}/stats → get full results
                           ← { stats: {...} }
```

**privacy:** uploaded files are deleted immediately after analysis completes.

## stack

| layer | tech |
|-------|------|
| frontend | next.js, tailwind |
| api | flask, gunicorn |
| queue | celery |
| db | neon postgres |
| cache | upstash redis |
| storage | cloudflare r2 |
| deploy | docker |


## current implementation

the backend processes a 150kb chat (~2k messages) in under 1 second. total api round-trip takes ~10s due to remote db/storage latency (neon postgres, cloudflare r2). progress updates stream via redis for real-time polling without hammering the database.

the two-step flow (upload → select members → analyze) lets users filter who appears in their wrapped before burning compute cycles. file validation ensures only whatsapp exports get through.


## local dev

```bash
# install deps
uv sync

# run flask api
cd backend && uv run flask run --port 8000

# run celery worker (separate terminal)
cd backend && uv run celery -A celery_worker.celery worker --loglevel=info

# run frontend
cd frontend && npm run dev
```

## cli

run analysis locally without the web interface:

```bash
# basic usage - analyzes chat.txt for 2025
uv run python -m cli chat.txt

# specify a different year
uv run python -m cli chat.txt --year 2025

# full output (more words, catchphrases, etc)
uv run python -m cli chat.txt --full

# ai-powered roasts (requires OPENAI_API_KEY)
uv run python -m cli chat.txt --ai-roast

# export llm context (saves to llm_context.json)
uv run python -m cli chat.txt --llm-context

# combine flags
uv run python -m cli path/to/chat.txt --year 2025 --full --ai-roast
```

| flag | description |
|------|-------------|
| `--year YYYY` | filter to specific year (default: 2025) |
| `--full` | extended output with more stats |
| `--ai-roast` | ai-generated roasts via openai (needs OPENAI_API_KEY) |
| `--llm-context` | export context to llm_context.json |

## env vars

```bash
# backend/.env
DATABASE_URL=postgresql://...
REDIS_URL=rediss://...
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=whatsapp-wrapped
OPENAI_API_KEY=sk-...  # for ai roasts
```

## api

| endpoint | method | description |
|----------|--------|-------------|
| `/api/health` | GET | health check |
| `/api/upload` | POST | upload chat, get participants |
| `/api/analyze` | POST | start analysis with selected members |
| `/api/jobs/{id}` | GET | get job status/progress |
| `/api/jobs/{id}/stats` | GET | get full results |
| `/api/jobs/{id}` | DELETE | delete job and files |

---

