from django.urls import path
from django.views.decorators.cache import cache_page

from .views import AboutPageView, HomePageView

CACHE_SECONDS = 12 * 60 * 60

urlpatterns = [
    path("", cache_page(CACHE_SECONDS)(HomePageView.as_view()), name="home"),
    path("about/", cache_page(CACHE_SECONDS)(AboutPageView.as_view()), name="about"),
]
