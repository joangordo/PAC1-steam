"""
parse_game_page.py
==================
Converteix l'HTML de la fitxa d'un joc en una fila del dataset (145 columnes).

La fitxa es llegeix per BLOCS (identificació, preu, ressenyes, contingut,
característiques, idiomes, requisits i multimèdia). Cada bloc té la seva
funció: si un bloc no existeix en un joc concret (p. ex. un joc gratuït no té
descompte), els seus camps queden buits i la resta de la fila es desa igual.

Criteri general: els valors es guarden tal com surten a la web (preus amb €,
dates en castellà...). La neteja és l'objectiu de la Pràctica 2.

Selectors comprovats sobre l'HTML real de les fitxes de Rust i VTube Studio
(botiga en castellà, octubre de 2026).
"""

import json
import re

from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Característiques: Steam les identifica amb un id numèric (category2=N a l'enllaç).
# Fem servir l'id i no el text perquè no depèn de l'idioma de la botiga.
# ---------------------------------------------------------------------------
FEATURE_IDS = {
    1: "feat_multiplayer", 2: "feat_single_player", 9: "feat_coop",
    49: "feat_pvp", 36: "feat_online_pvp", 47: "feat_lan_pvp",
    37: "feat_shared_screen_pvp", 38: "feat_online_coop", 48: "feat_lan_coop",
    39: "feat_shared_screen_coop", 24: "feat_shared_screen",
    27: "feat_cross_platform", 20: "feat_mmo", 22: "feat_achievements",
    23: "feat_cloud", 28: "feat_full_controller", 18: "feat_partial_controller",
    29: "feat_trading_cards", 30: "feat_workshop", 35: "feat_in_app_purchases",
    15: "feat_stats", 25: "feat_leaderboards", 17: "feat_level_editor",
    41: "feat_remote_play_phone", 42: "feat_remote_play_tablet",
    43: "feat_remote_play_tv", 44: "feat_remote_play_together",
    53: "feat_vr_supported", 54: "feat_vr_only", 62: "feat_family_sharing",
    8: "feat_vac", 13: "feat_captions", 14: "feat_commentary",
}

# Idiomes concrets que convertim en booleanes (nom tal com surt a la taula).
LANG_FLAGS = {
    "es": "español de españa", "es_latam": "español de hispanoamérica",
    "ca": "catalán", "en": "inglés", "zh_cn": "chino simplificado",
    "ja": "japonés", "ko": "coreano",
}

# Etiquetes dels requisits -> sufix de columna.
SYSREQ_LABELS = {
    "so": "os", "procesador": "cpu", "memoria": "ram", "gráficos": "gpu",
    "directx": "directx", "almacenamiento": "storage", "disco duro": "storage",
    "red": "network", "notas adicionales": "notes",
}
SYSREQ_KEYS = ["os", "cpu", "ram", "gpu", "directx", "storage", "network", "notes"]

# Ordre fix de les columnes del CSV final.
FIELDS = (
    ["appid", "name", "url", "app_type", "search_tag", "search_position", "release_date",
     "coming_soon", "early_access", "developers", "publishers", "n_developers",
     "n_publishers", "self_published", "franchise", "short_description",
     "about_n_words", "has_website",
     # Preu i negoci
     "price_original", "price_final", "discount_pct", "on_sale", "sale_end_text",
     "is_free", "n_purchase_options", "n_bundles", "n_dlc", "n_points_shop_items",
     "third_party_eula", "third_party_account", "kernel_anticheat", "anticheat_name",
     # Recepció
     "reviews_recent_label", "reviews_recent_pct", "reviews_recent_n",
     "reviews_lang_scope", "reviews_lang_label", "reviews_lang_pct", "reviews_lang_n",
     "reviews_lang_filtered",
     "metacritic_score", "n_press_quotes", "n_curators", "n_awards",
     # Contingut
     "genres", "n_genres", "tags", "n_tags", "tag_1", "tag_2", "tag_3", "tag_ids",
     "mature_content", "mature_content_text", "content_descriptor_ids", "age_gate",
     # Característiques
     "features", "feature_ids", "n_features"]
    + sorted(set(FEATURE_IDS.values()))
    + ["platform_win", "platform_mac", "platform_linux",
       # Idiomes
       "languages", "n_languages", "n_lang_interface", "n_lang_audio", "n_lang_subtitles"]
    + [f"{code}_{kind}" for code in LANG_FLAGS for kind in ("interface", "audio", "subtitles")]
    + [f"req_{level}_{key}" for level in ("min", "rec") for key in SYSREQ_KEYS]
    + ["requires_64bit", "has_recommended_reqs",
       # Multimèdia i metadades
       "n_screenshots", "n_trailers", "header_img_url", "capsule_img_url",
       "http_status", "scraped_at"]
)


# ---------------------------------------------------------------------------
# Utilitats de text
# ---------------------------------------------------------------------------
def to_int(text) -> int | None:
    """'44,384' / '44.384' / '4 306' -> 44384. None si no hi ha xifres."""
    digits = re.sub(r"[^\d]", "", str(text or ""))
    return int(digits) if digits else None


def parse_pct_n(text: str) -> tuple[int | None, int | None]:
    """'El 91 % de las 44,384 reseñas...' -> (91, 44384)."""
    text = text or ""
    m_pct = re.search(r"(\d+)\s*%", text)
    if not m_pct:
        m_n = re.search(r"\d[\d.,]*", text)
        return None, (to_int(m_n.group(0)) if m_n else None)
    m_n = re.search(r"\d[\d.,]*", text[m_pct.end():])
    return int(m_pct.group(1)), (to_int(m_n.group(0)) if m_n else None)


def clean(text: str) -> str:
    """Normalitza espais (inclosos els espais durs \\xa0)."""
    return re.sub(r"\s+", " ", (text or "").replace("\xa0", " ")).strip()


def join(values) -> str:
    return "|".join(v for v in values if v)


# ---------------------------------------------------------------------------
# Parsers per blocs de la fitxa
# ---------------------------------------------------------------------------
def parse_identity(soup, row: dict) -> None:
    name = soup.select_one("#appHubAppName") or soup.select_one(".apphub_AppName")
    row["name"] = clean(name.get_text()) if name else ""

    canonical = soup.select_one("link[rel=canonical]")
    if canonical:
        row["url"] = canonical.get("href", row.get("url", ""))

    # "Acerca de este juego" / "software" / "vídeo"... -> tipus d'aplicació
    about = soup.select_one("#game_area_description")
    about_text = clean(about.get_text(" ")) if about else ""
    m = re.match(r"Acerca de este (\w+)", about_text)
    row["app_type"] = m.group(1) if m else ""
    row["about_n_words"] = len(about_text.split()) if about_text else 0

    desc = soup.select_one(".game_description_snippet")
    row["short_description"] = clean(desc.get_text()) if desc else ""

    date = soup.select_one(".release_date .date")
    row["release_date"] = clean(date.get_text()) if date else ""
    row["coming_soon"] = bool(soup.select_one(".game_area_comingsoon")) or \
        any(w in row["release_date"].lower() for w in ("próximamente", "por determinar"))

    # Desenvolupadors, editors i franquícia (bloc "genresAndManufacturer")
    devs, pubs, franchise = [], [], ""
    for dev_row in soup.select("#genresAndManufacturer .dev_row"):
        label = clean(dev_row.b.get_text()).lower() if dev_row.b else ""
        names = [clean(a.get_text()) for a in dev_row.select("a")]
        if label.startswith("desarrollador"):
            devs += names
        elif label.startswith("editor"):
            pubs += names
        elif label.startswith("franquicia"):
            franchise = join(names)
    row.update(developers=join(devs), publishers=join(pubs), franchise=franchise,
               n_developers=len(devs), n_publishers=len(pubs),
               self_published=bool(devs) and set(devs) == set(pubs))

    row["has_website"] = any("sitio web" in a.get_text().lower()
                             for a in soup.select("a.linkbar"))


def parse_purchase(soup, row: dict) -> None:
    # Opcions de compra que NO són lots (els lots tenen la classe dynamic_bundle_description)
    options = [g for g in soup.select(".game_area_purchase_game")
               if not g.find_parent(class_="dynamic_bundle_description")]
    row["n_purchase_options"] = len(options)
    row["n_bundles"] = len(soup.select(".game_area_purchase_game_wrapper.dynamic_bundle_description"))

    main = options[0] if options else None
    wrapper = main.find_parent(class_="game_area_purchase_game_wrapper") if main else None
    scope = wrapper or main

    def txt(sel):
        el = main.select_one(sel) if main else None
        return clean(el.get_text()) if el else ""

    row["discount_pct"] = txt(".discount_pct")
    row["price_original"] = txt(".discount_original_price") or txt(".game_purchase_price")
    row["price_final"] = txt(".discount_final_price") or txt(".game_purchase_price")
    row["on_sale"] = bool(row["discount_pct"])
    countdown = scope.select_one(".game_purchase_discount_countdown") if scope else None
    row["sale_end_text"] = clean(countdown.get_text()) if countdown else ""
    price_low = row["price_final"].lower()
    row["is_free"] = any(w in price_low for w in ("gratuito", "free", "jugar"))

    # DLC: "Ver todos (N)" dona el total; si no hi és, comptem les files visibles
    dlc = soup.select_one("#gameAreaDLCSection")
    m = re.search(r"\((\d+)\)", dlc.get_text()) if dlc else None
    row["n_dlc"] = int(m.group(1)) if m else len(soup.select(".game_area_dlc_row"))

    # Botiga de punts (comparteix id de bloc amb els assoliments)
    block = soup.select_one("#achievement_block")
    row["n_points_shop_items"] = 0
    if block and "puntos" in block.get_text().lower():
        m = re.search(r"\((\d+)\)", block.get_text())
        row["n_points_shop_items"] = int(m.group(1)) if m else \
            len(block.select(".communitylink_points_shop_item"))

    # Avisos legals / DRM / anti-trampes
    notices = [clean(n.get_text(" ")) for n in soup.select(".DRM_notice")]
    joined = " ".join(notices).lower()
    row["third_party_eula"] = "aluf" in joined or "eula" in joined
    row["third_party_account"] = "cuenta de terceros" in joined
    row["kernel_anticheat"] = "kernel" in joined
    ac = soup.select_one(".anticheat_name")
    if ac:
        for span in ac.select("span"):
            span.extract()  # treiem el comentari "- Debe eliminarse a mano..."
    row["anticheat_name"] = clean(ac.get_text()) if ac else ""

    row["early_access"] = bool(soup.select_one(".early_access_header, #earlyAccessHeader")) \
        or "Acceso anticipado" in row.get("genres", "")


def parse_reviews(soup, row: dict) -> None:
    """Bloc #userReviews: fila 'Reseñas recientes' i fila de l'idioma (o 'Todas')."""
    row.update(reviews_recent_label="", reviews_recent_pct=None, reviews_recent_n=None,
               reviews_lang_scope="", reviews_lang_label="", reviews_lang_pct=None,
               reviews_lang_n=None, reviews_lang_filtered=False)
    for r in soup.select("#userReviews a.user_reviews_summary_row"):
        subtitle = clean(r.select_one(".subtitle").get_text()) if r.select_one(".subtitle") else ""
        label_el = r.select_one(".game_review_summary")
        label = clean(label_el.get_text()) if label_el else ""
        pct, n = parse_pct_n(r.get("data-tooltip-html", ""))
        if re.search(r"\d", label):          # p. ex. "3 reseñas de usuarios": no hi ha etiqueta
            n, label = n or to_int(label), ""
        if "recientes" in subtitle.lower():
            row.update(reviews_recent_label=label, reviews_recent_pct=pct, reviews_recent_n=n)
        else:
            row.update(reviews_lang_scope=subtitle.rstrip(":"), reviews_lang_label=label,
                       reviews_lang_pct=pct, reviews_lang_n=n,
                       reviews_lang_filtered=subtitle.lower().startswith("reseñas en"))

    meta = soup.select_one("#game_area_metascore .score")
    row["metacritic_score"] = to_int(meta.get_text()) if meta else None
    row["n_press_quotes"] = len(soup.select("#game_area_reviews a"))

    cur = soup.select_one(".steam_curators_block")
    m = re.search(r"([\d.,]+)\s+mentores", cur.get_text()) if cur else None
    row["n_curators"] = to_int(m.group(1)) if m else 0

    awards = soup.select("#AwardsDefault strong")
    row["n_awards"] = sum(1 for s in awards if clean(s.get_text()))


def parse_content(soup, row: dict) -> None:
    genres = [clean(a.get_text()) for a in soup.select("#genresAndManufacturer a[href*='/genre/']")]
    tags = [clean(a.get_text()) for a in soup.select("a.app_tag")]  # ordenats per vots
    row.update(genres=join(genres), n_genres=len(genres), tags=join(tags), n_tags=len(tags),
               tag_1=tags[0] if len(tags) > 0 else "", tag_2=tags[1] if len(tags) > 1 else "",
               tag_3=tags[2] if len(tags) > 2 else "")

    cd = soup.select_one("#game_area_content_descriptors")
    row["mature_content"] = cd is not None
    if cd:
        title = cd.select_one("h2")
        if title:
            title.extract()
    row["mature_content_text"] = clean(cd.get_text(" ")) if cd else ""


def parse_features(soup, row: dict) -> None:
    names, ids = [], []
    for a in soup.select("a.game_area_details_specs_ctn"):
        label = a.select_one(".label")
        m = re.search(r"category2=(\d+)", a.get("href", ""))
        if label:
            names.append(clean(label.get_text()))
        if m:
            ids.append(int(m.group(1)))
    row.update(features=join(names), feature_ids=join(str(i) for i in ids), n_features=len(names))
    for fid, col in FEATURE_IDS.items():
        row[col] = fid in ids


def parse_languages(soup, row: dict) -> None:
    langs = []
    counts = {"interface": 0, "audio": 0, "subtitles": 0}
    flags = {f"{c}_{k}": False for c in LANG_FLAGS for k in counts}
    for tr in soup.select("#languageTable tr"):
        name_el = tr.select_one("td.ellipsis")
        checks = tr.select("td.checkcol")
        if not name_el or not checks:      # capçalera o idioma "no disponible"
            continue
        name = clean(name_el.get_text())
        marks = [bool(clean(td.get_text())) for td in checks][:3]
        marks += [False] * (3 - len(marks))
        if not any(marks):
            continue
        langs.append(name)
        for kind, ok in zip(counts, marks):
            counts[kind] += ok
            for code, lang_name in LANG_FLAGS.items():
                if name.lower() == lang_name:
                    flags[f"{code}_{kind}"] = ok
    row.update(languages=join(langs), n_languages=len(langs),
               n_lang_interface=counts["interface"], n_lang_audio=counts["audio"],
               n_lang_subtitles=counts["subtitles"], **flags)


def _sysreq_column(col) -> dict:
    """Extreu {os, cpu, ram...} d'una columna de requisits (mínim o recomanat)."""
    out = {}
    for li in col.select("li"):
        strong = li.select_one("strong")
        if not strong:
            continue
        label = clean(strong.get_text()).rstrip(":* ").lower()
        key = SYSREQ_LABELS.get(label)
        if key:
            out[key] = clean(li.get_text().replace(strong.get_text(), "", 1))
    return out


def parse_sysreq(soup, row: dict) -> None:
    sections = soup.select(".sysreq_contents .game_area_sys_req")
    oses = {s.get("data-os") for s in sections}
    row.update(platform_win="win" in oses, platform_mac="mac" in oses,
               platform_linux="linux" in oses)

    # Ens quedem amb els requisits de Windows (o la primera secció si no n'hi ha)
    win = next((s for s in sections if s.get("data-os") == "win"), sections[0] if sections else None)
    left = win.select_one(".game_area_sys_req_leftCol, .game_area_sys_req_full") if win else None
    right = win.select_one(".game_area_sys_req_rightCol") if win else None
    req_min = _sysreq_column(left) if left else {}
    req_rec = _sysreq_column(right) if right else {}
    for key in SYSREQ_KEYS:
        row[f"req_min_{key}"] = req_min.get(key, "")
        row[f"req_rec_{key}"] = req_rec.get(key, "")
    row["has_recommended_reqs"] = bool(req_rec)
    row["requires_64bit"] = bool(win) and "64 bits" in win.get_text()


def parse_media(soup, row: dict) -> None:
    """Els tràilers i captures són dins d'un JSON a l'atribut data-props del carrusel."""
    car = soup.select_one("[data-featuretarget='gamehighlight-desktopcarousel']")
    try:
        props = json.loads(car["data-props"]) if car else {}
    except (KeyError, ValueError):
        props = {}
    row["n_trailers"] = len(props.get("trailers", []))
    row["n_screenshots"] = len(props.get("screenshots", []))
    header = soup.select_one("img.game_header_image_full")
    row["header_img_url"] = header.get("src", "") if header else ""


def parse_app_page(html: str) -> dict:
    """Aplica tots els parsers de blocs i retorna un diccionari amb la fila."""
    soup = BeautifulSoup(html, "html.parser")
    row = {}
    for block_parser in (parse_identity, parse_content, parse_purchase, parse_reviews,
                         parse_features, parse_languages, parse_sysreq, parse_media):
        try:
            block_parser(soup, row)
        except Exception as exc:  # un bloc trencat no ha d'aturar tota la fila
            row.setdefault("_errors", []).append(f"{block_parser.__name__}: {exc}")
    return row
