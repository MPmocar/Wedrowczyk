from functools import lru_cache

from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

_geolokator = Nominatim(user_agent="wedrowczyk-planer-zwiedzania", timeout=10)
_szukaj = RateLimiter(_geolokator.geocode, min_delay_seconds=1, swallow_exceptions=False)


@lru_cache(maxsize=None)
def wspolrzedne(nazwa):
    """Zwraca (lat, lon) dla nazwy miejsca albo None, jeśli nie znaleziono."""
    wynik = _szukaj(nazwa)
    if wynik is None:
        return None
    return (wynik.latitude, wynik.longitude)
