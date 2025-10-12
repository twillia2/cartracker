import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))  # config.py
sys.path.insert(0, str(project_root / 'src'))  # src modules
from config import Config
from utils import random_delay

def test_config():
    u = "https://finder.porsche.com/gb/en-GB/search/taycan?" \
    "model=taycan&category=taycan-sport-turismo&category=taycan-4-cross-turismo&maximum-price=60000&order=newest"
    config = Config("../config.json")
    assert(u == config.search_url)
    r_to = 30
    assert(r_to == config.request_timeout)

def test_no_passed_config():
    u = "https://finder.porsche.com/gb/en-GB/search/taycan?" \
    "model=taycan&category=taycan-sport-turismo&category=taycan-4-cross-turismo&maximum-price=60000&order=newest"
    config = Config()
    assert(u == config.search_url)

def test_random_delay():
    for i in range(100): 
        delay = random_delay()
        print(delay)

if __name__ == '__main__':
    test_random_delay()