import streamlit as st
from streamlit_searchbox import st_searchbox

from distance import macierz_odleglosci, minuty_marszu
from geocoding import podpowiedzi
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

st.title("Wędrowczyk")

st.subheader("1. Punkt startu")
wybrany_start = st_searchbox(
    szukaj_startu, key="sb_start", placeholder="Adres hotelu lub miejsce", debounce=400
)
if st.button("Ustaw jako start", disabled=wybrany_start is None):
    st.session_state.start = wybrany_start
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
        st.rerun()
for nr, (etykieta, _) in enumerate(miejsca, start=1):
    st.write(f"{nr}. {etykieta}")

if st.button("Wyznacz trasę"):
    if not st.session_state.start or not miejsca:
        st.warning("Ustaw punkt startu i dodaj co najmniej jedno miejsce.")
    else:
        punkty = [st.session_state.start] + miejsca
        nazwy = [etykieta for etykieta, _ in punkty]
        macierz = macierz_odleglosci([wsp for _, wsp in punkty])
        trasa, dlugosc = brute_force(macierz)

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
        st.success(f"Łącznie ok. {minuty_marszu(dlugosc):.0f} min marszu")

st.caption("Dane map: © OpenStreetMap contributors")
