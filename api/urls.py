from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("v3/", include("api.v3.urls")),
    path("auth/", include("rest_framework.urls")),
    path("auth-token/", obtain_auth_token),
]
