import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.http import HttpResponse
from .views import permission_denied_view
from portfolio import views
from . import views as backend_views
from django.contrib.sitemaps.views import index as sitemap_index
from django.contrib.sitemaps.views import sitemap as sitemap_view

from portfolio.sitemaps import StaticViewSitemap, BlogPostSitemap, ServiceSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "blog": BlogPostSitemap,
    "services": ServiceSitemap,
}

handler403 = permission_denied_view

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /api/",
        "Allow: /",
        "Sitemap: https://missbott.online/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

react_app = TemplateView.as_view(template_name="index.html")

# Get the admin URL from env or default to 'admin/'
# Standardizing this variable so we don't mix hardcoded strings
ADMIN_URL = os.environ.get('DJANGO_ADMIN_URL', 'admin/')


def _should_serve_media_publicly() -> bool:
    explicit_value = os.environ.get("SERVE_MEDIA_PUBLICLY")
    if explicit_value is not None:
        return explicit_value.lower() == "true"

    if settings.DEBUG:
        return True

    return os.environ.get("RENDER", "").lower() != "true"

urlpatterns = [
   path(
        "sitemap.xml",
        sitemap_index,
        {"sitemaps": sitemaps, "sitemap_url_name": "django-sitemap"},
        name="django-sitemap-index",
    ),
    re_path(
        r"^sitemap-(?P<section>.+)\.xml$",
        sitemap_view,
        {"sitemaps": sitemaps},
        name="django-sitemap",
    ),
    path("robots.txt", robots_txt, name="robots-txt"),
    path(f'{ADMIN_URL}/consultant-dashboard/', views.audit_dashboard_view, name='consultant_dashboard'),
    path('api/run-audit/', views.run_audit_api, name='run_audit_api'),
    path(f'{ADMIN_URL}', admin.site.urls),
    path('summernote/', include('django_summernote.urls')),
    path("api/growth/", include("growth_ops.urls")),
    path('api/', include('portfolio.urls')),
    path("api/audits/from-n8n/", views.run_audit_from_n8n, name="run_audit_from_n8n"),
    path(
        "web-developer-ireland",
        RedirectView.as_view(url="/custom-web-developer-ireland", permanent=True),
        name="landing_web_developer_ireland_alias",
    ),
    path("quote", react_app, name="quote"),
    ]

serve_media_publicly = _should_serve_media_publicly()

if serve_media_publicly:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

urlpatterns += [
    re_path(
        r'^(?!static/|admin/|adminportal/|api/|media/|sitemap.*\.xml$|robots\.txt$).*$', 
        backend_views.react_frontend_entry,
    ),
]
