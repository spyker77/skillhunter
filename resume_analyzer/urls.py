from django.urls import path

from .views import UploadResumeView

urlpatterns = [
    path("", UploadResumeView.as_view(), name="upload-resume"),
]
