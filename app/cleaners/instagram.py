import logging

from .base import BaseCleaner

logger = logging.getLogger("instagram")


class Instagram(BaseCleaner):
    HOSTNAMES = [
        "instagram.com",
        "www.instagram.com",
    ]

    TRACKING_QUERY_PARAMS = [
        "utm_source",
        "igshid",
    ]

    SHOULD_RESOLVE_REDIRECTS = False
