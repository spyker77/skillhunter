from django.contrib import admin
from django.conf import settings
from django.urls import path, include, re_path
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import GenericSitemap

from scrapers.models import Job
from pages.sitemaps import StaticViewSitemap

admin.site.site_header = "SkillHunter admin panel"
admin.site.site_title = "SkillHunter"

job_title_links = {
    "queryset": Job.objects.all(),
}

urlpatterns = [
    path("administration/", admin.site.urls),
    path("", include("pages.urls")),
    path("search/", include("scrapers.urls")),
    re_path(r"^api/v1/", include(("api.v1.urls", "api"), namespace="v1")),
    re_path(r"^robots\.txt", include("robots.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {
            "sitemaps": {
                "static": StaticViewSitemap,
                "dynamic": GenericSitemap(job_title_links),
            }
        },
        name="django.contrib.sitemaps.views.sitemap",
    ),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
