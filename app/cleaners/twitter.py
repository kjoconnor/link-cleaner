import logging

from .base import BaseCleaner

logger = logging.getLogger("twitter")


class Twitter(BaseCleaner):
    HOSTNAMES = [
        "twitter.com",
        "mobile.twitter.com",
        "m.twitter.com",
        "www.twitter.com",
    ]

    TRACKING_QUERY_PARAMS = [
        "s",
        "t",
    ]

    SHOULD_RESOLVE_REDIRECTS = False
