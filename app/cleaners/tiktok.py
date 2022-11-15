import logging

from urllib.parse import urlparse, urlunparse

import advocate

from .base import BaseCleaner, USER_AGENT

logger = logging.getLogger("tiktok")


# We'd prefer to _not_ make requests at all, since then we're tipping
# our hand that this link is being shared, but at least we're just
# giving them robot data rather than information about the recipient's
# device.

# This is a personalized link for example, we want the permalink video URL
# https://www.tiktok.com/t/<some_id>/
class TikTok(BaseCleaner):
    HOSTNAMES = [
        "tiktok.com",
        "vm.tiktok.com",
        "www.tiktok.com",
    ]

    SHOULD_RESOLVE_REDIRECTS = False

    @classmethod
    def clean_url(cls, url):
        logger.info(f"Cleaning url {url}")
        return cls.find_permalink(url)

    @staticmethod
    def find_permalink(url):
        parsed_url = urlparse(url)

        if parsed_url.path.startswith("/t/"):
            logger.info("Stripping personalized share link data")
            logger.info(f"Making a HEAD request for {url}")
            response = advocate.head(
                url,
                headers={"User-Agent": USER_AGENT},
                allow_redirects=False,
                timeout=5,
            )

            response.raise_for_status()

            parsed_url = urlparse(response.headers["Location"])

            # I'm guessing none of these query params will ever be needed, so don't
            # even bother trying to reassemble.
            reassembled_url = list(parsed_url)
            reassembled_url[4] = ""
            return urlunparse(reassembled_url)

        return url
