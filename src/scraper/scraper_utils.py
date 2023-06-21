import hashlib
import json
import asyncio
import nest_asyncio
import inspect
from time import sleep
from typing import Callable
from pathlib import Path

import pandas as pd
import httpx
from loguru import logger
from fake_useragent import UserAgent

from database import Restaurant, Session


RETRY_WAIT_TIME = 15


class ScraperClient(httpx.AsyncClient):
    def __init__(self, headers = {}):
        super().__init__(
            timeout = httpx.Timeout(10.0),
            limits = httpx.Limits(max_connections = 5)
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
            attempts = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    caller_func = inspect.currentframe().f_back.f_code.co_name # type: ignore
                    logger.error(f"{err_msg} @ {caller_func}: {e}")
                    logger.error(f"{attempts} attempt(s) made - retrying after {RETRY_WAIT_TIME}s")
                    sleep(RETRY_WAIT_TIME)
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
        

def save_all(file: Path, rst_list: list[Restaurant]):
    save_json(file, rst_list)
    try:
        with Session() as session:
            session.add_all(rst_list)
            session.commit()
    except Exception as e:
        file.with_suffix(".json").unlink(missing_ok = True)
        logger.exception(f"Failed to save to database - {e}")
        

def is_file(fn: str | Path) -> bool:
    if isinstance(fn, str):
        fn = Path(fn)
    return fn.is_file()
        

def load_locations(fn: str):
    file = Path(__file__).parent / fn
    file = file.with_suffix(".csv")
    df = pd.read_csv(file)
    names = df.iloc[:,0]
    return names.tolist()