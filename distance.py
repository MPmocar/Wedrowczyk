from math import asin, cos, radians, sin, sqrt

PROMIEN_ZIEMI_M = 6_371_000
PREDKOSC_MARSZU_M_MIN = 75  # ok. 4,5 km/h
MNOZNIK_DROGI = 1.4 # linia prosta -> realna droga po mieście


def haversine(p1, p2):
    """Odległość w metrach między dwoma punktami (lat, lon) po kuli ziemskiej."""
    lat1, lon1 = map(radians, p1)
    lat2, lon2 = map(radians, p2)
    a = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
    return 2 * PROMIEN_ZIEMI_M * asin(sqrt(a))


def macierz_odleglosci(punkty):
    """Macierz m[i][j] = odległość w metrach z punktu i do j."""
    return [[haversine(a, b) for b in punkty] for a in punkty]


def minuty_marszu(metry):
    """Szacowany czas marszu w minutach (z poprawką na krętość dróg)."""
    return metry * MNOZNIK_DROGI / PREDKOSC_MARSZU_M_MIN
