# Public site

The reader-facing website is served by `brief serve` (default http://127.0.0.1:8080).

## Routes

| Path | Description |
|------|-------------|
| `/` | Homepage — featured issue and top stories |
| `/issues` | Archive of published issues and sample preview |
| `/issues/{date}` | Full issue (e.g. `/issues/2026-07-06`) |
| `/issues/sample` | Placeholder preview issue |
| `/accessibility` | Accessibility information |
| `/feed.xml` | RSS feed |
| `/health` | Health check JSON |

## Data sources

The public site reads:

1. **Published issues** — `output/apac-tech/{date}/issue.json` (created by `brief publish`)
2. **Sample preview** — `content/placeholder/issue.json`

Run `brief sync-public` to rebuild `issue.json` from published stories in the database.

## Design and accessibility

- **Responsive layout** — phone, tablet, and desktop breakpoints
- **Atkinson Hyperlegible** — dyslexia- and low-vision-friendly typeface (not a generic system UI font)
- **Skip link**, semantic landmarks, visible focus rings
- **Reduced motion** and **dark mode** via system preferences
- **Keyboard navigation** and screen-reader labels on external links

See also the live page at `/accessibility` when the server is running.

## Sample content

The sample issue is clearly labelled **Sample issue — placeholder content**. Stories do not link externally; they demonstrate format and APAC editorial tone for demos.

## Static assets

| Path | Purpose |
|------|---------|
| `brief/static/public/css/site.css` | Styles |
| `brief/static/public/js/site.js` | Mobile navigation toggle |
| `brief/templates/public/*.j2` | Jinja2 page templates |

## Production deployment (future)

The MVP serves via Uvicorn locally. For production, place a reverse proxy (nginx, Caddy) in front of Uvicorn or export static issue pages — not yet automated in this repo.
