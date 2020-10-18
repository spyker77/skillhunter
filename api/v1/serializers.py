from rest_framework import serializers


class SkillSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    content = serializers.CharField()
    rated_skills = serializers.CharField()
