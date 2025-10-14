import sys
from pathlib import Path
from config import Config
import src.logger as logger
import src.scraper as scraper
from src.database import CarDB
from src.reason import UpdateResult

def run():
    config = Config('config.json') #default path is just the config.json here

    #logger
    log_dir = config.log_dir
    log_level = config.log_level
    log_stderr = config.log_stderr
    log = logger.setup_logger('cartracker', log_dir, log_level, log_stderr)

    #database
    db = CarDB(config.db_path)
    
    log.info(f'main::run(): "Starting..."')

    count = 0
    for car in scraper.get_listings(config.search_url):
        count += 1

        _, result = db.update_car(car)
        if result.value == UpdateResult.NEW_LISTING.value:
            log.info(f'main::run: New listing! VIN [{car['vin']}] price [{car['current_price']}] dealer [{car['dealer']}]')
        
        elif result.value == UpdateResult.PRICE_CHANGE.value:
            log.info(f'main::run: Price change. VIN [{car['vin']}] price [{car['current_price']}] \
                     price history [{car['price_history']}] dealer [{car['dealer']}]')

    log.info(f'main::run(): "Found [{count}] cars today. Finished"')
    sys.exit(0)

if __name__ == '__main__':
    run()