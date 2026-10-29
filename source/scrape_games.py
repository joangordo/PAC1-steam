"""
scrape_games.py
===============
FASE 2 — VISITA DE CADA FITXA I CONSTRUCCIÓ DEL DATASET

Per a cada enllaç descobert a la Fase 1:
  1. descarrega la fitxa del joc amb Requests (o la llegeix de la caché local),
  2. la converteix en una fila amb parse_game_page.py,
  3. escriu la fila al CSV final immediatament.

Mecanismes de bon ús i de robustesa:
  - Pausa aleatòria després de cada descàrrega.
  - Caché: cada fitxa descarregada es guarda a disc i no es torna a demanar mai.
  - Represa: si el procés s'atura, en tornar-lo a executar continua on era.
  - Aturada de seguretat: si 3 fitxes seguides fallen, el programa s'atura
    (pot voler dir que Steam ens està limitant i no té sentit insistir).

"""

import csv
from datetime import datetime, timezone
from pathlib import Path

from parse_game_page import FIELDS, parse_app_page
from web_utils import download, new_session, wait_politely

MAX_FAILURES_IN_A_ROW = 3


def already_done(output: str) -> set:
    """Appids que ja són al CSV final (per poder reprendre l'extracció)."""
    if not Path(output).exists():
        return set()
    with open(output, encoding="utf-8-sig", newline="") as f:
        return {row["appid"] for row in csv.DictReader(f)}


def scrape_games(links_csv, output, cc, lang, min_delay, max_delay, limit,
                 cache_dir, user_agent, robots, logger) -> int:
    with open(links_csv, encoding="utf-8-sig", newline="") as f:
        links = list(csv.DictReader(f))
    done = already_done(output)
    pending = [link for link in links if link["appid"] not in done]
    if limit:
        pending = pending[:limit]
    logger.info("Fase 2: %d enllaços, %d ja fets, %d pendents",
                len(links), len(done), len(pending))

    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    session = new_session(user_agent)
    write_header = not Path(output).exists()
    saved, failures = 0, 0

    with open(output, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        if write_header:
            writer.writeheader()

        for i, link in enumerate(pending, start=1):
            appid = link["appid"]
            cache_file = Path(cache_dir) / f"{appid}.html"
            status, age_gate = 200, False

            if cache_file.exists():
                html = cache_file.read_text(encoding="utf-8")
            else:
                # Seguim l'enllaç que va descobrir la Fase 1
                resp = download(session, link["url"], {"cc": cc, "l": lang}, robots, logger)
                if resp is None or resp.status_code != 200:
                    failures += 1
                    logger.error("[%d/%d] %s: no s'ha pogut descarregar (%d errors seguits)",
                                 i, len(pending), appid, failures)
                    if failures >= MAX_FAILURES_IN_A_ROW:
                        logger.error("Aturada de seguretat: %d errors seguits. Torna-ho a "
                                     "provar més tard; continuarà on s'ha quedat.", failures)
                        break
                    continue
                failures = 0
                status = resp.status_code
                age_gate = "agecheck" in resp.url     # la verificació d'edat no s'ha superat
                html = resp.text
                if not age_gate:
                    cache_file.write_text(html, encoding="utf-8")
                wait_politely(min_delay, max_delay)

            row = parse_app_page(html)
            for error in row.pop("_errors", []):
                logger.warning("%s: un bloc de la fitxa no s'ha pogut llegir (%s)", appid, error)

            # Dades que venen de la Fase 1 i metadades de l'extracció
            row.update(appid=appid, url=row.get("url") or link["url"],
                       search_tag=link.get("search_tag", ""),
                       search_position=link.get("search_position", ""),
                       tag_ids=link.get("tag_ids", ""),
                       content_descriptor_ids=link.get("content_descriptor_ids", ""),
                       capsule_img_url=link.get("capsule_img_url", ""),
                       age_gate=age_gate, http_status=status,
                       scraped_at=datetime.now(timezone.utc).isoformat(timespec="seconds"))

            writer.writerow(row)
            f.flush()   # la fila queda desada al disc ara mateix
            saved += 1
            logger.info("[%d/%d] %s - %s (%s)", i, len(pending), appid,
                        row.get("name"), row.get("reviews_lang_label"))

    logger.info("Fase 2 acabada: %d jocs nous desats a %s", saved, output)
    return saved
