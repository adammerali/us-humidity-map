import os
import time
import requests

API_KEY  = os.environ.get("OWM_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch_humidity(cities: dict, progress_cb=None) -> dict:
    if not API_KEY:
        raise EnvironmentError("OWM_API_KEY not set")

    results = {}
    for i, (city, (lat, lon)) in enumerate(cities.items()):
        r = requests.get(BASE_URL, params={
            "lat": lat, "lon": lon, "appid": API_KEY
        }, timeout=10)
        r.raise_for_status()
        results[city] = r.json()["main"]["humidity"]
        if progress_cb:
            progress_cb(i + 1, len(cities), city)
        time.sleep(0.2)

    return results
