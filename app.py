import time

import streamlit as st
from streamlit_folium import st_folium
from streamlit_searchbox import st_searchbox

from baza import zapisz_trase
from distance import macierz_odleglosci, minuty_marszu
from geocoding import podpowiedzi
from mapa import zbuduj_mape
from solver import brute_force

MAX_MIEJSC = 8


def _szukaj(fraza, blisko):
    """Podpowiedzi dla searchboxa: lista (tekst do wyświetlenia, wartość)."""
    try:
        wyniki = podpowiedzi(fraza, blisko)
    except Exception:
        return []
    unikalne = dict(wyniki)  # usuwa duplikaty etykiet
    return [(etykieta, (etykieta, wsp)) for etykieta, wsp in unikalne.items()]


def szukaj_startu(fraza):
    return _szukaj(fraza, None)


def szukaj_miejsca(fraza):
    start = st.session_state.start
    return _szukaj(fraza, start[1] if start else None)


st.session_state.setdefault("start", None)  # (etykieta, (lat, lon))
st.session_state.setdefault("miejsca", [])  # lista takich krotek
st.session_state.setdefault("licznik", 0)   # do czyszczenia pola po dodaniu
st.session_state.setdefault("licznik_startu", 0)  # j.w., dla pola startu
st.session_state.setdefault("wynik", None)  # ostatnio wyznaczona trasa

st.title("Wędrowczyk")

st.subheader("1. Punkt startu")
wybrany_start = st_searchbox(
    szukaj_startu,
    key=f"sb_start_{st.session_state.licznik_startu}",
    placeholder="Adres hotelu lub miejsce",
    debounce=400,
)
if st.button("Ustaw jako start", disabled=wybrany_start is None):
    st.session_state.start = wybrany_start
    st.session_state.wynik = None
if st.session_state.start:
    st.caption(f"Start: {st.session_state.start[0]}")

st.subheader("2. Miejsca do zwiedzenia")
miejsca = st.session_state.miejsca
wybrane = st_searchbox(
    szukaj_miejsca,
    key=f"sb_miejsce_{st.session_state.licznik}",
    placeholder="Nazwa miejsca lub adres",
    debounce=400,
)
if st.button("Dodaj do listy", disabled=wybrane is None):
    if len(miejsca) >= MAX_MIEJSC:
        st.warning(f"Maksymalnie {MAX_MIEJSC} miejsc (limit brute force).")
    elif wybrane in miejsca:
        st.info("To miejsce już jest na liście.")
    else:
        miejsca.append(wybrane)
        st.session_state.licznik += 1
        st.session_state.wynik = None
        st.rerun()
if miejsca:
    st.caption("Dotknij miejsca, aby usunąć je z listy:")
for i, (etykieta, _) in enumerate(miejsca):
    if st.button(f"✕ {i + 1}. {etykieta}", key=f"usun_{i}"):
        miejsca.pop(i)
        st.session_state.wynik = None
        st.rerun()

if st.button("Wyczyść wszystko"):
    st.session_state.start = None
    st.session_state.miejsca = []
    st.session_state.wynik = None
    st.session_state.licznik += 1
    st.session_state.licznik_startu += 1
    st.rerun()

if st.button("Wyznacz trasę"):
    if not st.session_state.start or not miejsca:
        st.warning("Ustaw punkt startu i dodaj co najmniej jedno miejsce.")
    else:
        punkty = [st.session_state.start] + miejsca
        nazwy = [etykieta for etykieta, _ in punkty]
        wsp = [w for _, w in punkty]
        macierz = macierz_odleglosci(wsp)
        start_obliczen = time.perf_counter()
        trasa, dlugosc = brute_force(macierz)
        czas_obliczen_ms = (time.perf_counter() - start_obliczen) * 1000
        try:
            zapisz_trase(nazwy, wsp, macierz, trasa, dlugosc, "brute_force", czas_obliczen_ms)
        except Exception as e:
            st.warning(f"Nie zapisano trasy w bazie: {e}")
        st.session_state.wynik = {
            "nazwy": nazwy,
            "wsp": wsp,
            "macierz": macierz,
            "trasa": trasa,
            "dlugosc": dlugosc,
        }

wynik = st.session_state.wynik
if wynik:
    nazwy, macierz, trasa = wynik["nazwy"], wynik["macierz"], wynik["trasa"]
    st.subheader("Kolejność zwiedzania")
    st.write(f"Start: {nazwy[0]}")
    narastajaco = 0
    for nr, (skad, dokad) in enumerate(zip(trasa, trasa[1:]), start=1):
        odcinek = minuty_marszu(macierz[skad][dokad])
        narastajaco += odcinek
        st.markdown(f"**{nr}. {nazwy[dokad]}**")
        st.caption(f"{odcinek:.0f} min od poprzedniego punktu · {narastajaco:.0f} min od startu")
    powrot = minuty_marszu(macierz[trasa[-1]][0])
    st.markdown(f"**Powrót do startu: {nazwy[0]}**")
    st.caption(f"{powrot:.0f} min od poprzedniego punktu · {narastajaco + powrot:.0f} min od startu")
    st.success(f"Łącznie ok. {minuty_marszu(wynik['dlugosc']):.0f} min marszu")

    st.subheader("Mapa")
    st_folium(
        zbuduj_mape(nazwy, wynik["wsp"], trasa),
        height=450,
        use_container_width=True,
        returned_objects=[],
    )

st.caption("Dane map: © OpenStreetMap contributors")
