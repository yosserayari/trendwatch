"""
test_retry.py — TEMPORARY test file, not part of the app.
Run this once to confirm retry.py works, then delete it.
"""

import requests
from scraper.retry import with_retry

attempt_counter = {"count": 0}

@with_retry(max_retries=3, base_delay=1.0, backoff_factor=2.0)
def flaky_function():
    attempt_counter["count"] += 1
    print(f"Trying... (attempt {attempt_counter['count']})")

    if attempt_counter["count"] < 3:
        # Use requests' own ConnectionError, since that's what a real
        # failed HTTP request actually raises — not Python's built-in one.
        raise requests.exceptions.ConnectionError("Simulated network failure")

    return "✅ Success!"


if __name__ == "__main__":
    result = flaky_function()
    print(result)