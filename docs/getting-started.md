# Getting started

This guide walks you through installing Brief APAC and publishing your first issue.

## Prerequisites

- **Python 3.10+**
- Network access for RSS ingestion
- Optional: `OPENAI_API_KEY` for higher-quality summaries

## Installation

```bash
cd brief-apac
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"
brief init
```

The `dev` extra installs `httpx2` for FastAPI test client compatibility.

## First run

### 1. Ingest stories

```bash
brief ingest
```

This fetches APAC-weighted RSS feeds defined in `config/sources.yaml`, scores regional relevance, and stores candidates in `data/brief.db`.

### 2. Draft summaries

```bash
brief draft --no-llm
```

Without an API key, summaries are extractive (pulled from feed excerpts). With `OPENAI_API_KEY` set in `.env`, omit `--no-llm` for drafted prose.

### 3. Review and approve

```bash
# Terminal 1 — API
brief review --no-https

# Terminal 2 — review UI
cd web && npm install && npm run dev:review
```

Open http://localhost:5173. For each drafted story you can:

- Edit the summary and **Why it matters** line
- Adjust category and read time
- **Approve** or **Reject**

Approve eight stories for a full issue (configurable in `config/edition.yaml`).

### 4. Publish

```bash
brief publish
```

Outputs are written to `output/apac-tech/YYYY-MM-DD/`:

| File | Purpose |
|------|---------|
| `issue.md` | Markdown issue |
| `issue.html` | Standalone HTML |
| `email.html` | Email-ready HTML |
| `feed.xml` | Per-issue RSS |
| `issue.json` | Public site data |

### 5. Preview the public site

```bash
cd web && npm run dev:public
```

Open http://localhost:8080. If no published issues exist yet, the **sample preview** at `/issues/sample` shows placeholder content.

If you published before `issue.json` support was added:

```bash
brief sync-public
```

## Optional: OpenAI summaries

```bash
cp .env.example .env
# Set OPENAI_API_KEY=...
brief draft
```

## Check queue status

```bash
brief status
```

## Next steps

- [Editorial workflow](editorial-workflow.md) — timing targets and editorial rules
- [Configuration](configuration.md) — add feeds and tune APAC scoring
- [Web UI](web-ui.md) — TypeScript review and public apps, Supabase dev setup
