import json
import logging
import os
import stat
import time

from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse, urlencode, urlunparse

import validators

from flask import Flask, request, send_file
from peewee import fn, PeeweeException

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

    try:
        cleaned_link_row = CleanedLink.create(
            original_url=url, netloc=parsed_url.netloc
        )
    except PeeweeException:
        cleaned_link_row = False

    start_time = time.time()
    cleaned_url = BaseCleaner.clean(url)
    end_time = time.time()

    if cleaned_link_row:
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


@app.route("/stats")
def cached_stats():
    if not os.path.exists("./stats.html"):
        Path("./stats.html").touch()

    file_stat = os.stat("./stats.html")
    last_modified = time.time() - file_stat[stat.ST_MTIME]

    if last_modified > 600 or file_stat[stat.ST_SIZE] == 0:
        stats_html = stats()
        with open("./stats.html", "w") as fh:
            fh.write(stats_html)

    return send_file("./stats.html")


def stats():
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    total_links = CleanedLink.select().count()
    top_netlocs = list(
        CleanedLink.select(
            CleanedLink.netloc, fn.COUNT(CleanedLink.netloc).alias("count")
        )
        .group_by(CleanedLink.netloc)
        .where(CleanedLink.created_at > one_day_ago)
        .order_by("count")
        .limit(10)
        .execute()
    )

    top_list_items = []
    for row in top_netlocs:
        domain = row.netloc
        count = row.count
        top_list_items.append(f"<tr><td>{domain}</td><td>{count}</td></tr>")

    top_list_html = "\n".join(top_list_items)

    generation_time = datetime.utcnow()

    return f"""
    {total_links} links cleaned all time.<br><br>

    Top domains of the last day:
    <table>
    <tr><th>Domain</th><th>Count</th></tr>
    {top_list_html}
    </table>
    </ul><br>
    <br>

    <footer>Generated at {generation_time}.</footer>
    """
