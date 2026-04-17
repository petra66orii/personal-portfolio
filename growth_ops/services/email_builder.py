from __future__ import annotations

import json
from typing import Any

from growth_ops.models import Lead, LeadScore, WebsiteEvidence, WebsiteReport
from growth_ops.services.evidence_checker import check_proof_points
from growth_ops.services.llm_gateway import LLMGatewayClient, LLMGatewayError

_ALLOWED_MARKETS = {"IE", "RO", "US", "OTHER"}
_ALLOWED_BUCKETS = {"A", "B"}
_ALLOWED_FINDING_SEVERITIES = {"low", "medium", "high", "critical"}


def _fallback_reason(code: str, **details: Any) -> str:
    safe_code = _safe_text(code, max_len=80).replace(" ", "_")
    if not details:
        return safe_code
    parts: list[str] = []
    for key, value in details.items():
        safe_key = _safe_text(key, max_len=40).replace(" ", "_")
        safe_value = _safe_text(value, max_len=120).replace(" ", "_")
        parts.append(f"{safe_key}={safe_value}")
    return _safe_text(f"{safe_code}:{'|'.join(parts)}", max_len=255)


def _to_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_text(value: Any, *, max_len: int = 2000) -> str:
    text = str(value or "").strip()
    return text[:max_len]


def _normalize_market(raw_market: Any) -> str:
    parsed = str(raw_market or "").strip().upper()
    if parsed in _ALLOWED_MARKETS:
        return parsed
    return "OTHER"


def _flatten_scalar_paths(payload: Any, *, max_items: int = 20) -> list[tuple[str, str]]:
    flattened: list[tuple[str, str]] = []

    def walk(node: Any, path: str) -> None:
        if len(flattened) >= max_items:
            return
        if isinstance(node, dict):
            for key, value in node.items():
                next_path = f"{path}.{key}" if path else str(key)
                walk(value, next_path)
            return
        if isinstance(node, list):
            return
        if node is None:
            return
        flattened.append((path, str(node)))

    walk(payload, "")
    return flattened


def _select_evidence_records(lead: Lead, report_obj: WebsiteReport | None) -> list[WebsiteEvidence]:
    if report_obj and isinstance(report_obj.evidence_ids, list) and report_obj.evidence_ids:
        numeric_ids: list[int] = []
        for value in report_obj.evidence_ids:
            try:
                numeric_ids.append(int(value))
            except (TypeError, ValueError):
                continue
        if numeric_ids:
            records = list(lead.website_evidence.filter(id__in=numeric_ids).order_by("id"))
            if records:
                return records
    return list(lead.website_evidence.order_by("id"))


def _build_evidence_refs_for_llm(evidence_records: list[WebsiteEvidence]) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for evidence in evidence_records:
        scalar_paths = _flatten_scalar_paths(evidence.payload, max_items=12)
        if scalar_paths:
            for path, value in scalar_paths:
                refs.append(
                    {
                        "evidence_id": str(evidence.id),
                        "evidence_type": evidence.evidence_type,
                        "evidence_path": path or "payload",
                        "evidence_excerpt": value[:500],
                    }
                )
        else:
            refs.append(
                {
                    "evidence_id": str(evidence.id),
                    "evidence_type": evidence.evidence_type,
                    "evidence_path": "payload",
                    "evidence_excerpt": json.dumps(evidence.payload, ensure_ascii=True)[:500],
                }
            )
    return refs[:200]


def _extract_report_findings_for_llm(report_payload: dict[str, Any]) -> list[dict[str, str]]:
    findings = report_payload.get("findings")
    if not isinstance(findings, list):
        return []
    output: list[dict[str, str]] = []
    for item in findings[:8]:
        if not isinstance(item, dict):
            continue
        title = _safe_text(item.get("title"), max_len=200)
        diagnosis = _safe_text(item.get("diagnosis"), max_len=1200)
        severity = _safe_text(item.get("severity"), max_len=16).lower()
        if not title or not diagnosis:
            continue
        if severity not in _ALLOWED_FINDING_SEVERITIES:
            severity = "medium"
        output.append(
            {
                "title": title,
                "diagnosis": diagnosis,
                "severity": severity,
            }
        )
    return output


