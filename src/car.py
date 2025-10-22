from datetime import datetime
from config import config
import json
import logging

log = logging.getLogger('cartracker')

def parse_highlights(car_options_highlights):
    if not car_options_highlights:
        # Return all False if no options
        return {key: False for key in config.car_options.keys()}
    
    # Join all options into one lowercase string for matching
    options_text = ' '.join(car_options_highlights).lower()
    
    # Check each spec keyword
    return {
        key: keyword.lower() in options_text
        for key, keyword in config.car_options.items()
    }

def extract_dealer_info(car_data):
    seller = car_data.get('offers', {}).get('seller')
    
    return {
        'name': seller.get('name'),
        'address': seller.get('address', '').strip() if seller.get('address') else None
    }

#def update_car_record(new_car_data: json, old_car_data: json):
    # update anything that's changed (most likely price but let's handle anything)
    # however we need to avoid updating the 'first_seen' value 
    #for k, v in new_car_data:
    #    if k in old_car_data:
    #        k[v] = new_car_data[k].value

def create_car_record(car_data: json):
    log.debug(f'car::create_car_record: vin [{car_data.get('vehicleIdentificationNumber')}]')
    # this accesses the info from the website assuming it follows the Car schema
    # https://schema.org/Car
    # get 2-digit MY and first reg from iso date like '2022-01-01T00:00:00.000Z'
    date_str = car_data.get('vehicleModelDate') or car_data.get('modelDate')
    my = date_str[2:4] if date_str and len(date_str) >= 4 else None
    
    reg_date_str = car_data.get('dateVehicleFirstRegistered')
    registration_date = reg_date_str.split('T')[0] if reg_date_str else None
    
    dealer = extract_dealer_info(car_data)
    price = extract_price(car_data)

    car_record = {
        'vin': car_data.get('vehicleIdentificationNumber', 'UNKNOWN'),
        'name': car_data.get('name'),
        'model': car_data.get('model'),
        'mileage': car_data.get('mileageFromOdometer', {}).get('value'),
        'color': car_data.get('color'),
        'interior_color': car_data.get('vehicleInteriorColor'),
        'previous_owners': car_data.get('numberOfPreviousOwners'),
        'current_price': extract_price(car_data),
        'url': car_data.get('offers',{}).get('url'),
        'my': my,
        'first_reg': registration_date,

        # parsed view of 'equipment highlights'        
        'options': car_data.get('internal_options'),
        # keep the un-parsed one in case we make a mistake parsing
        'raw_options': car_data.get('raw_options'),
        
        'dealer': dealer,
        'price_history': [
            {
                'price': price,
                'date': datetime.now().isoformat(),
                'currency': 'GBP',
                'dealer': dealer
            }
        ],
        'current_price': price,

        # timestamps
        'first_seen': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat(),
    }

    log.debug(f'car::create_car_record: {car_record}')

    return car_record

def extract_price(car_data):
    offers = car_data.get('offers', {})
    if isinstance(offers, dict):
        return offers.get('price')
    elif isinstance(offers, list) and offers:
        return offers[0].get('price')
    return None
