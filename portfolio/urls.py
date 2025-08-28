from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet, 
    SkillViewSet, 
    ContactMessageCreateView, 
    BlogPostViewSet,
    ServiceViewSet,
    ServiceInquiryCreateView,
    CredentialViewSet
)

router = DefaultRouter()
router.register('projects', ProjectViewSet)
router.register('skills', SkillViewSet)
router.register('blog', BlogPostViewSet, basename='blogpost')
router.register('services', ServiceViewSet, basename='service')

urlpatterns = [
    path('', include(router.urls)),
    path('contact/', ContactMessageCreateView.as_view(), name='contact'),
    path('service-inquiry/', ServiceInquiryCreateView.as_view(), name='service-inquiry'),
    path('credentials/', CredentialViewSet.as_view({'get': 'list'}), name='credentials'),
]
