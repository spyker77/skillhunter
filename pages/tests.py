from pathlib import Path
from urllib.parse import urlparse
from collections.abc import Sequence

from django.urls import reverse, resolve
from django.db.models.query import QuerySet

from .views import HomePageView, AboutPageView
from .sitemaps import StaticViewSitemap
from .apps import PagesConfig

import pytest


class TestHomePage:
    @pytest.fixture
    def response(self, client):
        url = reverse("home")
        response = client.get(url, follow=True)
        return response

    def test_homepage_status_code(self, response):
        assert response.status_code == 200

    def test_homepage_template(self, response):
        assert "home.html" in response.template_name

    def test_homepage_contains_correct_html(self, response):
        assert "SkillHunter" in response.rendered_content

    def test_homepage_does_not_contains_incorrect_html(self, response):
        assert "Hi there! I should not be on the page." not in response.rendered_content

    def test_homepage_url_resolves_homepageview(self):
        view = resolve("/")
        assert view.func.__name__ == HomePageView.as_view().__name__


class TestAboutPage:
    @pytest.fixture
    def response(self, client):
        url = reverse("about")
        response = client.get(url, follow=True)
        return response

    def test_aboutpage_status_code(self, response):
        assert response.status_code == 200

    def test_aboutpage_template(self, response):
        assert "about.html" in response.template_name

    def test_aboutpage_contains_correct_html(self, response):
        assert "About" in response.rendered_content

    def test_aboutpage_does_not_contains_incorrect_html(self, response):
        assert "Hi there! I should not be on the page." not in response.rendered_content

    def test_aboutpage_url_resolves_aboutpageview(self):
        view = resolve("/about/")
        assert view.func.__name__ == AboutPageView.as_view().__name__


class TestStaticViewSitemap:
    def test_staticviewsitemap_items_type(self):
        items = StaticViewSitemap.items(self)
        assert isinstance(items, Sequence) or isinstance(items, QuerySet)

    def test_staticviewsitemap_items_location(self):
        items = StaticViewSitemap.items(self)
        for item in items:
            location = StaticViewSitemap.location(self, item)
            parsed_location = urlparse(location)
            assert isinstance(parsed_location.path, str)
            assert parsed_location.scheme == ""
            assert parsed_location.netloc == ""


class TestPagesConfig:
    def test_pagesconfig_name(self):
        app_path = Path(__file__).resolve().parent
        app_name = str(app_path).split("/")[-1]
        assert PagesConfig.name == app_name