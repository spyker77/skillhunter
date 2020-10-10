from django.conf import settings


class TestSettings:
    def test_settings_production_variables(self):
        if settings.ENVIRONMENT == "production":
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