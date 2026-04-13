import ipaddress
import json
import logging
import socket
import threading
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BlogPost, ContactMessage, Project, Service, ServiceInquiry, SiteAudit
from .scripts.auditor import SiteAuditor
from .sanitization import sanitize_rich_html
from .serializers import (
    BlogPostSerializer,
    ContactMessageSerializer,
    ProjectSerializer,
    ServiceInquirySerializer,
    ServiceSerializer,
)
from .tasks import run_site_audit_task
from .throttling import ContactFormThrottle, NewsletterSignupThrottle, ServiceInquiryThrottle

logger = logging.getLogger(__name__)

BLOCKED_AUDIT_HOSTS = {
    "localhost",
    "127.0.0.1",
    "::1",
    "host.docker.internal",
    "web",
    "django",
    "n8n",
    "db",
    "redis",
}


def _parse_audit_payload(request):
    payload, parse_error = _parse_json_payload(request)
    if parse_error:
        return None, parse_error

    url = (payload.get("url") or "").strip()
    if not url:
        return None, JsonResponse({"error": "URL is required"}, status=400)

    return url, None


def _parse_json_payload(request):
    try:
        payload = json.loads(request.body.decode("utf-8") if request.body else "{}")
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "Invalid JSON payload"}, status=400)
    return payload, None


def _is_public_target(url, resolve_dns=True):
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        return False, "Only http/https URLs are allowed"

    hostname = (parsed.hostname or "").lower()
    if not hostname:
        return False, "URL hostname is required"

    if hostname in BLOCKED_AUDIT_HOSTS:
        return False, "Private/internal targets are not allowed"

    # Reject literal private IP targets without DNS resolution.
    try:
        ip_obj = ipaddress.ip_address(hostname)
    except ValueError:
        ip_obj = None

    if ip_obj is not None and (
        ip_obj.is_private
        or ip_obj.is_loopback
        or ip_obj.is_link_local
        or ip_obj.is_multicast
        or ip_obj.is_reserved
    ):
        return False, "Private/internal targets are not allowed"

    if resolve_dns:
        try:
            resolved = socket.getaddrinfo(hostname, None)
        except socket.gaierror:
            return False, "Could not resolve hostname"

        for item in resolved:
            ip_text = item[4][0]
            try:
                resolved_ip_obj = ipaddress.ip_address(ip_text)
            except ValueError:
                continue
            if (
                resolved_ip_obj.is_private
                or resolved_ip_obj.is_loopback
                or resolved_ip_obj.is_link_local
                or resolved_ip_obj.is_multicast
                or resolved_ip_obj.is_reserved
            ):
                return False, "Private/internal targets are not allowed"

    return True, None


def _find_existing_audit(url, technical_data, email_draft):
    """
    Lightweight idempotency for n8n retries:
    if same url + same payload was recently saved, reuse existing row.
    """
    recent_audits = SiteAudit.objects.filter(url=url).order_by("-created_at")[:25]
    normalized_email = email_draft or ""
    for audit in recent_audits:
        if audit.raw_audit_data == technical_data and (audit.ai_strategy_email or "") == normalized_email:
            return audit
    return None


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class ContactMessageCreateView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ContactFormThrottle]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        if response.status_code == status.HTTP_201_CREATED:
            message_data = response.data
            subject = f"New Contact Message from {message_data['name']}"
            message_body = f"""
You have received a new contact message through your portfolio:

Name: {message_data['name']}
Email: {message_data['email']}
Message:
{message_data['message']}

Sent on: {message_data['sent_at']}
            """
            try:
                send_mail(
                    subject=subject,
                    message=message_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=False,
                )
            except Exception as exc:
                logger.warning("Contact email notification failed: %s", exc)

        return response


class BlogPostViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BlogPostSerializer

    def get_queryset(self):
        return BlogPost.objects.filter(published=True)


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ServiceSerializer

    def get_queryset(self):
        return Service.objects.filter(active=True)


class ServiceDetailView(generics.RetrieveAPIView):
    queryset = Service.objects.filter(active=True)
    serializer_class = ServiceSerializer
    lookup_field = "slug"


