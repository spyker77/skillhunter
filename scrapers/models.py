import uuid
from django.db import models
from django.utils import timezone
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField


class Vacancy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=200, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    rated_skills = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    search_vector = SearchVectorField(null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Vacancies"
        indexes = [
            GinIndex(fields=["search_vector"], name="search_vector_idx"),
        ]


class Job(models.Model):
    title = models.CharField(max_length=50)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]


class Search(models.Model):
    query = models.CharField(max_length=200)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.query

    class Meta:
        verbose_name_plural = "Searches"


class Skill(models.Model):
    clean_name = models.CharField(max_length=50)
    unclean_names = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.clean_name

    class Meta:
        ordering = ["clean_name"]
