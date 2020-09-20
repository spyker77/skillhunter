from collections.abc import Sequence
from urllib.parse import urlparse

from django.urls import reverse, resolve
from django.db.models.query import QuerySet

from .views import HomePageView, AboutPageView
from .sitemaps import StaticViewSitemap

import pytest


class TestHomePage:
    @pytest.fixture
    def response(self, rf):
        url = reverse("home")
        request = rf.get(url)
        return HomePageView.as_view()(request)

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
    def response(self, rf):
        url = reverse("about")
        request = rf.get(url)
        return AboutPageView.as_view()(request)

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