def _extract_primary_issue_business_impact(report_payload: dict[str, Any], issue_key: str) -> str:
    findings = report_payload.get("findings")
    if not isinstance(findings, list):
        return ""
    issue_tokens = {
        "weak_cta": ("cta", "call-to-action"),
        "no_contact_method": ("contact", "enquiry"),
        "poor_performance": ("performance", "speed", "lcp"),
        "no_https": ("https", "secure", "ssl"),
        "weak_trust": ("trust", "testimonial", "review"),
        "seo_issues": ("seo", "robots", "sitemap", "meta"),
    }
    tokens = issue_tokens.get(issue_key, ())
    for item in findings:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").lower()
        diagnosis = str(item.get("diagnosis") or "").lower()
        business_impact = _safe_text(item.get("business_impact"), max_len=800)
        if not business_impact:
            continue
        combined = f"{title} {diagnosis}"
        if not tokens or any(token in combined for token in tokens):
            return business_impact
    return ""


def _normalize_proof_points(raw_points: Any) -> list[dict[str, str]]:
    if not isinstance(raw_points, list):
        return []
    output: list[dict[str, str]] = []
    for item in raw_points:
        if not isinstance(item, dict):
            continue
        claim = _safe_text(item.get("claim"), max_len=1000)
        evidence_id = _safe_text(item.get("evidence_id"), max_len=128)
        evidence_path = _safe_text(item.get("evidence_path"), max_len=255).replace("payload.", "")
        quoted_value = _safe_text(item.get("quoted_value"), max_len=500)
        if not claim or not evidence_id or not evidence_path:
            continue
        output.append(
            {
                "claim": claim,
                "evidence_id": evidence_id,
                "evidence_path": evidence_path,
                "quoted_value": quoted_value,
            }
        )
    return output


def _build_preview(company: str, issue_sentence: str, impact_sentence: str, *, max_len: int = 200) -> str:
    preview = f"{company}: {issue_sentence} {impact_sentence}".strip()
    return preview[:max_len]


def _latest_evidence_by_type(evidence_records: list[WebsiteEvidence], evidence_type: str) -> WebsiteEvidence | None:
    for item in reversed(evidence_records):
        if item.evidence_type == evidence_type and isinstance(item.payload, dict):
            return item
    return None


def _value_by_path(payload: Any, path: str) -> tuple[bool, Any]:
    if not path or not isinstance(payload, dict):
        return False, None
    current: Any = payload
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
            continue
        return False, None
    return True, current


def _supported_point_from_path(
    *,
    evidence: WebsiteEvidence | None,
    path: str,
    claim_prefix: str,
) -> dict[str, str] | None:
    if evidence is None or not isinstance(evidence.payload, dict):
        return None
    found, value = _value_by_path(evidence.payload, path)
    if not found:
        return None
    if value is None or isinstance(value, (dict, list)):
        return None
    quoted = _safe_text(value, max_len=500)
    if not quoted:
        return None
    claim = _safe_text(f"{claim_prefix} {quoted}.", max_len=1000)
    return {
        "claim": claim,
        "evidence_id": str(evidence.id),
        "evidence_path": path,
        "quoted_value": quoted,
    }


