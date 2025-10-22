import sys
import time
import json
import logging
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))  # config.py
sys.path.insert(0, str(project_root / 'src'))  # src modules
from config import config
import src.utils as utils
import src.car as car
from src.database import CarDB
from src.reason import UpdateResult

log = logging.getLogger('cartracker')

# virtualdisplay for python headless on rpi
if config.headless:
    from pyvirtualdisplay import Display
    display = Display(visible=0, size=(1920, 1080))
    display.start()


options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
options.add_argument('--headless')
if config.chromedriver_path:
    from selenium.webdriver.chrome.service import Service
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
else:
    driver = webdriver.Chrome(options=options)
driver.set_window_size(1920, 1080)


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
NEXT_PAGE_CLASS = 't81jpj1'

def random_sleep():
    if config.is_random:
        delay = utils.random_delay()
        log.info(f'scraper::random_sleep: sleeping random [{delay}] seconds')
        time.sleep(delay)
    else:
        log.info(f'scraper::random_sleep: sleeping default [3] seconds')
        time.sleep(3)
    return

def has_more_pages(soup, current_url) -> tuple [bool, str]:
    current_page = get_page_number_from_url(current_url)
    highest_visible_page = get_highest_visible_page(soup)
    next_hidden_page, next_url = get_next_hidden_page(soup)
    
    # with total number of pages = 5, pagination element can look like:
    # a) <- 1 *2* 3 ... ->
    # OR
    # b) <- 1 ... *4* 5 ->
    # OR
    # c) <- 1 2 *3* -> (and -> has a href element for page 4)
    # OR
    # d) <- 1 ... *4* ... -> (and -> has a href element for page 4)
    # OR
    # e) <- 1 ... 4 *5* -> (and -> has no href element for page 4)
    # where the starred page is our current page.
    # so we have to handle various scenarios to figure out if there's more
    # pages of search results to look for. involving 'current page', 'highest visible page'
    # (i.e. page 5 in 'b)')
    # and 'hidden page' (the next page provided by the right arrow, in 'c)' this would be page 4)
    # note: get_next_hidden_page() will return -1 if there is no page to make integer comparison easier
    # instead of trying to check Nones

    # scenarios:
    # 1. in 'a)' and 'b)' current_page = 2, highest_visible_page = 3, next_hidden_page = 4
    #       next_page = 3 
    #       (current < highest_visible)
    #       more_pages = true 
    # 2. in 'c)' and 'd)' current_page = 3, highest_visible_page = 3, next_hidden_page = 4
    #       next_page = 4 
    #       (current = highest_visible and current < next_hidden)
    #       more_pages = true
    # 3. in 'd)' current_page = 5, highest_visible_page = 5, next_hidden_page = -1
    #       (current = highest_visible and not next_hidden)
    #       more_pages = false

    log.info(f"scraper::has_more_pages: current_page: [{current_page}] highest_visible_page: [{highest_visible_page}] next_hidden_page: [{next_hidden_page}] ")

    if current_page < highest_visible_page:
        log.debug(f"scraper::has_more_pages: current_page [{current_page}] < highest_visible_page [{highest_visible_page}] return [True]")
        return True, next_url
    elif current_page < next_hidden_page:
        log.debug(f"scraper::has_more_pages: current_page [{current_page}] < next_hidden_page [{next_hidden_page}] return [True]")
        return True, next_url
    elif current_page == highest_visible_page and next_hidden_page < 0:
        log.debug(f"scraper::has_more_pages: current_page [{current_page}] == highest_visible_page [{highest_visible_page}] and next_hidden_page [{next_hidden_page}] < 0 return [False]")
        return False, None
    else:
        log.warning(f"scraper::has_more_pages: Unexpected! current_page [{current_page}] highest_visible_page [{highest_visible_page}] next_hidden_page [{next_hidden_page}] return [False]")
        return False, None

def get_highest_visible_page(soup):
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

def get_next_hidden_page(soup) -> tuple[int, str]:
    # we can sometimes have a next page url hidden as a 'next page' url on the arrow button
    # and because beautifulsoup can't read the shadow DOM to check if the button is enabled, 
    # we have to do it like this. but it works fine
    arrow = soup.find_all('fnssr-p-link-pure', class_=NEXT_PAGE_CLASS)

    if arrow:
        next_page_elem = arrow[-1].find('a')
        if next_page_elem.text == "Next Page":
            try:
                next_url = check_url(next_page_elem['href'])
                ret = get_page_number_from_url(next_url)
                log.debug(f"scraper::get_highest_hidden_page: Highest hidden page number: {ret} ")
                return ret, next_url
            except (ValueError, IndexError):
                return -1, None
    
    return -1, None

def get_page_number_from_url(url: str):
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # Get page parameter (returns list, so take first element)
        page_param = query_params.get('page', ['1'])[0]
        page_num = int(page_param)
        
        log.debug(f"scraper::get_page_number_from_url: Current page from URL: {page_num} url [{url}]")
        return page_num
    except (ValueError, IndexError):
        log.debug("scraper::get_page_number_from_url: Could not parse page number from URL, assuming page 1")
        return 1

def strip_query_params(url):
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

def check_url(url: str) -> str:
    url_pattern = re.compile(f"^{config.url_prefix}")
    if url_pattern.search(url):
        # probably valid if it starts with our base/prefix url
        log.debug(f'scraper::check_url: url [{url}] looks valid')
        return url
    else:
        log.debug(f'scraper::check_url: url [{url}] looks invalid appending prefix [{config.url_prefix}]')
        # else we'd better append our prefix
        url = config.url_prefix + url
        return url

