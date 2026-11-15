from contextlib import closing
from datetime import datetime
from pathlib import Path

import duckdb

from distance import MNOZNIK_DROGI, PREDKOSC_MARSZU_M_MIN, minuty_marszu

SCIEZKA_BAZY = Path(__file__).parent / "dane" / "wedrowczyk.duckdb"

SCHEMAT = """
CREATE SEQUENCE IF NOT EXISTS seq_trasy START 1;
CREATE TABLE IF NOT EXISTS trasy (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_trasy'),
    czas TIMESTAMP NOT NULL,
    liczba_miejsc INTEGER,
    dlugosc_m DOUBLE,
    algorytm VARCHAR,
    czas_obliczen_ms DOUBLE,
    mnoznik_drogi DOUBLE,
    predkosc_m_min DOUBLE,
    faktyczny_czas_min DOUBLE
);
CREATE TABLE IF NOT EXISTS punkty_trasy (
    id_trasy INTEGER,
    kolejnosc INTEGER,
    nazwa VARCHAR,
    lat DOUBLE,
    lon DOUBLE,
    minuty_od_poprzedniego DOUBLE,
    PRIMARY KEY (id_trasy, kolejnosc)
);
"""


def polacz():
    """Otwiera bazę (tworzy folder, plik i tabele, jeśli ich nie ma).

    Używaj z closing(), żeby zamknąć połączenie i zwolnić plik.
    """
    SCIEZKA_BAZY.parent.mkdir(exist_ok=True)
    con = duckdb.connect(str(SCIEZKA_BAZY))
    con.execute(SCHEMAT)
    return con


def zapisz_trase(nazwy, wspolrzedne, macierz, trasa, dlugosc, algorytm, czas_obliczen_ms):
    """Zapisuje wyznaczoną trasę i jej punkty. Zwraca id trasy."""
    with closing(polacz()) as con:
        con.begin()
        try:
            id_trasy = con.execute(
                "INSERT INTO trasy (czas, liczba_miejsc, dlugosc_m, algorytm, "
                "czas_obliczen_ms, mnoznik_drogi, predkosc_m_min) "
                "VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id",
                [datetime.now(), len(trasa) - 1, dlugosc, algorytm, czas_obliczen_ms,
                 MNOZNIK_DROGI, PREDKOSC_MARSZU_M_MIN],
            ).fetchone()[0]
            wiersze = []
            for kolejnosc, idx in enumerate(trasa):
                minuty = None
                if kolejnosc > 0:
                    minuty = minuty_marszu(macierz[trasa[kolejnosc - 1]][idx])
                lat, lon = wspolrzedne[idx]
                wiersze.append((id_trasy, kolejnosc, nazwy[idx], lat, lon, minuty))
            con.executemany("INSERT INTO punkty_trasy VALUES (?, ?, ?, ?, ?, ?)", wiersze)
            con.commit()
        except Exception:
            con.rollback()
            raise
    return id_trasy
