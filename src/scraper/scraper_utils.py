import hashlib
import json
import asyncio
import inspect
from time import sleep
from typing import Callable
from pathlib import Path

import pandas as pd
import httpx
import nest_asyncio
from loguru import logger
from fake_useragent import UserAgent

from database import Restaurant, Session


RETRY_WAIT_TIME = 15
MAX_CONNECTIONS = 5
TIMEOUT = 5
MAX_RETRIES = 5


class ScraperClient(httpx.AsyncClient):
    def __init__(self, headers = {}):
        super().__init__(
            http2 = True,
            timeout = httpx.Timeout(TIMEOUT),
            limits = httpx.Limits(max_connections = MAX_CONNECTIONS)
        )
        self.headers = {
            "Authority": "www.tripadvisor.com",
            "User-Agent": UserAgent().random,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.6",
            "Accept-Encoding": "gzip, deflate, br",
            **headers
        }
        
    def reset(self):
        self.headers["User-Agent"] = UserAgent().random


def wrap_except(err_msg: str = "Default exception") -> Callable:
    """Creates customized decorator for sync/async function for logging exceptions and re-running

    Args:
        err_msg (str, optional): Exception message description. Defaults to "Default exception".

    Returns:
        Callable: Customized decorator with message embedded
    """
    def decorator(func: Callable) -> Callable:
        async def inner(*args: list, **kwargs: dict) -> object:
            for i in range(MAX_RETRIES):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    caller_func = inspect.currentframe().f_back.f_code.co_name # type: ignore
                    logger.error(f"{err_msg} @ {caller_func}: {e}")
                    logger.error(f"{i + 1} attempt(s) made - waiting {RETRY_WAIT_TIME}s ({i + 1}/{MAX_RETRIES})")
                    await asyncio.sleep(RETRY_WAIT_TIME)
        if not inspect.iscoroutinefunction(func):
            sync_func = func
            async def async_func(*args, **kwargs):
                return sync_func(*args, **kwargs)
            func = async_func
            def sync_inner(*args: list, **kwargs: dict) -> object:
                nest_asyncio.apply()
                loop = asyncio.get_running_loop()
                return loop.run_until_complete(inner(*args, **kwargs))
            return sync_inner
        else:
            return inner
    return decorator


def ta_url(url_stem):
    url_root = "https://www.tripadvisor.com"
    return url_root + url_stem


@wrap_except("Could not get parameter value")
def find_nested_key(data: dict, target: str) -> dict:
    """Extracts specific key from nested JS state dictionary

    Args:
        data (dict): Dictionary representing JS state
        target (str): Target key

    Returns:
        dict: Dictionary corresponding to target key
    """
    results = [data[i]["data"] for i in data if target in data[i]["data"]][0]
    results = json.loads(results)
    return results


def hash_str(key: str) -> str:
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()
    h = int(h, 16) % (10**8)
    return str(h)


def hash_str_array(keys: list[str]) -> str:
    h = "".join([hash_str(key) for key in keys])
    return h


def save_json(file: str | Path, data: list):
    if isinstance(file, str):
        file = Path(file)
    file.parent.mkdir(parents = True, exist_ok = True)
    with open(file.with_suffix(".json"), "w") as f:
        temp = [dict(filter(lambda i: not i[0].startswith("_"), vars(i).items())) for i in data]        
        json.dump(temp, f, indent = 4)
        

def save_all(file: str | Path, rst_list: list[Restaurant]):
    if isinstance(file, str):
        file = Path(file)
    file = file.with_suffix(".json")
    save_json(file, rst_list)
    try:
        with Session() as session:
            session.add_all(rst_list)
            session.commit()
    except Exception as e:
        file.unlink(missing_ok = True)
        logger.exception(f"Failed to save to database - {e}")
        

def is_file(file: str | Path) -> bool:
    if isinstance(file, str):
        file = Path(file)
    return file.is_file()
        

def load_locations(file: str | Path) -> list[str]:
    if isinstance(file, str):
        file = Path(file)
    df = pd.read_csv(file.with_suffix(".csv"))
    names = df.iloc[:,0]
    return names.tolist()