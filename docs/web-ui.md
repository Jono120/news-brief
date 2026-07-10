# Web UI (TypeScript)

Brief APAC ships two TypeScript frontends under `web/`:

| App | Stack | Port | Purpose |
|-----|-------|------|---------|
| `web/review` | Vite + React | 5173 | Editorial review queue |
| `web/public` | Next.js | 8080 | Reader-facing public site |

The Python API (`brief review`) powers the review UI. The public site reads published `issue.json` files from `output/`.

## Prerequisites

- Node.js 20+
- Python environment with `brief` installed

## Install

```bash
cd web
npm install
```

## Development

Terminal 1 — API (SQLite or Supabase):

```bash
brief review --no-https
```

Terminal 2 — review UI + public site:

```bash
cd web
npm run dev:review   # http://localhost:5173
# or in another terminal:
npm run dev:public   # http://localhost:8080
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8787` by default (see `web/review/.env.development`). **The proxy scheme must match how you start the API:**

| API command | Vite proxy |
|-------------|------------|
| `brief review --no-https` | `http://127.0.0.1:8787` (default) |
| `brief review` (HTTPS) | `VITE_API_PROXY=https://127.0.0.1:8787 npm run dev:review` |

A `tls_get_more_records: packet length too long` error means the proxy is using HTTPS against a plain HTTP API (or the reverse).

## Design system

Shared typography and usability tokens live in `design/`:

- **Typeface:** [Atkinson Hyperlegible](https://fonts.bunny.net/family/atkinson-hyperlegible) — chosen for readability and character distinction
- **Colour:** warm neutral palette with APAC green accent (`#0b5b49`)
- **Accessibility:** skip links, visible focus rings, 44px touch targets, `prefers-reduced-motion`, dark mode, `forced-colors` support

`design/tokens.css`, `foundation.css`, and `components.css` are imported by both web apps. Email and published HTML templates use matching values from `brief/templates/macros/design.html.j2`.


1. Create a Supabase project (or run `supabase start` locally).
2. Apply the migration in `supabase/migrations/`.
3. Configure `.env`:

```bash
BRIEF_DATABASE=supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

4. Initialise and run the pipeline:

```bash
brief init
brief ingest
brief draft --no-llm
```

SQLite remains the default when `BRIEF_DATABASE` is unset.

## Production build

```bash
cd web
npm run build
npm run start -w @brief-apac/public
```

Serve the review UI static files from `web/review/dist` behind your API or CDN.
