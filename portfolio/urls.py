from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet, 
    ContactMessageCreateView, 
    BlogPostViewSet,
    ServiceViewSet,
    ServiceInquiryCreateView,
    ServiceDetailView,
    NewsletterSignupView
)

router = DefaultRouter()
router.register('projects', ProjectViewSet)
router.register('blog', BlogPostViewSet, basename='blogpost')

urlpatterns = [
    path('', include(router.urls)),
    path('contact/', ContactMessageCreateView.as_view(), name='contact'),
    path('service-inquiry/', ServiceInquiryCreateView.as_view(), name='service-inquiry'),
    path('services/', ServiceViewSet.as_view({'get': 'list'}), name='service-list'),
    path('services/<slug:slug>/', ServiceDetailView.as_view(), name='service-detail'),
    path('newsletter-signup/', NewsletterSignupView.as_view(), name='newsletter-signup'),
]
