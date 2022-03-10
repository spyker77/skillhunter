from django.urls import include, path

urlpatterns = [
    path("v3/", include("api.v3.urls")),
]
