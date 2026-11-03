# Steam Indie ES 2026

Pràctica 1 de *Tipologia i cicle de vida de les dades* (Màster universitari en Ciència de Dades, UOC).

**Integrants:** Joan Gordó Guardia · Ferran Rincon Puente

**Dataset a Zenodo (simulat):** https://doi.org/10.5281/zenodo.[XXXXXXX]

## Què fa aquest projecte

Un scraper en Python que construeix el **cens dels jocs indie traduïts al castellà** de la botiga de Steam
(https://store.steampowered.com/). Parteix d'una sola URL de cerca i treballa en tres fases:

1. **Descobriment (Selenium).** Obre la cerca de jocs Indie, fa scroll fins al final de la llista (la pàgina
   carrega els resultats a mesura que baixes) i extreu l'enllaç a la fitxa de cada joc. Si Steam respon
   "massa peticions" (HTTP 429), ho detecta al registre de xarxa del navegador i espera cada cop més.
2. **Extracció (Requests + BeautifulSoup).** Visita cada enllaç descobert i n'extreu **145 variables**: preu,
   valoracions, gèneres, etiquetes, característiques (inclosa la compatibilitat amb mando i RV), idiomes,
   requisits tècnics i multimèdia.
3. **Mostra audiovisual (opcional).** Per a una mostra aleatòria de jocs, descarrega les imatges i els
   tràilers, i reconstrueix els vídeos a partir dels fragments del streaming (HLS).

**Resultat:** `dataset/steam_indie_games.csv`, amb **26.298 jocs × 145 variables** (fitxes descarregades el 30 i el 31 d'octubre
de 2026). El diccionari de totes les variables és a `docs/variables.md`.

## Fitxers del repositori

| Fitxer | Contingut |
| --- | --- |
| `source/main.py` | Punt d'entrada: llegeix els paràmetres i executa les fases |
| `source/discover_games.py` | Fase 1: navegació per la cerca amb scroll infinit i descobriment d'enllaços |
| `source/scrape_games.py` | Fase 2: visita de cada fitxa, caché, represa i aturada de seguretat |
| `source/parse_game_page.py` | Converteix l'HTML d'una fitxa en una fila del dataset |
| `source/download_media.py` | Fase 3: descàrrega d'imatges i tràilers d'una mostra de jocs |
| `source/web_utils.py` | Bon ús: User-Agent, robots.txt, pauses, reintents i registre |
| `source/simulate_dataset.py` | Genera el dataset simulat que es publica a Zenodo |
| `dataset/steam_indie_games.csv` | Dataset resultant (UTF-8 amb BOM) |
| `docs/variables.md` | Diccionari de les 145 variables |
| `requirements.txt` | Llibreries necessàries |

En executar el codi es creen dues carpetes que **no es pugen al repositori** (vegeu `.gitignore`):

- `data/`: enllaços de la Fase 1 (`game_links.csv`), caché de les fitxes (`html_cache/`, uns 3 GB) i multimèdia
  de la Fase 3 (`media/`, amb el registre `media_sample.csv`).
- `logs/`: registre de l'execució (`scraper.log`) i còpia del `robots.txt`.

## Instal·lació

Requisits: Python 3.11 (o superior a 3.10) i Google Chrome. Selenium descarrega el driver de Chrome sol.

```bash
conda create -n prac1 python=3.11 -y
conda activate prac1
pip install -r requirements.txt
```

Per desar les versions exactes de l'entorn al `requirements.txt`:

```bash
pip list --format=freeze > requirements.txt
```

## Com utilitzar-lo

Totes les comandes s'executen des de la carpeta arrel del repositori:

```bash
python source/main.py --contact el_teu_correu@uoc.edu [opcions]
```

| Paràmetre | Per defecte | Què fa |
| --- | --- | --- |
| `--contact` | (obligatori) | Correu de contacte que s'inclou al User-Agent |
| `--step` | `all` | `discover` (Fase 1), `scrape` (Fase 2), `all` (fases 1 i 2) o `media` (Fase 3) |
| `--max-games` | 1000 | Nombre màxim de jocs a descobrir. Per al cens complet, un valor alt (50000) |
| `--game-lang` | (tots) | Només jocs traduïts a aquest idioma. Per al nostre dataset: `spanish` |
| `--subtags` | 0 | Nombre de subcategories d'Indie a recórrer (0 = només la cerca Indie) |
| `--limit` | (tots) | Fase 2: processa com a màxim N fitxes (per fer proves) |
| `--min-delay` / `--max-delay` | 2 / 4 | Pausa aleatòria entre peticions, en segons |
| `--show-browser` | no | Mostra la finestra de Chrome a la Fase 1 |
| `--cc` / `--lang` | `es` / `spanish` | País dels preus i idioma de la botiga |
| `--media-games` | 10 | Fase 3: nombre de jocs de la mostra audiovisual |

### Exemples

```bash
# Prova ràpida: 30 jocs, veient el navegador
python source/main.py --contact nom@uoc.edu --max-games 30 --game-lang spanish --show-browser

# Cens complet, en dues comandes
python source/main.py --contact nom@uoc.edu --step discover --game-lang spanish --max-games 50000
python source/main.py --contact nom@uoc.edu --step scrape

# Mostra audiovisual de 50 jocs (Fase 3)
python source/main.py --contact nom@uoc.edu --step media --media-games 50

# Dataset simulat per a Zenodo (cal pandas i numpy)
python source/simulate_dataset.py --seed 2026
```

**Temps orientatius:** la Fase 1 tarda uns 40 minuts per a tota la llista. La Fase 2 depèn de la caché: si cal
descarregar totes les fitxes, són moltes hores (una fitxa cada 2–4 s); si les fitxes ja són a la caché, unes
2 hores. La Fase 3 amb 50 jocs tarda unes 2,5 hores i ocupa uns 3,3 GB.

**Represa:** si la Fase 2 s'atura (per error o amb Ctrl+C), tornar a llançar `--step scrape` continua on s'havia
quedat. No torneu a llançar la Fase 1, perquè sobreescriu el fitxer d'enllaços.

## Bon ús i aspectes legals

- Es llegeix el `robots.txt` abans de començar i es comprova cada URL abans de visitar-la.
- User-Agent propi amb el nom del projecte i un correu de contacte, comprovat també des del navegador.
- Una sola petició alhora, amb pauses aleatòries de 2–4 s per defecte.
- Si Steam respon 429, el programa espera cada cop més; si una fitxa falla tres vegades seguides, s'atura.
- Caché local: cap fitxa es descarrega dues vegades.
- No s'inicia sessió a Steam ni es fan servir proxies.
- No es recullen dades personals d'usuaris (ni noms ni textos de ressenyes).
- El dataset real és només per a ús acadèmic i no es redistribueix. A Zenodo se'n publica una versió simulada
  amb llicència CC BY-NC-SA 4.0.
- Les imatges i els tràilers de la Fase 3 són obres dels desenvolupadors: es guarden només en local i no es
  publiquen enlloc.
