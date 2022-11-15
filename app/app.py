import json
import logging
import time

from urllib.parse import urlparse, urlencode, urlunparse

import validators

from flask import Flask, request

from cleaners import BaseCleaner
from db import CleanedLink

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")


@app.route("/clean/<path:url>")
def clean(url):
    parsed_url = urlparse(url)
    reassembled_url = list(parsed_url)

    captured_query_string = urlencode(request.args.to_dict())
    reassembled_url[4] = captured_query_string
    url = urlunparse(reassembled_url)

    if not validators.url(url):
        return "Invalid URL", 400

    cleaned_link_row = CleanedLink.create(original_url=url, netloc=parsed_url.netloc)

    start_time = time.time()
    cleaned_url = BaseCleaner.clean(url)
    end_time = time.time()

    cleaned_link_row.update(
        success=True,
        elapsed_time=(end_time - start_time),
        cleaned_url=cleaned_url,
    ).execute()

    if request.headers["Accept"] == "application/json":
        return json.dumps(
            {
                "cleaned_url": cleaned_url,
            }
        )
    else:
        return f'<a href="{cleaned_url}">{cleaned_url}</a>'
