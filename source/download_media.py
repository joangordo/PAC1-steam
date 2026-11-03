"""
download_media.py
=================
FASE 3 — CONTINGUT AUDIOVISUAL D'UNA MOSTRA DE JOCS

Per a una mostra de jocs del dataset (a l'atzar, però sempre la mateixa):
  1. llegeix la fitxa de cada joc de la caché.
  2. hi troba la capçalera, la càpsula, totes les captures i tots els tràilers.
  3. ho descarrega tot a data/media/<appid>/ i ho anota a data/media/media_sample.csv.

Només és una mostra: el dataset sencer té centenars de milers de captures i
desenes de milers de tràilers (massa temps i espai), i són obres dels
desenvolupadors amb drets d'autor.

Els tràilers no són un .mp4 sinó vídeo en streaming (HLS): una llista .m3u8 que
apunta a fragments de 3 s. Enganxant el fragment inicial i la resta en ordre en
surt un fitxer vàlid. El vídeo i l'àudio van per separat: en desem dos fitxers.
"""

import csv
import json
import random
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from web_utils import download, new_session, wait_politely

SAMPLE_SEED = 42          # mateixa llavor = mateixa mostra a cada execució
SEL_CAROUSEL = "[data-featuretarget='gamehighlight-desktopcarousel']"
MEDIA_COLUMNS = ["appid", "name", "kind", "url", "file", "bytes"]


class MediaRobots:
    """Els servidors de multimèdia de Steam (*.steamstatic.com) no tenen robots.txt:
    responen 404, i segons l'estàndard (RFC 9309) això vol dir cap restricció."""

    def allowed(self, url: str) -> bool:
        return True


def save_file(session, url, path, min_delay, max_delay, logger) -> int:
    """Descarrega una URL a `path`. Retorna els bytes desats (0 si falla)."""
    resp = download(session, url, None, MediaRobots(), logger)
    wait_politely(min_delay, max_delay)
    if resp is None or resp.status_code != 200:
        logger.warning("No s'ha pogut descarregar %s", url)
        return 0
    path.write_bytes(resp.content)
    return len(resp.content)


def hls_tracks(master: str, master_url: str) -> list[tuple[str, str]]:
    """De la llista principal .m3u8: la pista de vídeo de més qualitat i la d'àudio."""
    video, best, audio = None, -1, None
    lines = master.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("#EXT-X-MEDIA") and "TYPE=AUDIO" in line:
            audio = re.search(r'URI="([^"]+)"', line).group(1)
        elif line.startswith("#EXT-X-STREAM-INF") and i + 1 < len(lines):
            bandwidth = int(re.search(r"BANDWIDTH=(\d+)", line).group(1))
            if bandwidth > best:
                video, best = lines[i + 1].strip(), bandwidth
    tracks = [("video", video, "mp4"), ("audio", audio, "m4a")]
    return [(kind, urljoin(master_url, uri), ext) for kind, uri, ext in tracks if uri]


def hls_segments(playlist: str, playlist_url: str) -> list[str]:
    """Fragment inicial (#EXT-X-MAP) i, a continuació, els fragments en ordre."""
    parts = re.findall(r'#EXT-X-MAP:URI="([^"]+)"', playlist)
    parts += [l.strip() for l in playlist.splitlines() if l.strip() and not l.startswith("#")]
    return [urljoin(playlist_url, p) for p in parts]


def save_trailer(session, master_url, folder, prefix, min_delay, max_delay, logger) -> list:
    """Descarrega un tràiler HLS. Retorna [(tipus, fitxer, bytes), ...]."""
    resp = download(session, master_url, None, MediaRobots(), logger)
    wait_politely(min_delay, max_delay)
    if resp is None or resp.status_code != 200:
        logger.warning("No s'ha pogut llegir el tràiler %s", master_url)
        return []
    saved = []
    for kind, track_url, ext in hls_tracks(resp.text, master_url):
        resp = download(session, track_url, None, MediaRobots(), logger)
        wait_politely(min_delay, max_delay)
        if resp is None or resp.status_code != 200:
            continue
        path = folder / f"{prefix}_{kind}.{ext}"
        size, complete = 0, True
        with open(path, "wb") as f:
            for segment in hls_segments(resp.text, track_url):
                part = download(session, segment, None, MediaRobots(), logger)
                wait_politely(min_delay, max_delay)
                if part is None or part.status_code != 200:
                    complete = False
                    break
                f.write(part.content)
                size += len(part.content)
        if complete:
            saved.append((f"trailer_{kind}", path, size))
        else:
            path.unlink()      # un vídeo a mitges no serveix: l'esborrem
            logger.warning("Tràiler incomplet, descartat: %s", track_url)
    return saved


def download_media(dataset_csv, cache_dir, media_dir, n_games, min_delay, max_delay,
                   user_agent, logger) -> int:
    with open(dataset_csv, encoding="utf-8-sig", newline="") as f:
        dataset = list(csv.DictReader(f))
    sample = random.Random(SAMPLE_SEED).sample(dataset, min(n_games, len(dataset)))
    logger.info("Fase 3: contingut audiovisual de %d jocs (de %d)", len(sample), len(dataset))

    session = new_session(user_agent)
    rows = []
    for i, game in enumerate(sample, start=1):
        appid = game["appid"]
        cache_file = Path(cache_dir) / f"{appid}.html"
        if not cache_file.exists():
            logger.warning("[%d/%d] %s: no és a la caché, el saltem", i, len(sample), appid)
            continue
        soup = BeautifulSoup(cache_file.read_text(encoding="utf-8"), "html.parser")
        car = soup.select_one(SEL_CAROUSEL)
        try:
            props = json.loads(car["data-props"]) if car else {}
        except (KeyError, ValueError):
            props = {}
        folder = Path(media_dir) / appid
        folder.mkdir(parents=True, exist_ok=True)

        # Imatges: capçalera i càpsula (ja són al CSV) i captures a mida original
        images = [("header", "header", game.get("header_img_url")),
                  ("capsule", "capsule", game.get("capsule_img_url"))]
        images += [("screenshot", f"screenshot_{n:02d}", s.get("full"))
                   for n, s in enumerate(props.get("screenshots", []))]
        for kind, name, url in images:
            if not url:
                continue
            path = folder / f"{name}{Path(urlparse(url).path).suffix or '.jpg'}"
            size = save_file(session, url, path, min_delay, max_delay, logger)
            if size:
                rows.append(dict(appid=appid, name=game.get("name"), kind=kind,
                                 url=url, file=str(path), bytes=size))

        # Tràilers: vídeo en streaming HLS
        for n, trailer in enumerate(props.get("trailers", [])):
            if not trailer.get("hlsManifest"):
                continue
            for kind, path, size in save_trailer(session, trailer["hlsManifest"], folder,
                                                 f"trailer_{n:02d}", min_delay, max_delay, logger):
                rows.append(dict(appid=appid, name=game.get("name"), kind=kind,
                                 url=trailer["hlsManifest"], file=str(path), bytes=size))

        logger.info("[%d/%d] %s - %s: %d fitxers", i, len(sample), appid, game.get("name"),
                    sum(1 for r in rows if r["appid"] == appid))

    Path(media_dir).mkdir(parents=True, exist_ok=True)
    with open(Path(media_dir) / "media_sample.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=MEDIA_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    logger.info("Fase 3 acabada: %d fitxers, %.1f MB a %s", len(rows),
                sum(r["bytes"] for r in rows) / 1e6, media_dir)
    return len(rows)
