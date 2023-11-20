from celery import shared_task
from celery.utils.log import get_task_logger

from scrapers.models import Search

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=5, retry_backoff=True, ignore_result=True)
def save_query_with_metadata(self, query, user_agent, ip_address):
    try:
        Search.objects.create(query=query, ip_address=ip_address, user_agent=user_agent)
    except Exception as e:
        logger.error("Error saving search query.", exc_info=e)
        raise self.retry(exc=e)
