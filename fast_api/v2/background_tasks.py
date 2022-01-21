from asgiref.sync import sync_to_async
from fastapi import Request

from scrapers.models import Search

from .schemas import SearchSchema


async def save_query_with_meta_data(request: Request, query: str) -> None:
    ip_address = request.client.host
    user_agent = request.headers["user-agent"]
    validated = SearchSchema(query=query, ip_address=ip_address, user_agent=user_agent)
    await sync_to_async(Search.objects.create)(
        query=validated.query, ip_address=validated.ip_address, user_agent=validated.user_agent
    )
