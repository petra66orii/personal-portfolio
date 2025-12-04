import requests
import json
import threading
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, generics, status
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import permissions
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Project, ContactMessage, BlogPost, Service, ServiceInquiry, SiteAudit
from .serializers import (
    ProjectSerializer,
    ContactMessageSerializer,
    BlogPostSerializer,
    ServiceSerializer,
    ServiceInquirySerializer,
)
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from scripts.auditor import SiteAuditor 


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class ContactMessageCreateView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        # Create the contact message in the database
        response = super().create(request, *args, **kwargs)

        if response.status_code == status.HTTP_201_CREATED:
            # Get the created contact message data
            message_data = response.data

            # Send email notification
            try:
                subject = f"New Contact Message from {message_data['name']}"
                message_body = f"""
You have received a new contact message through your portfolio:

Name: {message_data['name']}
Email: {message_data['email']}
Message:
{message_data['message']}

Sent on: {message_data['sent_at']}
                """

                print(f"Attempting to send email from: {settings.DEFAULT_FROM_EMAIL}")
                print(f"Sending to: {settings.ADMIN_EMAIL}")
                print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
                print(f"EMAIL_HOST configured: {'EMAIL_HOST_PASSWORD' in dir(settings)}")

                send_mail(
                    subject=subject,
                    message=message_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=False,
                )
                print("Email sent successfully!")
            except Exception as e:
                # Log the error but don't fail the request
                print(f"Failed to send email notification: {e}")
                print(f"Error type: {type(e).__name__}")
                import traceback
                print(f"Full traceback: {traceback.format_exc()}")

        return response


class BlogPostViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for blog posts. Only returns published posts.
    """
    serializer_class = BlogPostSerializer
    
    def get_queryset(self):
        # Only return published blog posts
        return BlogPost.objects.filter(published=True)


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for services. Only returns active services.
    """
    serializer_class = ServiceSerializer
    
    def get_queryset(self):
        return Service.objects.filter(active=True)


class ServiceDetailView(generics.RetrieveAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    lookup_field = 'slug'


class ServiceInquiryCreateView(generics.CreateAPIView):
    """
    Create a new service inquiry and send email notification.
    """
    queryset = ServiceInquiry.objects.all()
    serializer_class = ServiceInquirySerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        # Create the service inquiry in the database
        response = super().create(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_201_CREATED:
            inquiry_data = response.data
            service_name = inquiry_data.get('service_name', 'General Inquiry')
            
            try:
                # Send email notification to admin
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
                
            except Exception as e:
                print(f"Error sending service inquiry email: {e}")
        
        return response

def send_inquiry_email_in_background(inquiry_data):
    """Sends the inquiry email notification in a separate thread."""
    try:
        service_name = inquiry_data.get('service_name', 'General Inquiry')
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
        print("Successfully sent service inquiry email.")
    except Exception as e:
        # This error will now only appear in your server logs, not affect the user.
        print(f"Error sending service inquiry email in background: {e}")


class ServiceInquiryCreateView(generics.CreateAPIView):
    queryset = ServiceInquiry.objects.all()
    serializer_class = ServiceInquirySerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        # Create the service inquiry in the database
        response = super().create(request, *args, **kwargs)
        
        # If the database write was successful...
        if response.status_code == status.HTTP_201_CREATED:
            inquiry_data = response.data
            
            # Start the email sending in a background thread
            email_thread = threading.Thread(
                target=send_inquiry_email_in_background, 
                args=(inquiry_data,)
            )
            email_thread.start()
        
        # Return the successful response to the user IMMEDIATELY
        return response


@method_decorator(csrf_exempt, name='dispatch')
class NewsletterSignupView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        MAILCHIMP_API_KEY = getattr(settings, "MAILCHIMP_API_KEY", None)
        MAILCHIMP_DATA_CENTER = getattr(settings, "MAILCHIMP_DATA_CENTER", None)
        MAILCHIMP_AUDIENCE_ID = getattr(settings, "MAILCHIMP_AUDIENCE_ID", None)

        if not all([MAILCHIMP_API_KEY, MAILCHIMP_DATA_CENTER, MAILCHIMP_AUDIENCE_ID]):
             return Response({'error': 'Mailchimp settings not configured.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        api_url = f'https://{MAILCHIMP_DATA_CENTER}.api.mailchimp.com/3.0/lists/{MAILCHIMP_AUDIENCE_ID}/members'
        
        headers = {
            'Authorization': f'apikey {MAILCHIMP_API_KEY}',
            'Content-Type': 'application/json',
        }
        
        data = {
            'email_address': email,
            'status': 'subscribed',
        }

        try:
            r = requests.post(api_url, headers=headers, data=json.dumps(data))
            r.raise_for_status()
            return Response({'message': 'Successfully subscribed!'}, status=status.HTTP_201_CREATED)
        except requests.exceptions.HTTPError as err:
            error_json = err.response.json()
            error_detail = error_json.get('detail', 'An error occurred.')
            return Response({'error': error_detail}, status=err.response.status_code)
        except Exception:
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
def blog_post_detail(request, slug):
    print(f"\n🔍 DEBUG: View called with slug: '{slug}'")
    
    # 1. Check if ANY posts exist
    count = BlogPost.objects.count()
    print(f"📊 DEBUG: Total posts in DB: {count}")

    # 2. Try to find it manually (bypassing get_object_or_404 for a second)
    try:
        post = BlogPost.objects.get(slug=slug)
        print(f"✅ DEBUG: Found post: {post.title}")
    except BlogPost.DoesNotExist:
        print(f"❌ DEBUG: Post NOT found for slug: '{slug}'")
        
        # 3. Print all available slugs to compare
        print("📋 DEBUG: Available slugs in DB:")
        for p in BlogPost.objects.all():
            print(f"   -> '{p.slug}'")
        
        # Re-raise the 404 so Django handles it
        post = get_object_or_404(BlogPost, slug=slug)

    data = {
        "id": post.id,
        "title": post.title,
        "content": post.content, 
        "excerpt": post.excerpt,
        "author": str(post.author), 
        "published_date": post.published_date,
        "slug": post.slug,
        "featured_image": post.featured_image.url if post.featured_image else None,
        "read_time": post.read_time
    }
    
    return JsonResponse(data)

@staff_member_required
def audit_dashboard_view(request):
    return render(request, "admin/audit_dashboard.html")


@require_POST
@staff_member_required
def run_audit_api(request):
    try:
        data = json.loads(request.body)
        url = data.get("url")

        if not url:
            return JsonResponse({"error": "URL is required"}, status=400)

        auditor = SiteAuditor(url)
        result = auditor.run_audit()  # full dict for React

        # 🔁 reuse the same persistence logic as admin action
        SiteAudit.from_audit_result(url, result)

        # Frontend still gets the full result
        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)