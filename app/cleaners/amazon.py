import logging

from .base import BaseCleaner

logger = logging.getLogger("amazon")


class Amazon(BaseCleaner):
    HOSTNAMES = [
        "amazon.com",
        "www.amazon.com",
    ]

    TRACKING_QUERY_PARAMS = ["tag", "linkCode", "ascsubtag"]

    SHOULD_RESOLVE_REDIRECTS = False
