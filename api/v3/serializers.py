from rest_framework import serializers

from scrapers.models import Job, Skill, Vacancy


class VacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = ["id", "url", "title", "content", "rated_skills"]
        read_only_fields = ["id"]


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ["id", "title"]
        read_only_fields = ["id"]


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "clean_name", "unclean_names"]
        read_only_fields = ["id"]


class RatedSkillSerializer(serializers.Serializer):
    skill = serializers.CharField(max_length=255)
    frequency = serializers.IntegerField()


class TailoredSkillsSerializer(serializers.Serializer):
    vacancy_name = serializers.CharField(max_length=255)
    number_of_vacancies = serializers.IntegerField()
    rated_skills = RatedSkillSerializer(many=True)


class TailoredVacancySerializer(serializers.Serializer):
    url = serializers.URLField(max_length=255)
    title = serializers.CharField(max_length=255)
    skills_frequency = serializers.IntegerField()


class ResumeSerializer(serializers.Serializer):
    file = serializers.FileField()

    class Meta:
        fields = ["file"]
