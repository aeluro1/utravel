# Certain scraping optimizations were implemented from: https://scrapfly.io/blog/how-to-scrape-tripadvisor/

import re
import json
import asyncio
import random
import string
import math
from dataclasses import dataclass, field

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
    name: str = ""
    url: str = ""
    food_url: str = ""
    fun_url: str = ""
    hotel_url: str = ""
    place_type: str = ""
    pos: tuple[float, float] = (-1, -1)
    
    
@dataclass
class Restaurant:
    name: str = ""
    url: str = ""
    rating: int = -1
    review_count: int = -1
    price: str = ""
    tags: list[str] = field(default_factory = list)
    imgs: list[str] = field(default_factory = list)
    contact: dict = field(default_factory = dict)


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
async def request_page(url: str, client: httpx.AsyncClient) -> str:
    response = await client.get(url)
    response.raise_for_status()
    return response.text

@wrap_except("Could not request page")
async def request_page_tree(url:str, client: httpx.AsyncClient) -> etree._Element:
    html = await request_page(url, client)
    return etree.HTML(html, None)

@wrap_except("Could not parse search page")
async def parse_search_page(tree: etree._Element) -> list[Restaurant]:
    items = []
    
    for elem in tree.xpath("//div[@data-test]"):
        # Gather required info using xpath
        body = elem.xpath(".//span[string-length(text()) > 0]/text()")
        if body[0] == "Sponsored":
            continue
        url = elem.xpath(".//a[contains(@href, 'Restaurant_Review') and string-length(text()) > 0]/@href")[0]
        item = Restaurant(
            url = ta_url(url)
        )
        
        items.append(item)
        
    logger.info(f"Collected all restaurants on page")
    return items

@wrap_except("Could not scrape restaurant page")
async def scrape_rst_page(rst: Restaurant, client: httpx.AsyncClient) -> Restaurant:
    html = await request_page(rst.url, client)
    data = get_page_data(html)["urqlCache"]["results"]
    data_rst = find_nested_key(data, "RestaurantPresentation_searchRestaurantsByGeo")
    data_rst = data_rst["RestaurantPresentation_searchRestaurantsByGeo"]["restaurants"][0]

    rst.name = data_rst["name"]
    rst.rating = data_rst["reviewSummary"]["rating"]
    rst.review_count = data_rst["reviewSummary"]["count"]
    rst.price = data_rst["topTags"][0]["secondary_name"]
    rst.tags = [tag["localizedName"] for tag in data_rst["topTags"]]
    # rst.imgs
    rst.contact = {
        "address": data_rst["localizedRealtimeAddress"],
        "telephone": data_rst["telephone"],
    }
    
    # # Implementation for scraping reviews if ever desired
    #
    # tree = etree.HTML(html, None)
    # data_rev = tree.xpath(".//div[contains(@class, 'review-container')]")
    # num_rev_page = len(data_rev)
    # num_rev_total = rst.review_count
    # num_page_total = math.ceil(num_rev_total / num_rev_page)
    # rev_urls = [rst.url.replace("-Reviews-", f"-Reviews-or{num_rev_page * i}-") for i in range(1, num_page_total)]
    # rev_list = []
    # responses = await asyncio.gather(*[request_page_tree(rev_url, client) for rev_url in rev_urls])
    # for response in [tree, *responses]:
    #     rev_list.extend(scrape_rev(response))
    
    return rst


def get_page_data(html: str) -> dict:
    """Extract JS pageManifest object's state data from graphql hidden in HTML page
    """
    data = re.findall(r"{pageManifest:({.+?})};", html, re.DOTALL)[0]
    return json.loads(data)


@wrap_except("Could not get parameter value")
def find_nested_key(data: dict, target: str) -> dict:
    results = [data[i]["data"] for i in data if target in data[i]["data"]][0]
    results = json.loads(results)
    return results


async def scrape(locs: list[str] = [], num_pages_max: int | None = None):
    if len(locs) == 0:
        locs = get_locations()
    
    async with build_client() as client:
        responses = [asyncio.ensure_future(request_loc(loc, client)) for loc in locs]
        locs_data = await asyncio.gather(*responses)
        
        for loc_data in locs_data:
            await scrape_food(loc_data, client, num_pages_max)
            
                
async def scrape_food(loc_data: Location, client: httpx.AsyncClient, num_pages_max: int | None = None):
    url = getattr(loc_data, f"food_url")
    
    chrome = SeleniumDriver()
    tree = etree.HTML(chrome.get(url, "//span[contains(text(), 'results')]"), None)
    chrome.close()
    
    rst_list = await parse_search_page(tree)
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
    
    next_pages_data = [asyncio.ensure_future(request_page_tree(next_url, client)) for next_url in next_urls]
    for next_page_data in asyncio.as_completed(next_pages_data):
        rst_list.extend(await parse_search_page(await next_page_data))
        
    await scrape_rst_page(rst_list[0], client)
    
    with open(f"{loc_data.name}", "w") as f:
        temp = [vars(i) for i in rst_list]
        print(temp)
        # json.dump(temp, f, indent = 4)
    

if __name__ == "__main__":
    asyncio.run(scrape(["Los Angeles"], 3))