def send_inquiry_email_in_background(inquiry_data):
    """Sends the inquiry email notification in a background thread."""
    try:
        service_name = inquiry_data.get("service_name", "General Inquiry")
        subject = f"New Service Inquiry: {service_name}"
        message = f"""
New service inquiry received:

Name: {inquiry_data.get('name')}
Email: {inquiry_data.get('email')}
Company: {inquiry_data.get('company', 'Not provided')}
Service: {service_name}
Budget Range: {inquiry_data.get('budget_range', 'Not specified')}
Timeline: {inquiry_data.get('timeline', 'Not specified')}
Phone: {inquiry_data.get('phone', 'Not provided')}
Website: {inquiry_data.get('website_url', 'Not provided')}

Project Details:
{inquiry_data.get('project_details')}
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )
    except Exception as exc:
        logger.warning("Service inquiry email failed: %s", exc)


class ServiceInquiryCreateView(generics.CreateAPIView):
    queryset = ServiceInquiry.objects.all()
    serializer_class = ServiceInquirySerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ServiceInquiryThrottle]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        if response.status_code == status.HTTP_201_CREATED:
            inquiry_data = response.data
            email_thread = threading.Thread(
                target=send_inquiry_email_in_background,
                args=(inquiry_data,),
                daemon=True,
            )
            email_thread.start()

        return response


@method_decorator(csrf_exempt, name="dispatch")
class NewsletterSignupView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_classes = [NewsletterSignupThrottle]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        mailchimp_api_key = getattr(settings, "MAILCHIMP_API_KEY", None)
        mailchimp_data_center = getattr(settings, "MAILCHIMP_DATA_CENTER", None)
        mailchimp_audience_id = getattr(settings, "MAILCHIMP_AUDIENCE_ID", None)

        if not all([mailchimp_api_key, mailchimp_data_center, mailchimp_audience_id]):
            logger.error("Newsletter signup requested but Mailchimp is not configured.")
            return Response(
                {"error": "Newsletter signup is temporarily unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        api_url = f"https://{mailchimp_data_center}.api.mailchimp.com/3.0/lists/{mailchimp_audience_id}/members"

        headers = {
            "Authorization": f"apikey {mailchimp_api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "email_address": email,
            "status": "subscribed",
        }

        try:
            resp = requests.post(api_url, headers=headers, data=json.dumps(data), timeout=15)
            resp.raise_for_status()
            return Response({"message": "Successfully subscribed!"}, status=status.HTTP_201_CREATED)
        except requests.exceptions.HTTPError as err:
            status_code = err.response.status_code if err.response is not None else 400
            logger.info("Newsletter signup rejected by Mailchimp: status=%s", status_code)
            if status_code == status.HTTP_400_BAD_REQUEST:
                return Response(
                    {"error": "Unable to process this signup request."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"error": "Newsletter signup is temporarily unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception:
            logger.exception("Newsletter signup failed")
            return Response(
                {"error": "Newsletter signup is temporarily unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


def blog_post_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, published=True)

    data = {
        "id": post.id,
        "title": post.title,
        "content": sanitize_rich_html(post.content),
        "excerpt": post.excerpt,
        "author": str(post.author),
        "published_date": post.published_date,
        "slug": post.slug,
        "featured_image": post.featured_image.url if post.featured_image else None,
        "read_time": post.read_time,
    }
    return JsonResponse(data)


@staff_member_required
def audit_dashboard_view(request):
    return render(request, "admin/audit_dashboard.html")


@require_POST
def run_audit_api(request):
    """Staff-only endpoint for synchronous dashboard audits."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({"error": "forbidden"}, status=403)

    if not getattr(settings, "ALLOW_REMOTE_AUDIT_EXECUTION", False):
        return JsonResponse(
            {
                "error": (
                    "remote_audit_execution_disabled; "
                    "submit completed audit results via /api/audits/from-n8n/"
                )
            },
            status=503,
        )

    url, error = _parse_audit_payload(request)
    if error:
        return error

    is_public_target, reason = _is_public_target(url, resolve_dns=True)
    if not is_public_target:
        return JsonResponse({"error": reason}, status=400)

    try:
        auditor = SiteAuditor(url)
        result = auditor.run_audit()
        SiteAudit.from_audit_result(url, result)
        return JsonResponse(result, status=200)
    except Exception:
        logger.exception("run_audit_api failed")
        return JsonResponse({"error": "audit_failed"}, status=500)


@csrf_exempt
@require_POST
def run_audit_from_n8n(request):
    """
    Key-protected n8n endpoint.

    Preferred mode:
    - n8n sends completed audit payload (technical_data/email_draft) and Django only persists it.

    Compatibility mode:
    - if ALLOW_REMOTE_AUDIT_EXECUTION=true and no technical_data is provided,
      Django will enqueue local server-side audit execution.
    """
    incoming_key = request.headers.get("X-N8N-KEY")
    expected_key = getattr(settings, "N8N_DJANGO_API_KEY", "")

    if not expected_key or incoming_key != expected_key:
        logger.warning("Invalid N8N key from %s", request.META.get("REMOTE_ADDR"))
        return JsonResponse({"error": "unauthorized"}, status=401)

    payload, parse_error = _parse_json_payload(request)
    if parse_error:
        return parse_error

    url = (payload.get("url") or "").strip()
    if not url:
        return JsonResponse({"error": "URL is required"}, status=400)

    technical_data = payload.get("technical_data")
    email_draft = payload.get("email_draft", "")

    try:
        if technical_data is not None:
            if not isinstance(technical_data, dict):
                return JsonResponse({"error": "technical_data must be an object"}, status=400)

            # In ingest mode, avoid live DNS lookups; validate shape/host only.
            is_allowed_target, reason = _is_public_target(url, resolve_dns=False)
            if not is_allowed_target:
                return JsonResponse({"error": reason}, status=400)

            existing_audit = _find_existing_audit(url, technical_data, email_draft)
            if existing_audit is not None:
                return JsonResponse(
                    {"status": "already_saved", "url": url, "audit_id": existing_audit.id},
                    status=200,
                )

            result = {
                "technical_data": technical_data,
                "email_draft": email_draft,
            }
            saved_audit = SiteAudit.from_audit_result(url, result)
            return JsonResponse(
                {"status": "saved", "url": url, "audit_id": saved_audit.id},
                status=201,
            )

        if not getattr(settings, "ALLOW_REMOTE_AUDIT_EXECUTION", False):
            return JsonResponse(
                {
                    "error": (
                        "technical_data is required when remote audit execution is disabled"
                    )
                },
                status=400,
            )

        is_public_target, reason = _is_public_target(url, resolve_dns=True)
        if not is_public_target:
            return JsonResponse({"error": reason}, status=400)

        run_site_audit_task.delay(url)
        return JsonResponse({"status": "queued", "url": url}, status=202)
    except Exception:
        logger.exception("run_audit_from_n8n failed")
        return JsonResponse({"error": "audit_processing_failed"}, status=500)
