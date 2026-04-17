# Agent Prompt Library (Miss Bott)

## Purpose

This document defines the internal prompt library used by the Miss Bott LLM gateway layer.

The prompts are designed for:

- structured interpretation
- drafting
- summarization
- safe rewriting of unsupported claims

They are **not** used to replace deterministic business logic in Growth Ops V1/V2/V3/V3.5.

## Prompt Directory

- `services/llm-gateway/app/prompts/agent_orchestrator.md`
- `services/llm-gateway/app/prompts/website_auditor.md`
- `services/llm-gateway/app/prompts/website_reporter.md`
- `services/llm-gateway/app/prompts/outreach_writer.md`
- `services/llm-gateway/app/prompts/evidence_checker.md`
- `services/llm-gateway/app/prompts/reply_triage.md`
- `services/llm-gateway/app/prompts/content_engine.md`

## Reference Sources Used

Reference-only inspiration came from local `agency-agents` role files:

- `specialized/agents-orchestrator`
- `marketing/marketing-growth-hacker`
- `marketing/marketing-content-creator`
- `support/support-analytics-reporter`
- `testing/testing-evidence-collector`
- `testing/testing-reality-checker`
- `testing/testing-workflow-optimizer`
- optional influence:
  - `design/design-brand-guardian`
  - `project-management/project-management-project-shepherd`

No runtime dependency or code import from the reference repo is used.

## Metadata Convention

Each prompt file includes required header metadata:

- `prompt_name`
- `prompt_version`
- `source_agent_reference`

This matches the gateway prompt loader contract.

## Prompt-to-Pipeline Mapping

### `agent_orchestrator.md`

Purpose:
- stage guidance and dependency interpretation for pipeline-safe orchestration decisions.

Pipeline fit:
- cross-stage interpretation aid for V1->V3.5 handoffs.

### `website_auditor.md`

Purpose:
- evidence-first audit interpretation with strict factual boundaries.

Pipeline fit:
- aligned to V1 evidence quality and normalization workflows.

### `website_reporter.md`

Purpose:
- deterministic evidence-to-report transformation guidance.

Pipeline fit:
- used by `/v1/report` style reporting in V2.

### `outreach_writer.md`

Purpose:
- deterministic, structured outbound draft writing from approved evidence/report context.

Pipeline fit:
- used by `/v1/draft-email` and V3 draft generation paths.

### `evidence_checker.md`

Purpose:
- safe rewrite of unsupported claims while preserving valid proof references.

Pipeline fit:
- used by `/v1/check-email` and evidence-safe rewriting in V3.

### `reply_triage.md`

Purpose:
- classify inbound responses and produce concise suggested replies.

Pipeline fit:
- optional support for reply handling layer adjacent to V3/V3.5 queues.

### `content_engine.md`

Purpose:
- convert approved insights into structured thought-leadership content drafts.

Pipeline fit:
- optional support layer for insight/content workflows, outside deterministic scoring logic.

## Deterministic Code vs Prompt Responsibilities

Prompt layer responsibilities:

- interpretation framing
- narrative drafting
- rewriting unsafe factual text into supported wording
- summarization from provided inputs

Deterministic code responsibilities (remain in Django/services code):

- scoring logic and thresholds
- evidence truth validation and canonical dedupe
- approval state transitions
- scheduling decisions
- queue filtering and operational selection
- send execution and idempotency

## LLM Gateway Clarification

- `growth_ops/services/llm_gateway.py` is a Django client wrapper to gateway HTTP endpoints.
- Prompt files in `services/llm-gateway/app/prompts/` are runtime prompt templates used by the gateway service.

## Current Endpoint Wiring (as implemented)

Currently wired endpoints in `services/llm-gateway/app/main.py`:

- `/v1/report` -> `website_reporter.md`
- `/v1/draft-email` -> `outreach_writer.md`
- `/v1/check-email` -> `evidence_checker.md`

Other prompt files are library-ready for future endpoint expansion without changing core deterministic architecture.

