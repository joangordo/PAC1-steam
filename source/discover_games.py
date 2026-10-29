"""
discover_games.py
=================
FASE 1 — DESCOBRIMENT D'ENLLAÇOS I NAVEGACIÓ AUTÒNOMA

El codi parteix d'una sola URL (la cerca de jocs Indie) i:

  1. (Opcional) Llegeix a l'HTML de la cerca les subcategories disponibles
     (etiquetes com "Roguelike" o "Puzle") i les recorre una per una.
  2. A cada cerca fa scroll amb Selenium: Steam carrega els resultats a poc a
     poc (scroll infinit), així que cal moure la pàgina perquè n'apareguin més.
  3. Llegeix l'HTML resultant i n'extreu l'enllaç a la fitxa de cada joc.

No fem servir el sitemap: és el nostre codi qui troba els enllaços a l'HTML.
El resultat és un CSV amb els enllaços, que la Fase 2 visitarà un per un.
"""

import csv
import math
import re
from pathlib import Path
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from web_utils import BASE_URL, wait_politely

INDIE_TAG = 492          # id de l'etiqueta "Indie" a Steam
ONLY_GAMES = 998         # filtre "category1=998": només jocs (sense DLC ni bandes sonores)

# Selectors CSS de la pàgina de cerca (comprovats amb les eines del navegador, F12)
SEL_RESULT_ROW = "#search_resultsRows a.search_result_row"
SEL_TITLE = "span.title"
SEL_CAPSULE = "div.search_capsule img"
SEL_TAG_FILTER = "div.tab_filter_control_row[data-param='tags']"
COOKIE_BUTTONS = ["rejectAllButton", "acceptAllButton"]   # bàner de cookies (UE)

LINK_COLUMNS = ["search_tag", "search_position", "appid", "url", "name",
                "tag_ids", "content_descriptor_ids", "capsule_img_url"]


# --------------------------------------------------------------------------
# Navegador
# --------------------------------------------------------------------------
def open_browser(user_agent: str, headless: bool) -> webdriver.Chrome:
    """Obre un Chrome net (sense cap sessió de Steam) amb el nostre User-Agent."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    # Sense això, Chrome en mode invisible s'identificaria com a "HeadlessChrome".
    options.add_argument(f"--user-agent={user_agent}")
    options.add_argument("--window-size=1366,900")
    driver = webdriver.Chrome(options=options)   # Selenium descarrega el driver sol
    driver.set_page_load_timeout(30)
    return driver


def check_user_agent(driver, expected: str, logger) -> None:
    """L'enunciat demana comprovar quin User-Agent fa servir el codi."""
    real = driver.execute_script("return navigator.userAgent")
    logger.info("User-Agent real del navegador: %s", real)
    if real != expected:
        logger.warning("El User-Agent del navegador no és l'esperat")


def close_cookie_banner(driver, logger) -> None:
    """Si apareix el bàner de cookies, el tanquem (rebutjant-les si es pot)."""
    for button_id in COOKIE_BUTTONS:
        try:
            button = driver.find_element(By.ID, button_id)
            if button.is_displayed():
                button.click()
                logger.info("Bàner de cookies tancat")
                return
        except NoSuchElementException:
            continue


def search_url(tag_ids: list[int], cc: str, lang: str) -> str:
    params = {"tags": ",".join(map(str, tag_ids)), "category1": ONLY_GAMES,
              "cc": cc, "l": lang}
    return f"{BASE_URL}/search/?{urlencode(params)}"


def load_search(driver, url, robots, logger) -> bool:
    """Obre una pàgina de cerca i espera que hi apareguin resultats."""
    if not robots.allowed(url):
        return False
    driver.get(url)
    close_cookie_banner(driver, logger)
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SEL_RESULT_ROW)))
        return True
    except TimeoutException:
        Path("logs").mkdir(exist_ok=True)
        Path("logs/search_error.html").write_text(driver.page_source, encoding="utf-8")
        logger.error("La cerca no mostra resultats. HTML desat a logs/search_error.html")
        return False


def scroll_until(driver, target, min_delay, max_delay, logger, patience=3) -> int:
    """Fa scroll fins tenir `target` resultats o fins que en deixin d'arribar.

    Cada scroll fa que Steam demani un nou bloc de resultats. Després de cada
    scroll esperem uns segons. Si 3 scrolls seguits no porten res de nou,
    considerem que la llista s'ha acabat.
    """
    count_js = "return document.querySelectorAll(arguments[0]).length;"
    count = driver.execute_script(count_js, SEL_RESULT_ROW)
    failed = 0
    while count < target and failed < patience:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        wait_politely(min_delay, max_delay)
        new_count = driver.execute_script(count_js, SEL_RESULT_ROW)
        failed = 0 if new_count > count else failed + 1
        logger.info("Scroll: %d resultats carregats", new_count)
        count = new_count
    return count


