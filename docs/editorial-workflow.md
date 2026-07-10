# Editorial workflow

Brief APAC is designed around a repeatable weekday loop. The MVP hypothesis: a credible APAC issue should take **under 45 minutes** end to end.

## Daily loop

```text
ingest → draft → review → publish → (optional) serve / email
```

| Step | Command | Target time | Who |
|------|---------|-------------|-----|
| Ingest + draft | `brief ingest` then `brief draft` | 2–5 min | Automated |
| Human review | `brief review` | 20–30 min | Editor |
| Publish | `brief publish` | < 1 min | Automated |
| Public sync | `brief sync-public` | < 1 min | If needed |

## Story lifecycle

Stories move through these states in SQLite:

| Status | Meaning |
|--------|---------|
| `candidate` | Ingested and scored; awaiting draft |
| `drafted` | Summary and “Why it matters” generated |
| `approved` | Editor-approved for the next issue |
| `rejected` | Excluded from publication |
| `published` | Included in a shipped issue |

## Editorial principles

1. **APAC lens first** — prefer stories that matter in regional context, not only because a US company announced something.
2. **Score threshold** — stories below `min_apac_score` (default `0.35`) are filtered at ingest.
3. **Issue size** — default eight stories per issue (`stories_per_issue` in `config/edition.yaml`).
4. **Why it matters** — every story carries a regional relevance line; required on regional editions, encouraged everywhere.
5. **Source attribution** — published issues link to original articles; summaries stay short and factual.

## Review UI checklist

For each drafted story, confirm:

- [ ] Headline accurately reflects the source
- [ ] Summary is neutral and concise (two sentences where possible)
- [ ] “Why it matters” is specific to APAC readers
- [ ] Category is correct
- [ ] Read time is reasonable

## Output artefacts

After `brief publish`, one directory per issue date contains all publish formats. The public site reads `issue.json`; run `brief sync-public` to rebuild JSON from the database if needed.

## Not in scope (MVP)

- Email delivery (Postmark, Buttondown, etc.)
- Subscriber management
- Sponsor slots
- Multi-editor authentication

These follow once the editorial loop feels sustainable.
