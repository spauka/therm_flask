import logging
import random
from time import sleep

logger = logging.getLogger(__name__)


def retry(
    starting_retry_wait=5.0,
    multiplier=1.5,
    exception: tuple[type[Exception], ...] | type[Exception] = Exception,
):
    """
    Decorator to add timeout with exponential backoff to function
    on exception
    """

    def retry_func(f):
        def f_with_retry(*args, retry_wait=starting_retry_wait, retry_count=0, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:  # pylint: disable=broad-exception-caught
                if isinstance(e, exception):
                    wait_time = retry_wait + random.uniform(1, retry_wait)
                    next_retry_wait = retry_wait * multiplier
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
                else:
                    raise e
            return f_with_retry(
                *args,
                retry_wait=next_retry_wait,
                retry_count=retry_count + 1,
                **kwargs,
            )

        return f_with_retry

    return retry_func
