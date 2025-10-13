import sys
import requests
import random
import time
import json
import logging
import re
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))  # config.py
sys.path.insert(0, str(project_root / 'src'))  # src modules
from config import config
import src.utils as utils
import src.car as car

log = logging.getLogger('cartracker')

# logic should be:
# check listing db (keyed on vin)
# if new car:
#   store price, spec, location, stock number (reg)    
# if existing car:
#   check price change, check location change (spec should be the same so don't re-check, but could do...)
#   if change:
#       add notification
# send summary w/ changes highlighted

# manufacturer specifics
EQUIPMENT_HIGHLIGHTS_CLASS = '_1oxeqv25'
PAGINATION_CLASS = 't81jpj5'

def random_sleep():
    if config.is_random:
        delay = utils.random_delay()
        log.info(f'scraper::random_sleep: sleeping random [{delay}] seconds')
        time.sleep(delay)
    else:
        log.info(f'scraper::random_sleep: sleeping default [15] seconds')
        time.sleep(15)
    return

def has_more_pages(soup, current_url):
    pagination_dots = soup.find('span', class_=PAGINATION_CLASS)
    if pagination_dots:
        return True
    
    # if there's no '...' visible then we're at the end of the pages
    # but may not be currently on the last one
    current_page = get_current_page_number(current_url)
    highest_visible_page = get_highest_available_page(soup)
    
    log.debug(f"scraper::has_more_pages: No '...' found current page: {current_page}, highest visible: {highest_visible_page}")
    # if current page is not the highest visible in the pagination bar, there are more pages
    return current_page < highest_visible_page

def get_highest_available_page(soup):
    pagination_links = soup.find_all('a', attrs={'aria-label': re.compile("^Page")})
    
    highest = 0
    for link in pagination_links:
        link_text = link.get_text(strip=True)
        try:
            page_num = int(link_text)
            highest = max(highest, page_num)
        except ValueError:
            # not a page number
            continue
    
    log.debug(f"scraper::get_highest_available_page: Highest visible page number: {highest}")
    return highest

def get_current_page_number(current_url):
    try:
        parsed_url = urlparse(current_url)
        query_params = parse_qs(parsed_url.query)
        
        # Get page parameter (returns list, so take first element)
        page_param = query_params.get('page', ['1'])[0]
        page_num = int(page_param)
        
        log.debug(f"scraper::get_current_page_number: Current page from URL: {page_num}")
        return page_num
    except (ValueError, IndexError):
        log.debug("scraper::get_current_page_number: Could not parse page number from URL, assuming page 1")
        return 1

def get_next_page_url(soup, current_url):
    current_page = get_current_page_number(current_url)
    next_page = current_page + 1
    
    log.debug(f"scraper::get_next_page_url: Current page: {current_page}, looking for page {next_page}")
    
    # find all pagination links
    pagination_links = soup.find_all('a', attrs={'aria-label': re.compile("^Page")})
    
    if not pagination_links:
        log.debug("scraper::get_next_page_url: No pagination links found")
        return None
    
    # Look for the next page link by text content
    for link in pagination_links:
        link_text = link.get_text(strip=True)
        
        try:
            link_page = int(link_text)
            
            if link_page == next_page:
                href = link.get('href')
                if href:
                    # Build absolute URL using URL_PREFIX
                    url_prefix = config.get('scraper', 'url_prefix')
                    if not href.startswith('http'):
                        href = url_prefix.rstrip('/') + href
                    
                    log.debug(f"scraper::get_next_page_url: Found next page {next_page} URL: {href}")
                    return href
        except ValueError:
            # Not a page number link (could be "..." or other text)
            continue
    
    log.debug(f"scraper::get_next_page_url: Could not find page {next_page} link")
    return None

def get_cars_on_page(soup):
    cars = []

    container = soup.find('div', attrs={'data-testid': 'searchlist-container'})
    listings = container.find_all('article', attrs={'data-testid': 'searchlistitem-card'})
    
    #LIMIT = 4
    #COUNT = 0
    
    for listing in listings:
        car_json = listing.find('script', type='application/ld+json')
        random_sleep()
        
        if car_json:
            car_data = json.loads(car_json.string)
            c = process_listing_details(car_data)
            # create our internal view of the car
            internal_car = car.create_car_record(c)
            cars.append(internal_car)
            #testing only
            #COUNT += 1
            #if COUNT >= LIMIT:
            #    return cars

    return cars

def get_listings(start_url):
    HEADERS = {
        'User-Agent': random.choice(config.user_agents)
    }
    
    log.info(f'scraper::get_listings: User-Agent [{config.user_agent}] URL [{start_url}] timeout [{config.request_timeout}]')

    all_cars = []
    page_count = 0
    current_url = start_url

    log.info(f'scraper::get_listings: Starting...')

    while current_url:
        page_count += 1
        random_sleep()
        log.info(f'scraper::get_listings: Fetching page [{page_count}] current_url [{current_url}]')

        try:
            response = requests.get(current_url, headers=HEADERS, timeout=config.request_timeout)
            response.raise_for_status()
        
            soup = BeautifulSoup(response.content, 'html.parser')
            log.debug(f'scraper::get_listings: response')

            cars_on_page = get_cars_on_page(soup)
            log.info(f'scraper::get_listings: Got [{len(cars_on_page)}] cars from page [{page_count}]')
            
            all_cars.extend(cars_on_page)

            more_pages = has_more_pages(soup, current_url)
            log.info(f'scraper::get_listings: more_pages [{more_pages}]')

            if not more_pages:
                log.info(f'scraper::get_listings: No more pages')
                break

            next_url = get_next_page_url(soup, current_url)

            if next_url:
                log.debug(f'scraper::get_listings: current_url [{current_url}] = next_url [{next_url}]')
                current_url = next_url
            else:
                log.error(f'scraper::get_listings: Failed to get next_url, stopping reads')
                break
        except requests.RequestException as e:
            log.error(f'scraper::get_listings: Error getting url [{current_url}] e [{str(e)}]', exc_info=True)
            break
        except Exception as e:
            log.error(f'scraper::get_listings: Error processing url [{current_url}] e [{str(e)}]', exc_info=True)
            break

    log.info(f'scraper::get_listings: Page read complete. Got [{page_count}] pages, [{len(all_cars)}] cars')

    return all_cars

def process_listing_details(car_data: json):
    HEADERS = {
        'User-Agent': config.user_agent
    }
    
    log.debug(f'scraper::process_listing_details: entry. car_data [{car_data}]')
    # get the url of the actual listing
    try:            
        car_url = car_data["offers"]["url"]
    except KeyError:
        print(f'scraper::process_listing_details: KeyError getting url for [{car_data['vehicleIdentificationNumber']}]')

    response = requests.get(config.url_prefix + car_url, headers=HEADERS, timeout=config.request_timeout)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    log.debug(f'scraper::process_listing_details: got response []')

    eh = soup.find('div', class_=EQUIPMENT_HIGHLIGHTS_CLASS)
    option_highlights = []
    for c in eh.children:
        option_highlights.append(c.text)

    car_data['raw_options'] = option_highlights

    car_data['internal_options'] = car.parse_highlights(option_highlights)

    return car_data


