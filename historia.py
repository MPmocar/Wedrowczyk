import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import gspread
import streamlit as st

from distance import MNOZNIK_DROGI, PREDKOSC_MARSZU_M_MIN, minuty_marszu

NAZWA_ZAKLADKI = "trasy"
NAGLOWKI = [
    "id_trasy", "czas", "srodowisko", "wroc_do_startu", "liczba_miejsc",
    "dlugosc_trasy_m", "algorytm", "mnoznik_drogi", "predkosc_m_min",
    "faktyczny_czas_min", "kolejnosc", "nazwa", "lat", "lon", "minuty_od_poprzedniego",
]


@st.cache_resource(show_spinner=False)
def _zakladka():
    """Loguje się do Google (raz na proces) i zwraca zakładkę z trasami."""
    klient = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
    arkusz = klient.open_by_key(st.secrets["gsheets"]["spreadsheet_id"])
    zakladka = arkusz.worksheet(NAZWA_ZAKLADKI)
    if not zakladka.row_values(1):
        zakladka.append_row(NAGLOWKI, value_input_option="RAW")
    return zakladka


def zapisz_trase(nazwy, wspolrzedne, macierz, trasa, dlugosc, wroc_do_startu,
                 algorytm="brute_force", srodowisko=None):
    """Dopisuje trasę do arkusza (jeden wiersz na punkt). Zwraca id trasy."""
    if srodowisko is None:
        srodowisko = st.secrets["gsheets"].get("srodowisko", "nieznane")
    zakladka = _zakladka()
    id_trasy = str(uuid.uuid4())
    czas = datetime.now(ZoneInfo("Europe/Warsaw")).isoformat(timespec="seconds")
    wiersze = []
    for kolejnosc, idx in enumerate(trasa):
        minuty = ""
        if kolejnosc > 0:
            minuty = round(minuty_marszu(macierz[trasa[kolejnosc - 1]][idx]), 1)
        lat, lon = wspolrzedne[idx]
        wiersze.append([
            id_trasy, czas, srodowisko, wroc_do_startu, len(trasa) - 1,
            round(dlugosc), algorytm, MNOZNIK_DROGI, PREDKOSC_MARSZU_M_MIN,
            "", kolejnosc, nazwy[idx], lat, lon, minuty,
        ])
    zakladka.append_rows(wiersze, value_input_option="RAW")
    return id_trasy
