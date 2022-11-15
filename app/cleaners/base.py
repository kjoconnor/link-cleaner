import logging

from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

import advocate

REDIRECT_LIMIT = 50
USER_AGENT = "LinkCleaner/1.0"

logger = logging.getLogger("cleaner")

registry = {}


class BaseCleaner(object):
    TRACKING_QUERY_PARAMS = [
        "utm_source",
        "utm_medium",
    ]

    SHOULD_RESOLVE_REDIRECTS = True

    @classmethod
    def clean(cls, url):
        logger.info(f"Starting clean for {url}")
        cleaner = cls.find_cleaner(url)
        logger.info(f"Using cleaner {cleaner}")
        cleaned_url = cleaner.clean_url(url)
        logger.info(f"Got cleaned url of {cleaned_url}")

        return cleaned_url

    def register(cls):
        registry[cls.__name__] = cls

    @classmethod
    def __init_subclass__(cls, **kwargs):
        print(f"Init subclassing with {cls}")
        super().__init_subclass__(**kwargs)
        print(cls)
        cls.register(cls)

    @classmethod
    def clean_url(cls, url):
        if getattr(cls, "SHOULD_RESOLVE_REDIRECTS"):
            redirected_url = cls.resolve_redirects(url)

        no_params_url = cls.remove_tracking_query_params(redirected_url)
        return no_params_url

    @classmethod
    def find_cleaner(cls, url):
        netloc = urlparse(url).netloc

        for name, registered_cls in registry.items():
            if netloc in registered_cls.HOSTNAMES:
                logger.info(f"Matched netloc of {netloc} in {name}")
                return registered_cls

        logger.info(f"Using base Cleaner class")
        return cls

    @staticmethod
    def resolve_redirects(url):
        logger.info(f"Resolving redirects for {url}")
        response = advocate.get(
            url,
            headers={"User-Agent": USER_AGENT},
            allow_redirects=False,
            timeout=5,
        )
        response.raise_for_status()

        redirects = 0

        while (response.status_code >= 300 and response.status_code < 400) and not (
            redirects > REDIRECT_LIMIT
        ):
            redirects += 1

            target_location = response.headers.get("Location")
            logger.info(
                f"[current redirects: {redirects}] Redirected to {target_location}"
            )
            response = advocate.get(
                target_location,
                headers={"User-Agent": USER_AGENT},
                allow_redirects=False,
                timeout=5,
            )
            response.raise_for_status()
        else:
            if redirects > REDIRECT_LIMIT:
                return "Reached maximum redirects allowed", 400
            else:
                return response.request.url

    @classmethod
    def remove_tracking_query_params(cls, url):
        logger.info("Removing tracking query params")

        parsed_url = urlparse(url)

        parsed_qs = dict(parse_qsl(parsed_url.query))

        for param in cls.TRACKING_QUERY_PARAMS:
            _ = parsed_qs.pop(param)

        reassembled_url = list(parsed_url)
        reassembled_url[4] = urlencode(parsed_qs)

        return urlunparse(reassembled_url)
