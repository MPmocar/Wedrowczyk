from itertools import permutations


def dlugosc_trasy(trasa, macierz, wroc_do_startu=True):
    """Suma odległości między kolejnymi punktami trasy."""
    suma = sum(macierz[a][b] for a, b in zip(trasa, trasa[1:]))
    if wroc_do_startu:
        suma += macierz[trasa[-1]][trasa[0]]
    return suma


def brute_force(macierz, wroc_do_startu=True):
    """Punkt 0 to start. Sprawdza wszystkie kolejności pozostałych punktów.

    Zwraca (najlepsza_trasa, jej_długość).
    """
    pozostale = range(1, len(macierz))
    najlepsza, najlepsza_dlugosc = None, float("inf")
    for perm in permutations(pozostale):
        trasa = (0, *perm)
        d = dlugosc_trasy(trasa, macierz, wroc_do_startu)
        if d < najlepsza_dlugosc:
            najlepsza, najlepsza_dlugosc = list(trasa), d
    return najlepsza, najlepsza_dlugosc
