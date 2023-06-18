# Certain scraping optimizations were implemented from: https://scrapfly.io/blog/how-to-scrape-tripadvisor/

import re
import json
import asyncio
import random
import string
import math
from dataclasses import dataclass, asdict

import httpx
import requests
from bs4 import BeautifulSoup
from loguru import logger
from lxml import etree
from lxml.cssselect import CSSSelector

from scraper_utils import (
    build_client,
    wrap_except,
    ta_url,
    get_locations,
)
from scraper_se import SeleniumDriver


@dataclass
class Location:
    name: str
    url: str
    food_url: str
    fun_url: str
    hotel_url: str
    place_type: str
    pos: tuple[float, float]
    
    
@dataclass
class Restaurant:
    name: str
    url: str
    rating: str
    review_count: int
    price: str
    tags: list[str]
    imgs: list[str]
    contact: dict


@wrap_except("Failed to scrape location summary")
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
        food_url = ta_url(data["RESTAURANTS_URL"]),
        fun_url = ta_url(data["ATTRACTIONS_URL"]),
        hotel_url = ta_url(data["HOTELS_URL"]),
        place_type = data["placeType"],
        pos = (data["latitude"], data["longitude"])
    )
    
    logger.info(f"[{loc.name}] Successfully scraped location summary")
    
    return loc

@wrap_except("Could not request page")
async def request_page(url: str, client: httpx.AsyncClient, tree: bool = False) -> str | etree._Element:
    response = await client.get(url)
    response.raise_for_status()
    html = response.text
    return (etree.HTML(html, None) if tree else html)

@wrap_except("Could not parse page")
def parse_search_page(tree: etree._Element) -> list[Restaurant]:
    items = []
    
    for elem in tree.xpath("//div[@data-test]"):
        # Gather required info using xpath
        body = elem.xpath(".//span[string-length(text()) > 0]/text()")
        if body[0] == "Sponsored":
            continue
        url = elem.xpath(".//a[contains(@href, 'Restaurant_Review') and string-length(text()) > 0]")[0]
        name = url.xpath("text()")[-1]
        url = url.xpath("@href")[0]
        review_count = 0#int(body[0].replace(",",""))
        tags = body[3].split(", ")
        price = body[4]
        rating = elem.xpath(".//svg/@aria-label")[0].split()[0]
        item = Restaurant(
            name = name,
            url = ta_url(url),
            rating = rating,
            review_count = review_count,
            price = price,
            tags = tags,
            imgs = [],
            contact = {}
        )
        
        items.append(item)
        logger.info(f"Added restaurant: {name}")
        
    logger.info(f"Collected all restaurants on page")        
    return items


def get_page_data(html):
    """Extract JS pageManifest object's state data from graphql hidden in HTML page
    """
    data = re.findall(r"{pageManifest:({.+?})};", html, re.DOTALL)[0]
    return json.loads(data)


async def scrape(locs: list[str] = [], num_pages_max: int | None = None):
    if len(locs) == 0:
        locs = get_locations()
    
    async with build_client() as client:
        responses = []
        for loc in locs:
            responses.append(asyncio.ensure_future(request_loc(loc, client)))
        locs_data = await asyncio.gather(*responses)
        
        for loc_data in locs_data:
            await scrape_food(loc_data, client, num_pages_max)
            
                
async def scrape_food(loc_data: Location, client: httpx.AsyncClient, num_pages_max: int | None = None):
    url = getattr(loc_data, f"food_url")
    
    chrome = SeleniumDriver()
    tree = etree.HTML(chrome.get(url, "//span[contains(text(), 'results')]"), None)
    chrome.close()
    
    rst_list = parse_search_page(tree)
    num_results_page = len(rst_list)
    num_results_total = int(tree.xpath("//span[contains(text(), 'results')]/span/text()")[0])
    num_pages_total = math.ceil(num_results_total / num_results_page)
    if num_pages_max and num_pages_max < num_pages_total:
        logger.info(f"Scraping {num_pages_max}/{num_pages_total} pages")
        num_pages_total = num_pages_max if num_pages_max and num_pages_max < num_pages_total else num_pages_total
    else:
        logger.info(f"Scraping all pages")
    next_page_url = ta_url(tree.xpath("//a[@data-page-number and contains(text(), 'Next')]/@href")[0])
    next_urls = [next_page_url.replace(f"oa{num_results_page}", f"oa{num_results_page * i}") for i in range(1, num_pages_total)]
    
    next_pages_data = [asyncio.ensure_future(request_page(next_url, client, tree = True)) for next_url in next_urls]
    for next_page_data in asyncio.as_completed(next_pages_data):
        rst_list.extend(parse_search_page(await next_page_data))
    
    with open(f"{loc_data.name}", "w") as f:
        temp = [vars(i) for i in rst_list]
        json.dump(temp, f, indent = 4)
    

if __name__ == "__main__":
    asyncio.run(scrape(["Los Angeles"], 3))