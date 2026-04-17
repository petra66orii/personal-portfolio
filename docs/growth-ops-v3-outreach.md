# Growth Ops V3 Outreach

## Purpose

Growth Ops V3 adds a deterministic outreach layer on top of V1 ingestion and V2 report/score outputs.

V3 converts:

```text
Lead + Report + Score -> Outreach Decision -> Outbound Draft
```

V3.5 extends this with contact enrichment and operational readiness:

```text
Draft -> Contact Discovery -> Contact Upsert -> Readiness Classification -> Queue
```

## Scope

V3/V3.5 includes:

- deterministic outreach opportunity classification
- deterministic email subject/body generation
- outbound draft create/reuse logic
- homepage/contact-route extraction for emails, phones, and action links
- `Contact` upsert/reuse from extracted website routes
- readiness status metadata for human review
- queue command for ready/pending draft inspection

## Out of Scope

V3/V3.5 does **not** include:

- automatic email sending
- autonomous sequencing/scheduling execution
- LLM-based draft generation in this deterministic path
- background workers/Celery

## Key Modules

- `growth_ops/services/outreach_engine.py`
- `growth_ops/services/email_builder.py`
- `growth_ops/services/drafting.py`
- `growth_ops/services/contact_finder.py`
- `growth_ops/services/contact_enrichment.py`
- `growth_ops/services/outreach_readiness.py`
- `growth_ops/services/scoring_pipeline.py` (`run_outreach_for_lead`)
- `growth_ops/management/commands/run_growth_v3.py`
- `growth_ops/management/commands/run_outreach_queue.py`

## V3 Decision Layer

`classify_outreach_opportunity(...)` evaluates report/score data and returns:

- `should_contact`
- `priority` (`high` / `medium` / `low`)
- `offer_type`
- `angle`
- `reason_summary`

Current score-based contact thresholds:

- `score >= 60` -> contact, `high`
- `45 <= score <= 59` -> contact, `medium`
- `score < 45` -> skip, `low`

## Deterministic Email Builder

`build_outreach_email(...)` selects one primary issue and generates a concise outreach email without LLM calls.

Issue selection order:

1. weak/missing CTA
2. no contact method
3. poor performance
4. weak trust / no HTTPS
5. SEO issues
6. fallback general issue

The email references one issue and one business impact only.

## Draft Persistence and Dedupe

`upsert_outbound_draft(...)` creates or reuses `OutboundDraft`.

Reuse criteria:

- same lead
- same decision key (`offer_type`, `angle`, `priority`)
- same subject/body

If a matching draft exists and `--force` is not set, it is reused.

## V3.5 Contact Discovery and Readiness

`run_outreach_for_lead(...)` performs enrichment after draft create/reuse:

1. load latest `homepage_html_snippet`
2. extract contact candidates from homepage HTML
3. optionally fetch up to 2 ranked action/contact links
4. upsert `Contact` records
5. classify readiness
6. store diagnostics in `draft.evidence_check`

### Contact routes supported

- email (`mailto` + visible text extraction)
- phone (`tel` + visible phone patterns)
- action/contact links:
  - `contact`
  - `get-in-touch`
  - `enquire` / `inquiry`
  - `free-trial` / `trial`
  - `join`
  - `sign-up` / `signup`
  - `membership`
  - `locations`
  - `clubs`
  - `find-us`

### Readiness logic

`classify_draft_readiness(...)` sets:

- `status`: `ready` or `pending`
- `reason`
- `contactability_type`: `email` | `phone` | `contact_link` | `none`

`ready` when at least one usable route exists:

- email, or
- phone, or
- selected contact/action link

## Metadata Storage

Draft diagnostics are written to `OutboundDraft.evidence_check`, including:

- `extracted_emails`
- `extracted_phones`
- `contact_links`
- `selected_email`
- `selected_phone`
- `selected_contact_link`
- `readiness_status`
- `readiness_reason`
- `contactability_type`
- nested `v35_contacts`, `v35_readiness`, `v35_diagnostics`

## Commands

Generate/reuse outreach drafts:

```bash
docker compose exec web python manage.py run_growth_v3 --limit 20
docker compose exec web python manage.py run_growth_v3 --lead-id 8
docker compose exec web python manage.py run_growth_v3 --lead-id 8 --force
```

Review queue:

```bash
docker compose exec web python manage.py run_outreach_queue --limit 20
docker compose exec web python manage.py run_outreach_queue --priority high --limit 20
docker compose exec web python manage.py run_outreach_queue --include-pending --limit 20
```

## Idempotency and Safety

- reruns reuse drafts when decision/content is unchanged
- reruns reuse contacts based on lead/email or lead/phone flow
- no automatic send side effects in V3/V3.5 commands
- per-lead failures are isolated (pipeline continues)

