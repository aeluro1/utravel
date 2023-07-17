# Certain scraping optimizations were implemented from: https://scrapfly.io/blog/how-to-scrape-tripadvisor/

import re
import json
import asyncio
import random
import string
import math
import functools
import argparse
from pathlib import Path
from pprint import pprint

import aiometer
from loguru import logger
from lxml import etree

from scraper_utils import (
    ScraperClient,
    wrap_except,
    ta_url,
    load_locations,
    find_nested_key,
    hash_str_array,
    save_all,
    is_file
)
from scraper_se import SeleniumDriver
from database import Location, Restaurant


MAX_PAGES = 5 # Set to -1 for all pages
MAX_CONN_AT_ONCE = 5
MAX_CONN_PER_SEC = 1
SAVE_PATH = Path(__file__).resolve().parent / "data"
CSV_PATH = Path(__file__).resolve().parent / "csv"


@wrap_except("Failed to scrape location summary")
async def request_loc(client: ScraperClient, query: str) -> Location:
    """Clone a graphql request to obtain location details

    Args:
        client (ScraperClient): HTTPX client
        query (str): Location

    Returns:
        Location: Location dataclass
    """
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
async def request_page(client: ScraperClient, url: str) -> str:
    """Request a page's HTML content

    Args:
        client (ScraperClient): HTTPX client
        url (str): URL to request

    Returns:
        str: HTML as a string
    """
    response = await client.get(url)
    response.raise_for_status()
    return response.text


@wrap_except("Could not request page")
async def request_page_tree(client: ScraperClient, url:str) -> etree._Element:
    """Request a page's HTML content as an XML tree

    Args:
        client (ScraperClient): HTTPX client
        url (str): URL to request

    Returns:
        etree._Element: Root element of tree
    """
    html = await request_page(client, url)
    return etree.HTML(html, None)


@wrap_except("Could not parse search page")
def parse_search_page(tree: etree._Element) -> list[Restaurant]:
    """Parses search results page for individual items

    Args:
        tree (etree._Element): Root element of page

    Returns:
        list[Restaurant]: List of Restaurant dataclasses
    """
    items = []
    
    for elem in tree.xpath("//div[@data-test]"):
        # Gather required info using xpath
        if elem.xpath("@data-test")[0] == "SL_list_item":
            continue
        url = elem.xpath(".//a[contains(@href, 'Restaurant_Review') and string-length(text()) > 0]/@href")[0]
        item = Restaurant(
            url = ta_url(url)
        )
        
        imgs = elem.xpath(".//div[contains(@style, 'background-image')]/@style")
        r = re.compile(r"url\(\"(.*?)\"\)")
        imgs = [re.findall(r, img)[0] for img in imgs]
        item.imgs = json.dumps(imgs)
        
        items.append(item)
        
    return items


@wrap_except("Could not scrape search page")
async def scrape_search_page(client: ScraperClient, rst_list: list[Restaurant]) -> list[Restaurant]:
    # Use aiometer to throttle connections to bypass bot checks
    rst_list = await asyncio.gather(*[scrape_rst_page(client, rst) for rst in rst_list]) # Too fast
    # jobs = [functools.partial(scrape_rst_page, client, rst) for rst in rst_list]
    # rst_list = await aiometer.run_all(jobs, max_at_once = MAX_CONN_AT_ONCE, max_per_second = MAX_CONN_PER_SEC)
    
    return rst_list


@wrap_except("Could not scrape restaurant page")
async def scrape_rst_page(client: ScraperClient, rst: Restaurant) -> Restaurant:
    """Scrapes content of restaurant page

    Args:
        client (ScraperClient): HTTPX client
        rst (Restaurant): Restaurant dataclass containing URL to parse

    Returns:
        Restaurant: Modified Restaurant dataclass
    """
    html = await request_page(client, rst.url)
    data = get_page_data(html)["urqlCache"]["results"]
    data_rst = find_nested_key(data, "RestaurantPresentation_searchRestaurantsByGeo")
    data_rst = data_rst["RestaurantPresentation_searchRestaurantsByGeo"]["restaurants"][0]

    try:
        rst.name = data_rst["name"]
        rst.address = data_rst["localizedRealtimeAddress"]
        rst.phone = data_rst["telephone"]
        rst.id = hash_str_array([rst.address, rst.name]) # type: ignore
        rst.rating = data_rst["reviewSummary"]["rating"]
        rst.review_count = data_rst["reviewSummary"]["count"]
        # rst.imgs
        rst.tags = json.dumps([tag["tag"]["localizedName"] for tag in data_rst["topTags"]])
        temp_price = data_rst["topTags"][0]["secondary_name"]
        rst.price = temp_price if temp_price is not None else ""
    except Exception:
        pass

    
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
    
    logger.debug(f"Successfully scraped restaurant: {rst.name}")
    return rst


