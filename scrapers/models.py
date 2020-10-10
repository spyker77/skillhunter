from urllib.parse import urlencode

import uuid
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField


class Vacancy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    rated_skills = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    search_vector = SearchVectorField(null=True)

    def __str__(self):
        """Return human-readable vacancy title for the record in the admin."""
        return self.title

    class Meta:
        """Custom plural name of the model and the index for a full text search."""

        verbose_name_plural = "Vacancies"
        indexes = [
            GinIndex(fields=["search_vector"], name="search_vector_idx"),
        ]


class Job(models.Model):
    title = models.CharField(max_length=50)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """Return human-readable job title for the record in the admin."""
        return self.title

    def get_absolute_url(self):
        job_title = self.title.lower()
        query = {"q": job_title}
        link_for_sitemap = reverse("search_results") + "?" + urlencode(query)
        return link_for_sitemap

    class Meta:
        """Default ordering by title in the Job section of the admin."""

        ordering = ["title"]


class Search(models.Model):
    query = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(default="1.1.1.1")
    user_agent = models.CharField(max_length=255, blank=True)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """Return human-readable user's query for the record in the admin."""
        return self.query

    class Meta:
        """Custom plural name of the model."""

        verbose_name_plural = "Searches"


class Skill(models.Model):
    clean_name = models.CharField(max_length=50)
    unclean_names = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """Return human-readable clean name of the skill for the record in the admin."""
        return self.clean_name

    class Meta:
        """Default ordering by clean name in the Skill section of the admin."""

        ordering = ["clean_name"]