def _build_deterministic_supported_proof_points(
    *,
    evidence_records: list[WebsiteEvidence],
    report_payload: dict[str, Any],
    decision: dict[str, Any],
    deterministic_email: dict[str, str],
) -> list[dict[str, str]]:
    issue_key = str(deterministic_email.get("primary_issue") or _select_primary_issue(report_payload=report_payload, decision=decision))
    homepage = _latest_evidence_by_type(evidence_records, "homepage_html_snippet")
    robots = _latest_evidence_by_type(evidence_records, "robots_txt")
    sitemap = _latest_evidence_by_type(evidence_records, "sitemap_xml")
    pagespeed = _latest_evidence_by_type(evidence_records, "pagespeed_json")
    lighthouse = _latest_evidence_by_type(evidence_records, "lighthouse_json")
    perf = pagespeed or lighthouse

    candidates: list[dict[str, str] | None] = []
    if issue_key == "poor_performance":
        candidates.extend(
            [
                _supported_point_from_path(
                    evidence=perf,
                    path="performance_score",
                    claim_prefix="Detected mobile performance score value is",
                ),
                _supported_point_from_path(
                    evidence=perf,
                    path="lcp_ms",
                    claim_prefix="Detected largest contentful paint value is",
                ),
            ]
        )
    elif issue_key == "seo_issues":
        candidates.extend(
            [
                _supported_point_from_path(
                    evidence=robots,
                    path="status_code",
                    claim_prefix="Detected robots.txt status code is",
                ),
                _supported_point_from_path(
                    evidence=sitemap,
                    path="status_code",
                    claim_prefix="Detected sitemap.xml status code is",
                ),
            ]
        )
    elif issue_key == "no_https":
        candidates.append(
            _supported_point_from_path(
                evidence=homepage,
                path="requested_url",
                claim_prefix="Detected homepage requested URL is",
            )
        )
    else:
        candidates.extend(
            [
                _supported_point_from_path(
                    evidence=homepage,
                    path="status_code",
                    claim_prefix="Detected homepage status code is",
                ),
                _supported_point_from_path(
                    evidence=homepage,
                    path="requested_url",
                    claim_prefix="Detected homepage requested URL is",
                ),
            ]
        )

    # Always try to include one performance metric when available.
    if perf is not None:
        candidates.append(
            _supported_point_from_path(
                evidence=perf,
                path="performance_score",
                claim_prefix="Detected mobile performance score value is",
            )
        )
    if robots is not None:
        candidates.append(
            _supported_point_from_path(
                evidence=robots,
                path="status_code",
                claim_prefix="Detected robots.txt status code is",
            )
        )
    if sitemap is not None:
        candidates.append(
            _supported_point_from_path(
                evidence=sitemap,
                path="status_code",
                claim_prefix="Detected sitemap.xml status code is",
            )
        )

    output: list[dict[str, str]] = []
    seen_keys: set[tuple[str, str, str]] = set()
    for candidate in candidates:
        if candidate is None:
            continue
        dedupe_key = (
            candidate["evidence_id"],
            candidate["evidence_path"],
            candidate["quoted_value"].lower(),
        )
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)
        output.append(candidate)
        if len(output) >= 6:
            break
    return output


def _append_seed_proof_points_to_summary(
    *,
    base_summary: str,
    seed_proof_points: list[dict[str, str]],
) -> str:
    summary = _safe_text(base_summary, max_len=1200)
    if not seed_proof_points:
        return _safe_text(summary, max_len=2000)

    lines = ["", "Verified proof points (use exact evidence refs and quoted values):"]
    for point in seed_proof_points[:5]:
        line = (
            f"- {point['claim']} "
            f"[evidence_id={point['evidence_id']}; evidence_path={point['evidence_path']}; quoted_value={point['quoted_value']}]"
        )
        lines.append(_safe_text(line, max_len=300))
    combined = f"{summary}\n" + "\n".join(lines)
    return _safe_text(combined, max_len=2000)


def _select_primary_issue(*, report_payload: dict[str, Any], decision: dict[str, Any]) -> str:
    cta_clarity = str(report_payload.get("cta_clarity") or "").strip().lower()
    cta = report_payload.get("cta")
    performance = report_payload.get("performance")
    trust = report_payload.get("trust")
    seo = report_payload.get("seo")
    technical = report_payload.get("technical")
    angle = str(decision.get("angle") or "").strip().lower()

    has_contact_method = None
    if isinstance(cta, dict):
        has_contact_method = cta.get("has_contact_method")
    if has_contact_method is None and isinstance(trust, dict):
        has_contact_method = trust.get("has_contact_info")

    perf_score = _to_float((performance or {}).get("score")) if isinstance(performance, dict) else None
    lcp_ms = _to_float((performance or {}).get("lcp_ms")) if isinstance(performance, dict) else None
    trust_rating = str((trust or {}).get("rating") or "").strip().lower() if isinstance(trust, dict) else ""
    seo_issues = (seo or {}).get("issues") if isinstance(seo, dict) else []
    seo_issue_count = len([issue for issue in seo_issues if str(issue).strip()]) if isinstance(seo_issues, list) else 0
    has_https = (technical or {}).get("has_https") if isinstance(technical, dict) else None

    if cta_clarity in {"missing", "weak", "unclear", "poor"}:
        return "weak_cta"
    if has_contact_method is False:
        return "no_contact_method"
    if (lcp_ms is not None and lcp_ms > 3000) or (perf_score is not None and perf_score < 70):
        return "poor_performance"
    if has_https is False:
        return "no_https"
    if trust_rating == "weak":
        return "weak_trust"
    if seo_issue_count > 0:
        return "seo_issues"

    if angle == "cta_missing":
        return "weak_cta"
    if angle == "slow_site":
        return "poor_performance"
    if angle == "low_trust":
        return "weak_trust"
    if angle == "seo_hygiene":
        return "seo_issues"
    return "general"


