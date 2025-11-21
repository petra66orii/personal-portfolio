import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.views.generic import TemplateView
from .views import permission_denied_view

handler403 = permission_denied_view

urlpatterns = [
    path(os.environ.get('DJANGO_ADMIN_URL', 'admin/'), admin.site.urls),
    path('summernote/', include('django_summernote.urls')),
    path('api/', include('portfolio.urls')),
]

# Serve media files. Static files are handled by WhiteNoise.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# Redirect all other paths to index.html, but exclude static/, admin/, api/, and media/ so those are served normally
urlpatterns += [
    re_path(r'^(?!static/|admin/|api/|media/).*$', TemplateView.as_view(template_name="index.html")),
]