import json
import logging
import requests
from typing import Union
from time import sleep

from config import RAW_XML_DIR, RSS_CATS_PATH

logger = logging.getLogger(__name__)


def load_rss_cats() -> list:
    with open(RSS_CATS_PATH, 'r') as f:
        return json.load(f)
    
def _fetch_rss(cat: str) -> Union[bytes, None]:
    url = f'https://rss.arxiv.org/rss/{cat}'
    response = request_get_with_retry(
        url
    )
    if response:
        return response.content
    return None

def request_get_with_retry(*args, retry=3, **kwargs):
    response = None
    for i in range(retry):
        try:
            response = requests.get(*args, **kwargs)
            response.raise_for_status()
            if response:
                return response
            raise
        except Exception as e:
            if i != retry - 1:
                statuscode = "NULL"
                try:
                    statuscode = response.status_code
                except Exception:
                    pass
                logger.warning("request retrying ..." + str(statuscode) + str(e))
                continue
            logger.error("requets fail after 3 times retry ...")
    return None

def fetch_rss():
    for cat in load_rss_cats():
        content = _fetch_rss(cat)
        if not content:
            logger.error(f"fetch rss {cat} fail")
            continue
        cat_str = cat.replace(".", "_")
        filepath = RAW_XML_DIR / f"{cat_str}.xml"
        print(f"fetching {cat} to {filepath}")
        with open(filepath, 'wb') as f:
            f.write(content)
        sleep(1) # be polite