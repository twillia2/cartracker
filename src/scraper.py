import sys
import requests
import random
import time
import json
import logging
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

# porsche specifics
EQUIPMENT_HIGHLIGHTS_CLASS = '_1oxeqv25'

def get_listings(url):
    HEADERS = {
        'User-Agent': random.choice(config.user_agents)
    }
    
    log.info(f'scraper::get_listings: User-Agent [{config.user_agent}] URL [{url}] timeout [{config.request_timeout}]')

    response = requests.get(url, headers=HEADERS, timeout=config.request_timeout)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    log.info(f'scraper::get_listings: got response')
    log.debug(f'scraper::get_listings: response: [{soup}]')

    container = soup.find('div', attrs={'data-testid': 'searchlist-container'})
    listings = container.find_all('article', attrs={'data-testid': 'searchlistitem-card'})

    LIMIT = 4
    COUNT = 0

    cars = []
    for listing in listings:
        car_json = listing.find('script', type='application/ld+json')
        if config.is_random:
            delay = utils.random_delay()
            log.info(f'scraper::get_listings: sleeping random [{delay}] seconds')
            time.sleep(delay)
        else:
            log.info(f'scraper::get_listings: sleeping default [15] seconds')
            time.sleep(15)
        
        if car_json:
            COUNT += 1
            car_data = json.loads(car_json.string)
            c = process_listing_details(car_data)
            
            # create our internal view of the car
            internal_car = car.create_car_record(c)
            cars.append(internal_car)
            #testing only
            if COUNT >= LIMIT:
                return cars
            
    return cars


def process_listing_details(car_data: json):
    HEADERS = {
        'User-Agent': config.user_agent
    }
    
    log.debug(f'scraper::process_listing: entry. car_data [{car_data}]')
    # get the url of the actual listing
    try:            
        car_url = car_data["offers"]["url"]
    except KeyError:
        print(f'fetch_porsche_listings: KeyError getting url for [{car_data['vehicleIdentificationNumber']}]')

    response = requests.get(config.url_prefix + car_url, headers=HEADERS, timeout=config.request_timeout)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    log.debug(f'scraper::process_listing: got response []')

    eh = soup.find('div', class_=EQUIPMENT_HIGHLIGHTS_CLASS)
    option_highlights = []
    for c in eh.children:
        option_highlights.append(c.text)

    car_data['raw_options'] = option_highlights

    car_data['internal_options'] = car.parse_highlights(option_highlights)

    return car_data


