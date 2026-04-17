from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max

from growth_ops.models import Lead
from growth_ops.services.scoring_pipeline import run_outreach_for_lead


class Command(BaseCommand):
    help = "Run deterministic Growth Ops V3 outreach draft generation on scored leads."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--limit",
            type=int,
            default=20,
            help="Maximum number of eligible leads to process (default: 20).",
        )
        parser.add_argument(
            "--lead-id",
            type=int,
            help="Process a single lead by id.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Create a new draft even when an equivalent one already exists.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        limit: int = max(1, int(options.get("limit") or 20))
        lead_id: int | None = options.get("lead_id")
        force: bool = bool(options.get("force"))

        if lead_id is not None:
            queryset = Lead.objects.filter(pk=lead_id)
            if not queryset.exists():
                raise CommandError(f"Lead {lead_id} was not found.")
        else:
            queryset = (
                Lead.objects.filter(scores__isnull=False, website_reports__isnull=False)
                .annotate(best_score=Max("scores__score"))
                .order_by("-best_score", "created_at")
            )[:limit]

        leads = list(queryset)
        leads_considered = len(leads)
        leads_processed = 0
        drafts_created = 0
        drafts_reused = 0
        drafts_skipped = 0
        failures = 0

        self.stdout.write(
            self.style.NOTICE(
                f"Starting Growth V3 run: leads={leads_considered} force={force}"
            )
        )

        for index, lead in enumerate(leads, start=1):
            prefix = f"[{index}/{leads_considered}] lead_id={lead.id} {lead.company_name}"
            try:
                result = run_outreach_for_lead(lead, force=force)
                leads_processed += 1
                decision = result.get("decision", {})
                priority = str(decision.get("priority") or "low")
                if result["draft_created"]:
                    drafts_created += 1
                    self.stdout.write(
                        f"{prefix}: decision={priority}/contact, draft_id={result['draft_id']} (created)"
                    )
                elif result["draft_reused"]:
                    drafts_reused += 1
                    self.stdout.write(
                        f"{prefix}: decision={priority}/contact, draft_id={result['draft_id']} (reused)"
                    )
                else:
                    drafts_skipped += 1
                    self.stdout.write(f"{prefix}: decision={priority}/skip, no draft")
            except Exception as exc:
                failures += 1
                self.stderr.write(self.style.ERROR(f"{prefix}: failed - {exc}"))
                continue

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Growth V3 pipeline complete."))
        self.stdout.write(f"leads_considered: {leads_considered}")
        self.stdout.write(f"leads_processed: {leads_processed}")
        self.stdout.write(f"drafts_created: {drafts_created}")
        self.stdout.write(f"drafts_reused: {drafts_reused}")
        self.stdout.write(f"drafts_skipped: {drafts_skipped}")
        self.stdout.write(f"failures: {failures}")
