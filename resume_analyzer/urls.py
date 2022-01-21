from django.urls import path

from .views import upload_resume

urlpatterns = [
    path("", upload_resume, name="tailored_vacancies"),
]
