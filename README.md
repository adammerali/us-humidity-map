# us-humidity-map

Pulls current relative humidity for 25 US cities from OpenWeatherMap and plots them on an interactive map. Color-coded by humidity %, hover for city details.

## Setup

Get a free API key at [openweathermap.org](https://openweathermap.org/api), then:

```bash
pip install -r requirements.txt
export OWM_API_KEY=your_key_here   # Windows: set OWM_API_KEY=your_key_here
python main.py
```

Outputs `humidity_map.html`.
