from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand, CommandError

from growth_ops.models import Lead
from growth_ops.services.scoring_pipeline import run_report_and_score_for_lead


class Command(BaseCommand):
    help = "Run deterministic Growth Ops V2 report + score pipeline."

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
            help="Process a single lead by id (overrides default status selection).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Regenerate report and score even when equivalent rows already exist.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        limit: int = max(1, int(options.get("limit") or 20))
        lead_id: int | None = options.get("lead_id")
        force: bool = bool(options.get("force"))

        if lead_id is not None:
            queryset = Lead.objects.filter(pk=lead_id).order_by("created_at")
            if not queryset.exists():
                raise CommandError(f"Lead {lead_id} was not found.")
        else:
            queryset = Lead.objects.filter(status="evidence_collected").order_by("created_at")[:limit]

        leads = list(queryset)
        leads_considered = len(leads)
        leads_processed = 0
        reports_created = 0
        reports_reused = 0
        scores_created = 0
        scores_reused = 0
        failures = 0

        self.stdout.write(
            self.style.NOTICE(
                f"Starting Growth V2 run: leads={leads_considered} force={force}"
            )
        )

        for index, lead in enumerate(leads, start=1):
            prefix = f"[{index}/{leads_considered}] lead_id={lead.id} {lead.company_name}"
            try:
                result = run_report_and_score_for_lead(lead, force=force)
                leads_processed += 1
                if result["report_created"]:
                    reports_created += 1
                else:
                    reports_reused += 1
                if result["score_created"]:
                    scores_created += 1
                else:
                    scores_reused += 1
                self.stdout.write(
                    f"{prefix}: report_id={result['report_id']} "
                    f"({'created' if result['report_created'] else 'reused'}), "
                    f"score_id={result['score_id']} "
                    f"({'created' if result['score_created'] else 'reused'})"
                )
            except Exception as exc:
                failures += 1
                self.stderr.write(self.style.ERROR(f"{prefix}: failed - {exc}"))
                continue

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Growth V2 pipeline complete."))
        self.stdout.write(f"leads_considered: {leads_considered}")
        self.stdout.write(f"leads_processed: {leads_processed}")
        self.stdout.write(f"reports_created: {reports_created}")
        self.stdout.write(f"reports_reused: {reports_reused}")
        self.stdout.write(f"scores_created: {scores_created}")
        self.stdout.write(f"scores_reused: {scores_reused}")
        self.stdout.write(f"failures: {failures}")
