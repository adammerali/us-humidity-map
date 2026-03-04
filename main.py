from cities import CITIES
from fetch import fetch_humidity
from visualize import plot_map

print(f"fetching humidity for {len(CITIES)} cities...")
humidity = fetch_humidity(CITIES)
plot_map(CITIES, humidity)