# unused but might be useful if they change something
def infer_next_page(current_url, next_page):
    parsed = urlparse(current_url)
    params = parse_qs(parsed.query)
    
    # update url's page parameter
    params['page'] = [str(next_page)]
    
    # reconstruct query string (parse_qs returns lists, urlencode expects them)
    new_query = urlencode(params, doseq=True)
    
    # rebuild URL
    new_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))

    log.debug(f"scraper::infer_next_page: built url [{new_url}]")
    return new_url

def get_cars_on_page(soup, db):
    cars = []

    #container = soup.find('div', attrs={'data-testid': 'searchlist-container'})
    container = soup.find('section', class_='_1hzhguz0')
    #listings = container.find_all('article', attrs={'data-testid': 'searchlistitem-card'})
    car_jsons = container.find('script', type='application/ld+json')
    if car_jsons:
        intermediate = json.loads(car_jsons.string)
        cars_as_json = intermediate['itemListElement']
        #LIMIT = 4
        #COUNT = 0
        
        for car_json in cars_as_json:
            if car_json:
                c = process_listing_details(car_json, db)
                # create our internal view of the car
                internal_car = car.create_car_record(c)
                cars.append(internal_car)

                write_car_to_db(internal_car, db)
                #testing only
                #COUNT += 1
                #if COUNT >= LIMIT:
                #    return cars

    return cars

def write_car_to_db(internal_car: car, db: CarDB):
    log.debug("scraper::write_car_to_db")
    written_car, result = db.update_car(internal_car)
    if result.value == UpdateResult.NEW_LISTING.value:
        log.info(f'main::run: New listing! VIN [{written_car['vin']}] price [{written_car['current_price']}] dealer [{written_car['dealer']['name']}] url [{written_car['url']}]')
        
    elif result.value == UpdateResult.PRICE_CHANGE.value:
        # need to read the old prices from the db, not this new internal_car object that only has today's price
        ph = db.get_price_history_for_vin(written_car['vin'])
        log.info(f'main::run: Price change! VIN [{written_car['vin']}] New price [{written_car['current_price']}] price history [{utils.log_price_history(ph)}] dealer [{written_car['dealer']['name']}] url [{written_car['url']}]')
            

def get_listings(start_url, db):
    log.info(f'scraper::get_listings: URL [{start_url}] timeout [{config.request_timeout}]')

    all_cars = []
    page_count = 0
    current_url = start_url

    log.info(f'scraper::get_listings: Starting...')

    while current_url:
        page_count += 1
        log.info(f'scraper::get_listings: Fetching page [{page_count}] current_url [{current_url}]')

        try:
            driver.get(current_url)
            WebDriverWait(driver, 10).until(
               EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            response = driver.page_source
        
            soup = BeautifulSoup(response, 'html.parser')
            log.debug(f'scraper::get_listings: response from url {current_url}')

            cars_on_page = get_cars_on_page(soup, db)
            log.info(f'scraper::get_listings: Got [{len(cars_on_page)}] cars from page [{page_count}]')
            
            all_cars.extend(cars_on_page)

            more_pages, next_url = has_more_pages(soup, current_url)
            log.info(f'scraper::get_listings: more_pages [{more_pages}]')
            if not more_pages:
                break

            if next_url:
                log.debug(f'scraper::get_listings: current_url [{current_url}] = next_url [{next_url}]')
                current_url = next_url
                random_sleep()
            else:
                log.error(f'scraper::get_listings: Failed to get next_url, stopping reads')
                break
        #except requests.RequestException as e:
        #    log.error(f'scraper::get_listings: Error getting url [{current_url}] e [{str(e)}]', exc_info=True)
        #    break
        except Exception as e:
            log.error(f'scraper::get_listings: Error processing url [{current_url}] e [{str(e)}]', exc_info=True)
            break

    log.info(f'scraper::get_listings: Page read complete. Got [{page_count}] pages, [{len(all_cars)}] cars')

    return all_cars

def process_listing_details(car_data: json, db: CarDB):
    log.debug(f'scraper::process_listing_details: entry. car_data [{car_data}]')
    # get the url of the actual listing
    try:            
        car_url = check_url(car_data["offers"]["url"])
    except KeyError:
        print(f'scraper::process_listing_details: KeyError getting url for [{car_data['vehicleIdentificationNumber']}]')

    # use the url to see if we already know this car
    # the listing url _should_ be unique (and stored)
    # unfortunately we don't have the vin at this point but 
    # we can avoid scraping the details page again if the car is 
    # known. if it is known but the price has changed we can re-scrape
    current_price = car_data["offers"]["price"]
    last_price = -1
    # we do need to strip the query params first though
    car_url = strip_query_params(car_url)
    existing_car = db.get_by_url(car_url)
    if existing_car is not None:
        last_price = existing_car['price_history'][-1]['price']
    if (current_price == last_price) and not config.force_resync:
            # update last seen and skip this car
            car_data['last_seen'] = datetime.now().isoformat()
            log.info(f'scraper::process_listing_details: unchanged car at url [{car_url}] skipping')
    else:
        # get the full listing
        random_sleep()

        driver.get(car_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        response = driver.page_source
        soup = BeautifulSoup(response, 'html.parser')
        log.debug(f'scraper::process_listing_details: new or changed car: got response from url [{car_url}]')

        eh = soup.find('div', class_=EQUIPMENT_HIGHLIGHTS_CLASS)
        option_highlights = []
        for c in eh.children:
            option_highlights.append(c.text)

        car_data['raw_options'] = option_highlights
        car_data['internal_options'] = car.parse_highlights(option_highlights)
        car_data['offers']['url'] = car_url

    return car_data