def _issue_copy(*, issue_key: str, report_payload: dict[str, Any]) -> tuple[str, str]:
    cta_clarity = str(report_payload.get("cta_clarity") or "weak").strip().lower()
    performance = report_payload.get("performance")
    seo = report_payload.get("seo")
    perf_score = _to_float((performance or {}).get("score")) if isinstance(performance, dict) else None
    lcp_ms = _to_float((performance or {}).get("lcp_ms")) if isinstance(performance, dict) else None

    if issue_key == "weak_cta":
        return (
            f"the homepage call-to-action is {cta_clarity}, so the next step is easy to miss.",
            "That usually means fewer enquiries from visitors who were ready to contact you.",
        )
    if issue_key == "no_contact_method":
        return (
            "there is no clear contact route visible on the homepage.",
            "If people cannot quickly find how to contact you, it can cost enquiries.",
        )
    if issue_key == "poor_performance":
        if perf_score is not None and lcp_ms is not None:
            return (
                f"mobile performance is slow (score {int(round(perf_score))}, LCP {int(round(lcp_ms))}ms).",
                "Slow pages lose attention early and can reduce conversion from paid and organic traffic.",
            )
        return (
            "mobile performance is below target.",
            "Slow load times usually reduce both engagement and enquiry intent.",
        )
    if issue_key == "no_https":
        return (
            "the site appears to run without HTTPS.",
            "A non-secure connection reduces trust for new visitors before they enquire.",
        )
    if issue_key == "weak_trust":
        return (
            "trust signals are light for first-time visitors.",
            "When trust is unclear, high-intent prospects often delay or skip contacting.",
        )
    if issue_key == "seo_issues":
        first_issue = ""
        if isinstance(seo, dict) and isinstance(seo.get("issues"), list):
            non_empty = [str(item).strip() for item in seo["issues"] if str(item).strip()]
            first_issue = non_empty[0] if non_empty else ""
        detail = f" ({first_issue})" if first_issue else ""
        return (
            f"there is an SEO hygiene gap{detail}.",
            "That can limit discoverability and reduce qualified inbound traffic over time.",
        )
    return (
        "one high-impact website issue stood out on review.",
        "Fixing it first should improve conversion confidence and lead flow.",
    )


def _subject(*, lead: Lead, issue_key: str) -> str:
    company = (lead.company_name or "your website").strip()
    if issue_key == "weak_cta":
        return f"Quick CTA fix for {company}"
    if issue_key == "no_contact_method":
        return f"Quick contact-path fix for {company}"
    if issue_key == "poor_performance":
        return f"Quick speed fix for {company}"
    if issue_key in {"weak_trust", "no_https"}:
        return f"Quick trust fix for {company}"
    if issue_key == "seo_issues":
        return f"Quick SEO fix for {company}"
    return f"Quick website idea for {company}"


def _build_deterministic_outreach_email(
    *,
    lead: Lead,
    report_payload: dict[str, Any],
    decision: dict[str, Any],
) -> dict[str, str]:
    company = (lead.company_name or "your team").strip()
    issue_key = _select_primary_issue(report_payload=report_payload, decision=decision)
    issue_sentence, impact_sentence = _issue_copy(issue_key=issue_key, report_payload=report_payload)
    subject = _subject(lead=lead, issue_key=issue_key)

    body_lines = [
        f"Hi {company} team,",
        "",
        f"I had a quick look at {company}'s website and noticed that {issue_sentence}",
        impact_sentence,
        "",
        "If useful, I can share a short plan for fixing this first.",
        "Open to a quick call next week?",
        "",
        "Best,",
        "Petra",
        "Miss Bott",
    ]
    body = "\n".join(body_lines)
    preview = _build_preview(company, issue_sentence, impact_sentence)
    business_impact = _extract_primary_issue_business_impact(report_payload, issue_key) or impact_sentence
    return {
        "subject": subject,
        "body": body,
        "preview": preview,
        "issue_sentence": issue_sentence,
        "primary_issue": issue_key,
        "business_impact": business_impact[:800],
    }


