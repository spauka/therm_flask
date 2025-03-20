import logging
import random
from inspect import iscoroutinefunction
from functools import wraps
from asyncio import sleep as asleep
from time import sleep

logger = logging.getLogger(__name__)


def retry(
    starting_retry_wait: float = 1.0,
    multiplier: float = 1.5,
    max_wait: float = 300.0,
    max_retry: int = 0,
    exception: tuple[type[Exception], ...] | type[Exception] = Exception,
):
    """
    Decorator to add timeout with exponential backoff to function
    on exception. If the wrapped function is asynchronous, use an async sleep
    """

    def retry_func(f):
        if iscoroutinefunction(f):
            # Wrap an asynchronous coroutine
            @wraps(f)
            async def async_f_with_retry(
                *args, retry_wait=starting_retry_wait, retry_count=0, max_wait=max_wait, **kwargs
            ):
                while True:
                    try:
                        return await f(*args, **kwargs)
                    except Exception as e:  # pylint: disable=broad-exception-caught
                        # If we've exceeded the max retries, or if the exception is not a known
                        # type, pass the exception forward.
                        if max_retry > 0 and retry_count == max_retry:
                            raise e
                        if not isinstance(e, exception):
                            raise e

                        # Otherwise, wait for wait-time and retry the function
                        wait_time = (retry_wait / 2) + random.uniform(1, retry_wait)
                        retry_wait = min(retry_wait * multiplier, max_wait)
                        logger.error(
                            (
                                "Retrying function %s due to exception %s. "
                                "Attempt %d. Waiting %.2f to try again.",
                            ),
                            f.__name__,
                            e.__class__.__name__,
                            retry_count,
                            wait_time,
                            exc_info=e,
                        )
                        await asleep(wait_time)

            return async_f_with_retry

        # Otherwise the function is synchronous, return the synchronous version of the retry function
        @wraps(f)
        def f_with_retry(
            *args, retry_wait=starting_retry_wait, retry_count=0, max_wait=max_wait, **kwargs
        ):
            while True:
                try:
                    return f(*args, **kwargs)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    # If we've exceeded the max retries, or if the exception is not a known
                    # type, pass the exception forward.
                    if max_retry > 0 and retry_count == max_retry:
                        raise e
                    if not isinstance(e, exception):
                        raise e

                    # Otherwise, wait for wait-time and retry the function
                    wait_time = (retry_wait / 2) + random.uniform(1, retry_wait)
                    retry_wait = min(retry_wait * multiplier, max_wait)
                    logger.error(
                        (
                            "Retrying function %s due to exception %s. "
                            "Attempt %d. Waiting %.2f to try again.",
                        ),
                        f.__name__,
                        e.__class__.__name__,
                        retry_count,
                        wait_time,
                        exc_info=e,
                    )
                    sleep(wait_time)

        return f_with_retry

    return retry_func
