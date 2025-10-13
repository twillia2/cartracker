# cartracker

A fairly dumb car listings scraper for a specific manufacturer. Website specific logic in `scraper.py` 

Maintains a simple tinydb database of listings for price tracking (not yet implemented)

## Example config

```
{
    "logger": {
        "level": "DEBUG",
        "directory": "logs",
        "stderr": false
    },
    "scraper": {
        "search_url": "https://www.carbrand.com/en-gb/search/cars?model=goodmodel&order=price_asc",
        "url_prefix": "https://www.carbrand.com",
        "user_agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "user_agents": ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"],
        "request_timeout": 30,
        "random_delays": true
    },
    "database": {
        "path": "data/cars.json"
    },
    "options": {
        "bose": "bose",
        "pano_roof": "panoramic",
        "acc": "adaptive cruise",
        "hud": "head-up",
        "matrix": "led matrix"
  }
}
```

