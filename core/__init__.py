"""SkillHunter helps you identify most in-demand skills in the job market."""

from .celery import app as celery_app

__all__ = ("celery_app",)
