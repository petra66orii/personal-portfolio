from django.core.exceptions import PermissionDenied
from django.urls import reverse
import os

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Normalize the path to ensure it starts/ends with slashes for comparison
        admin_path = os.environ.get('DJANGO_ADMIN_URL', 'admin/')
        self.admin_url_path = f"/{admin_path.strip('/')}/"

    def __call__(self, request):
        # Check if the user is trying to access the admin area
        if request.path.startswith(self.admin_url_path):
            # 1. Allow the login page
            if 'login' in request.path:
                return self.get_response(request)
            
            # 2. Also allow the logout page just in case
            if 'logout' in request.path:
                 return self.get_response(request)

            # 3. If NOT on login page, AND not staff, then block.
            if not request.user.is_authenticated or not request.user.is_staff:
                raise PermissionDenied

        response = self.get_response(request)
        return response