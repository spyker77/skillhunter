import os

from django.conf import settings

import pytest


class TestSettings:
    def test_settings_production_variables(self):
        if os.environ["ENVIRONMENT"] == "production":
            assert settings.X_FRAME_OPTIONS
            assert settings.SECURE_BROWSER_XSS_FILTER
            assert settings.SECURE_REFERRER_POLICY
            assert settings.SECURE_SSL_REDIRECT
            assert settings.SECURE_PROXY_SSL_HEADER
            assert settings.SECURE_HSTS_SECONDS
            assert settings.SECURE_HSTS_INCLUDE_SUBDOMAINS
            assert settings.SECURE_HSTS_PRELOAD
            assert settings.SECURE_CONTENT_TYPE_NONSNIFF
            assert settings.SESSION_COOKIE_SECURE
            assert settings.CSRF_COOKIE_SECURE
            assert settings.DATABASES
            assert settings.CACHES

    def test_settings_debug_variables(self):
        if os.environ["DEBUG"] == "True":
            assert settings.DEBUG_TOOLBAR_CONFIG
            assert len(settings.CSP_SCRIPT_SRC) == 2
            assert len(settings.CSP_STYLE_SRC) == 2
