# Wędrowczyk – dokumentacja projektu

Aplikacja webowa (Streamlit), otwierana na telefonie, która dla listy miejsc w mieście
wyznacza najkrótszą kolejność ich odwiedzenia (problem komiwojażera, TSP).

## 1. Jak to działa w skrócie

Użytkownik wybiera punkt startu i miejsca (z podpowiedziami), a aplikacja:

```
nazwy miejsc ──► [geocoding] ──► współrzędne ──► [distance] ──► macierz odległości
                                                                       │
mapa ◄── [mapa] ◄── kolejność trasy ◄── [solver] ◄─────────────────────┘
```

- **Podpowiedzi i współrzędne:** Photon (photon.komoot.io), darmowy geokoder na danych OpenStreetMap.
- **Odległości:** wzór haversine (linia prosta po kuli ziemskiej), czas marszu = odległość × mnożnik
  drogi / prędkość.
- **Kolejność:** brute force (sprawdzenie wszystkich permutacji), do 8 miejsc plus start.
- **Wynik:** ponumerowana lista z czasami i mapa folium.
- **Tryb trasy:** zamknięta (powrót do startu) albo otwarta (koniec w ostatnim punkcie).

## 2. Drzewo plików i folderów

```
wedrowczyk/
├── __pycache__/        # tylko lokalnie (ignorowany przez Git)
├── .git/               # historia repozytorium (nie edytować ręcznie)
├── .venv/              # tylko lokalnie (ignorowany przez Git)
├── .gitignore
├── app.py
├── distance.py
├── DOKUMENTACJA.md
├── geocoding.py
├── LICENSE
├── mapa.py
├── requirements.txt
└── solver.py
```

### Foldery

**`__pycache__/`**
- Skompilowane wersje plików `.py` (np. `app.cpython-314.pyc`; `314` to wersja Pythona).
- Python tworzy je sam, żeby przy kolejnym imporcie nie kompilować kodu od nowa.
- Można skasować, odtworzy się. Nie ma go w repo (`.gitignore`).

**`.git/`**
- Cała „pamięć" repozytorium. Bez niego folder przestaje być repo i znika historia commitów.
- `objects/` – zapisane wersje plików i commity (identyfikowane skrótami, np. `0141553`).
- `refs/`, `HEAD` – wskaźniki „na którym commicie i gałęzi jestem" (`main`).
- `config` – ustawienia repo, m.in. adres zdalnego repo `origin` (GitHub) i informacja,
  że lokalny `main` śledzi `origin/main` (dlatego `git push` bez argumentów wie, dokąd wysłać).
- `index` – „poczekalnia": to, co dodano przez `git add`, a jeszcze nie zacommitowano.
- `COMMIT_EDITMSG` – treść ostatniego komunikatu commita.
- `FETCH_HEAD`, `ORIG_HEAD` – ślady ostatnich operacji (pobranie z GitHuba, rebase).
- `hooks/` – skrypty uruchamiane automatycznie przy commicie (domyślnie tylko przykłady).
- `logs/` – dziennik zmian gałęzi.

**`.venv/`**
- Wirtualne środowisko: prywatny, odizolowany Python tego projektu (ok. 490 MB, bo zawiera
  Streamlit, pandas, numpy i inne zależności).
- `Scripts/` – programy (`python.exe`, `pip.exe`, `streamlit.exe`, `Activate.ps1`).
- `Lib/` – zainstalowane biblioteki.
- `pyvenv.cfg` – informacja, z jakiego Pythona powstało środowisko; `include-system-site-packages = false`
  oznacza, że nie widzi bibliotek z globalnego Pythona (pełna izolacja).
- Nie idzie do repo: jest ogromne i zależne od komputera. Odtwarza się z `requirements.txt`.

### Pliki konfiguracyjne i opisowe

**`.gitignore`**
- Lista wzorców, których Git ma nie śledzić: `.venv/`, `__pycache__/`, `*.pyc`,
  `.streamlit/secrets.toml` (przyszłe klucze API, które nie mogą trafić do publicznego repo).
- Linie z `#` to komentarze. Działa tylko na pliki, których Git jeszcze nie śledzi.

