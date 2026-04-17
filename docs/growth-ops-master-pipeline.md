# Growth Ops Master Pipeline

## Purpose

This document describes the complete deterministic Growth Ops pipeline in this repo, from lead discovery to outreach-ready draft queue.

Pipeline stages:

```text
V1 Ingestion -> V2 Report + Score -> V3 Outreach Drafting -> V3.5 Contact Readiness + Queue
```

## Stage Summary

| Stage | Input | Output | Primary Command |
| --- | --- | --- | --- |
| V1 | keyword/location query | `Lead`, `WebsiteEvidence` | `run_growth_pipeline` |
| V2 | leads with evidence | `WebsiteReport`, `LeadScore` | `run_growth_v2` |
| V3 | scored + reported leads | `OutboundDraft` | `run_growth_v3` |
| V3.5 | outbound drafts | readiness metadata + contact routes + queue view | `run_outreach_queue` |

## Architecture Map

```text
Google Places
  -> lead_ingest
  -> evidence_fetcher
  -> evidence_ingest
  -> reporting
  -> scoring
  -> outreach_engine
  -> email_builder
  -> drafting
  -> contact_finder/contact_enrichment
  -> outreach_readiness
  -> queue command
```

No internal loopback to `/api/growth/...` is used for the management command pipeline.

## Data Models Used

- `Lead`
- `Contact`
- `WebsiteEvidence`
- `WebsiteReport`
- `LeadScore`
- `OutboundDraft`
- `OutboundSend` (send workflow exists separately, not part of this deterministic generation path)

## V1: Ingestion

### What it does

- discovers candidates via Google Places
- normalizes and upserts leads
- fetches website evidence
- persists evidence with dedupe

### Evidence types currently used

- `homepage_html_snippet`
- `robots_txt`
- `sitemap_xml`
- `pagespeed_json`

### Command

```bash
docker compose exec web python manage.py run_growth_pipeline --keyword "gym" --location "Galway" --limit 10
```

## V2: Report + Score

### What it does

- builds deterministic report payload from evidence
- persists/reuses `WebsiteReport`
- computes and persists/reuses `LeadScore`

### Command

```bash
docker compose exec web python manage.py run_growth_v2 --limit 20
docker compose exec web python manage.py run_growth_v2 --lead-id 7
docker compose exec web python manage.py run_growth_v2 --lead-id 7 --force
```

## V3: Deterministic Outreach Drafting

### What it does

- classifies outreach opportunity from report + score
- generates deterministic single-issue email
- creates or reuses `OutboundDraft`

### Command

```bash
docker compose exec web python manage.py run_growth_v3 --limit 20
docker compose exec web python manage.py run_growth_v3 --lead-id 8
docker compose exec web python manage.py run_growth_v3 --lead-id 8 --force
```

## V3.5: Contact Enrichment + Readiness + Queue

### What it does

- extracts emails/phones/action links from homepage evidence
- optionally fetches up to 2 ranked action/contact pages
- upserts contacts into `Contact`
- classifies draft readiness (`ready`/`pending`)
- exposes deterministic review queue output

### Readiness rule (current)

`ready` if at least one exists:

- selected email
- selected phone
- selected contact/action link

Otherwise `pending`.

### Queue command

```bash
docker compose exec web python manage.py run_outreach_queue --limit 20
docker compose exec web python manage.py run_outreach_queue --priority high --limit 20
docker compose exec web python manage.py run_outreach_queue --include-pending --limit 20
```

## Idempotency and Reuse Guarantees

### Lead dedupe

Matching order:

1. `google_place_id`
2. normalized `website_url`
3. `company_name` (+ optional location)

### Evidence dedupe

Matching includes:

- `lead`
- `evidence_type`
- normalized URL
- `tool`
- canonicalized payload comparison for fetch-based evidence types

Original payload is still stored unchanged.

### Report dedupe

Reuses report when lead/model/prompt/evidence IDs/payload match.

### Score dedupe

Reuses score when score/bucket/reason codes/recommendation match.

### Draft dedupe

Reuses draft when decision key + subject/body match.

### Contact dedupe

Upserts contacts by lead/email or lead/phone routes, reusing existing rows where possible.

## Status Progression (High Level)

Typical progression:

```text
new -> evidence_collected -> reported -> scored -> draft_pending
```

Actual statuses are persisted by each stage service and command.

## Environment Configuration

Canonical keys currently used in this pipeline:

- `GOOGLE_PLACES_KEY`
- `PAGESPEED_API_KEY`

Operational keys for API/auth/send paths are configured separately in backend settings and deployment environment.

## Operational Runbook

Recommended deterministic run order:

1. Run V1 ingestion for target market segment.
2. Run V2 report/score on collected leads.
3. Run V3 draft generation on scored leads.
4. Run queue command and review `ready` drafts first.

## Linked Stage Docs

- [Growth Ops V1 Ingestion](growth-ops-v1-ingestion.md)
- [Growth Ops V2 Report](growth-ops-v2-report.md)
- [Growth Ops V3 Outreach](growth-ops-v3-outreach.md)

