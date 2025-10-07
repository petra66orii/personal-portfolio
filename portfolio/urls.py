from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet, 
    ContactMessageCreateView, 
    BlogPostViewSet,
    ServiceViewSet,
    ServiceInquiryCreateView,
    CredentialViewSet,
    ServiceDetailView
)

router = DefaultRouter()
router.register('projects', ProjectViewSet)
router.register('blog', BlogPostViewSet, basename='blogpost')
router.register('services', ServiceViewSet, basename='service')

urlpatterns = [
    path('', include(router.urls)),
    path('contact/', ContactMessageCreateView.as_view(), name='contact'),
    path('service-inquiry/', ServiceInquiryCreateView.as_view(), name='service-inquiry'),
    path('credentials/', CredentialViewSet.as_view({'get': 'list'}), name='credentials'),
    path('services/<slug:slug>/', ServiceDetailView.as_view(), name='service-detail'),
]
