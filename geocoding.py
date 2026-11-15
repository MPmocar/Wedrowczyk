from functools import lru_cache

import requests

PHOTON_URL = "https://photon.komoot.io/api/"
NAGLOWKI = {"User-Agent": "wedrowczyk-planer-zwiedzania"}


def _etykieta(wlasciwosci):
    """Składa czytelny opis: nazwa, ulica nr, miasto, kraj."""
    ulica = " ".join(filter(None, [wlasciwosci.get("street"), wlasciwosci.get("housenumber")]))
    czesci = [wlasciwosci.get("name"), ulica, wlasciwosci.get("city"), wlasciwosci.get("country")]
    return ", ".join(c for c in czesci if c)


@lru_cache(maxsize=512)
def podpowiedzi(fraza, blisko=None, limit=5):
    """Zwraca listę (etykieta, (lat, lon)) pasujących miejsc.

    blisko = (lat, lon) lekko faworyzuje wyniki w pobliżu tego punktu.
    """
    if len(fraza) < 3:
        return []
    parametry = {"q": fraza, "limit": limit}
    if blisko:
        parametry["lat"], parametry["lon"] = blisko
    odp = requests.get(PHOTON_URL, params=parametry, headers=NAGLOWKI, timeout=10)
    odp.raise_for_status()
    wyniki = []
    for f in odp.json()["features"]:
        lon, lat = f["geometry"]["coordinates"]  # GeoJSON: najpierw lon, potem lat
        wyniki.append((_etykieta(f["properties"]), (lat, lon)))
    return wyniki
