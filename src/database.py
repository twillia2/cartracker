from config import config
from tinydb import TinyDB, Query
from datetime import datetime
from reason import UpdateResult

class CarDB:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = config.db_path

        self.db = TinyDB(db_path)
        self.cars = self.db.table('cars')
    
    def update_car(self, car_record):
        Car = Query()
        existing = self.cars.get(Car.vin == car_record['vin'])
        
        if existing:
            # already exists - update price history if price changed
            price_changed = existing['current_price'] != car_record['current_price']
            if price_changed:
                # price history
                existing['price_history'].append({
                    'price': car_record['current_price'],
                    'date': datetime.now().isoformat(),
                    'currency': 'GBP',
                    'dealer': car_record['dealer']
                })
                existing['current_price'] = car_record['current_price']
            
            # update in database
            self.cars.update(existing, Car.vin == car_record['vin'])
            result = UpdateResult.PRICE_CHANGE if price_changed else UpdateResult.NO_CHANGE
            return existing, result
        else:
            # new car - insert it
            self.cars.insert(car_record)
            return car_record, UpdateResult.NEW_LISTING
    
    def get_by_vin(self, vin):
        Car = Query()
        return self.cars.get(Car.vin == vin)
    
    def get_price_history_for_vin(self, vin):
        return self.get_by_vin(vin)['price_history']
    
    def get_by_url(self, url):
        Car = Query()
        return self.cars.get(Car.url == url)
    
    def search_by_option(self, option_name):
        #find  specific option (case-insensitive partial match)
        Car = Query()
        return self.cars.search(
            Car.options.test(lambda opts: any(option_name.lower() in opt.lower() for opt in opts))
        )
    
    def search_by_price_range(self, min_price, max_price):
        Car = Query()
        return self.cars.search(
            (Car.current_price >= min_price) & (Car.current_price <= max_price)
        )
    
    def get_price_drops(self, min_drop=1000):
        cars_with_drops = []
        
        for car in self.cars.all():
            if len(car['price_history']) > 1:
                original_price = car['price_history'][0]['price']
                current_price = car['current_price']
                
                if original_price and current_price:
                    drop = original_price - current_price
                    if drop >= min_drop:
                        car['price_drop'] = drop
                        cars_with_drops.append(car)
        
        return sorted(cars_with_drops, key=lambda x: x['price_drop'], reverse=True)
    
    def get_all_cars(self):
        return self.cars.all()
    