from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    def items(self):
        return ["home", "about", "swagger-ui", "fastapi-docs", "fastapi-redoc"]

    def location(self, item):
        return reverse(item)
