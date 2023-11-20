from celery import shared_task
from django.core.management import call_command

from core.utils.celery import lock_task


@shared_task(ignore_result=True)
@lock_task("lock:warmup_cache", timeout=10)
def task_warmup_cache():
    call_command("warmup_cache")