def build_llm_draft_payload(
    *,
    lead: Lead,
    score_obj: LeadScore,
    decision: dict[str, Any],
    report_payload: dict[str, Any],
    report_obj: WebsiteReport | None,
    sequence_step: int,
    deterministic_email: dict[str, str],
    evidence_refs: list[dict[str, str]],
    seed_proof_points: list[dict[str, str]],
) -> dict[str, Any]:
    findings = _extract_report_findings_for_llm(report_payload)
    base_summary = _safe_text(
        report_payload.get("summary")
        or report_payload.get("executive_summary")
        or deterministic_email.get("business_impact")
        or "",
        max_len=2000,
    )
    report_summary = _append_seed_proof_points_to_summary(
        base_summary=base_summary,
        seed_proof_points=seed_proof_points,
    )

    return {
        "lead_id": int(lead.id),
        "company_name": _safe_text(lead.company_name, max_len=255),
        "website_url": _safe_text(lead.website_url, max_len=500),
        "market": _normalize_market(lead.market),
        "industry": _safe_text(lead.industry, max_len=120) or None,
        "bucket": str(score_obj.bucket),
        "score": int(score_obj.score),
        "offer_type": _safe_text(decision.get("offer_type"), max_len=128) or "general_audit",
        "sequence_step": max(1, min(int(sequence_step), 10)),
        "report_summary": report_summary,
        "report_findings": findings,
        "evidence": evidence_refs,
    }


def _deterministic_output(
    deterministic_email: dict[str, str],
    *,
    fallback_used: bool,
    fallback_reason: str,
) -> dict[str, Any]:
    return {
        "subject": _safe_text(deterministic_email.get("subject"), max_len=255),
        "body": _safe_text(deterministic_email.get("body"), max_len=8000),
        "preview": _safe_text(deterministic_email.get("preview"), max_len=200),
        "proof_points": [],
        "risk_flags": ["DETERMINISTIC_V3"],
        "draft_generation_mode": "deterministic",
        "llm_prompt_name": "",
        "llm_prompt_version": "",
        "llm_fallback_used": bool(fallback_used),
        "llm_fallback_reason": _safe_text(fallback_reason, max_len=255),
        "claim_check": {
            "status": "fallback",
            "notes": [f"deterministic_fallback:{_safe_text(fallback_reason, max_len=200)}"],
        },
        "model": "",
        "prompt_version": "",
    }