# --------------------------------------------------------------------------
# Lectura de l'HTML (BeautifulSoup)
# --------------------------------------------------------------------------
def read_subtags(html: str, how_many: int) -> list[tuple[int, str]]:
    """Llegeix el filtre d'etiquetes de la cerca i en retorna les primeres.

    Així les subcategories no estan escrites al codi: les descobreix a la web.
    """
    soup = BeautifulSoup(html, "html.parser")
    found = []
    for row in soup.select(SEL_TAG_FILTER):
        tag_id = row.get("data-value", "")
        name = row.get("data-loc") or row.get_text(" ", strip=True)
        if tag_id.isdigit() and int(tag_id) != INDIE_TAG:
            pair = (int(tag_id), name.strip())
            if pair not in found:
                found.append(pair)
    return found[:how_many]


def read_result_rows(html: str, search_tag: str) -> list[dict]:
    """Extreu de cada fila de resultats l'enllaç a la fitxa i dades bàsiques."""
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for position, row in enumerate(soup.select(SEL_RESULT_ROW), start=1):
        appid = (row.get("data-ds-appid") or "").strip()
        if not appid or "," in appid:      # els lots porten diversos appids: fora
            continue
        title = row.select_one(SEL_TITLE)
        capsule = row.select_one(SEL_CAPSULE)
        rows.append({
            "search_tag": search_tag,
            "search_position": position,
            "appid": appid,
            "url": (row.get("href") or "").split("?")[0],   # enllaç descobert
            "name": title.get_text(strip=True) if title else "",
            "tag_ids": "|".join(re.findall(r"\d+", row.get("data-ds-tagids") or "")),
            "content_descriptor_ids": "|".join(re.findall(r"\d+", row.get("data-ds-descids") or "")),
            "capsule_img_url": capsule.get("src", "") if capsule else "",
        })
    return rows


# --------------------------------------------------------------------------
# Fase 1 completa
# --------------------------------------------------------------------------
def discover_games(max_games, subtags, cc, lang, min_delay, max_delay,
                   headless, output, user_agent, robots, logger) -> int:
    driver = open_browser(user_agent, headless)
    games = {}   # appid -> fila (així evitem duplicats entre subcategories)
    try:
        # 1. Cerca principal: jocs Indie
        base_url = search_url([INDIE_TAG], cc, lang)
        logger.info("Cerca inicial: %s", base_url)
        if not load_search(driver, base_url, robots, logger):
            return 0
        check_user_agent(driver, user_agent, logger)

        # 2. Quines cerques farem? Només Indie, o Indie + cada subcategoria
        searches = [("Indie", [INDIE_TAG], max_games)]
        if subtags > 0:
            found = read_subtags(driver.page_source, subtags)
            if found:
                per_tag = math.ceil(max_games / len(found))
                searches = [(name, [INDIE_TAG, tag_id], per_tag) for tag_id, name in found]
                logger.info("Subcategories descobertes: %s", ", ".join(n for _, n in found))
            else:
                logger.warning("No s'han trobat subcategories: es fa només la cerca Indie")

        # 3. Recorrem cada cerca: scroll + extracció d'enllaços
        for name, tag_ids, target in searches:
            if len(games) >= max_games:
                break
            if tag_ids != [INDIE_TAG]:      # la cerca Indie ja està oberta
                wait_politely(min_delay, max_delay)
                if not load_search(driver, search_url(tag_ids, cc, lang), robots, logger):
                    continue
            scroll_until(driver, target, min_delay, max_delay, logger)
            new = 0
            for row in read_result_rows(driver.page_source, name):
                if row["appid"] not in games and new < target and len(games) < max_games:
                    games[row["appid"]] = row
                    new += 1
            logger.info("Cerca '%s': %d jocs nous (total %d)", name, new, len(games))
    finally:
        driver.quit()   # tanquem sempre el navegador

    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=LINK_COLUMNS)
        writer.writeheader()
        writer.writerows(games.values())
    logger.info("Fase 1 acabada: %d enllaços desats a %s", len(games), output)
    return len(games)
