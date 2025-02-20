from datetime import datetime, timezone


def datetime_now() -> datetime:
    """Return the current datetime in UTC"""
    return datetime.now(timezone.utc)