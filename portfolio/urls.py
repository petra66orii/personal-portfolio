from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, SkillViewSet

router = DefaultRouter()
router.register('projects', ProjectViewSet)
router.register('skills', SkillViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
