from celery import shared_task
from .scripts.auditor import SiteAuditor
from .models import SiteAudit

@shared_task
def run_site_audit_task(url: str):
    auditor = SiteAuditor(url)
    result = auditor.run_audit()
    SiteAudit.from_audit_result(url, result)
    return True
