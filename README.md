# cartracker

A fairly dumb car listings scraper for a specific manufacturer. Uses either curl_cffi or selenium to do its browsing.

Maintains a simple tinydb database of car listings for price tracking.

## Configuration Options


logger

| option | type | description | valid values |
|--------|------|-------------|--------------|
| level | string | The log level. | INFO, DEBUG |
| directory | string | Logs written to this directory in '%Y-%m-%d'.log filename format | /path/to/logs/ |
| stderr | bool | Log to stderr as well as to the logfile. Defaults to `false` | `true`, `false` |


scraper

| option | type | description | valid values |
|--------|------|-------------|--------------|
| search_url | string | The url containing the initial search results | https://blah.com/search&attr |
| url_prefix | string | Prefix url to be used if/when we find sub-URLs in json objects on the search_url | https://blah.com |
| request_timeout | int | Time in seconds for scraper library to wait for a response (if applicable) | 10, 30, 60 etc |
| random_delays | bool | Randomise the wait between fetching new URLs. Defaults to `true` | `true`, `false` |
| scraper_library | string | Specify the library to use. | `curl_cffi`, `selenium` |
| curl_cffi_impersonate | string | Specify an 'impersonate' value for `curl_cffi` to use. Defaults to `safari18_4` | See your version of `curl_impersonate` |
| headless | bool | Allows the scraper to run on a commandline only system (but still requires xorg and chromium etc) | Defaults to `false` | `true`, `false` |
| force_resync | bool | Re-request, parse and write to db the full details for each listing, even if they appear unchanged. Defaults to `false` | `true`, `false` |
| chromedriver_path | string | Path to the chromium driver. Optional | /path/to/file |


database

| option | type | description | valid values |
|--------|------|-------------|--------------|
| path | string | Path to tinydb database file. Directory must exist. | /path/to/file |


car_options

A key / value list used for string matching specific equipment options off each car listing. Will be specific to the target website.



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
        "request_timeout": 30,
        "random_delays": true,
        "library": "selenium"
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


