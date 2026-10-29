"""
web_utils.py
============
Eines comunes per fer un BON ÚS del web scraping (requisit de l'enunciat):

- User-Agent propi que identifica el projecte i dona un contacte.
- Lectura i respecte del robots.txt abans de fer cap petició.
- Pauses aleatòries entre peticions per no saturar el servidor.
- Descàrregues amb reintents i espera creixent si el servidor ens limita.
- Registre (log) de tot el que passa, a pantalla i a fitxer.
"""

import logging
import random
import time
from pathlib import Path
from urllib.robotparser import RobotFileParser

import requests

BASE_URL = "https://store.steampowered.com"

# Imitem un Chrome d'escriptori (perquè Steam ens serveixi la web normal) i hi
# afegim el nom del projecte i un correu, perquè el propietari sàpiga qui som.
CHROME_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)

# Cookies que superen la pàgina de verificació d'edat dels jocs per a adults.
AGE_COOKIES = {
    "birthtime": "470703601",          # data de naixement fictícia (1984)
    "lastagecheckage": "1-January-1985",
    "wants_mature_content": "1",
    "mature_content": "1",
}


def build_user_agent(contact: str) -> str:
    """User-Agent complet que fan servir Selenium i Requests."""
    return f"{CHROME_UA} UOC-TCVD-PRAC1/1.0 (academic project; contact: {contact})"


def setup_logging(log_file: str = "logs/scraper.log") -> logging.Logger:
    """Mostra els missatges per pantalla i els desa també en un fitxer."""
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("steam_scraper")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        for handler in (logging.StreamHandler(),
                        logging.FileHandler(log_file, encoding="utf-8")):
            handler.setFormatter(fmt)
            logger.addHandler(handler)
    return logger


def wait_politely(min_s: float, max_s: float) -> float:
    """Espera un temps aleatori. Evita un ritme mecànic i limita la càrrega."""
    seconds = random.uniform(min_s, max_s)
    time.sleep(seconds)
    return seconds


class RobotsRules:
    """Descarrega el robots.txt i respon si una URL es pot visitar."""

    def __init__(self, user_agent: str, logger: logging.Logger):
        self.user_agent = user_agent
        self.logger = logger
        self.parser = RobotFileParser()
        self.text = None
        url = f"{BASE_URL}/robots.txt"
        try:
            resp = requests.get(url, headers={"User-Agent": user_agent}, timeout=15)
            resp.raise_for_status()
            self.text = resp.text
            self.parser.parse(self.text.splitlines())
            logger.info("robots.txt llegit (%d línies)", len(self.text.splitlines()))
        except requests.RequestException as exc:
            # Si no el podem llegir, som prudents: no visitem res.
            logger.error("No s'ha pogut llegir el robots.txt (%s). No es rastrejarà res.", exc)
            self.parser.parse(["User-agent: *", "Disallow: /"])

    def allowed(self, url: str) -> bool:
        ok = self.parser.can_fetch(self.user_agent, url)
        if not ok:
            self.logger.warning("El robots.txt NO permet visitar: %s", url)
        return ok

    def crawl_delay(self):
        return self.parser.crawl_delay(self.user_agent)

    def save_copy(self, path: str = "logs/robots.txt") -> None:
        """Guarda una còpia com a evidència per a la memòria."""
        if self.text:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(self.text, encoding="utf-8")


def new_session(user_agent: str) -> requests.Session:
    """Sessió HTTP sense cap compte de Steam: només User-Agent i cookies d'edat."""
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent, "Accept-Language": "es-ES,es;q=0.9"})
    for name, value in AGE_COOKIES.items():
        session.cookies.set(name, value, domain="store.steampowered.com")
    return session


def download(session, url, params, robots, logger, retries=3):
    """Descarrega una URL respectant el robots.txt.

    Si el servidor respon 429 (massa peticions) o un error 5xx, esperem
    30 s, després 60 s, després 120 s. Retorna la resposta o None.
    """
    if not robots.allowed(url):
        return None
    wait = 30
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, params=params, timeout=20)
            if resp.status_code == 200:
                return resp
            if resp.status_code not in (429, 500, 502, 503, 504):
                logger.warning("HTTP %d a %s (no es reintenta)", resp.status_code, url)
                return resp
            logger.warning("HTTP %d a %s: esperem %d s (intent %d/%d)",
                           resp.status_code, url, wait, attempt, retries)
        except requests.RequestException as exc:
            logger.warning("Error de xarxa a %s (%s), intent %d/%d", url, exc, attempt, retries)
        time.sleep(wait)
        wait *= 2
    return None
