from django.shortcuts import redirect
import os
from urllib.parse import quote

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Normalize the path to ensure it starts/ends with slashes for comparison
        admin_path = os.environ.get('DJANGO_ADMIN_URL', 'admin/')
        self.admin_url_path = f"/{admin_path.strip('/')}/"

    def __call__(self, request):
        # Check if the user is trying to access the admin area
        if request.path.startswith(self.admin_url_path):
            login_path = f"{self.admin_url_path}login/"
            logout_path = f"{self.admin_url_path}logout/"

            # Allow auth endpoints.
            if request.path.startswith(login_path):
                return self.get_response(request)

            if request.path.startswith(logout_path):
                return self.get_response(request)

            # Non-staff/non-authenticated users should be redirected to login.
            # Returning 403 here blocks Django's normal admin login flow.
            if not request.user.is_authenticated or not request.user.is_staff:
                next_param = quote(request.get_full_path(), safe="")
                return redirect(f"{login_path}?next={next_param}")

        response = self.get_response(request)
        return response
