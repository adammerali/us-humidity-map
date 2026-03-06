import threading
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from cities import CITIES
from fetch import fetch_humidity

# Bounding box for continental US + insets for AK/HI
CONUS_XLIM = (-128, -65)
CONUS_YLIM = (23,  52)


def humidity_color(value: int):
    norm = mcolors.Normalize(vmin=0, vmax=100)
    return cm.RdYlBu(norm(value))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("US Humidity Map")
        self.configure(bg="#1e1e2e")
        self.resizable(True, True)

        self._humidity: dict = {}
        self._build_ui()

    # ---- UI construction ----

    def _build_ui(self):
        # Top bar
        bar = tk.Frame(self, bg="#1e1e2e")
        bar.pack(fill="x", padx=10, pady=(8, 0))

        self._status = tk.StringVar(value="Press Refresh to fetch data.")
        tk.Label(bar, textvariable=self._status, bg="#1e1e2e",
                 fg="#cdd6f4", font=("Segoe UI", 10)).pack(side="left")

        self._btn = tk.Button(bar, text="Refresh", command=self._start_fetch,
                              bg="#89b4fa", fg="#1e1e2e",
                              font=("Segoe UI", 10, "bold"),
                              relief="flat", padx=12, pady=4)
        self._btn.pack(side="right")

        self._progress = ttk.Progressbar(bar, length=200, mode="determinate")
        self._progress.pack(side="right", padx=(0, 10))

        # Matplotlib figure
        self._fig, self._ax = plt.subplots(figsize=(11, 6),
                                           facecolor="#1e1e2e")
        self._canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._canvas.get_tk_widget().pack(fill="both", expand=True,
                                          padx=10, pady=8)

        self._draw_empty()

    # ---- Drawing ----

    def _draw_empty(self):
        ax = self._ax
        ax.set_facecolor("#181825")
        ax.set_xlim(*CONUS_XLIM)
        ax.set_ylim(*CONUS_YLIM)
        ax.set_title("US Relative Humidity", color="#cdd6f4",
                     fontsize=14, pad=10)
        ax.set_xlabel("Longitude", color="#6c7086", fontsize=8)
        ax.set_ylabel("Latitude",  color="#6c7086", fontsize=8)
        ax.tick_params(colors="#6c7086", labelsize=7)
        for spine in ax.spines.values():
            spine.set_edgecolor("#313244")
        self._canvas.draw()

    def _redraw(self):
        ax = self._ax
        ax.cla()
        self._draw_empty()

        if not self._humidity:
            self._canvas.draw()
            return

        lons, lats, values, labels = [], [], [], []
        for city, h in self._humidity.items():
            if city in CITIES:
                lat, lon = CITIES[city]
                # skip AK/HI for main plot (out of bounds)
                if CONUS_XLIM[0] <= lon <= CONUS_XLIM[1] and \
                   CONUS_YLIM[0] <= lat <= CONUS_YLIM[1]:
                    lons.append(lon)
                    lats.append(lat)
                    values.append(h)
                    labels.append(city)

        norm = mcolors.Normalize(vmin=0, vmax=100)
        colors = [humidity_color(v) for v in values]

        sc = ax.scatter(lons, lats, c=values, cmap="RdYlBu",
                        norm=norm, s=90, edgecolors="white",
                        linewidths=0.4, zorder=5)

        for lon, lat, city, h in zip(lons, lats, labels, values):
            ax.annotate(f"{h}%", (lon, lat),
                        textcoords="offset points", xytext=(5, 4),
                        fontsize=5.5, color="#cdd6f4", zorder=6)

        if not hasattr(self, "_cbar") or self._cbar is None:
            self._cbar = self._fig.colorbar(sc, ax=ax, fraction=0.025, pad=0.02)
            self._cbar.set_label("Humidity (%)", color="#cdd6f4", fontsize=9)
            self._cbar.ax.yaxis.set_tick_params(color="#6c7086")
            plt.setp(self._cbar.ax.yaxis.get_ticklabels(), color="#cdd6f4", fontsize=7)
        else:
            self._cbar.update_normal(sc)

        self._canvas.draw()

    # ---- Fetch logic (runs in background thread) ----

    def _start_fetch(self):
        self._btn.config(state="disabled")
        self._progress["value"] = 0
        self._status.set("Fetching...")
        threading.Thread(target=self._fetch_thread, daemon=True).start()

    def _fetch_thread(self):
        try:
            def on_progress(done, total, city):
                pct = done / total * 100
                self.after(0, lambda: self._progress.configure(value=pct))
                self.after(0, lambda: self._status.set(
                    f"Fetching... {done}/{total}  ({city})"))

            humidity = fetch_humidity(CITIES, progress_cb=on_progress)
            self._humidity = humidity
            self.after(0, self._on_fetch_done)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.after(0, lambda: self._btn.config(state="normal"))

    def _on_fetch_done(self):
        self._status.set(f"Loaded {len(self._humidity)} cities.")
        self._btn.config(state="normal")
        self._progress["value"] = 100
        self._redraw()


if __name__ == "__main__":
    app = App()
    app.mainloop()
