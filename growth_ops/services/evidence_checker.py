from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from growth_ops.models import WebsiteEvidence

NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")


@dataclass(frozen=True)
class EvidenceCheckResult:
    status: str
    supported_proof_points: list[dict[str, Any]]
    unsupported_proof_points: list[dict[str, Any]]
    unsupported_claims: list[str]
    risk_flags: list[str]


def _get_by_path(payload: Any, path: str) -> tuple[bool, Any]:
    if not path:
        return False, None
    current = payload
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
            continue
        return False, None
    return True, current


def _normalize_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, ensure_ascii=True).lower()
    return str(value).strip().lower()


def _claim_has_numeric_match(claim: str, evidence_text: str) -> bool:
    numbers = NUMBER_RE.findall(claim)
    if not numbers:
        return True
    return all(number in evidence_text for number in numbers)


def _is_proof_point_supported(proof_point: dict[str, Any], evidence_map: dict[str, WebsiteEvidence]) -> tuple[bool, str]:
    evidence_id = str(proof_point.get("evidence_id", "")).strip()
    evidence_path = str(proof_point.get("evidence_path", "")).strip()
    claim = str(proof_point.get("claim", "")).strip()
    quoted_value = str(proof_point.get("quoted_value", "")).strip()

    if not evidence_id:
        return False, "missing_evidence_id"
    if evidence_id not in evidence_map:
        return False, "evidence_not_found"
    if not evidence_path:
        return False, "missing_evidence_path"
    if not claim:
        return False, "missing_claim"

    evidence_record = evidence_map[evidence_id]
    found, value = _get_by_path(evidence_record.payload, evidence_path.replace("payload.", ""))
    if not found:
        return False, "evidence_path_not_found"

    normalized_value = _normalize_value(value)
    normalized_claim = claim.lower()
    normalized_quote = quoted_value.lower()

    if quoted_value:
        if normalized_quote not in normalized_value:
            return False, "quoted_value_not_in_evidence"
        if normalized_quote not in normalized_claim:
            return False, "claim_missing_quoted_value"
        return True, "supported"

    if isinstance(value, (str, int, float, bool)):
        value_text = str(value).strip().lower()
        if value_text and value_text not in normalized_claim:
            return False, "claim_missing_evidence_value"

    if not _claim_has_numeric_match(normalized_claim, normalized_value):
        return False, "numeric_mismatch"

    return True, "supported"


def check_proof_points(
    *,
    proof_points: list[dict[str, Any]],
    evidence_records: list[WebsiteEvidence],
) -> EvidenceCheckResult:
    evidence_map = {str(record.id): record for record in evidence_records}
    supported: list[dict[str, Any]] = []
    unsupported: list[dict[str, Any]] = []

    for point in proof_points:
        point_payload = dict(point)
        is_supported, reason = _is_proof_point_supported(point_payload, evidence_map)
        if is_supported:
            supported.append(point_payload)
            continue
        point_payload["unsupported_reason"] = reason
        unsupported.append(point_payload)

    status_value = "pass" if not unsupported else "needs_rewrite"
    risk_flags = []
    if unsupported:
        risk_flags.append("UNSUPPORTED_CLAIMS_DETECTED")
    return EvidenceCheckResult(
        status=status_value,
        supported_proof_points=supported,
        unsupported_proof_points=unsupported,
        unsupported_claims=[str(item.get("claim", "")) for item in unsupported if item.get("claim")],
        risk_flags=risk_flags,
    )
