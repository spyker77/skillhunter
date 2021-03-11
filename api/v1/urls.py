from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.views import SkillViewSet

router = DefaultRouter()
router.register(r"skills", SkillViewSet, basename="skill")

urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]
