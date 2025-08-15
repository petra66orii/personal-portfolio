from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('portfolio.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Redirect all other paths to index.html, but exclude static/, assets/, admin/, and api/ so those are served normally
urlpatterns += [
    re_path(r'^(?!static/|assets/|admin/|api/).*$', TemplateView.as_view(template_name="index.html")),
]