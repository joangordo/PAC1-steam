"""
simulate_dataset.py
===================
Genera un DATASET SIMULAT a partir del dataset real, per publicar-lo a Zenodo.

El dataset real no es pot redistribuir (les dades són de Valve i dels
desenvolupadors). El simulat té exactament les mateixes 145 columnes i tipus, i
distribucions semblants, però cap fila correspon a un joc real.

Com es construeix cada fila:
  1. Les columnes es reparteixen en BLOCS de variables relacionades (preu,
     ressenyes, idiomes, requisits...).
  2. Cada bloc es copia d'un joc real triat a l'atzar, i cada bloc d'un joc
     diferent. Així es mantenen les relacions dins de cada bloc (per exemple, un
     preu i el seu descompte), però la fila resultant és una barreja de molts jocs.
  3. Els blocs que depenen de si el joc està publicat (data, preu, ressenyes)
     es trien entre jocs amb el mateix valor de coming_soon, perquè la fila sigui
     coherent (un joc no publicat no té ressenyes).
  4. Als valors numèrics de recompte s'hi afegeix soroll (±20%), i als preus
     una variació (±15%).
  5. Els identificadors i els textos (appid, nom, URL, descripcions, estudis,
     imatges, notes dels requisits) se substitueixen per valors inventats.

Ús (des de l'arrel del repositori):
  python source/simulate_dataset.py
  python source/simulate_dataset.py --input dataset/steam_indie_games.csv \
      --output dataset/steam_indie_games_simulat.csv --rows 26298 --seed 2026
"""

import argparse
import csv
import re
import sys

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Blocs de columnes que es copien junts d'un mateix joc real
# ---------------------------------------------------------------------------
STATUS = ["coming_soon", "early_access", "release_date"]
PRICE = ["price_original", "price_final", "discount_pct", "on_sale", "sale_end_text", "is_free",
         "n_purchase_options", "n_bundles", "n_dlc", "n_points_shop_items"]
LEGAL = ["third_party_eula", "third_party_account", "kernel_anticheat", "anticheat_name"]
REVIEWS = ["reviews_recent_label", "reviews_recent_pct", "reviews_recent_n", "reviews_lang_scope",
           "reviews_lang_label", "reviews_lang_pct", "reviews_lang_n", "reviews_lang_filtered",
           "metacritic_score", "n_press_quotes", "n_curators", "n_awards"]
CONTENT = ["genres", "n_genres", "tags", "n_tags", "tag_1", "tag_2", "tag_3", "tag_ids",
           "mature_content", "mature_content_text", "content_descriptor_ids", "age_gate"]
MEDIA = ["n_screenshots", "n_trailers"]
META = ["app_type", "search_tag", "http_status", "scraped_at"]
STUDIO = ["n_developers", "n_publishers", "self_published", "has_website", "about_n_words", "franchise"]

# Blocs que depenen de si el joc està publicat
CONDITIONAL = {"price": PRICE, "reviews": REVIEWS}

# Columnes de recompte a les quals s'afegeix soroll (±20%)
NOISY_COUNTS = ["n_dlc", "n_points_shop_items", "reviews_recent_n", "reviews_lang_n", "n_curators",
                "about_n_words", "n_screenshots", "n_trailers"]


def blocks_by_prefix(columns):
    """Blocs que es defineixen pel nom de les columnes (característiques, idiomes, requisits)."""
    features = ["features", "feature_ids", "n_features"] + [c for c in columns if c.startswith("feat_")]
    lang = (["languages", "n_languages", "n_lang_interface", "n_lang_audio", "n_lang_subtitles"]
            + [c for c in columns if re.search(r"_(interface|audio|subtitles)$", c) and not c.startswith("n_")])
    reqs = (["platform_win", "platform_mac", "platform_linux"]
            + [c for c in columns if c.startswith("req_")] + ["requires_64bit", "has_recommended_reqs"])
    return features, lang, reqs


# ---------------------------------------------------------------------------
# Utilitats per als preus en brut ("19,99€", "Gratuito")
# ---------------------------------------------------------------------------
def parse_euros(text):
    """'19,99€' -> 19.99; None si no és un preu."""
    m = re.search(r"(\d+(?:[.,]\d+)?)", str(text))
    if not m or "€" not in str(text):
        return None
    return float(m.group(1).replace(".", "").replace(",", ".")) if "," in m.group(1) else float(m.group(1))


