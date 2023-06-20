import hashlib
import json
from typing import Callable
from pathlib import Path

import pandas as pd
import httpx
from loguru import logger
from fake_useragent import UserAgent

from database import Restaurant, Session


LOC_PATH = Path(__file__).parent / "locations.csv"


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
    """Creates customized decorator for some function for logging exceptions

    Args:
        err_msg (str, optional): Exception message description. Defaults to "Default exception".

    Returns:
        Callable: Customized decorator with message embedded
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


def save_json(fn: str | Path, data: list):
    if isinstance(fn, str):
        fn = Path(fn)
    fn.parent.mkdir(parents = True, exist_ok = True)
    with open(fn.with_suffix(".json"), "w") as f:
        temp = [dict(filter(lambda i: not i[0].startswith("_"), vars(i).items())) for i in data]        
        json.dump(temp, f, indent = 4)
        

def save_all(file: Path, rst_list: list[Restaurant]):
    save_json(file, rst_list)
    with Session() as session:
        session.add_all(rst_list)
        session.commit()
        

def is_file(fn: str | Path) -> bool:
    if isinstance(fn, str):
        fn = Path(fn)
    return fn.is_file()
        

def get_locations():
    df = pd.read_csv(LOC_PATH)
    names = df.iloc[1:,0]
    return names.tolist()