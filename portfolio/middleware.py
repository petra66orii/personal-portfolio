from django.shortcuts import redirect
from django.http import HttpResponsePermanentRedirect
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


class CanonicalUrlMiddleware:
    """
    Enforces canonical host and normalizes trailing slashes only for known SEO routes.
    """

    STATIC_CANONICAL_PATHS = {
        "/",
        "/about",
        "/services",
        "/blog",
        "/contact",
        "/custom-web-development-agency",
        "/custom-web-developer-ireland",
        "/web-development-agency-galway",
        "/web-development-agency-dublin",
        "/django-react-developer",
        "/international-web-development",
        "/web-developer-ireland",
    }

    def __init__(self, get_response):
        self.get_response = get_response
        self.canonical_host = os.environ.get("CANONICAL_HOST", "missbott.online").lower()

    def _is_known_canonical_path(self, path: str) -> bool:
        if path in self.STATIC_CANONICAL_PATHS:
            return True

        if path.startswith("/services/") and path.count("/") == 2:
            return True

        if path.startswith("/blog/") and path.count("/") == 2:
            return True

        return False

    def __call__(self, request):
        if request.method not in {"GET", "HEAD"}:
            return self.get_response(request)

        host = request.get_host().split(":")[0].lower()
        path = request.path
        query_string = request.META.get("QUERY_STRING")
        query_suffix = f"?{query_string}" if query_string else ""

        needs_host_redirect = self.canonical_host and host == f"www.{self.canonical_host}"
        needs_slash_redirect = (
            path != "/"
            and path.endswith("/")
            and self._is_known_canonical_path(path.rstrip("/"))
        )

        if needs_host_redirect or needs_slash_redirect:
            normalized_path = path.rstrip("/") if needs_slash_redirect else path
            target_host = self.canonical_host if needs_host_redirect else host
            target = f"https://{target_host}{normalized_path}{query_suffix}"
            return HttpResponsePermanentRedirect(target)

        return self.get_response(request)


class IndexingDirectivesMiddleware:
    """
    Adds noindex directives to utility pages that should not compete in search results.
    """

    NOINDEX_PATHS = {
        "/quote",
        "/quote/",
        "/privacy-policy",
        "/privacy-policy/",
        "/cookie-policy",
        "/cookie-policy/",
        "/terms-of-use",
        "/terms-of-use/",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path in self.NOINDEX_PATHS:
            response["X-Robots-Tag"] = "noindex, nofollow"
        return response
