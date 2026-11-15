import folium


def zbuduj_mape(etykiety, wspolrzedne, trasa):
    """Mapa z numerowanymi znacznikami i linią trasy (S = start)."""
    kolejnosc = [wspolrzedne[i] for i in trasa] + [wspolrzedne[trasa[0]]]
    mapa = folium.Map(location=wspolrzedne[0], zoom_start=13)
    folium.PolyLine(kolejnosc, weight=4, color="#3388ff", opacity=0.8).add_to(mapa)
    for nr, idx in enumerate(trasa):
        symbol = "S" if nr == 0 else str(nr)
        kolor = "#2e7d32" if nr == 0 else "#1565c0"
        html = (
            f'<div style="background:{kolor};color:white;border-radius:50%;'
            "width:28px;height:28px;line-height:28px;text-align:center;"
            f'font-weight:bold;border:2px solid white;">{symbol}</div>'
        )
        folium.Marker(
            wspolrzedne[idx],
            tooltip=etykiety[idx],
            icon=folium.DivIcon(icon_size=(28, 28), icon_anchor=(14, 14), html=html),
        ).add_to(mapa)
    mapa.fit_bounds(kolejnosc)
    return mapa
