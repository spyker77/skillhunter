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


class Skill(models.Model):
    name = models.CharField(max_length=50)
    type_hard = models.BooleanField(default=True)

    def __str__(self):
        return self.name