def build_outreach_email(
    *,
    lead: Lead,
    report_payload: dict[str, Any],
    score_obj: LeadScore,
    decision: dict[str, Any],
    report_obj: WebsiteReport | None = None,
    sequence_step: int = 1,
) -> dict[str, Any]:
    deterministic_email = _build_deterministic_outreach_email(
        lead=lead,
        report_payload=report_payload,
        decision=decision,
    )

    if str(score_obj.bucket) not in _ALLOWED_BUCKETS:
        return _deterministic_output(
            deterministic_email,
            fallback_used=False,
            fallback_reason="non_draftable_bucket",
        )
    if not str(lead.website_url or "").strip():
        return _deterministic_output(
            deterministic_email,
            fallback_used=True,
            fallback_reason="missing_website_url",
        )

    evidence_records = _select_evidence_records(lead, report_obj)
    evidence_refs = _build_evidence_refs_for_llm(evidence_records)
    if not evidence_records or not evidence_refs:
        return _deterministic_output(
            deterministic_email,
            fallback_used=True,
            fallback_reason=_fallback_reason("missing_evidence_for_llm"),
        )

    deterministic_seed_points = _build_deterministic_supported_proof_points(
        evidence_records=evidence_records,
        report_payload=report_payload,
        decision=decision,
        deterministic_email=deterministic_email,
    )
    if not deterministic_seed_points:
        return _deterministic_output(
            deterministic_email,
            fallback_used=True,
            fallback_reason=_fallback_reason(
                "missing_supported_proof_points_for_draft_payload",
                evidence_count=len(evidence_records),
                lead_id=lead.id,
            ),
        )

    llm = LLMGatewayClient()
    try:
        draft_payload = build_llm_draft_payload(
            lead=lead,
            score_obj=score_obj,
            decision=decision,
            report_payload=report_payload,
            report_obj=report_obj,
            sequence_step=sequence_step,
            deterministic_email=deterministic_email,
            evidence_refs=evidence_refs,
            seed_proof_points=deterministic_seed_points,
        )
        draft_response = llm.draft_email(draft_payload)

        llm_subject = _safe_text(draft_response.get("subject"), max_len=255)
        llm_body = _safe_text(draft_response.get("body"), max_len=8000)
        if not llm_subject or not llm_body:
            raise ValueError("llm_draft_missing_subject_or_body")

        draft_points = _normalize_proof_points(draft_response.get("proof_points"))
        initial_supported_points: list[dict[str, Any]] = []
        initial_unsupported_claims: list[str] = []
        initial_risk_flags: list[str] = []
        unsupported_count = 0

        if draft_points:
            initial_check = check_proof_points(
                proof_points=draft_points,
                evidence_records=evidence_records,
            )
            initial_supported_points = list(initial_check.supported_proof_points)
            initial_unsupported_claims = list(initial_check.unsupported_claims)
            initial_risk_flags = list(initial_check.risk_flags)
            unsupported_count = len(initial_check.unsupported_proof_points)

        checker_supported_points = list(initial_supported_points)
        used_seed_points_for_checker = False
        if not checker_supported_points:
            checker_supported_points = list(deterministic_seed_points)
            used_seed_points_for_checker = True
        if not checker_supported_points:
            raise ValueError(
                _fallback_reason(
                    "llm_draft_no_supported_proof_points",
                    llm_points=len(draft_points),
                    llm_unsupported=unsupported_count,
                    seed_points=len(deterministic_seed_points),
                )
            )

        unsupported_claims = list(initial_unsupported_claims)
        if not unsupported_claims:
            unsupported_claims = [
                "Rewrite all factual statements so they are grounded only in supported_proof_points."
            ]

        check_payload = {
            "lead_id": int(lead.id),
            "company_name": _safe_text(lead.company_name, max_len=255),
            "original_subject": llm_subject,
            "original_body": llm_body,
            "unsupported_claims": unsupported_claims,
            "supported_proof_points": checker_supported_points,
        }
        check_response = llm.check_email(check_payload)

        checked_subject = _safe_text(check_response.get("subject"), max_len=255) or llm_subject
        checked_body = _safe_text(check_response.get("body"), max_len=8000) or llm_body
        checked_points = _normalize_proof_points(check_response.get("proof_points"))
        if not checked_points:
            checked_points = checker_supported_points

        final_check = check_proof_points(
            proof_points=checked_points,
            evidence_records=evidence_records,
        )
        if final_check.unsupported_proof_points:
            raise ValueError(
                _fallback_reason(
                    "llm_checked_points_not_supported",
                    unsupported=len(final_check.unsupported_proof_points),
                    checked_points=len(checked_points),
                )
            )

        check_notes_raw = check_response.get("notes")
        check_notes = (
            [_safe_text(item, max_len=200) for item in check_notes_raw if _safe_text(item, max_len=200)]
            if isinstance(check_notes_raw, list)
            else []
        )

        claim_status = "rewritten" if (unsupported_count > 0 or used_seed_points_for_checker) else "ok"
        risk_flags: list[str] = []
        raw_risk_flags = draft_response.get("risk_flags")
        if isinstance(raw_risk_flags, list):
            risk_flags.extend(str(item).strip() for item in raw_risk_flags if str(item).strip())
        risk_flags.extend(initial_risk_flags)
        risk_flags.extend(final_check.risk_flags)
        if used_seed_points_for_checker:
            risk_flags.append("LLM_PROOF_POINTS_SEEDED")
        risk_flags.extend(["LLM_DRAFTED", "LLM_CHECKED"])
        deduped_risk_flags = list(dict.fromkeys(risk_flags))

        preview = _build_preview(
            (lead.company_name or "your team").strip(),
            deterministic_email.get("issue_sentence", "one high-impact website issue stood out on review."),
            deterministic_email.get("business_impact", ""),
        )

        prompt_name = _safe_text(check_response.get("prompt_name"), max_len=128) or _safe_text(
            draft_response.get("prompt_name"), max_len=128
        )
        prompt_version = _safe_text(check_response.get("prompt_version"), max_len=64) or _safe_text(
            draft_response.get("prompt_version"), max_len=64
        )
        model_name = _safe_text(check_response.get("model"), max_len=128) or _safe_text(
            draft_response.get("model"), max_len=128
        )

        return {
            "subject": checked_subject,
            "body": checked_body,
            "preview": _safe_text(preview, max_len=200),
            "proof_points": final_check.supported_proof_points,
            "risk_flags": deduped_risk_flags,
            "draft_generation_mode": "llm_draft_checked",
            "llm_prompt_name": prompt_name,
            "llm_prompt_version": prompt_version,
            "llm_fallback_used": False,
            "llm_fallback_reason": "",
            "claim_check": {
                "status": claim_status,
                "notes": check_notes,
            },
            "model": model_name,
            "prompt_version": prompt_version,
        }
    except (LLMGatewayError, ValueError, TypeError, KeyError) as exc:
        return _deterministic_output(
            deterministic_email,
            fallback_used=True,
            fallback_reason=_fallback_reason("llm_draft_fallback", reason=str(exc)),
        )
