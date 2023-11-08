import pdftotext
from django.contrib.postgres.search import SearchQuery
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.tasks import save_query_with_metadata
from core.utils import parse_request
from resume_analyzer.analyzer import analyze_resume
from scrapers.models import Job, Skill, Vacancy
from scrapers.utils import sort_skills

from .serializers import (
    JobSerializer,
    ResumeSerializer,
    SkillSerializer,
    TailoredSkillsSerializer,
    TailoredVacancySerializer,
    VacancySerializer,
)


@extend_schema(tags=["vacancy"])
class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all().order_by("id")
    serializer_class = VacancySerializer


@extend_schema(tags=["job"])
class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by("id")
    serializer_class = JobSerializer


@extend_schema(tags=["skill"])
class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all().order_by("id")
    serializer_class = SkillSerializer


@extend_schema(tags=["tailored-skills"])
class TailoredSkillsViewSet(viewsets.GenericViewSet):
    serializer_class = TailoredSkillsSerializer
    pagination_class = None

    def get_queryset(self, query):
        search_query = SearchQuery(query)
        return Vacancy.objects.filter(search_vector=search_query)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="limit",
                type=int,
                required=False,
                description="A number of most wanted skills to display.",
            ),
            OpenApiParameter(
                name="q",
                required=True,
                description="A job title to be processed.",
            ),
        ],
        description="Specify a job title and get the ranked skills that companies look for.",
    )
    def list(self, request):
        query, limit, user_agent, ip_address = parse_request(request)
        save_query_with_metadata.delay(query, user_agent, ip_address)
        queryset = self.get_queryset(query)
        tailored_skills = sort_skills(queryset)[:limit]
        data = {
            "vacancy_name": query,
            "number_of_vacancies": queryset.count(),
            "rated_skills": tailored_skills,
        }
        return Response(data)


@extend_schema(tags=["tailored-vacancies"])
class TailoredVacanciesViewSet(viewsets.ViewSet):
    serializer_class = ResumeSerializer
    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]

    LIMIT_OF_VACANCIES = 200

    @extend_schema(
        responses={200: TailoredVacancySerializer(many=True)},
        description="Upload resume in PDF and get tailored vacancies.",
    )
    def create(self, request):
        try:
            tailored_vacancies = analyze_resume(request.FILES["resume"])
            return Response(tailored_vacancies[: self.LIMIT_OF_VACANCIES], status=status.HTTP_200_OK)
        except pdftotext.Error:
            return Response({"detail": "Vacancies not found."}, status=status.HTTP_404_NOT_FOUND)
