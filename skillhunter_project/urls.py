from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from pages.sitemaps import StaticViewSitemap

admin.site.site_header = "SkillHunter admin panel"
admin.site.site_title = "SkillHunter"

sitemaps = {
    "static": StaticViewSitemap,
}

urlpatterns = [
    path("administration/", admin.site.urls),
    path("", include("pages.urls")),
    path("search/", include("scrapers.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    url(r"^robots\.txt", include("robots.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls)),] + urlpatterns
