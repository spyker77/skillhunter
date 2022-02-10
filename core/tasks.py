from celery import shared_task

from scrapers.models import Search


@shared_task
def save_query_with_metadata(query, user_agent, ip_address):
    Search.objects.create(query=query, ip_address=ip_address, user_agent=user_agent)
