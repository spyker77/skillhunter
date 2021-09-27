from rest_framework import serializers

from scrapers.models import Vacancy


class VacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = ["title", "content", "rated_skills"]