**`requirements.txt`**
- Lista bibliotek, jedna na linię. Streamlit Cloud czyta ją po `git push` i instaluje na serwerze.
- `streamlit` – aplikacja, `requests` – zapytania HTTP do Photona, `folium` – mapa,
  `streamlit-folium` – osadzenie mapy w Streamlit, `streamlit-searchbox` – pole z podpowiedziami.
- Lokalnie odpowiada jej `python -m pip install -r requirements.txt`.

**`LICENSE`**
- Licencja MIT: każdy może używać, zmieniać i rozpowszechniać kod, zachowując informację
  o autorze, bez żadnej gwarancji.

**`DOKUMENTACJA.md`**
- Ten plik. Format Markdown, w VS Code podgląd pod `Ctrl+Shift+V`.

### Pliki Pythona

**`app.py`** – interfejs; jedyny plik uruchamiany bezpośrednio (`streamlit run app.py`).
- Pola wyszukiwania (start i miejsca), przyciski: „Ustaw jako start", „Dodaj do listy",
  `✕` przy miejscu (usuwanie pojedynczego), „Wyczyść wszystko", „Wyznacz trasę".
- Przełącznik „Wróć do punktu startu na końcu" (domyślnie włączony).
- Stała `MAX_MIEJSC = 8` (limit brute force).
- Wynik (lista z czasami + mapa) rysowany ze `st.session_state.wynik`.

**`geocoding.py`** – `podpowiedzi(fraza, blisko=None, limit=5)`
- Zwraca listę `(etykieta, (lat, lon))`. Fraza krótsza niż 3 znaki daje pustą listę.
- `blisko=(lat, lon)` faworyzuje wyniki w pobliżu punktu (używane: współrzędne startu).
- Wyniki cache'owane (`lru_cache`). Photon zwraca współrzędne jako `lon, lat` (GeoJSON),
  funkcja odwraca je na `(lat, lon)`.

**`distance.py`**
- Stałe: `PROMIEN_ZIEMI_M`, `PREDKOSC_MARSZU_M_MIN = 75` (ok. 4,5 km/h),
  `MNOZNIK_DROGI = 1.4` (linia prosta → realna droga po mieście).
- `haversine(p1, p2)` – odległość w metrach między dwoma punktami `(lat, lon)`.
- `macierz_odleglosci(punkty)` – macierz `m[i][j]` w metrach.
- `minuty_marszu(metry)` – czas marszu w minutach (z mnożnikiem).
- Mnożnik nie zmienia kolejności trasy (skaluje wszystkie odległości jednakowo), tylko
  wyświetlane minuty.

**`solver.py`**
- `dlugosc_trasy(trasa, macierz, wroc_do_startu=True)` – suma odcinków trasy.
- `brute_force(macierz, wroc_do_startu=True)` – punkt 0 to start; sprawdza wszystkie
  permutacje pozostałych punktów, zwraca `(najlepsza_trasa, długość)`.
- Złożoność `(n-1)!` (9 punktów to 40 320 kombinacji). Przyjmuje dowolną macierz,
  więc podmiana na realne czasy to zmiana tylko w `distance.py`.

**`mapa.py`** – `zbuduj_mape(etykiety, wspolrzedne, trasa, wroc=True)`
- Mapa folium: zielony znacznik `S` (start), niebieskie numerowane znaczniki, linia trasy;
  przy `wroc=True` linia wraca do startu. `fit_bounds` dopasowuje przybliżenie.

## 3. Jak pliki są ze sobą połączone

```
app.py ──► geocoding.py   (podpowiedzi)
   │
   ├────► distance.py     (macierz_odleglosci, minuty_marszu)
   ├────► solver.py       (brute_force)
   └────► mapa.py         (zbuduj_mape)
```

`app.py` importuje funkcje z pozostałych plików, a one nie wiedzą nic o `app.py`. Dzięki temu
każdą część można testować osobno (np. `solver.py` samą macierzą, bez internetu) i wymieniać
bez dotykania reszty.

## 4. Jak działa Streamlit

- **Cały `app.py` wykonuje się od góry do dołu przy każdej interakcji** (kliknięcie, wpisanie, zmiana przełącznika).
- Zwykłe zmienne znikają między przebiegami, więc trwałe rzeczy (start, lista miejsc, wynik)
  trzymamy w `st.session_state` (osobny dla każdej karty przeglądarki).
- `if st.button(...)` jest prawdziwe tylko w przebiegu, w którym kliknięto. Dlatego wynik zapisujemy
  do `session_state` i rysujemy poza blokiem przycisku.
