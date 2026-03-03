import plotly.graph_objects as go


def plot_map(cities: dict, humidity: dict, output: str = "humidity_map.html"):
    lats   = [cities[c][0] for c in humidity]
    lons   = [cities[c][1] for c in humidity]
    names  = list(humidity.keys())
    values = list(humidity.values())

    fig = go.Figure(go.Scattergeo(
        lat=lats, lon=lons,
        text=[f"<b>{n}</b><br>{v}%" for n, v in zip(names, values)],
        hoverinfo="text",
        mode="markers",
        marker=dict(
            size=14,
            color=values,
            colorscale="Blues",
            cmin=0, cmax=100,
            colorbar=dict(title="Humidity (%)"),
            line=dict(width=1, color="white"),
        ),
    ))

    fig.update_layout(
        title=dict(text="US Relative Humidity", x=0.5),
        geo=dict(
            scope="usa",
            projection_type="albers usa",
            showland=True, landcolor="rgb(240,240,240)",
            showlakes=True, lakecolor="rgb(200,220,255)",
        ),
        margin=dict(l=0, r=0, t=50, b=0),
    )

    fig.write_html(output)
    print(f"saved: {output}")
