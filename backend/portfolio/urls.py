from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, SkillViewSet, ContactMessageCreateView

router = DefaultRouter()
router.register('projects', ProjectViewSet)
router.register('skills', SkillViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('contact/', ContactMessageCreateView.as_view(), name='contact'),
]