- Klucze pól wyszukiwania mają liczniki (`sb_miejsce_0`, `_1`, …). Nowy klucz = nowe, puste pole;
  tak „czyścimy" pole po dodaniu miejsca lub resecie.
- Zmiana przełącznika powrotu, dodanie/usunięcie miejsca lub zmiana startu zeruje poprzedni wynik,
  żeby na ekranie nie wisiała trasa nieaktualna.

## 5. Droga od edycji do telefonu

```
edycja kodu ──► git commit ──► git push ──► GitHub ──► Streamlit Cloud ──► telefon
(komputer)     (zapis w        (wysłanie)   (repo)     (pobiera repo,
                historii)                              instaluje requirements.txt,
                                                       uruchamia `streamlit run app.py`)
```

Po `git push` Streamlit Cloud sam wykrywa zmianę i przebudowuje aplikację (auto-deploy).
Aplikacja usypia po ok. 12 h bez ruchu; wybudzenie trwa chwilę. Streamlit Cloud ma ulotny dysk
(dane zapisane na nim znikają przy restarcie).

## 6. Z kim aplikacja rozmawia na zewnątrz

- **Photon** (photon.komoot.io) – podpowiedzi i współrzędne, wywoływany z `geocoding.py`. Darmowy,
  ale „extensive usage will be throttled": stąd cache, minimum 3 znaki i `debounce=400` ms w polu.
- **Kafelki OpenStreetMap** – mapę rysuje przeglądarka, bezpośrednio z serwerów OSM. Stąd obowiązek
  podpisu „© OpenStreetMap contributors" (jest na dole strony).
- **GitHub i Streamlit Cloud** – tylko przy wdrożeniu.

Aplikacja nie ma backendu ani bazy danych: cała logika działa w jednym procesie Pythona,
a stan żyje tylko tak długo, jak otwarta karta.

## 7. Ściąga poleceń (PowerShell, w folderze projektu)

```bash
# aktywacja środowiska wirtualnego (przed (.venv) w wierszu poleceń)
.\.venv\Scripts\Activate.ps1

# uruchomienie aplikacji lokalnie (http://localhost:8501), zatrzymanie: Ctrl+C
streamlit run app.py

# instalacja bibliotek z requirements.txt
python -m pip install -r requirements.txt

# Git: stan, historia, zapis i wysyłka
git status
git log --oneline
git add nazwa_pliku
git commit -m "opis zmiany"
git push

# czy plik jest ignorowany przez Git i którą regułą
git check-ignore -v nazwa_pliku
```

Uwagi:
- Jeśli PowerShell zgłosi błąd polityki wykonywania skryptów przy aktywacji `.venv`:
  `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`.
- Działa tylko jedna instancja `streamlit run` na raz; kolejne zajmują kolejne porty (8502, …).

## 8. Stałe i miejsca do zmiany

| Co | Gdzie | Uwagi |
|---|---|---|
| Mnożnik krętości dróg (1,4) | `distance.py`, `MNOZNIK_DROGI` | zmienia tylko wyświetlane minuty |
| Prędkość marszu (75 m/min) | `distance.py`, `PREDKOSC_MARSZU_M_MIN` | |
| Limit miejsc (8) | `app.py`, `MAX_MIEJSC` | wynika z brute force: 9 punktów to 40 320 kombinacji |
| Opóźnienie podpowiedzi (400 ms) | `app.py`, `debounce` | większe = mniej zapytań do Photona |
| Minimalna długość frazy (3) | `geocoding.py`, `podpowiedzi` | |

## 9. Plan na później

- Komunikacja miejska: realne czasy przejazdu zamiast haversine (podmiana funkcji macierzy
  w `distance.py`), klucz API w `st.secrets`.
- Heurystyki (nearest neighbour + 2-opt) lub Held-Karp dla większej liczby miejsc;
  przy 2-opt trzeba uwzględnić różnicę między trasą zamkniętą i otwartą.
- Historia tras w bazie danych (nowa architektura, trwałe przechowywanie poza dyskiem
  Streamlit Cloud).
- GPS telefonu jako punkt startu (wymaga HTTPS, czyli wdrożonej aplikacji).
- `README.md` – strona tytułowa repo na GitHubie.
