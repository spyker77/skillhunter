from celery import shared_task
from django.core.management import call_command

from core.utils.celery import lock_task


@shared_task
@lock_task("lock:purge_db", timeout=60)
def task_purge_db():
    call_command("purge_db")


@shared_task
@lock_task("lock:scrape_hh", timeout=60)
def task_scrape_hh():
    call_command("scrape_hh")


@shared_task
@lock_task("lock:scrape_indeed", timeout=60)
def task_scrape_indeed():
    call_command("scrape_indeed")


@shared_task
@lock_task("lock:scrape_sh", timeout=60)
def task_scrape_sh():
    call_command("scrape_sh")
