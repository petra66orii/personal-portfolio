from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .models import SiteAudit
from scripts.auditor import SiteAuditor
import threading
import os

# Import your models
from .models import Project, ContactMessage, BlogPost, Service, ServiceInquiry

@admin.action(description='✅ Approve Lead & Send 15-min Booking Link')
def approve_and_invite(modeladmin, request, queryset):
    """
    Production action to approve leads and send the invitation email.
    Includes safety checks to prevent double-sending.
    """
    success_count = 0
    already_approved_count = 0
    
    # Load credentials
    email_user = os.getenv('EMAIL_HOST_USER')
    # Note: In production, you might not strictly need to pass auth_user/password 
    # if EMAIL_HOST_USER/PASSWORD are set in settings.py, but keeping it explicit 
    # ensures it uses the specific env vars you tested.

    # Safety Check: Credentials
    if not email_user:
        modeladmin.message_user(request, "Error: Missing Email Credentials in environment.", level=messages.ERROR)
        return

    CALENDLY_LINK = "https://calendly.com/developer-missbott/15-minute-free-discovery-call"

    for inquiry in queryset:
        # 1. SAFETY CHECK: Skip if already approved
        if inquiry.status == 'approved':
            already_approved_count += 1
            continue

        # 2. Generate Message Body (Draft or Template)
        if inquiry.ai_email_draft:
            message_body = f"""{inquiry.ai_email_draft}

To move forward, please select a time for our 15-minute fit check here:
{CALENDLY_LINK}

Best regards,

Miss Bott
Technical Lead
https://missbott.online"""
        else:
            # Fallback template
            message_body = f"""Hi {inquiry.name},

Thank you for your inquiry regarding {inquiry.get_budget_range_display()}. 
I'd love to discuss the scope.

Please book a time here:
{CALENDLY_LINK}

Best,
Miss Bott"""

        # 3. Attempt to Send
        try:
            send_mail(
                subject=f"Re: Project Inquiry - {inquiry.company or inquiry.name}",
                message=message_body,
                from_email=email_user,
                recipient_list=[inquiry.email],
                fail_silently=False,
            )
            
            # Update Status only on success
            inquiry.status = 'approved'
            inquiry.save()
            success_count += 1
            
        except Exception as e:
            modeladmin.message_user(request, f"Failed to send to {inquiry.email}: {e}", level=messages.ERROR)

    # 4. Final Summary Message
    if success_count > 0:
        modeladmin.message_user(request, f"Successfully sent invites to {success_count} leads.", level=messages.SUCCESS)
    
    if already_approved_count > 0:
        modeladmin.message_user(request, f"Skipped {already_approved_count} leads (already approved).", level=messages.WARNING)


class ServiceInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'lead_score_display', 'status', 'created_at')
    list_filter = ('status', 'lead_score', 'service')
    actions = [approve_and_invite]
    
    # Read-only fields
    readonly_fields = ('ai_summary', 'lead_score', 'ai_analysis_raw')
    
    fieldsets = (
        ('Client Data', {'fields': ('name', 'email', 'company', 'website_url')}),
        ('Project', {'fields': ('service', 'project_details', 'budget_range')}),
        ('AI Intelligence', {
            'fields': ('lead_score', 'ai_summary', 'ai_analysis_raw', 'is_analyzed'),
            'description': "Automated Analysis"
        }),
        ('Response Action', {
            'fields': ('ai_email_draft', 'status'), 
            'description': "Review and edit the draft below before clicking 'Approve & Send'"
        }),
    )

    def lead_score_display(self, obj):
        return f"{obj.lead_score}/10"
    lead_score_display.short_description = "Score"
    lead_score_display.admin_order_field = 'lead_score'

admin.site.register(ServiceInquiry, ServiceInquiryAdmin)

# Register other models
admin.site.register(Project)
admin.site.register(ContactMessage)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'service_type', 'featured', 'active', 'order']
    list_filter = ['service_type', 'featured', 'active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    list_editable = ['featured', 'active', 'order']

class BlogPostAdmin(SummernoteModelAdmin):
    summernote_fields = ('content', 'content_en', 'content_ro', 'content_es') 
    list_display = ('title', 'created_at')
    search_fields = ['title', 'content']

admin.site.register(BlogPost, BlogPostAdmin)



@admin.action(description="⚡ Run Technical Audit (Lighthouse + GPT)")
def run_technical_audit(modeladmin, request, queryset):
    """
    Runs the audit script. Warning: This takes ~15-20 seconds per site.
    """
    success_count = 0

    for audit in queryset:
        modeladmin.message_user(
            request,
            f"Starting audit for {audit.url}... Please wait.",
            level=messages.INFO,
        )

        try:
            auditor = SiteAuditor(audit.url)
            result = auditor.run_audit()

            # 🔁 reuse unified helper
            SiteAudit.from_audit_result(audit.url, result, instance=audit)

            success_count += 1

        except Exception as e:
            modeladmin.message_user(
                request,
                f"Audit failed for {audit.url}: {e}",
                level=messages.ERROR,
            )

    if success_count > 0:
        modeladmin.message_user(
            request,
            f"Completed {success_count} audits.",
            level=messages.SUCCESS,
        )


@admin.register(SiteAudit)
class SiteAuditAdmin(admin.ModelAdmin):
    list_display = ("url", "performance_score", "created_at")
    actions = [run_technical_audit]
    readonly_fields = ("raw_audit_data", "ai_strategy_email")