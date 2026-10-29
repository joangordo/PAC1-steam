# Diccionari de variables — Steam Indie Games Dataset

145 columnes. **Fase:** F1 = llistat de cerca (`discover_games.py`), F2 = fitxa del joc (`parse_game_page.py`). Exemples reals de la fitxa de *Rust* (octubre 2026).

Criteri: els camps es guarden **en brut** (text amb unitats, dates en castellà). La neteja i la
conversió de tipus es faran a la Pràctica 2. Els percentatges i recomptes que venen dins d'una
frase (ressenyes, mentors, DLC) sí que s'extreuen ja com a enters.

Tipus: `id` · `text` · `url` · `data` · `num` · `cat` · `multi` (multivalor, separador `|`) · `ord` · `bool`.

## 1. Identificació i temps
| Columna | Tipus | Fase | Exemple |
|---|---|---|---|
| appid | id | F1 | 252490 |
| name | text | F2 | Rust |
| url | url | F2 | https://store.steampowered.com/app/252490/Rust/ |
| app_type | cat | F2 | juego (o software, vídeo…) |
| search_tag | cat | F1 | Roguelike (subcategoria on s'ha trobat; "Indie" si no se n'usen) |
| search_position | ord | F1 | 1 |
| release_date | data (brut) | F2 | 8 FEB 2018 |
| coming_soon, early_access | bool | F2 | False, False |
| developers, publishers | multi | F2 | Facepunch Studios |
| n_developers, n_publishers | num | F2 | 1, 1 |
| self_published | bool | F2 | True |
| franchise | cat | F2 | (buit) |
| short_description | text | F2 | En Rust, el único propósito es sobrevivir… |
| about_n_words | num | F2 | 521 |
| has_website | bool | F2 | True |

## 2. Preu i model de negoci
| Columna | Tipus | Fase | Exemple |
|---|---|---|---|
| price_original, price_final | num (brut) | F2 | 39,99€ · 19,99€ |
| discount_pct | num (brut) | F2 | -50% |
| on_sale | bool | F2 | True |
| sale_end_text | data (brut) | F2 | ¡PROMOCIÓN ESPECIAL! La oferta finaliza el 9 de noviembre |
| is_free | bool | F2 | False |
| n_purchase_options | num | F2 | 1 |
| n_bundles | num | F2 | 3 |
| n_dlc | num | F2 | 5 |
| n_points_shop_items | num | F2 | 54 |
| third_party_eula, third_party_account | bool | F2 | True, False |
| kernel_anticheat | bool | F2 | True |
| anticheat_name | cat | F2 | Easy Anti-Cheat |

## 3. Recepció
| Columna | Tipus | Fase | Exemple |
|---|---|---|---|
| reviews_recent_label | ord | F2 | Muy positivas |
| reviews_recent_pct, reviews_recent_n | num | F2 | 80 · 8433 |
| reviews_lang_scope | cat | F2 | Reseñas en Español de España |
| reviews_lang_label | ord | F2 | Muy positivas |
| reviews_lang_pct, reviews_lang_n | num | F2 | 91 · 44384 |
| reviews_lang_filtered | bool | F2 | True |
| metacritic_score | num | F2 | 69 |
| n_press_quotes | num | F2 | 3 |
| n_curators | num | F2 | 4306 |
| n_awards | num | F2 | 1 |

Ordinal de ressenyes (pitjor → millor): Extremadamente negativas < Muy negativas < Negativas <
Mayormente negativas < Variadas < Mayormente positivas < Positivas < Muy positivas < Extremadamente positivas.

## 4. Contingut
| Columna | Tipus | Fase | Exemple |
|---|---|---|---|
| genres | multi | F2 | Acción\|Aventura\|Indie\|Multijugador masivo\|Rol |
| n_genres | num | F2 | 5 |
| tags (ordenats per vots) | multi | F2 | Supervivencia\|Fabricación\|Multijugador… |
| n_tags | num | F2 | 20 |
| tag_1, tag_2, tag_3 | cat | F2 | Supervivencia · Fabricación · Multijugador |
| tag_ids | multi | F1 | ids numèrics dels tags |
| mature_content | bool | F2 | True |
| mature_content_text | text | F2 | Contains violence and caveman themed nudity… |
| content_descriptor_ids | multi | F1 | 2\|5 |
| age_gate | bool | F2 | False |

## 5. Característiques
`features` (multi, text), `feature_ids` (multi, id numèric de Steam), `n_features` (num) i 33
booleanes `feat_*` construïdes a partir de l'id (independent de l'idioma de la botiga):

single_player, multiplayer, pvp, online_pvp, lan_pvp, shared_screen_pvp, coop, online_coop,
lan_coop, shared_screen_coop, shared_screen, cross_platform, mmo, achievements, cloud,
full_controller, partial_controller, trading_cards, workshop, in_app_purchases, stats,
leaderboards, level_editor, remote_play_phone, remote_play_tablet, remote_play_tv,
remote_play_together, vr_supported, vr_only, family_sharing, vac, captions, commentary.

## 6. Plataformes i idiomes
| Columna | Tipus | Exemple |
|---|---|---|
| platform_win, platform_mac, platform_linux | bool | True, True, False |
| languages | multi | Español de España\|Inglés\|Francés… |
| n_languages | num | 25 |
| n_lang_interface, n_lang_audio, n_lang_subtitles | num | — |
| {es, es_latam, ca, en, zh_cn, ja, ko}_{interface, audio, subtitles} | bool (21 col.) | es_audio = True |

## 7. Requisits tècnics (Windows; text cru → numèrics a PRAC2)
`req_min_*` i `req_rec_*` per a: os, cpu, ram, gpu, directx, storage, network, notes (16 columnes),
més `requires_64bit` (bool) i `has_recommended_reqs` (bool). Exemple: req_min_ram = "12 GB de RAM".

## 8. Multimèdia i metadades
| Columna | Tipus | Fase | Exemple |
|---|---|---|---|
| n_screenshots, n_trailers | num | F2 | 33 · 4 |
| header_img_url, capsule_img_url | url | F2 / F1 | https://…/header.jpg |
| http_status | num | F2 | 200 |
| scraped_at | data | F2 | 2026-10-30T18:47:39+00:00 |

## Notes
- **Ressenyes per idioma.** La fitxa només mostra la valoració calculada amb les ressenyes en
  l'idioma de la botiga (Rust: 91 % de 44.384 en castellà) i les recents. La valoració global en
  tots els idiomes no apareix a l'HTML i no s'inclou al dataset.
- **Tràilers i captures** surten d'un JSON incrustat a l'atribut `data-props` del carrusel.
- **No disponibles a l'HTML estàtic:** la compatibilitat amb Steam Deck (es carrega amb
  JavaScript) i la classificació PEGI (no apareix a les fitxes analitzades). Es descarten.
