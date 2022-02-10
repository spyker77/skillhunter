from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    JobViewSet,
    SkillViewSet,
    TailoredSkillsViewSet,
    TailoredVacanciesViewSet,
    VacancyViewSet,
)

router = DefaultRouter()
router.register(r"vacancy", VacancyViewSet, basename="vacancy")
router.register(r"job", JobViewSet, basename="job")
router.register(r"skill", SkillViewSet, basename="skill")
router.register(r"tailored-skills", TailoredSkillsViewSet, basename="tailored-skills")
router.register(r"tailored-vacancies", TailoredVacanciesViewSet, basename="tailored-vacancies")

urlpatterns = [
    path("", include(router.urls)),
]