def format_euros(value):
    """19.99 -> '19,99€' (format de la botiga en castellà)."""
    return f"{value:.2f}".replace(".", ",") + "€"


def jitter_price(text, factor):
    """Aplica un factor al preu i l'arrodoneix a ,99 com fan les botigues."""
    value = parse_euros(text)
    if value is None:
        return text                       # "Gratuito", buit, etc.: es manté
    new = max(0.49, round(value * factor) - 0.01)
    return format_euros(new)


# ---------------------------------------------------------------------------
# Generació
# ---------------------------------------------------------------------------
def simulate(real: pd.DataFrame, n_rows: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    columns = list(real.columns)
    features, lang, reqs = blocks_by_prefix(columns)
    blocks = {"status": STATUS, "price": PRICE, "legal": LEGAL, "reviews": REVIEWS,
              "content": CONTENT, "features": features, "lang": lang, "reqs": reqs,
              "media": MEDIA, "meta": META, "studio": STUDIO}

    # Comprovem que tota columna real, excepte els identificadors, té un bloc
    identifiers = {"appid", "name", "url", "search_position", "short_description",
                   "developers", "publishers", "header_img_url", "capsule_img_url"}
    covered = set(identifiers).union(*blocks.values())
    missing = [c for c in columns if c not in covered]
    if missing:
        raise SystemExit(f"Columnes sense bloc assignat: {missing}")

    published = real["coming_soon"].astype(str).str.lower() != "true"
    pools = {True: np.flatnonzero(published.values), False: np.flatnonzero(~published.values)}
    sim = pd.DataFrame(index=range(n_rows), columns=columns, dtype=object)

    # 1. Bloc d'estat: decideix si el joc simulat està publicat
    donors = rng.integers(0, len(real), n_rows)
    for c in STATUS:
        sim[c] = real[c].values[donors]
    sim_published = published.values[donors]

    # 2. Resta de blocs: cada un d'un joc diferent
    for name, cols in blocks.items():
        if name == "status":
            continue
        if name in CONDITIONAL:
            # Donant amb el mateix estat de publicació que el joc simulat
            donors = np.array([rng.choice(pools[bool(p)]) for p in sim_published])
        else:
            donors = rng.integers(0, len(real), n_rows)
        for c in cols:
            sim[c] = real[c].values[donors]

    # 3. Soroll als recomptes (±20%) i variació als preus (±15%)
    for c in NOISY_COUNTS:
        values = pd.to_numeric(sim[c], errors="coerce")
        noisy = (values * rng.uniform(0.8, 1.2, n_rows)).round()
        sim[c] = noisy.where(values.isna(), noisy.clip(lower=0)).astype("Int64")
    factors = rng.uniform(0.85, 1.15, n_rows)
    sim["price_original"] = [jitter_price(p, f) for p, f in zip(sim["price_original"], factors)]
    # Si hi ha descompte, el preu final es recalcula a partir del preu original
    finals = []
    for orig, final, disc, f in zip(sim["price_original"], sim["price_final"], sim["discount_pct"], factors):
        d = re.search(r"(\d+)", str(disc)) if isinstance(disc, str) else None
        o = parse_euros(orig)
        if d and o is not None:
            finals.append(format_euros(max(0.49, round(o * (1 - int(d.group(1)) / 100), 2))))
        else:
            finals.append(jitter_price(final, f))
    sim["price_final"] = finals

    # 4. Identificadors i textos inventats
    width = len(str(n_rows))
    ids = 90_000_000 + rng.permutation(n_rows)          # cap appid real arriba a aquest rang
    sim["appid"] = ids
    sim["name"] = [f"Joc simulat {i:0{width}d}" for i in range(1, n_rows + 1)]
    sim["url"] = [f"https://example.org/simulat/app/{a}/" for a in ids]
    sim["header_img_url"] = [f"https://example.org/simulat/img/{a}/header.jpg" for a in ids]
    sim["capsule_img_url"] = [f"https://example.org/simulat/img/{a}/capsule.jpg" for a in ids]
    sim["search_position"] = rng.permutation(n_rows) + 1
    sim["short_description"] = [f"Descripció simulada del joc {i:0{width}d}." for i in range(1, n_rows + 1)]
    sim["mature_content_text"] = np.where(sim["mature_content"].astype(str).str.lower() == "true",
                                          "Avís de contingut simulat.", "")
    sim["franchise"] = np.where(sim["franchise"].notna() & (sim["franchise"].astype(str) != ""),
                                [f"Franquícia simulada {k:03d}" for k in rng.integers(1, 300, n_rows)], "")
    for c in ("req_min_notes", "req_rec_notes"):
        sim[c] = np.where(sim[c].notna() & (sim[c].astype(str) != ""), "Notes simulades.", "")

    # Estudis inventats: uns quants estudis amb molts jocs i molts amb un de sol (com a la realitat)
    studio_pool = [f"Estudi simulat {k:04d}" for k in range(1, 6001)]
    weights = 1 / np.arange(1, len(studio_pool) + 1) ** 0.9
    weights /= weights.sum()

    def studios(n):
        n = int(n) if pd.notna(n) and int(n) > 0 else 0
        return "|".join(rng.choice(studio_pool, size=n, replace=False, p=weights)) if n else ""

    devs = [studios(n) for n in pd.to_numeric(sim["n_developers"], errors="coerce")]
    pubs = []
    for d, n, own in zip(devs, pd.to_numeric(sim["n_publishers"], errors="coerce"), sim["self_published"]):
        pubs.append(d if str(own).lower() == "true" else studios(n))
    sim["developers"], sim["publishers"] = devs, pubs
    return sim[columns]


def check(real: pd.DataFrame, sim: pd.DataFrame) -> None:
    """Comprovacions de privacitat i de semblança amb el dataset real."""
    assert list(sim.columns) == list(real.columns), "les columnes no coincideixen"
    leaks = {
        "appid": set(sim.appid.astype(str)) & set(real.appid.astype(str)),
        "name": set(sim.name) & set(real.name.dropna()),
        "short_description": set(sim.short_description) & set(real.short_description.dropna()),
        "developers": set(sim.developers) & set(real.developers.dropna()),
    }
    print("Comprovació de privacitat (valors reals copiats):")
    for col, found in leaks.items():
        print(f"  {col:18} {len(found)}")
    print("\nSemblança amb el dataset real:")
    pct_real = (real.coming_soon.astype(str).str.lower() == "true").mean() * 100
    pct_sim = (sim.coming_soon.astype(str).str.lower() == "true").mean() * 100
    print(f"  Jocs no publicats:           real {pct_real:5.1f}%   simulat {pct_sim:5.1f}%")
    for col in ("reviews_lang_pct", "reviews_lang_n", "n_languages", "n_screenshots"):
        r, s = pd.to_numeric(real[col], errors="coerce"), pd.to_numeric(sim[col], errors="coerce")
        print(f"  {col:28} mediana real {r.median():8.1f}   simulat {s.median():8.1f}")
    prices_r = real.price_final.map(parse_euros).dropna()
    prices_s = sim.price_final.map(parse_euros).dropna()
    print(f"  {'price_final (€)':28} mediana real {prices_r.median():8.2f}   simulat {prices_s.median():8.2f}")


def main() -> int:
    p = argparse.ArgumentParser(description="Genera el dataset simulat a partir del real")
    p.add_argument("--input", default="dataset/steam_indie_games.csv")
    p.add_argument("--output", default="dataset/steam_indie_games_simulat.csv")
    p.add_argument("--rows", type=int, default=None, help="nombre de files (per defecte, les del real)")
    p.add_argument("--seed", type=int, default=2026, help="llavor aleatòria (mateixa llavor = mateix resultat)")
    args = p.parse_args()

    real = pd.read_csv(args.input, encoding="utf-8-sig", dtype=str, keep_default_na=False,
                       na_values=[""])
    sim = simulate(real, args.rows or len(real), args.seed)
    sim.to_csv(args.output, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)
    print(f"Dataset simulat desat a {args.output}: {len(sim)} files x {len(sim.columns)} columnes\n")
    check(real, sim)
    return 0


if __name__ == "__main__":
    sys.exit(main())
