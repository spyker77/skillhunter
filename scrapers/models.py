import uuid
from django.db import models
from django.utils import timezone


class Vacancy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=200, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    rated_skills = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=["id"], name="id_index"),
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


class Skill(models.Model):
    name = models.CharField(max_length=50)
    type_hard = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Stopword(models.Model):
    LANGUAGES = (
        ("EN", "English"),
        ("RU", "Russian"),
    )
    name = models.CharField(max_length=50)
    language = models.CharField(max_length=2, choices=LANGUAGES)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
