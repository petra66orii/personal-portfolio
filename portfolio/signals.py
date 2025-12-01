# contact/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ServiceInquiry
from scripts.ai_screener import analyze_lead
import threading

@receiver(post_save, sender=ServiceInquiry)
def trigger_ai_analysis(sender, instance, created, **kwargs):
    """
    When a new inquiry is saved, run the AI analysis in a separate thread
    so the user doesn't have to wait for OpenAI to respond.
    """
    if created and not instance.is_analyzed:
        thread = threading.Thread(target=analyze_lead, args=(instance,))
        thread.start()