# Australia and New Zealand RSS sources

This catalogue lists ANZ-focused feeds for Brief APAC. Outlets are grouped by **tier**: **mvp** (enabled in `config/sources.yaml`), **validate** (candidate URLs to confirm before enabling), and **defer** (not suitable for unattended MVP ingest).

Global and broader APAC sources remain in the main feed list — see [Configuration](configuration.md).

## MVP feeds (enabled)

These feeds returned valid RSS during research and are configured for ingest.

### New Zealand

| Outlet | Feed URL | `countries` | `region_boost` | `default_category` | Notes |
|--------|----------|-------------|----------------|-------------------|-------|
| **Reseller News** | https://www.reseller.co.nz/feed | NZ | 0.30 | startups | NZ channel; strong A/NZ partner and vendor coverage |
| **BusinessDesk** | https://businessdesk.co.nz/feed | NZ | 0.25 | startups | NZ business and startup raises; broader than pure tech |
| **Computerworld NZ** | https://www.computerworld.com/nz/feed | NZ | 0.12 | engineering | Enterprise IT; mixed global syndication — low boost filters noise |
| **iTnews NZ** | https://www.itnews.com.au/RSS/rss-nz.ashx | NZ | 0.30 | engineering | nextmedia NZ edition; shares publisher with IT News AU |

### Australia

| Outlet | Feed URL | `countries` | `region_boost` | `default_category` | Notes |
|--------|----------|-------------|----------------|-------------------|-------|
| **ARN** | https://www.arnnet.com.au/feed | ANZ | 0.25 | startups | AU/NZ channel partners, AI, enterprise |
| **techpartner.news** | https://www.techpartner.news/rss/rss.ashx | AU | 0.20 | engineering | AU MSP/channel, cyber, government IT |
| **Startup Daily** | https://startupdaily.net/feed | ANZ | 0.28 | startups | AU/NZ startup ecosystem |
| **IT News Australia** | https://www.itnews.com.au/RSS/rss.ashx | AU | 0.20 | engineering | Verified working; nextmedia AU edition |

## Validate before enabling

Run `brief feeds check` on candidate URLs before adding them to `config/sources.yaml`.

| Outlet | Candidate URL | Issue |
|--------|---------------|-------|
| **NZ Herald Technology** | Section RSS from [NZ Herald RSS page](https://www.nzherald.co.nz/technology/nz-herald-news-rss-feeds/SOA2EBUD5L72DYXMP3A267XOKI/) | Landing page works; direct XML URL not confirmed |
| **iTnews NZ** | `https://www.itnews.com.au/RSS/rss-nz.ashx` | Intermittent 404 from some HTTP clients; confirm via `brief feeds check` |
| **iTnews category feeds** | Listed on [itnews.com.au/rss](https://www.itnews.com.au/rss) | Security/cloud URLs need per-category discovery |

## Deferred (not MVP)

| Outlet | Reason |
|--------|--------|
| **Scoop SciTech** | Feeds via [Newsagent](https://www.scoop.co.nz/about/rss.html); commercial/licensed syndication — not suitable for unattended MVP ingest |
| **InnovationAus** | `https://www.innovationaus.com/feed/` returned HTTP 500 |
| **CRN Australia** (`crn.com.au`) | No equivalent public RSS to US CRN feeds |
| **Information Age (ACS)** | No working public RSS at tested paths |
| **ZDNet** | Global feed, not ANZ-specific; adds US noise without regional lens |

## Licensing and syndication

- **Scoop** content is syndicated through Newsagent; do not ingest without a licence.
- **NZ Herald** RSS terms may restrict commercial reuse — confirm before enabling.
- MVP feeds listed above are publicly accessible RSS endpoints used for headline and excerpt aggregation only; always respect each outlet's terms of use.

## Overlap guidance for editors

1. **nextmedia family** — IT News AU, iTnews NZ, and techpartner.news share a publisher. URL dedupe prevents duplicate database rows, but the review queue may still feel repetitive. Monitor overlap after the first ingest; consider lowering `max_per_source` for techpartner.news (e.g. 8 vs 15) if needed.
2. **Computerworld NZ** — High share of global stories. Low `region_boost` (0.12) plus keyword scoring should filter most non-ANZ items.
3. **BusinessDesk** — Broader business coverage (energy, markets). Stories without tech keywords typically score below `min_apac_score` naturally.
4. **Startup Daily** — Strong ANZ startup signal; occasional politics or social stories — category guesser and editor review handle miscategorisation.

## Adding a new feed

1. Find a stable RSS or Atom URL and confirm it returns entries (not an HTML landing page).
2. Run `brief feeds check` — the candidate URL can be added temporarily to `config/sources.yaml` or tested in isolation.
3. Add an entry to `config/sources.yaml` with `region: APAC`, `countries`, `tier`, `region_boost`, and `default_category`.
4. Run `brief feeds check` on the full list, then `brief ingest` and `brief status`.
5. Update this catalogue if the feed is promoted to **mvp** or moved to **validate** / **defer**.

Optional YAML fields (`countries`, `tier`, `notes`) are ignored by ingest if absent; they document intent and support future per-country filtering.