def get_page_data(html: str) -> dict:
    """Extract JS pageManifest object's state data from graphql hidden in HTML page

    Args:
        html (str): Page HTML

    Returns:
        dict: Dictionary representing JS state
    """
    data = re.findall(r"{pageManifest:({.+?})};", html, re.DOTALL)[0]
    return json.loads(data)


async def scrape(locs: list[str], num_pages_max: int = MAX_PAGES):
    """Scrapes a location summary - entry point for specific type scraping

    Args:
        locs (list[str], optional): _description_. Defaults to [].
        num_pages_max (int | None, optional): _description_. Defaults to None.
    """
    headers = {"Referer": "https://www.tripadvisor.com/"}
    async with ScraperClient(headers) as client:
        responses = [asyncio.ensure_future(request_loc(client, loc)) for loc in locs]
        locs_data = await asyncio.gather(*responses)
        
        for loc_data in locs_data:
            try:
                await scrape_food(client, loc_data, num_pages_max)
            except Exception as e:
                logger.error(f"[{loc_data.name}] Could not process location - {e}")
            
                
async def scrape_food(client: ScraperClient, loc_data: Location, num_pages_max: int = MAX_PAGES):
    """Scrapes all restaurants for a specified location generated from scrape()

    Args:
        client (ScraperClient): HTTPX client
        loc_data (Location): Location dataclass
        num_pages_max (int | None, optional): Maximum number of pages to scrape. Defaults to None.
    """
    url = getattr(loc_data, f"food_url")
    
    chrome = SeleniumDriver()
    wait_list = ["//span[contains(text(), 'results')]", "//div[contains(@style, 'background-image')]"]
    tree = etree.HTML(chrome.get(url, wait_list), None)
    
    # Get total number of results to calculate number of pages
    rst_list_init = parse_search_page(tree)
    num_results_page = len(rst_list_init)
    num_results_total = int(tree.xpath("//span[contains(text(), 'results')]/span/text()")[0])
    num_pages_total = math.ceil(num_results_total / num_results_page)
    if num_pages_max < 0 or num_pages_max > num_pages_total:
        num_pages_max = num_pages_total
    logger.info(f"[{loc_data.name}] Scraping {num_pages_max}/{num_pages_total} pages")
    page_count = 0
    
    # Process first page
    fn = SAVE_PATH / f"{loc_data.name} - {page_count + 1}"
    if not is_file(fn.with_suffix(".json")):
        rst_list = await scrape_search_page(client, rst_list_init)
        save_all(fn, rst_list)
        logger.info(f"[{loc_data.name}] First page scraped")
    page_count += 1

    next_url = ta_url(tree.xpath("//a[@data-page-number and contains(text(), 'Next')]/@href")[0])
    next_urls = []
    for i in range(1, num_pages_max):
        fn = SAVE_PATH / f"{loc_data.name} - {i + 1}"
        if is_file(fn.with_suffix(".json")):
            page_count += 1
        else:
            next_urls.append(next_url.replace(f"oa{num_results_page}", f"oa{num_results_page * i}"))
    logger.info(f"[{loc_data.name}] Starting process at page {page_count + 1}/{num_pages_max}")
    
    # next_pages = [asyncio.ensure_future(request_page_tree(client, n)) for n in next_urls] # Asynchronously iterate through pages
    # for next_page_data in asyncio.as_completed(next_pages):
    # for next_page_data in [await request_page_tree(client, n) for n in next_urls]: # Synchronously iterate through pages
    for next_url in next_urls: # Synchronously lazily iterate using Selenium
        fn = SAVE_PATH / f"{loc_data.name} - {page_count + 1}"
        rst_list_temp = parse_search_page(etree.HTML(chrome.get(next_url, wait_list), None))
        rst_list = await scrape_search_page(client, rst_list_temp)
        save_all(fn, rst_list)
        page_count += 1
        if page_count % 3 == 0:
            client.reset()
        
        logger.info(f"[{loc_data.name}] Successfully scraped {page_count}/{num_pages_max} pages")

    logger.info(f"[{loc_data.name}] Location processed")
    
    chrome.close()


def main(args: argparse.Namespace):
    csv_file = CSV_PATH / args.csv
    locs = load_locations(csv_file)
    if args.read:
        pprint(locs)
        exit()
    asyncio.run(scrape(locs, args.num))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "TripAdvisor Scraper")
    parser.add_argument(
        "--csv",
        action = "store",
        help = "CSV file containing locations to scrape",
        required = True
    )
    parser.add_argument(
        "--num", "-n",
        action = "store",
        help = "number of search pages to scrape",
        type = int,
        default = MAX_PAGES
    )
    parser.add_argument(
        "--read", "-r",
        action = "store_true",
        help = "print out the list of locations in a CSV"
    )
    args = parser.parse_args()
    
    main(args)