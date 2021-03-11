from django.urls import path

from resume_analyzer import views

urlpatterns = [
    path("", views.upload_resume, name="tailored_vacancies"),
]
