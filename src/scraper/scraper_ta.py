# Certain scraping optimizations were implemented from: https://scrapfly.io/blog/how-to-scrape-tripadvisor/

import re
import json
import asyncio
import random
import string
from dataclasses import dataclass, asdict

import httpx
import requests
from bs4 import BeautifulSoup
from loguru import logger

from scraper_utils import (
    build_client,
    wrap_except,
    ta_url,
    get_locations,
)


@dataclass
class Location:
    name: str
    url: str
    food_url: str
    fun_url: str
    hotel_url: str
    place_type: str
    pos: tuple[float, float]


@wrap_except("Failed to scrape location: {} - {}")
async def request_loc(query: str, client: httpx.AsyncClient) -> Location:
    # Clone a graphql request for location search
    request = [{
        "query": "5eec1d8288aa8741918a2a5051d289ef",
        "variables": {
            "request": {
                "query": query,
                "limit": 10,
                "scope": "WORLDWIDE",
                "locale": "en-US",
                "scopeGeoId": 1,
                "searchCenter": None,
                "types": [
                    "LOCATION",
                    "QUERY_SUGGESTION",
                    "RESCUE_RESULT"
                ],
                "locationTypes": [
                    "GEO",
                    "AIRPORT",
                    "ACCOMMODATION",
                    "ATTRACTION",
                    "ATTRACTION_PRODUCT",
                    "EATERY",
                    "NEIGHBORHOOD",
                    "AIRLINE",
                    "SHOPPING",
                    "UNIVERSITY",
                    "GENERAL_HOSPITAL",
                    "PORT",
                    "FERRY",
                    "CORPORATION",
                    "VACATION_RENTAL",
                    "SHIP",
                    "CRUISE_LINE",
                    "CAR_RENTAL_OFFICE"
                ],
                "userId": None,
                "articleCategories": [
                    "default",
                    "love_your_local",
                    "insurance_lander"
                ],
                "enabledFeatures": [
                    "typeahead-q",
                    "articles"
                ]
            }
        }
    }]
    
    headers = {
        "X-Requested-By": "".join([random.choice(string.ascii_lowercase + string.digits) for i in range(180)]),
        "Referer": "https://www.tripadvisor.com/",
        "Origin": "https://www.tripadvisor.com"
    }
    
    response = await client.post(
        url = "https://www.tripadvisor.com/data/graphql/ids",
        json = request,
        headers = headers
    )
    
    response.raise_for_status()
    
    # Get location entry from different search results
    data = response.json()
    data = data[0]["data"]["Typeahead_autocomplete"]["results"]
    data = [datum["details"] for datum in data if "details" in datum][0]
    loc = Location(
        name = data["localizedName"],
        url = data["url"],
        food_url = data["RESTAURANTS_URL"],
        fun_url = data["ATTRACTIONS_URL"],
        hotel_url = data["HOTELS_URL"],
        place_type = data["placeType"],
        pos = (data["latitude"], data["longitude"])
    )
    
    logger.info(f"Successfully scraped location: {query}")
    
    return loc


def extract_page_manifest(html):
    """Extract JS pageManifest object's state data from graphql hidden in HTML page
    """
    requests.get("")
    data = re.findall(r"pageManifest:({.+?})};", html, re.DOTALL)[0]
    return json.loads(data)


async def main(locs: list[str] = []):
    locs = get_locations()
    
    async with build_client() as client:
        responses = []
        for loc in locs:
            responses.append(asyncio.ensure_future(request_loc(loc, client)))
        locs_data = await asyncio.gather(*responses)
        
        for loc_data in locs_data:
            for cat in ["food", "fun", "hotel"]:
                try:
                     response = await client.get(ta_url(loc_data[f"{cat}_url"]))
                     response.raise_for_status()
                except Exception as e:
                    logger.exception(f"Scraper was blocked for: {loc_data['name']}, {cat} - {e}")
                    
            # scrape_food(ta_url(loc_data["food_url"]), client)
            # scrape_fun(ta_url(loc_data["fun_url"]), client)
            # scrape_hotel(ta_url(loc_data["hotel_url"]), client)
            

def scrape_food(url, client):
    pass


def scrape_fun(url, client):
    pass


def scrape_hotel(url, client):
    pass


if __name__ == "__main__":
    asyncio.run(main())