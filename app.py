import streamlit as st

from distance import macierz_odleglosci, minuty_marszu
from geocoding import wspolrzedne
from solver import brute_force

MAX_MIEJSC = 8

st.title("Wędrowczyk")

miasto = st.text_input("Miasto", placeholder="np. Kraków")
start = st.text_input("Punkt startu (adres hotelu)")
miejsca_tekst = st.text_area("Miejsca do zwiedzenia (jedno w linii)", height=200)

if st.button("Wyznacz trasę"):
    miejsca = [m.strip() for m in miejsca_tekst.splitlines() if m.strip()]
    if not miasto or not start or not miejsca:
        st.warning("Uzupełnij miasto, punkt startu i co najmniej jedno miejsce.")
    elif len(miejsca) > MAX_MIEJSC:
        st.warning(f"Maksymalnie {MAX_MIEJSC} miejsc (limit brute force).")
    else:
        nazwy = [start] + miejsca
        try:
            with st.spinner("Szukam miejsc na mapie..."):
                punkty = [wspolrzedne(f"{n}, {miasto}") for n in nazwy]
        except Exception as e:
            st.error(f"Błąd połączenia z Nominatim: {e}")
            st.stop()

        brak = [n for n, p in zip(nazwy, punkty) if p is None]
        if brak:
            st.error("Nie znaleziono: " + ", ".join(brak))
            st.stop()

        macierz = macierz_odleglosci(punkty)
        trasa, dlugosc = brute_force(macierz)

        st.subheader("Kolejność zwiedzania")
        st.write(f"Start: {start}")
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
