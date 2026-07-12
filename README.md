# Brief APAC

A workflow MVP for a TLDR-style tech briefing focused on the **Asia-Pacific** region — built and documented in **New Zealand English (en-NZ)**.

Brief APAC proves that a credible weekday issue can be produced in under 45 minutes: ingest regional sources, draft summaries, review in a browser, and publish to the web, email, and RSS.

## What it does

1. **Ingest** APAC-weighted RSS sources
2. **Score** regional relevance
3. **Draft** summaries (extractive by default, optional OpenAI)
4. **Review** in a local editor UI
5. **Publish** markdown, HTML, email HTML, RSS, and public `issue.json`

## Quick start

```bash
cd brief-apac
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -e ".[dev]"
brief init
brief ingest
brief draft --no-llm

# Terminal 1 — API
brief review --no-https

# Terminal 2 — review UI (first time: cd web && npm install)
cd web && npm run dev:review
```

Open http://localhost:5173, approve eight stories, then:

```bash
brief publish
cd web && npm run dev:public
```

- **Review UI:** http://localhost:5173 (Vite + React)  
- **API:** http://127.0.0.1:8787  
- **Public site:** http://localhost:8080 (Next.js)  
- **Published files:** `output/apac-tech/YYYY-MM-DD/`

## Documentation

| Guide | Description |
|-------|-------------|
| [Getting started](docs/getting-started.md) | Installation, first issue, daily commands |
| [Editorial workflow](docs/editorial-workflow.md) | Ingest → review → publish loop |
| [Configuration](docs/configuration.md) | Feeds, scoring, edition settings |
| [ANZ sources](docs/sources-anz.md) | Australia and New Zealand RSS catalogue |
| [Public site](docs/public-site.md) | Reader-facing website and accessibility |
| [Localisation](docs/localisation.md) | en-NZ conventions for this project |

## CLI reference

| Command | Purpose |
|---------|---------|
| `brief init` | Create the database (SQLite or Supabase) |
| `brief feeds check` | Validate RSS feeds in `config/sources.yaml` (no DB writes) |
| `brief ingest` | Pull RSS feeds from `config/sources.yaml` |
| `brief draft` | Draft summaries for top candidates |
| `brief draft --no-llm` | Extractive summaries only (no API key) |
| `brief review` | Start the REST API for the review UI (port 8787) |
| `brief publish` | Publish approved stories to `output/` |
| `brief serve` | Run the Next.js public site (port 8080) |
| `brief sync-public` | Rebuild `issue.json` for published issues |
| `brief status` | Show queue counts by status |

## Project layout

```
brief-apac/
  brief/            Python package (CLI, ingest, publish, API)
  web/
    review/         Vite + React review UI (TypeScript)
    public/         Next.js public site (TypeScript)
  supabase/         PostgreSQL migrations for dev/prod
  config/           Edition and RSS source configuration
  content/          Placeholder public content
  tests/            Pytest suite (scoring, drafting, repository, API)
  docs/             Project documentation (en-NZ)
  data/             SQLite database (gitignored, default backend)
  output/           Published issues (gitignored)
```

## Tooling

Production dependencies are pinned in `requirements.txt`. Dev tooling (pytest, ruff) in `requirements-dev.txt`.

Run the checks:

```bash
python -m pytest
python -m ruff check brief tests
```

| Package | Version |
|---------|---------|
| FastAPI | 0.139.0 |
| Uvicorn | 0.50.0 |
| Typer | 0.26.8 |
| Rich | 15.0.0 |
| HTTPX | 0.28.1 |
| Jinja2 | 3.1.6 |

## Licence

Documentation and sample content use New Zealand English spelling. See [docs/localisation.md](docs/localisation.md) for conventions.
