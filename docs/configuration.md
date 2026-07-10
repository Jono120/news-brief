# Configuration

Brief APAC is configured through YAML files in `config/`. Technical keys and enum slugs stay in English; human-facing labels use clear English prose.

## Edition settings

File: `config/edition.yaml`

| Key | Default | Description |
|-----|---------|-------------|
| `edition.slug` | `apac-tech` | URL and output directory slug |
| `edition.name` | `Brief APAC` | Display name |
| `edition.tagline` | `Keep up with APAC tech in 5 minutes` | Site and issue headline |
| `edition.timezone` | `Pacific/Auckland` | Edition timezone |
| `edition.send_time_local` | `07:30` | Target local send time |
| `edition.stories_per_issue` | `8` | Stories per published issue |
| `edition.min_apac_score` | `0.35` | Minimum ingest relevance score |
| `edition.min_apac_story_ratio` | `0.4` | Target share of APAC-weighted stories |

### APAC keywords

Under `scoring.apac_keywords`, add lowercase terms used to boost regional relevance — countries, cities, and abbreviations (e.g. `auckland`, `wellington`, `aotearoa` as a search term for New Zealand content).

### Categories

Each category has a `slug` (machine) and `label` (display):

```yaml
categories:
  - slug: policy
    label: "Policy & Regulation"
```

## RSS sources

File: `config/sources.yaml`

For the Australia and New Zealand catalogue (mvp / validate / defer tiers, licensing notes), see [ANZ sources](sources-anz.md).

```yaml
sources:
  - name: Example APAC Source
    url: https://example.com/rss
    region: APAC
    countries: [NZ]
    tier: mvp
    region_boost: 0.2
    default_category: startups
    notes: "Optional editor notes"
```

| Field | Description |
|-------|-------------|
| `name` | Display name in review UI and published issues |
| `url` | RSS or Atom feed URL |
| `region` | `APAC` or `GLOBAL` |
| `region_boost` | Added to keyword-based APAC score (0.0–0.3 typical) |
| `default_category` | Fallback category slug when auto-detection is uncertain |
| `countries` | Optional — `NZ`, `AU`, or `ANZ` (documentation and future filtering) |
| `tier` | Optional — `mvp`, `validate`, or `defer` (documentation only) |
| `notes` | Optional — editor guidance; ignored by ingest |

After adding or changing feeds, run `brief feeds check` then `brief ingest`.

## Environment variables

Copy `.env.example` to `.env`:

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Optional — LLM-assisted summaries |
| `OPENAI_MODEL` | Optional — defaults to `gpt-4o-mini` |

## Placeholder content

File: `content/placeholder/issue.json`

Sample stories for the public preview (`/issues/sample`). Safe to edit for demos; marked `is_sample: true` in the UI.

## Output paths

Published issues:

```text
output/{edition.slug}/{YYYY-MM-DD}/
```

Database: `data/brief.db` (gitignored).
