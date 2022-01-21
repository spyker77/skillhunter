import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from django.views.generic.base import TemplateView
from django_otp.admin import OTPAdminSite
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from pages.sitemaps import StaticViewSitemap
from scrapers.models import Job

admin.site.site_header = "SkillHunter admin panel"
admin.site.site_title = "SkillHunter"
# Enforce 2FA while login into admin panel.
admin.site.__class__ = OTPAdminSite


urlpatterns = [
    path("__debug__/", include(debug_toolbar.urls)),
    path("administration/", admin.site.urls),
    path("", include("pages.urls")),
    path("search/", include("scrapers.urls")),
    path("tailored-vacancies/", include("resume_analyzer.urls")),
    re_path(r"^api/v1/", include(("api.v1.urls", "api"), namespace="v1")),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": {"static": StaticViewSitemap, "dynamic": GenericSitemap({"queryset": Job.objects.all()})}},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    # Swagger UI for DRF.
    path("schema/", SpectacularAPIView.as_view(api_version="v1"), name="schema"),
    path(
        "deprecated-docs/",
        SpectacularSwaggerView.as_view(template_name="swagger-ui.html", url_name="schema"),
        name="swagger-ui",
    ),
    # Default paths provided by FastAPI.
    path("docs", TemplateView.as_view(), name="fastapi-docs"),
    path("redoc", TemplateView.as_view(), name="fastapi-redoc"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
