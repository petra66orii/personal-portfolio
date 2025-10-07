from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Sends a test email to the configured ADMIN_EMAIL.'

    def handle(self, *args, **options):
        self.stdout.write("Attempting to send a test email...")
        
        subject = 'Django Test Email'
        message = 'If you are seeing this, your email settings are configured correctly.'
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('Successfully sent the test email!'))
            self.stdout.write(f"Check the inbox for {settings.ADMIN_EMAIL}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR('Failed to send the test email.'))
            self.stderr.write(f"Error: {e}")
            self.stdout.write("Check your .env file and email settings in settings.py.")
