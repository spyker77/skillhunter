import json
from collections import OrderedDict, defaultdict

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.response import Response

from api.v1.serializers import SkillSerializer
from scrapers.models import Search, Vacancy


class SkillViewSet(viewsets.ViewSet):
    def _combine_rated_skills(self, rated_skills_to_merge):
        super_dict = defaultdict(list)
        for rated_skills in rated_skills_to_merge:
            if rated_skills is not None:
                for k, v in rated_skills.items():
                    super_dict[k].append(v)
        return super_dict

    def _sort_skills(self, serialized_data):
        # Get rated skills for each vacancy and convert it from str to dict.
        rated_skills_to_merge = (json.loads(vacancy.get("rated_skills")) for vacancy in serialized_data)
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
        if query is None:
            return query, limit
        ip_address = self.request.META.get("REMOTE_ADDR")
        user_agent = self.request.META.get("HTTP_USER_AGENT")
        # Additionally, save the search query for future analysis.
        Search.objects.create(query=query, ip_address=ip_address, user_agent=user_agent)
        return query, limit

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="format",
                description="The data format of the result (json/xml/yaml).",
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="limit",
                description="The number of most wanted skills to display.",
                required=False,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="q",
                description="The job title to be processed.",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
        ],
    )
    def list(self, request):
        query, limit = self._get_meta_data(request)
        # Handler is primarily for crawlers that reach the path without the q parameter.
        if query is None:
            return Response({"Error": "A required q parameter was not specified for this request."}, 400)
        queryset = Vacancy.objects.filter(search_vector=query)
        serializer = SkillSerializer(queryset, many=True)
        serialized_data = serializer.data
        sorted_skills = self._sort_skills(serialized_data)
        if limit:
            sorted_skills = sorted_skills[: int(limit)]
        data = OrderedDict(
            {
                "vacancy_name": query,
                "number_of_vacancies": len(queryset),
                "rated_skills": sorted_skills,
            }
        )
        return Response(data)
