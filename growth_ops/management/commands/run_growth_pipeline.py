from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand, CommandError

from growth_ops.services.evidence_fetcher import collect_basic_evidence, fetch_pagespeed
from growth_ops.services.evidence_ingest import persist_evidence_items
from growth_ops.services.google_places import discover_place_candidates
from growth_ops.services.lead_ingest import upsert_lead_from_candidate


class Command(BaseCommand):
    help = "Discover Google Places leads, upsert them, and collect basic website evidence."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--keyword", required=True, help="Search keyword (e.g. 'gym').")
        parser.add_argument("--location", required=True, help="Search location (e.g. 'Galway').")
        parser.add_argument(
            "--limit",
            type=int,
            default=10,
            help="Maximum number of place candidates to process (default: 10).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        keyword: str = options["keyword"]
        location: str = options["location"]
        limit: int = max(1, options["limit"] or 10)

        try:
            candidates = discover_place_candidates(keyword=keyword, location=location, limit=limit)
        except Exception as exc:
            raise CommandError(f"Failed to discover Google Place candidates: {exc}") from exc

        candidates_discovered = len(candidates)
        leads_processed = 0
        leads_skipped = 0
        evidence_created = 0
        evidence_reused = 0
        failures = 0

        self.stdout.write(
            self.style.NOTICE(
                f"Discovered {candidates_discovered} candidates for keyword='{keyword}' location='{location}'."
            )
        )

        for index, candidate in enumerate(candidates, start=1):
            company_name = (candidate.get("company_name") or "").strip() or "unknown"
            website_url = (candidate.get("website_url") or "").strip()
            place_id = (candidate.get("google_place_id") or "").strip()
            prefix = f"[{index}/{candidates_discovered}] {company_name}"
            if place_id:
                prefix = f"{prefix} (place_id={place_id})"

            if not website_url:
                leads_skipped += 1
                self.stdout.write(self.style.WARNING(f"{prefix}: skipped (no website_url)."))
                continue

            try:
                lead, created = upsert_lead_from_candidate(candidate)
                leads_processed += 1
                self.stdout.write(
                    f"{prefix}: lead_id={lead.id} {'created' if created else 'updated'}; website={lead.website_url}"
                )

                evidence_items = collect_basic_evidence(lead.website_url)
                pagespeed_payload = fetch_pagespeed(lead.website_url)
                evidence_items.append(
                    {
                        "evidence_type": "pagespeed_json",
                        "url": lead.website_url,
                        "tool": "pagespeed_api",
                        "payload": pagespeed_payload,
                    }
                )
                summary = persist_evidence_items(lead=lead, items=evidence_items)
                evidence_created += int(summary["created_count"])
                evidence_reused += int(summary["reused_count"])
                self.stdout.write(
                    f"  evidence created={summary['created_count']} reused={summary['reused_count']}"
                )
            except Exception as exc:
                failures += 1
                self.stderr.write(self.style.ERROR(f"{prefix}: failed - {exc}"))
                continue

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Growth pipeline complete."))
        self.stdout.write(f"candidates_discovered: {candidates_discovered}")
        self.stdout.write(f"leads_processed: {leads_processed}")
        self.stdout.write(f"leads_skipped: {leads_skipped}")
        self.stdout.write(f"evidence_created: {evidence_created}")
        self.stdout.write(f"evidence_reused: {evidence_reused}")
        self.stdout.write(f"failures: {failures}")
