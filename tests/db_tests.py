import json
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))  # For config.py
sys.path.insert(0, str(project_root / 'src'))  # For src modules
from car import create_car_record
from database import CarDB

car_data_json_string = {"@context": "https://schema.org", "@type": "Car", "name": "Taycan 4 Cross Turismo (MY22)", "model": "J1", "color": "Jet Black Metallic", "image": "https://images.finder.porsche.com/f02c778c-346b-4610-9f51-ae175510ed49/960", "brand": {"@type": "Brand", "name": "Porsche", "logo": "https://cdn.ui.porsche.com/porsche-design-system/marque/porsche-marque-trademark.medium.min.fff6e9b91481cc5b1fc6c9b62987ccaf@2x.webp"}, "manufacturer": {"@type": "Organization"}, "dateVehicleFirstRegistered": "2021-12-29T00:00:00.000Z", "mileageFromOdometer": {"@type": "QuantitativeValue", "value": 42000, "unitCode": "SMI"}, "numberOfPreviousOwners": 2, "vehicleIdentificationNumber": "WP0ZZZY1ZNSA62499", "vehicleInteriorColor": "Black/bordeaux Red Two-tone Leather Interior With Smooth-finish Leather", "vehicleTransmission": "Automatic", "modelDate": "2022-01-01T00:00:00.000Z", "offers": {"@type": "Offer", "url": "/gb/en-GB/details/porsche-taycan-4-cross-turismo-my22-preowned-RLDD97?model=taycan&category=taycan-sport-turismo&category=taycan-4-cross-turismo&maximum-price=60000&order=newest", "price": 47890, "priceCurrency": "GBP", "itemCondition": "https://schema.org/UsedCondition", "availability": "https://schema.org/InStock", "seller": {"@type": "Organization", "name": "Porsche Centre tomw", "address": " The Boulevard, City One West Park \n Leeds, LS12 6BG"}, "warranty": {"@type": "WarrantyPromise", "durationOfWarranty": {"@type": "QuantitativeValue", "value": 24, "unitCode": "MON"}}}, "vehicleModelDate": "2022-01-01T00:00:00.000Z", "itemCondition": "https://schema.org/UsedCondition", "vehicleEngine": {"@type": "EngineSpecification", "fuelType": "ELECTRIC"}, "vehicleInteriorType": "Black/Bordeaux Red two-tone leather interior with smooth-finish leather", "vehicleConfiguration": "Taycan 4 Cross Turismo", "bodyType": "Cross Turismo", "driveWheelConfiguration": "https://schema.org/AllWheelDriveConfiguration", "raw_options": ["BOSE® Surround Sound System", "Sport Chrono Package", "Air Suspension", "Panoramic Roof", "ParkAssist (Front and Rear) including Reversing Camera", "Adaptive Cruise Control incl. Porsche Active Safe", "Head-Up Display", "Performance Battery Plus"], "internal_options": {"bose": True, "burmester": False, "sport_chrono": True, "air_suspension": True, "pano_roof": True, "park_assist": True, "acc": True, "hud": True, "perf_battery": True, "matrix": False, "leds": False}}

def test_car_creation():
    c = create_car_record(car_data_json_string)

    db = CarDB('data/testdb.json')
    _, result = db.update_car(c)

    print(result)


if __name__ == '__main__':
    test_car_creation()