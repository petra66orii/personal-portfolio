import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.views.generic import TemplateView
from django.http import HttpResponse
from .views import permission_denied_view
from portfolio import views
from django.contrib.sitemaps.views import index as sitemap_index
from django.contrib.sitemaps.views import sitemap as sitemap_view

from portfolio.sitemaps import StaticViewSitemap, BlogPostSitemap, ProjectSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "blog": BlogPostSitemap,
    "projects": ProjectSitemap,
}

handler403 = permission_denied_view

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Sitemap: https://missbott.online/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

react_app = TemplateView.as_view(template_name="index.html")

# Get the admin URL from env or default to 'admin/'
# Standardizing this variable so we don't mix hardcoded strings
ADMIN_URL = os.environ.get('DJANGO_ADMIN_URL', 'admin/')

urlpatterns = [
    path("sitemap.xml", sitemap_index, {"sitemaps": sitemaps}, name="django-sitemap-index"),
    path("sitemap-<section>.xml", sitemap_view, {"sitemaps": sitemaps}, name="django-sitemap"),
    path("robots.txt", robots_txt, name="robots-txt"),
    path(f'{ADMIN_URL}/consultant-dashboard/', views.audit_dashboard_view, name='consultant_dashboard'),
    path('api/run-audit/', views.run_audit_api, name='run_audit_api'),
    path(f'{ADMIN_URL}', admin.site.urls),
    path('summernote/', include('django_summernote.urls')),
    path('api/', include('portfolio.urls')),
    path("api/audits/from-n8n/", views.run_audit_api, name="run_audit_from_n8n"),
    path("", react_app, name="home"),
    path("services", react_app, name="services"),
    path("services/strategic-discovery-session", react_app, name="service_discovery"),
    path("services/foundation-stack", react_app, name="service_foundation"),
    path("services/commerce-stack", react_app, name="service_commerce"),
    path("services/application-stack", react_app, name="service_application"),
    path("blog", react_app, name="blog_index"),
    path("contact", react_app, name="contact"),
    ]

# Serve media files
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

urlpatterns += [
    re_path(
    r'^(?!static/|admin/|adminportal/|api/|media/|sitemap\.xml$|robots\.txt$).*$', 
    TemplateView.as_view(template_name="index.html")
),
]