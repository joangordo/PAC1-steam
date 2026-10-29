# Steam Indie Games Dataset — PRAC1

Pràctica 1 de *Tipologia i cicle de vida de les dades* (Màster en Ciència de Dades, UOC).

**Integrants:** Joan Gordó Guardia · Ferran Rincon Puente

**DOI del dataset a Zenodo:** https://

## Què fa aquest projecte

Un scraper en Python que construeix un dataset de jocs Indie de la botiga de Steam
(https://store.steampowered.com/) en dues fases:

1. **Descobriment (Selenium).** Parteix d'una sola URL de cerca, fa scroll per carregar
   els resultats (la pàgina els carrega a mesura que baixes) i extreu l'enllaç a la fitxa
   de cada joc. Opcionalment, descobreix a la mateixa pàgina subcategories d'Indie
   (Roguelike, Puzle…) i les recorre una per una.
2. **Extracció (Requests + BeautifulSoup).** Visita cada enllaç descobert i n'extreu
   145 variables: preu, valoracions, gèneres, etiquetes, característiques, idiomes,
   requisits tècnics, multimèdia…

## Fitxers del repositori

| Fitxer | Contingut |
| --- | --- |
| `source/main.py` | Punt d'entrada: llegeix els paràmetres i executa les fases |
| `source/discover_games.py` | Fase 1: navegació per la cerca i descobriment d'enllaços |
| `source/scrape_games.py` | Fase 2: visita de cada fitxa, caché, represa i escriptura del CSV |
| `source/parse_game_page.py` | Converteix l'HTML d'una fitxa en una fila del dataset |
| `source/web_utils.py` | Bon ús: User-Agent, robots.txt, pauses, reintents i log |
| `dataset/steam_indie_games.csv` | Dataset resultant |
| `docs/variables.md` | Diccionari de les 145 variables |
| `requirements.txt` | Llibreries necessàries |

Les carpetes `data/` (fitxers intermedis i caché de fitxes) i `logs/` es creen en
executar el codi i no es pugen al repositori.

## Com utilitzar-lo

Requisits: Python 3.10 o superior i Google Chrome instal·lat.

```bash
pip install -r requirements.txt
python source/main.py --contact el_teu_correu@uoc.edu [opcions]
```

| Paràmetre | Per defecte | Què fa |
| --- | --- | --- |
| `--contact` | (obligatori) | Correu que s'inclou al User-Agent |
| `--step` | `all` | `discover` (Fase 1), `scrape` (Fase 2) o `all` (totes dues) |
| `--max-games` | 1000 | Nombre màxim de jocs a descobrir |
| `--subtags` | 0 | Nombre de subcategories d'Indie a recórrer (0 = només Indie) |
| `--limit` | — | Fase 2: processa com a màxim N fitxes (per fer proves) |
| `--min-delay` / `--max-delay` | 2 / 4 | Pausa aleatòria entre peticions, en segons |
| `--show-browser` | no | Mostra la finestra de Chrome a la Fase 1 |
| `--cc` / `--lang` | `es` / `spanish` | País dels preus i idioma de la botiga |

Exemples:

```bash
# Prova ràpida: 30 jocs, veient el navegador
python source/main.py --contact nom@uoc.edu --max-games 30 --show-browser

# Execució completa: 1.000 jocs repartits en 5 subcategories d'Indie
python source/main.py --contact nom@uoc.edu --max-games 1000 --subtags 5

# Només la Fase 2 (sobre els enllaços ja descoberts)
python source/main.py --contact nom@uoc.edu --step scrape
```

Si l'execució s'atura (per error o amb Ctrl+C), en tornar-la a llançar continua on s'havia quedat.

## Bon ús i aspectes legals

- Es llegeix i es respecta el `robots.txt` abans de cada petició.
- User-Agent propi amb el nom del projecte i un correu de contacte.
- Una sola petició alhora, amb pauses aleatòries de 2–4 s.
- Si el servidor falla 3 cops seguits, el programa s'atura.
- No s'inicia sessió a Steam ni es fan servir proxies.
- No es desen dades personals d'usuaris.
- El dataset real és només per a ús acadèmic. A Zenodo se'n publica una versió simulada.
