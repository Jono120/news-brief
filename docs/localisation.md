# Localisation

Brief APAC documentation and user-facing prose follow **New Zealand English (en-NZ)** unless noted otherwise.

## Spelling

| Use | Avoid (US) |
|-----|------------|
| organise, organisation | organize, organization |
| colour | color |
| behaviour | behavior |
| centre | center (in prose) |
| licence (noun) | license (noun) |
| programme (general) | program — except **computer program** |
| summarise | summarize |
| labelled | labeled |
| neighbouring | neighboring |

## Māori orthography

When Te Reo terms appear in English prose, use macrons where standard:

| Avoid | Prefer |
|-------|--------|
| Maori | Māori |
| whanau | whānau |

Place names follow official spelling (e.g. **Aotearoa New Zealand** in narrative context). RSS keyword lists may use ASCII forms (`new zealand`, `nz`) for matching — that is intentional for ingestion, not display copy.

## What stays in English (unchanged)

- Code, CLI commands, file paths, environment variables
- JSON/YAML keys and category slugs (`startups`, `policy`, etc.)
- Package names, URLs, and API identifiers
- Story headlines quoted from source articles

## User-facing surfaces

| Surface | Locale |
|---------|--------|
| `docs/*.md`, root `README.md` | en-NZ |
| Public site templates (`brief/templates/public/`) | en-NZ |
| Edition tagline and site descriptions | en-NZ |
| Placeholder sample stories | en-NZ |
| Review UI | en-NZ |
| LLM draft prompt | Requests neutral English; editor may localise on review |

## Contributing copy

Before merging documentation or UI strings:

1. Spot-check for US spellings (`organize`, `color`, `center`).
2. Verify Māori macrons in any Te Reo terms.
3. Keep commands and code blocks byte-for-byte accurate.
