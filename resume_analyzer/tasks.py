from celery import shared_task
from django.core.management import call_command

from core.utils.celery import lock_task


@shared_task
@lock_task("lock:warmup_cache", timeout=60)
def task_warmup_cache():
    call_command("warmup_cache")
