# Growth Ops V1 Ingestion

## Purpose

Growth Ops V1 replaces the previous n8n-heavy lead discovery and evidence ingestion flow with a Django-native pipeline that runs inside this repo and writes directly to existing `growth_ops` models.

## Scope

V1 includes:

- Google Places discovery
- lead normalization
- lead upsert
- homepage fetch
- `robots.txt` fetch
- `sitemap.xml` fetch
- evidence persistence
- evidence dedupe

## Out of Scope

V1 does **not** include:

- report generation
- scoring
- outreach draft generation
- sequencing
- Celery/background workers

## Architecture Overview

Execution flow:

1. `run_growth_pipeline` management command starts the run.
2. `google_places` service discovers place candidates and normalizes candidate fields.
3. `lead_ingest` service upserts each candidate into `Lead` using deterministic matching rules.
4. `evidence_fetcher` service fetches:
   - homepage HTML
   - `robots.txt`
   - `sitemap.xml`
5. `evidence_ingest` service persists evidence into `WebsiteEvidence` with dedupe.
6. Data is stored in existing models:
   - `Lead`
   - `WebsiteEvidence`

No internal HTTP loopback is used (the command does not call this app’s own `/api/growth/...` endpoints).

## V1 Files Involved

- `growth_ops/management/commands/run_growth_pipeline.py`
- `growth_ops/services/google_places.py`
- `growth_ops/services/lead_ingest.py`
- `growth_ops/services/evidence_fetcher.py`
- `growth_ops/services/evidence_ingest.py`
- `growth_ops/views.py` (refactored to consume extracted services for API compatibility)

## Command Usage

Example:

```bash
docker compose exec web python manage.py run_growth_pipeline --keyword "gym" --location "Galway" --limit 3
```

High-level behavior:

- continues processing on per-lead failures
- skips candidates without website
- prints per-lead progress and final counters

## Environment / Configuration

Canonical Google Places environment variable for V1:

- `GOOGLE_PLACES_KEY`

This key must be configured in runtime environment before running the command.

## V1 Evidence Types

Fetch-based evidence persisted in V1:

- `homepage_html_snippet`
- `robots_txt`
- `sitemap_xml`

## Dedupe Behavior

### Lead dedupe

Lead matching order:

1. `google_place_id`
2. normalized `website_url`
3. `company_name` (plus optional `location`)

### Evidence dedupe

Evidence matching always includes:

- `lead`
- `evidence_type`
- normalized `url`
- `tool`

For fetch-based evidence types (`homepage_html_snippet`, `robots_txt`, `sitemap_xml`), payload dedupe uses canonicalized comparison payloads (stable fields/body normalization) to avoid false misses caused by volatile fetch output.

Important: full original payload is still stored unchanged in `WebsiteEvidence.payload`; canonicalization is used only for duplicate comparison.

## Validation Note

Verified rerun outcome for V1 fetch ingestion:

- `evidence_created: 0`
- `evidence_reused: 9`
