from datetime import datetime, timedelta
from functools import lru_cache, wraps


def expiring_lru_cache(seconds: int = 60, maxsize: int = 128):
    """
    A LRU cache with expiry time for entries.

    From https://realpython.com/lru-cache-python/#evicting-cache-entries-based-on-both-time-and-space
    """

    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.utcnow() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.lifetime

            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache
