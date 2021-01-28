from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from django_otp.admin import OTPAdminSite
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from pages.sitemaps import StaticViewSitemap
from scrapers.models import Job

API_VERSION_V1 = "v1"

admin.site.site_header = "SkillHunter admin panel"
admin.site.site_title = "SkillHunter"
# Enforce 2FA while login into admin panel.
admin.site.__class__ = OTPAdminSite

job_title_links = {"queryset": Job.objects.all()}

urlpatterns = [
    path("administration/", admin.site.urls),
    path("", include("pages.urls")),
    path("search/", include("scrapers.urls")),
    re_path(r"^robots\.txt", include("robots.urls")),
    re_path(r"^api/v1/", include(("api.v1.urls", "api"), namespace=API_VERSION_V1)),
    # Create docs for API.
    path(
        "schema/", SpectacularAPIView.as_view(api_version=API_VERSION_V1), name="schema"
    ),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(
            template_name="swagger-ui.html", url_name="schema"
        ),
        name="swagger-ui",
    ),
    # Create sitemap.xml.
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
