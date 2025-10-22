import sys
from config import Config
import src.logger as logger
import src.scraper as scraper
import src.scraper_selenium as selenium
from src.database import CarDB

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

    if config.force_resync:
        log.info(f'main::run(): force_resync enabled, will fetch all listings')

    count = 0
    if config.scraper_library == "selenium":
        count = len(selenium.get_listings(config.search_url, db))
    elif config.scraper_library == "curl_cffi":
        count = len(scraper.get_listings(config.search_url, db))
    else:
        log.error(f'main::run() unknown scraper_library value in config [{config.scraper_library}]')
        sys.exit(1)

    log.info(f'main::run(): Found [{count}] cars today. Finished')
    sys.exit(0)

if __name__ == '__main__':
    run()