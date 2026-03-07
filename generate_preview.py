"""Run once to generate preview.png for the README."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from cities import CITIES

np.random.seed(7)

# Fake but geographically plausible humidity: southeast humid, southwest dry
def sample_humidity(lat, lon):
    base = 60
    base -= (lon + 90) * 0.4   # drier further west
    base += (lat - 35) * -0.5  # slightly more humid in south
    base += np.random.uniform(-12, 12)
    return int(np.clip(base, 10, 98))

humidity = {city: sample_humidity(lat, lon) for city, (lat, lon) in CITIES.items()}

XLIM = (-128, -65)
YLIM = (23, 52)

fig, ax = plt.subplots(figsize=(12, 6.5), facecolor="#1e1e2e")
ax.set_facecolor("#181825")
ax.set_xlim(*XLIM)
ax.set_ylim(*YLIM)
ax.set_title("US Relative Humidity", color="#cdd6f4", fontsize=14, pad=10)
ax.set_xlabel("Longitude", color="#6c7086", fontsize=8)
ax.set_ylabel("Latitude",  color="#6c7086", fontsize=8)
ax.tick_params(colors="#6c7086", labelsize=7)
for spine in ax.spines.values():
    spine.set_edgecolor("#313244")

lons  = [CITIES[c][1] for c in humidity if XLIM[0] <= CITIES[c][1] <= XLIM[1] and YLIM[0] <= CITIES[c][0] <= YLIM[1]]
lats  = [CITIES[c][0] for c in humidity if XLIM[0] <= CITIES[c][1] <= XLIM[1] and YLIM[0] <= CITIES[c][0] <= YLIM[1]]
vals  = [humidity[c]  for c in humidity if XLIM[0] <= CITIES[c][1] <= XLIM[1] and YLIM[0] <= CITIES[c][0] <= YLIM[1]]
names = [c            for c in humidity if XLIM[0] <= CITIES[c][1] <= XLIM[1] and YLIM[0] <= CITIES[c][0] <= YLIM[1]]

norm = mcolors.Normalize(vmin=0, vmax=100)
sc = ax.scatter(lons, lats, c=vals, cmap="RdYlBu", norm=norm,
                s=90, edgecolors="white", linewidths=0.4, zorder=5)

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
