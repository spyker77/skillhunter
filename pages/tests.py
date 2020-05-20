from django.urls import reverse, resolve

from .views import HomePageView, AboutPageView

import pytest


class TestHomePage:
    @pytest.fixture
    def response(self, client):
        self.url = reverse("home")
        return client.get(self.url)

    def test_homepage_status_code(self, response):
        assert response.status_code == 200

    def test_homepage_template(self, response):
        assert "home.html" in response.template_name

    def test_homepage_contains_correct_html(self, response):
        assert "Skillhunter" in response.rendered_content

    def test_homepage_does_not_contains_incorrect_html(self, response):
        assert "Hi there! I should not be on the page." not in response.rendered_content

    def test_homepage_url_resolves_homepageview(self):
        self.view = resolve("/")
        assert self.view.func.__name__ == HomePageView.as_view().__name__


class TestAboutPage:
    @pytest.fixture
    def response(self, client):
        self.url = reverse("about")
        return client.get(self.url)

    def test_aboutpage_status_code(self, response):
        assert response.status_code == 200

    def test_aboutpage_template(self, response):
        assert "about.html" in response.template_name

    def test_aboutpage_contains_correct_html(self, response):
        assert "About" in response.rendered_content

    def test_aboutpage_does_not_contains_incorrect_html(self, response):
        assert "Hi there! I should not be on the page." not in response.rendered_content

    def test_aboutpage_url_resolves_aboutpageview(self):
        self.view = resolve("/about/")
        assert self.view.func.__name__ == AboutPageView.as_view().__name__
