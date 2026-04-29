"""Run once to generate preview.png for the README."""
import json
import os
import numpy as np
import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from cities import CITIES

GEOJSON_URL = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
GEOJSON_CACHE = "states.json"

XLIM = (-128, -65)
YLIM = (23,  52)


def load_states():
    if not os.path.exists(GEOJSON_CACHE):
        print("downloading state boundaries...")
        r = requests.get(GEOJSON_URL, timeout=15)
        r.raise_for_status()
        with open(GEOJSON_CACHE, "w") as f:
            f.write(r.text)
    with open(GEOJSON_CACHE) as f:
        return json.load(f)


def draw_states(ax, states):
    for feature in states["features"]:
        geom = feature["geometry"]
        polys = (geom["coordinates"] if geom["type"] == "Polygon"
                 else [p for p in geom["coordinates"]])
        for poly in polys:
            coords = poly if geom["type"] == "Polygon" else poly[0]
            xs = [c[0] for c in coords]
            ys = [c[1] for c in coords]
            ax.fill(xs, ys, color="#2a2a3e", zorder=1)
            ax.plot(xs, ys, color="#45475a", linewidth=0.5, zorder=2)


np.random.seed(7)

def sample_humidity(lat, lon):
    base = 60 - (lon + 90) * 0.4 + (lat - 35) * -0.5
    return int(np.clip(base + np.random.uniform(-12, 12), 10, 98))

humidity = {city: sample_humidity(lat, lon) for city, (lat, lon) in CITIES.items()}

fig, ax = plt.subplots(figsize=(13, 7), facecolor="#1e1e2e")
ax.set_facecolor("#181825")
ax.set_xlim(*XLIM)
ax.set_ylim(*YLIM)
ax.set_title("US Relative Humidity", color="#cdd6f4", fontsize=14, pad=10)
ax.set_xlabel("Longitude", color="#6c7086", fontsize=8)
ax.set_ylabel("Latitude",  color="#6c7086", fontsize=8)
ax.tick_params(colors="#6c7086", labelsize=7)
for spine in ax.spines.values():
    spine.set_edgecolor("#313244")

states = load_states()
draw_states(ax, states)

lons  = [CITIES[c][1] for c in humidity if XLIM[0] <= CITIES[c][1] <= XLIM[1] and YLIM[0] <= CITIES[c][0] <= YLIM[1]]
lats  = [CITIES[c][0] for c in humidity if XLIM[0] <= CITIES[c][1] <= XLIM[1] and YLIM[0] <= CITIES[c][0] <= YLIM[1]]
vals  = [humidity[c]  for c in humidity if XLIM[0] <= CITIES[c][1] <= XLIM[1] and YLIM[0] <= CITIES[c][0] <= YLIM[1]]
names = [c            for c in humidity if XLIM[0] <= CITIES[c][1] <= XLIM[1] and YLIM[0] <= CITIES[c][0] <= YLIM[1]]

norm = mcolors.Normalize(vmin=0, vmax=100)
sc = ax.scatter(lons, lats, c=vals, cmap="RdYlBu", norm=norm,
                s=70, edgecolors="white", linewidths=0.4, zorder=5)

for lon, lat, name, h in zip(lons, lats, names, vals):
    ax.annotate(f"{h}%", (lon, lat),
                textcoords="offset points", xytext=(5, 4),
                fontsize=5.5, color="#cdd6f4", zorder=6)

cbar = fig.colorbar(sc, ax=ax, fraction=0.025, pad=0.02)
cbar.set_label("Humidity (%)", color="#cdd6f4", fontsize=9)
cbar.ax.yaxis.set_tick_params(color="#6c7086")
plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#cdd6f4", fontsize=7)

plt.tight_layout()
plt.savefig("preview.png", dpi=150, bbox_inches="tight", facecolor="#1e1e2e")
print("saved preview.png")
