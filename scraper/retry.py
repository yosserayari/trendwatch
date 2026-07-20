import time
import functools
import requests


def with_retry(max_retries: int = 3, base_delay: float = 1.0, backoff_factor: float = 2.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)

                except requests.exceptions.HTTPError as e:
                    status = e.response.status_code if e.response is not None else None
                    attempt += 1
                    if attempt > max_retries:
                        print(f"❌ Giving up after {max_retries} retries (HTTP {status}): {e}")
                        raise

                    if status == 429 and e.response is not None:
                        retry_after = e.response.headers.get("Retry-After")
                        delay = float(retry_after) if retry_after else base_delay * (backoff_factor ** (attempt - 1))
                    else:
                        delay = base_delay * (backoff_factor ** (attempt - 1))

                    print(f"⚠️ HTTP {status} error. Waiting {delay:.1f}s before retry {attempt}/{max_retries}...")
                    time.sleep(delay)

                except (requests.ConnectionError, requests.Timeout) as e:
                    attempt += 1
                    if attempt > max_retries:
                        print(f"❌ Giving up after {max_retries} retries: {e}")
                        raise

                    delay = base_delay * (backoff_factor ** (attempt - 1))
                    print(f"⚠️ Network error ({e}). Waiting {delay:.1f}s before retry {attempt}/{max_retries}...")
                    time.sleep(delay)

        return wrapper
    return decorator