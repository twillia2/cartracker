import random
import json

def random_delay() -> float:
    # 70% chance of normal delay (7-10 seconds)
    # 20% chance of longer pause (10-20 seconds) 
    # 10% chance of quick (2-4 seconds)
    
    rand = random.random()
    if rand < 0.7:
        delay = random.uniform(10.0, 20.0)
    elif rand < 0.9:
        delay = random.uniform(20.0, 30.0)
    else:
        delay = random.uniform(4.0, 6.0)
    
    return delay

def log_price_history(price_history: json):
    ret = "price_history:"
    # remove dealer from the price change logging
    # because it's too verbose
    for record in price_history:
        ret += " "
        if 'price' in record:
            ret += f" [{record['price']}]"
        if 'date' in record:
            ret += f" at [{record['date']}]"
    
    return ret