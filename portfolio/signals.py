# contact/signals.py
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ServiceInquiry
from .scripts.ai_screener import analyze_lead
import threading

@receiver(post_save, sender=ServiceInquiry)
def trigger_ai_analysis(sender, instance, created, **kwargs):
    """
    When enabled, run AI analysis in a separate thread so inquiry submission
    does not block on model latency.
    """
    if not getattr(settings, "ENABLE_INAPP_AI_SCREENING", False):
        return

    if created and not instance.is_analyzed:
        thread = threading.Thread(target=analyze_lead, args=(instance,), daemon=True)
        thread.start()
