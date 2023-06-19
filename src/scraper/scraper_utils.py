import pandas as pd
from typing import Callable
from pathlib import Path
from pprint import pprint


import httpx

from loguru import logger
from fake_useragent import UserAgent

LOC_PATH = Path(__file__).parent / "locations.csv"


def build_client() -> httpx.AsyncClient:
    headers = {
        "Authority": "www.tripadvisor.com",
        "User-Agent": UserAgent().random,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.6",
        "Accept-Encoding": "gzip, deflate, br"
    }
    
    client = httpx.AsyncClient(
        # http2 = True,
        headers = headers,
        timeout = httpx.Timeout(10.0),
        limits = httpx.Limits(max_connections = 5)
    )
    
    return client


def wrap_except(err_msg: str = "Default exception") -> Callable:
    """Creates customized decorator for some function for logging exceptions
    """
    def decorator(func: Callable) -> Callable:
        def inner(*args: list, **kwargs: dict) -> object:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if len(args) != 0:
                    logger.exception(f"{err_msg}: {args[0]} - {e}")
                else:
                    logger.exception(f"{err_msg} - {e}")
                return None      
        return inner
    return decorator


def ta_url(url_stem):
    url_root = "https://www.tripadvisor.com"
    return url_root + url_stem


def get_locations():
    df = pd.read_csv(LOC_PATH)
    names = df.iloc[1:,0]
    return names.tolist()


def main():
    locs = get_locations()
    pprint(locs)


if __name__ == "__main__":
    main()
    

