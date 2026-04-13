from django.db import migrations, models


def dedupe_sent_sends_and_sequences(apps, schema_editor):
    OutboundSend = apps.get_model("growth_ops", "OutboundSend")
    Sequence = apps.get_model("growth_ops", "Sequence")

    sent_records = OutboundSend.objects.filter(status="sent").order_by("draft_id", "-sent_at", "-created_at", "-id")
    seen_drafts = set()
    for send_record in sent_records.iterator():
        if send_record.draft_id in seen_drafts:
            send_record.status = "failed"
            existing_error = (send_record.error or "").strip()
            send_record.error = (
                f"{existing_error}; deduplicated during migration".strip("; ")
                if existing_error
                else "deduplicated during migration"
            )
            send_record.save(update_fields=["status", "error"])
            continue
        seen_drafts.add(send_record.draft_id)

    sequences = Sequence.objects.order_by("lead_id", "-created_at", "-id")
    seen_leads = set()
    for sequence in sequences.iterator():
        if sequence.lead_id in seen_leads:
            sequence.delete()
            continue
        seen_leads.add(sequence.lead_id)


class Migration(migrations.Migration):

    dependencies = [
        ("growth_ops", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(dedupe_sent_sends_and_sequences, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="outboundsend",
            constraint=models.UniqueConstraint(
                condition=models.Q(status="sent"),
                fields=("draft",),
                name="growth_send_one_sent_per_draft",
            ),
        ),
        migrations.AddConstraint(
            model_name="sequence",
            constraint=models.UniqueConstraint(
                fields=("lead",),
                name="growth_sequence_unique_lead",
            ),
        ),
    ]
