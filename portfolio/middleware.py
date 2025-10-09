from django.core.exceptions import PermissionDenied
import os

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # We fetch the secret admin URL from your environment variables
        self.admin_url_path = f"/{os.environ.get('DJANGO_ADMIN_URL', 'admin/')}"

    def __call__(self, request):
        # Check if the requested path starts with the secret admin URL
        if request.path.startswith(self.admin_url_path):
            # If the user is not authenticated or not a staff member, deny permission.
            if not request.user.is_staff:
                raise PermissionDenied

        response = self.get_response(request)
        return response