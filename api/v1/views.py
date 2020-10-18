import ast
from collections import defaultdict, OrderedDict

from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response

from scrapers.models import Vacancy, Search
from .serializers import SkillSerializer


class SkillViewSet(viewsets.ViewSet):
    """
    Returns a list of skills ordered by number of occurrences in vacancies description,
    including the job title and number of vacancies analyzed.

    Possible parameters:

    -   **q** - stands for job title (required)

    -   **limit** - stands for the number of most wanted skills (optional)

    -   **format** - stands for a specific data format, among which
    json/xml/yaml (optional)

    Example URI:

    -   https://skillhunter.app/api/v1/skills/?q=python+developer

    -   https://skillhunter.app/api/v1/skills/?q=python+developer&limit=20

    -   https://skillhunter.app/api/v1/skills/?q=python+developer&limit=20&format=xml
    """

    def _combine_rated_skills(self, rated_skills_to_merge):
        super_dict = defaultdict(list)
        for rated_skills in rated_skills_to_merge:
            if rated_skills != None:
                for k, v in rated_skills.items():
                    super_dict[k].append(v)
        return super_dict

    def _sort_skills(self, serialized_data):
        # Get rated skills for each vacancy and convert it from str to dict.
        rated_skills_to_merge = (
            ast.literal_eval(vacancy.get("rated_skills")) for vacancy in serialized_data
        )
        # Combine skills from all suitable vacancies into one dict.
        super_dict = self._combine_rated_skills(rated_skills_to_merge)
        # Summ skills that are the same.
        merged_skills = {k: sum(v) for k, v in super_dict.items()}
        # Sort summed skills in descending order.
        sorted_skills = sorted(merged_skills.items(), key=lambda x: x[1], reverse=True)
        return sorted_skills

    def _get_meta_data(self, request):
        query = self.request.query_params.get("q")
        limit = self.request.query_params.get("limit")
        ip_address = self.request.META.get("REMOTE_ADDR")
        user_agent = self.request.META.get("HTTP_USER_AGENT")
        # Additionally, save the search query for future analysis.
        if query and settings.ENVIRONMENT == "production":
            Search.objects.create(
                query=query, ip_address=ip_address, user_agent=user_agent
            )
        return query, limit

    def list(self, request):
        query, limit = self._get_meta_data(request)
        queryset = Vacancy.objects.filter(search_vector=query)
        serializer = SkillSerializer(queryset, many=True)
        serialized_data = serializer.data
        sorted_skills = self._sort_skills(serialized_data)
        if limit:
            sorted_skills[: int(limit)]
        data = OrderedDict(
            {
                "vacancy_name": query,
                "number_of_vacancies": len(queryset),
                "rated_skills": sorted_skills,
            }
        )
        return Response(data)
