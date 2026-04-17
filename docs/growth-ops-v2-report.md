# 📄 Growth Ops V2 — Documentation (Production-Ready)

## 1. Purpose

V2 converts **raw website evidence into actionable intelligence**:

```text
Evidence → Report → Score → Qualified Lead
```

It is:

- deterministic (no LLM dependency)
- idempotent (safe to rerun)
- reusable (no duplicate reports/scores)
- status-driven (pipeline-safe)

---

## 2. Pipeline Overview

### Input

Leads with:

```text
status = "evidence_collected"
```

### Flow

```text
WebsiteEvidence (V1)
    ↓
build_report_payload()   → WebsiteReport
    ↓
compute_lead_score()     → LeadScore
    ↓
Lead.status = "scored"
```

---

## 3. Components

### 📁 `services/reporting.py`

Responsible for report generation + persistence.

#### Core functions

##### `get_latest_evidence_for_lead(lead)`

- fetches most recent evidence per type
- ensures consistent input set

---

##### `build_report_payload(evidence)`

Deterministic analysis of:

- homepage HTML
- robots.txt
- sitemap.xml

Produces:

```json
{
  "summary": "...",
  "findings": [...],
  "cta_clarity": {...},
  "seo": {...},
  "technical": {...},
  "performance": {...}
}
```

---

##### `upsert_report(...)`

Handles dedupe + persistence.

### Reuse rule:

Report is reused if:

```text
same lead
same model
same prompt_version
same canonical payload
same evidence_ids
```

Returns:

- existing report (reused)
- or new report (created)

---

### 📁 `services/scoring_pipeline.py`

Responsible for scoring + orchestration.

#### Core functions

##### `run_report_and_score_for_lead(lead, force=False)`

Executes:

1. build or reuse report
2. compute score
3. persist score
4. update lead status

---

##### `compute_lead_score(...)` (existing)

Uses:

- report findings
- evidence signals

Outputs:

```text
score (0–100)
bucket (A/B/C)
reason_codes
recommendation
```

---

##### `upsert_lead_score(...)`

Reuse rule:
Score is reused if:

```text
same lead
same score value
same reason_codes
same recommendation
```

---

## 4. Management Command

### 📁 `management/commands/run_growth_v2.py`

---

### Default behaviour

```bash
python manage.py run_growth_v2
```

Processes:

```text
Lead.objects.filter(status="evidence_collected")
```

---

### Options

#### `--limit`

```bash
--limit 10
```

Limits number of leads processed.

---

#### `--lead-id`

```bash
--lead-id 5
```

Processes a single lead (ignores bulk selection).

---

#### `--force`

```bash
--force
```

Forces:

- new report creation
- new score creation

Bypasses reuse logic.

---

## 5. Status Transitions

```text
NEW
  ↓
EVIDENCE_COLLECTED  (V1 complete)
  ↓
REPORTED            (report created)
  ↓
SCORED              (score created)
```

V2 ensures:

- no regression in status
- no reprocessing unless forced

---

## 6. Idempotency Guarantees

### Without `--force`

Running V2 repeatedly:

```text
reports_created = 0
reports_reused  = N
scores_created  = 0
scores_reused   = N
```

No duplicates are created.

---

### With `--force`

```text
reports_created = N
scores_created  = N
```

Used for:

- testing
- model updates
- rule changes

---

## 7. Data Models Used

### `WebsiteEvidence`

- input from V1
- deduplicated via canonical payload

---

### `WebsiteReport`

Fields:

- `lead`
- `model` → `"rules_v1"`
- `prompt_version` → `"growth_report_v2_rules_1"`
- `evidence_ids`
- `report` (JSON)
- `summary`

---

### `LeadScore`

Fields:

- `lead`
- `score`
- `bucket`
- `reason_codes`
- `recommendation`

---

## 8. Deterministic Design

V2 intentionally avoids LLMs.

### Why:

- predictable outputs
- no API cost
- easy debugging
- perfect dedupe capability
- stable scoring baseline

---

## 9. Known Limitations (V2)

### 1. Signal depth is limited

Currently relies on:

- basic HTML inspection
- sitemap/robots presence
- CTA heuristics

---

### 2. Low differentiation

Many leads may produce similar scores due to:

- limited evidence types
- conservative scoring rules

---

### 3. No performance data yet

Unless PageSpeed/Lighthouse is added in V1.

---

## 10. Extension Points (V3+)

### Report improvements

- richer CTA detection
- content depth scoring
- contact extraction
- trust signals

---

### Evidence expansion

- PageSpeed / Lighthouse
- tech fingerprint
- structured metadata extraction

---

### Scoring upgrades

- configurable weights
- industry-specific scoring
- revenue potential estimation

---

### Downstream (V3)

- outbound draft generation
- sequencing
- reply tracking

---

## 11. Example Run

```bash
python manage.py run_growth_v2 --limit 10
```

Output:

```text
[1/3] lead_id=5: report_id=12 (created), score_id=12 (created)

reports_created: 3
reports_reused: 0
scores_created: 3
scores_reused: 0
```

Second run:

```text
reports_created: 0
reports_reused: 3
scores_created: 0
scores_reused: 3
```
