"""
main.py
=======
Punt d'entrada del projecte. Executa les dues fases del scraper:

  Fase 1 (discover): troba els enllaços a les fitxes de jocs Indie.
  Fase 2 (scrape):   visita cada fitxa i genera el dataset.

Exemples (des de la carpeta arrel del projecte):
  python source/main.py --contact nom@uoc.edu --max-games 30 --show-browser
  python source/main.py --contact nom@uoc.edu --max-games 1000 --subtags 5
  python source/main.py --contact nom@uoc.edu --step scrape
"""

import argparse
import sys
import time

from web_utils import RobotsRules, build_user_agent, setup_logging

LINKS_CSV = "data/game_links.csv"          # resultat de la Fase 1 (fitxer intermedi)
CACHE_DIR = "data/html_cache"              # fitxes descarregades
DATASET_CSV = "dataset/steam_indie_games.csv"


def read_arguments():
    p = argparse.ArgumentParser(description="Scraper de jocs Indie de Steam (PRAC1 TCVD, UOC)")
    p.add_argument("--contact", required=True,
                   help="correu de contacte que s'inclou al User-Agent")
    p.add_argument("--step", choices=["discover", "scrape", "all"], default="all",
                   help="fase a executar (per defecte: all = totes dues)")
    p.add_argument("--max-games", type=int, default=1000,
                   help="nombre màxim de jocs a descobrir (per defecte: 1000)")
    p.add_argument("--subtags", type=int, default=0,
                   help="nombre de subcategories d'Indie a recórrer (0 = només Indie)")
    p.add_argument("--limit", type=int, default=None,
                   help="Fase 2: processa com a màxim N fitxes (per fer proves)")
    p.add_argument("--min-delay", type=float, default=2.0,
                   help="pausa mínima entre peticions, en segons (per defecte: 2)")
    p.add_argument("--max-delay", type=float, default=4.0,
                   help="pausa màxima entre peticions, en segons (per defecte: 4)")
    p.add_argument("--show-browser", action="store_true",
                   help="mostra la finestra de Chrome a la Fase 1 (útil per comprovar-ho)")
    p.add_argument("--cc", default="es", help="país dels preus (per defecte: es)")
    p.add_argument("--lang", default="spanish", help="idioma de la botiga (per defecte: spanish)")
    return p.parse_args()


def main() -> int:
    args = read_arguments()
    logger = setup_logging()
    user_agent = build_user_agent(args.contact)
    logger.info("User-Agent configurat: %s", user_agent)

    # Bon ús: abans de res, llegim el robots.txt i en guardem una còpia
    robots = RobotsRules(user_agent, logger)
    robots.save_copy()
    delay = robots.crawl_delay()
    if delay and delay > args.min_delay:      # si el lloc demana més pausa, la respectem
        args.min_delay, args.max_delay = float(delay), float(delay) + 2

    start = time.time()
    if args.step in ("discover", "all"):
        from discover_games import discover_games     # Selenium només si cal
        found = discover_games(args.max_games, args.subtags, args.cc, args.lang,
                               args.min_delay, args.max_delay, not args.show_browser,
                               LINKS_CSV, user_agent, robots, logger)
        if found == 0:
            logger.error("La Fase 1 no ha trobat cap joc. Revisa logs/scraper.log")
            return 1

    if args.step in ("scrape", "all"):
        from scrape_games import scrape_games
        scrape_games(LINKS_CSV, DATASET_CSV, args.cc, args.lang, args.min_delay,
                     args.max_delay, args.limit, CACHE_DIR,
                     user_agent, robots, logger)

    logger.info("Temps total: %.1f minuts", (time.time() - start) / 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
