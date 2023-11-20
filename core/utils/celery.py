from collections.abc import Callable
from functools import wraps

from celery.utils.log import get_task_logger
from decouple import config
from redis import Redis
from redis.lock import Lock

logger = get_task_logger(__name__)

redis_client: Redis = Redis.from_url(config("REDIS_URL", default="redis://redis"))


def lock_task(key: str, timeout: float = 3600) -> Callable:
    """
    Decorator to add a Redis lock mechanism to a Celery task. Prevents task execution
    if the task is already running.

    Args:
        key (str): A unique string to identify the lock.
        timeout (float): Timeout for the lock, in seconds. Defaults to 3600.

    Returns:
        Callable: The decorated task function.
    """

    def decorator(task: Callable) -> Callable:
        @wraps(task)
        def wrapper(*args, **kwargs):
            lock: Lock = redis_client.lock(key, timeout=timeout)
            have_lock = False

            try:
                if have_lock := lock.acquire(blocking=False):
                    return task(*args, **kwargs)
                else:
                    logger.info(f"Task {task.__name__} is already running.")
            except Exception as e:
                logger.error(f"Error acquiring lock for task {task.__name__}.", exc_info=e)
            finally:
                if have_lock and lock.locked():
                    lock.release()

        return wrapper

    return decorator
