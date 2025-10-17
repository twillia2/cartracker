import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))  # config.py
sys.path.insert(0, str(project_root / 'src'))  # src modules
from config import Config
from utils import random_delay
from utils import log_price_history
import scraper as scraper
import car as car
import json
from database import CarDB

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

def test_url_creation():
    short_url = "gb/en-GB/search/taycan?" \
    "model=taycan&category=taycan-sport-turismo&category=taycan-4-cross-turismo&maximum-price=60000&order=newest"
    actual_url = "https://finder.porsche.com/gb/en-GB/search/taycan?" \
    "model=taycan&category=taycan-sport-turismo&category=taycan-4-cross-turismo&maximum-price=60000&order=newest"
    assert(scraper.check_url(short_url) == actual_url)
    assert(scraper.check_url(actual_url) == actual_url)

def test_price_log():
    json_str = '{"vin": "WP0ZZZY1ZNSA62688", "name": "Taycan 4 Cross Turismo (MY22)", "model": "J1", "mileage": 25150, "color": "Volcano Grey Metallic", "interior_color": "Black/bordeaux Red Two-tone Leather Interior With Smooth-finish Leather", "previous_owners": 1, "current_price": 52890, "url": "/gb/en-GB/details/porsche-taycan-4-cross-turismo-my22-preowned-90GR8W?model=taycan&category=taycan-sport-turismo&category=taycan-4-cross-turismo&page=5", "my": "22", "first_reg": "2021-12-15", "options": null, "raw_options": null, "dealer": {"name": "Porsche Centre Nottingham", "address": "Landmere Lane, Edwalton \\n Nottingham, NG12 4DE"}, "price_history": [{"price": 54890, "date": "2025-10-14T09:31:51.765974", "currency": "GBP", "dealer": {"name": "Porsche Centre Nottingham", "address": "Landmere Lane, Edwalton \\n Nottingham, NG12 4DE"}}, {"price": 53890, "date": "2025-10-15T09:31:51.765974", "currency": "GBP", "dealer": {"name": "Porsche Centre Nottingham", "address": "Landmere Lane, Edwalton \\n Nottingham, NG12 4DE"}}, {"price": 52890, "date": "2025-10-16T09:31:51.765974", "currency": "GBP", "dealer": {"name": "Porsche Centre Nottingham", "address": "Landmere Lane, Edwalton \\n Nottingham, NG12 4DE"}}], "first_seen": "2025-10-16T09:31:51.765975", "last_updated": "2025-10-16T09:31:51.765976"}'
    j = json.loads(json_str)
    log_price_history(j['price_history'])

def test_duplicate_car_check():
    json_str = '{"@context":"https://schema.org","@type":"Car","name":"Taycan Sport Turismo (MY22)","model":"J1","color":"Gentian Blue Metallic","image":"https://images.finder.porsche.com/5df59467-54f3-414c-90f4-132ed260a942/960","brand":{"@type":"Brand","name":"Porsche","logo":"https://cdn.ui.porsche.com/porsche-design-system/marque/porsche-marque-trademark.medium.min.fff6e9b91481cc5b1fc6c9b62987ccaf@2x.webp"},"manufacturer":{"@type":"Organization"},"dateVehicleFirstRegistered":"2022-10-26T00:00:00.000Z","mileageFromOdometer":{"@type":"QuantitativeValue","value":33399,"unitCode":"SMI"},"numberOfPreviousOwners":3,"vehicleIdentificationNumber":"WP0ZZZY1ZNSA75297","vehicleInteriorColor":"Black/crayon Two-tone Leather Interior With Smooth-finish Leather","vehicleTransmission":"Automatic","modelDate":"2022-01-01T00:00:00.000Z","offers":{"@type":"Offer","url":"/gb/en-GB/details/porsche-taycan-sport-turismo-my22-preowned-V3D9GR?model=taycan&category=taycan-sport-turismo&category=taycan-4-cross-turismo&order=price_asc","price":50890,"priceCurrency":"GBP","itemCondition":"https://schema.org/UsedCondition","availability":"https://schema.org/InStock","seller":{"@type":"Organization","name":"Porsche Centre Nottingham","address":" Landmere Lane, Edwalton \\n Nottingham, NG12 4DE"},"warranty":{"@type":"WarrantyPromise","durationOfWarranty":{"@type":"QuantitativeValue","value":24,"unitCode":"MON"}}},"vehicleModelDate":"2022-01-01T00:00:00.000Z","itemCondition":"https://schema.org/UsedCondition","vehicleEngine":{"@type":"EngineSpecification","fuelType":"ELECTRIC"},"vehicleInteriorType":"Black/Crayon two-tone leather interior with smooth-finish leather","vehicleConfiguration":"Taycan Sport Turismo","bodyType":"Sport Turismo","driveWheelConfiguration":"https://schema.org/RearWheelDriveConfiguration"}'
    json_str_new_price = '{"@context":"https://schema.org","@type":"Car","name":"Taycan Sport Turismo (MY22)","model":"J1","color":"Gentian Blue Metallic","image":"https://images.finder.porsche.com/5df59467-54f3-414c-90f4-132ed260a942/960","brand":{"@type":"Brand","name":"Porsche","logo":"https://cdn.ui.porsche.com/porsche-design-system/marque/porsche-marque-trademark.medium.min.fff6e9b91481cc5b1fc6c9b62987ccaf@2x.webp"},"manufacturer":{"@type":"Organization"},"dateVehicleFirstRegistered":"2022-10-26T00:00:00.000Z","mileageFromOdometer":{"@type":"QuantitativeValue","value":33399,"unitCode":"SMI"},"numberOfPreviousOwners":3,"vehicleIdentificationNumber":"WP0ZZZY1ZNSA75297","vehicleInteriorColor":"Black/crayon Two-tone Leather Interior With Smooth-finish Leather","vehicleTransmission":"Automatic","modelDate":"2022-01-01T00:00:00.000Z","offers":{"@type":"Offer","url":"/gb/en-GB/details/porsche-taycan-sport-turismo-my22-preowned-V3D9GR?model=taycan&category=taycan-sport-turismo&category=taycan-4-cross-turismo&order=price_asc","price":50580,"priceCurrency":"GBP","itemCondition":"https://schema.org/UsedCondition","availability":"https://schema.org/InStock","seller":{"@type":"Organization","name":"Tom Test Porsche Centre","address":" Test Street, AB1 2CD"},"warranty":{"@type":"WarrantyPromise","durationOfWarranty":{"@type":"QuantitativeValue","value":24,"unitCode":"MON"}}},"vehicleModelDate":"2022-01-01T00:00:00.000Z","itemCondition":"https://schema.org/UsedCondition","vehicleEngine":{"@type":"EngineSpecification","fuelType":"ELECTRIC"},"vehicleInteriorType":"Black/Crayon two-tone leather interior with smooth-finish leather","vehicleConfiguration":"Taycan Sport Turismo","bodyType":"Sport Turismo","driveWheelConfiguration":"https://schema.org/RearWheelDriveConfiguration"}'
    
    j = json.loads(json_str_new_price)
    db = CarDB('tests/testdb.json')
    c = scraper.process_listing_details(j, db)
    internal_car = car.create_car_record(c)
    scraper.write_car_to_db(internal_car, db)

if __name__ == "__main__":
    test_duplicate_car_check()