import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.views.generic import TemplateView
from .views import permission_denied_view
from portfolio import views

handler403 = permission_denied_view

# Get the admin URL from env or default to 'admin/'
# Standardizing this variable so we don't mix hardcoded strings
ADMIN_URL = os.environ.get('DJANGO_ADMIN_URL', 'admin/')

urlpatterns = [
    path(f'{ADMIN_URL}/consultant-dashboard/', views.audit_dashboard_view, name='consultant_dashboard'),
    path('api/run-audit/', views.run_audit_api, name='run_audit_api'),
    path(ADMIN_URL, admin.site.urls),
    path('summernote/', include('django_summernote.urls')),
    path('api/', include('portfolio.urls')),
    path("api/audits/from-n8n/", views.run_audit_api, name="run_audit_from_n8n"),
]

# Serve media files
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

urlpatterns += [
    re_path(r'^(?!static/|admin/|adminportal/|api/|media/).*$', TemplateView.as_view(template_name="index.html")),
]