from rest_framework import viewsets, generics, status
from django.core.mail import send_mail
from django.conf import settings
from .models import Project, Skill, ContactMessage
from .serializers import (
    ProjectSerializer,
    SkillSerializer,
    ContactMessageSerializer
)


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


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
