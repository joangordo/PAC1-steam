# Diccionari de variables — Steam Indie ES 2026

Dataset: `dataset/steam_indie_games.csv` · **26.298 jocs × 145 columnes**

**Fase d'origen:** F1 = llistat de la cerca (`discover_games.py`) · F2 = fitxa del joc (`parse_game_page.py`) · P = la genera el programa durant l'extracció (`scrape_games.py`).

**Exemples:** valors reals de la fitxa de *Rust* (appid 252490). Si Rust no té valor en aquella columna, s'indica el d'un altre joc.

**Criteri:** els valors es guarden en brut, tal com surten a la web (preus amb €, dates en castellà, requisits amb unitats). Les columnes multivalor fan servir `|` com a separador. La neteja es farà a la Pràctica 2.

## 1. Identificació i temps (18 columnes)

| Columna | Tipus | Fase | Descripció | Exemple |
|---|---|---|---|---|
| `appid` | identificador | F1/F2 | Identificador numèric del joc a Steam | 252490 |
| `name` | text | F2 | Nom del joc | Rust |
| `url` | URL | F2 | Adreça de la fitxa del joc | https://store.steampowered.com/app/252490/Rust/ |
| `app_type` | categòrica | F2 | Tipus d'aplicació segons la fitxa ("juego") | juego |
| `search_tag` | categòrica | F1 | Cerca on s'ha trobat el joc ("Indie" o la subcategoria) | Indie |
| `search_position` | ordinal | F1 | Posició del joc a la llista de la cerca (ordre per nom) | 18657 |
| `release_date` | data (en brut) | F2 | Data de llançament tal com surt a la fitxa | 8 FEB 2018 |
| `coming_soon` | booleana | F2 | El joc encara no s'ha publicat | False |
| `early_access` | booleana | F2 | El joc és en accés anticipat | False |
| `developers` | multivalor | F2 | Desenvolupadors | Facepunch Studios |
| `publishers` | multivalor | F2 | Editors | Facepunch Studios |
| `n_developers` | numèrica | F2 | Nombre de desenvolupadors | 1 |
| `n_publishers` | numèrica | F2 | Nombre d'editors | 1 |
| `self_published` | booleana | F2 | El desenvolupador i l'editor són els mateixos | True |
| `franchise` | categòrica | F2 | Franquícia a la qual pertany el joc | BURIED TAPES *(altre joc)* |
| `short_description` | text | F2 | Descripció curta de la fitxa | En Rust, el único propósito es sobrevivir. Todo lo que te… |
| `about_n_words` | numèrica | F2 | Nombre de paraules de la descripció llarga | 521 |
| `has_website` | booleana | F2 | La fitxa enllaça a un lloc web oficial | True |

## 2. Preu i model de negoci (14 columnes)

| Columna | Tipus | Fase | Descripció | Exemple |
|---|---|---|---|---|
| `price_original` | numèrica (en brut) | F2 | Preu sense descompte, amb el símbol € | 39,99€ |
| `price_final` | numèrica (en brut) | F2 | Preu actual, amb el símbol € | 19,99€ |
| `discount_pct` | numèrica (en brut) | F2 | Descompte actiu ("-50%") | -50% |
| `on_sale` | booleana | F2 | El joc té un descompte actiu | True |
| `sale_end_text` | data (en brut) | F2 | Text de la data de final de l'oferta | ¡PROMOCIÓN ESPECIAL! La oferta finaliza el 9 de noviembre |
| `is_free` | booleana | F2 | El joc és gratuït | False |
| `n_purchase_options` | numèrica | F2 | Opcions de compra que no són lots (edicions) | 1 |
| `n_bundles` | numèrica | F2 | Lots que inclouen el joc | 3 |
| `n_dlc` | numèrica | F2 | Nombre de DLC | 5 |
| `n_points_shop_items` | numèrica | F2 | Articles a la botiga de punts de Steam | 54 |
| `third_party_eula` | booleana | F2 | Cal acceptar una llicència de l'editor (ALUF/EULA) | True |
| `third_party_account` | booleana | F2 | Cal un compte d'un servei extern | False |
| `kernel_anticheat` | booleana | F2 | Inclou un sistema anti-trampes a nivell de kernel | True |
| `anticheat_name` | categòrica | F2 | Nom del sistema anti-trampes | Easy Anti‑Cheat |

## 3. Recepció (12 columnes)

| Columna | Tipus | Fase | Descripció | Exemple |
|---|---|---|---|---|
| `reviews_recent_label` | ordinal (9 nivells) | F2 | Etiqueta de les ressenyes dels últims 30 dies | Muy positivas |
| `reviews_recent_pct` | numèrica | F2 | % de ressenyes positives dels últims 30 dies | 80 |
| `reviews_recent_n` | numèrica | F2 | Nombre de ressenyes dels últims 30 dies | 8259 |
| `reviews_lang_scope` | categòrica | F2 | Àmbit de la valoració principal ("Todas las reseñas" o "Reseñas en Español de España") | Reseñas en Español de España |
| `reviews_lang_label` | ordinal (9 nivells) | F2 | Etiqueta de la valoració principal | Muy positivas |
| `reviews_lang_pct` | numèrica | F2 | % de ressenyes positives de la valoració principal | 91 |
| `reviews_lang_n` | numèrica | F2 | Nombre de ressenyes de la valoració principal | 44390 |
| `reviews_lang_filtered` | booleana | F2 | La valoració principal només compta les ressenyes en castellà | True |
| `metacritic_score` | numèrica | F2 | Puntuació de Metacritic | 69 |
| `n_press_quotes` | numèrica | F2 | Nombre de cites de premsa a la fitxa | 3 |
| `n_curators` | numèrica | F2 | Nombre de mentors (curators) que han analitzat el joc | 3278 |
| `n_awards` | numèrica | F2 | Nombre de premis que mostra la fitxa | 1 |

## 4. Contingut (12 columnes)

| Columna | Tipus | Fase | Descripció | Exemple |
|---|---|---|---|---|
| `genres` | multivalor | F2 | Gèneres | Acción\|Aventura\|Indie\|Multijugador masivo\|Rol |
| `n_genres` | numèrica | F2 | Nombre de gèneres | 5 |
| `tags` | multivalor | F2 | Etiquetes d'usuari, ordenades per vots (fins a 20) | Supervivencia\|Fabricación\|Multijugador\|Mundo abierto\|… |
| `n_tags` | numèrica | F2 | Nombre d'etiquetes | 20 |
| `tag_1` | categòrica | F2 | Etiqueta més votada | Supervivencia |
| `tag_2` | categòrica | F2 | Segona etiqueta més votada | Fabricación |
| `tag_3` | categòrica | F2 | Tercera etiqueta més votada | Multijugador |
| `tag_ids` | multivalor | F1 | Identificadors de les etiquetes (del llistat de la cerca) | 1662\|1702\|3859\|1695\|1100689\|1643\|1775 |
| `mature_content` | booleana | F2 | La fitxa té avís de contingut per a adults | True |
| `mature_content_text` | text | F2 | Text de l'avís de contingut per a adults | Los desarrolladores describen su contenido así: Contains … |
| `content_descriptor_ids` | multivalor | F1 | Identificadors dels descriptors de contingut (del llistat de la cerca) | 1\|2\|5 |
| `age_gate` | booleana | P | La verificació d'edat no s'ha pogut superar | False |

## 5. Característiques (36 columnes)

| Columna | Tipus | Fase | Descripció | Exemple |
|---|---|---|---|---|
| `features` | multivalor | F2 | Característiques tal com surten a la fitxa | Multijugador masivo\|JcJ en línea\|Cooperativo en línea\|… |
| `feature_ids` | multivalor | F2 | Identificadors numèrics de les característiques | 20\|36\|38\|27\|22\|29\|30\|35\|15\|42 |
| `n_features` | numèrica | F2 | Nombre de característiques | 10 |
| `feat_achievements` | booleana | F2 | Característica: Logros de Steam | True |
| `feat_captions` | booleana | F2 | Característica: Subtítols disponibles | False |
| `feat_cloud` | booleana | F2 | Característica: Steam Cloud | False |
| `feat_commentary` | booleana | F2 | Característica: Comentaris disponibles | False |
| `feat_coop` | booleana | F2 | Característica: Cooperatiu | True |
| `feat_cross_platform` | booleana | F2 | Característica: Multijugador multiplataforma | True |
| `feat_family_sharing` | booleana | F2 | Característica: Préstec familiar | False |
| `feat_full_controller` | booleana | F2 | Característica: Compatibilitat total amb mando | False |
| `feat_in_app_purchases` | booleana | F2 | Característica: Compres dins de l'aplicació | True |
| `feat_lan_coop` | booleana | F2 | Característica: Cooperatiu LAN | False |
| `feat_lan_pvp` | booleana | F2 | Característica: JcJ LAN | False |
| `feat_leaderboards` | booleana | F2 | Característica: Marcadors de Steam | False |
| `feat_level_editor` | booleana | F2 | Característica: Editor de nivells | False |
| `feat_mmo` | booleana | F2 | Característica: MMO | True |
| `feat_multiplayer` | booleana | F2 | Característica: Multijugador | True |
| `feat_online_coop` | booleana | F2 | Característica: Cooperatiu en línia | True |
| `feat_online_pvp` | booleana | F2 | Característica: JcJ en línia | True |
| `feat_partial_controller` | booleana | F2 | Característica: Compatibilitat parcial amb mando | False |
| `feat_pvp` | booleana | F2 | Característica: JcJ | True |
| `feat_remote_play_phone` | booleana | F2 | Característica: Remote Play al mòbil | False |
| `feat_remote_play_tablet` | booleana | F2 | Característica: Remote Play a la tauleta | True |
| `feat_remote_play_together` | booleana | F2 | Característica: Remote Play Together | False |
| `feat_remote_play_tv` | booleana | F2 | Característica: Remote Play a la TV | False |
| `feat_shared_screen` | booleana | F2 | Característica: Pantalla compartida | False |
| `feat_shared_screen_coop` | booleana | F2 | Característica: Cooperatiu a pantalla compartida | False |
| `feat_shared_screen_pvp` | booleana | F2 | Característica: JcJ a pantalla compartida | False |
| `feat_single_player` | booleana | F2 | Característica: Un jugador | False |
| `feat_stats` | booleana | F2 | Característica: Estadístiques | True |
| `feat_trading_cards` | booleana | F2 | Característica: Cromos de Steam | True |
| `feat_vac` | booleana | F2 | Característica: Anti-trampes VAC | True |
| `feat_vr_only` | booleana | F2 | Característica: Només RV | False |
| `feat_vr_supported` | booleana | F2 | Característica: Compatible amb RV | False |
| `feat_workshop` | booleana | F2 | Característica: Steam Workshop | True |

## 6. Plataformes (3 columnes)

| Columna | Tipus | Fase | Descripció | Exemple |
|---|---|---|---|---|
| `platform_win` | booleana | F2 | Té requisits per a Windows | True |
| `platform_mac` | booleana | F2 | Té requisits per a macOS | True |
| `platform_linux` | booleana | F2 | Té requisits per a Linux / SteamOS | False |

## 7. Idiomes (26 columnes)

| Columna | Tipus | Fase | Descripció | Exemple |
|---|---|---|---|---|
| `languages` | multivalor | F2 | Idiomes disponibles | Español de España\|Inglés\|Francés\|Italiano\|Alemán\|Jap… |
| `n_languages` | numèrica | F2 | Nombre d'idiomes | 25 |
| `n_lang_interface` | numèrica | F2 | Idiomes amb interfície | 25 |
| `n_lang_audio` | numèrica | F2 | Idiomes amb veu | 13 |
| `n_lang_subtitles` | numèrica | F2 | Idiomes amb subtítols | 13 |
| `es_interface` | booleana | F2 | Disponible en castellà (Espanya): interfície | True |
| `es_audio` | booleana | F2 | Disponible en castellà (Espanya): veu | True |
| `es_subtitles` | booleana | F2 | Disponible en castellà (Espanya): subtítols | True |
| `es_latam_interface` | booleana | F2 | Disponible en castellà (Hispanoamèrica): interfície | True |
| `es_latam_audio` | booleana | F2 | Disponible en castellà (Hispanoamèrica): veu | False |
| `es_latam_subtitles` | booleana | F2 | Disponible en castellà (Hispanoamèrica): subtítols | False |
| `ca_interface` | booleana | F2 | Disponible en català: interfície | False |
| `ca_audio` | booleana | F2 | Disponible en català: veu | False |
| `ca_subtitles` | booleana | F2 | Disponible en català: subtítols | False |
| `en_interface` | booleana | F2 | Disponible en anglès: interfície | True |
| `en_audio` | booleana | F2 | Disponible en anglès: veu | True |
| `en_subtitles` | booleana | F2 | Disponible en anglès: subtítols | True |
| `zh_cn_interface` | booleana | F2 | Disponible en xinès simplificat: interfície | True |
| `zh_cn_audio` | booleana | F2 | Disponible en xinès simplificat: veu | True |
| `zh_cn_subtitles` | booleana | F2 | Disponible en xinès simplificat: subtítols | True |
| `ja_interface` | booleana | F2 | Disponible en japonès: interfície | True |
| `ja_audio` | booleana | F2 | Disponible en japonès: veu | True |
| `ja_subtitles` | booleana | F2 | Disponible en japonès: subtítols | True |
| `ko_interface` | booleana | F2 | Disponible en coreà: interfície | True |
| `ko_audio` | booleana | F2 | Disponible en coreà: veu | True |
| `ko_subtitles` | booleana | F2 | Disponible en coreà: subtítols | True |

## 8. Requisits tècnics (Windows) (18 columnes)

| Columna | Tipus | Fase | Descripció | Exemple |
|---|---|---|---|---|
| `req_min_os` | categòrica (en brut) | F2 | Requisit mínim: sistema operatiu | Windows 11 64bit |
| `req_min_cpu` | text | F2 | Requisit mínim: processador | AMD Ryzen 5 1400 or Intel Core i5-6600 |
| `req_min_ram` | numèrica (en brut) | F2 | Requisit mínim: memòria RAM | 12 GB de RAM |
| `req_min_gpu` | text | F2 | Requisit mínim: targeta gràfica | AMD Radeon RX 470, NVIDIA GeForce GTX 1060, Intel® Arc™ A580 |
| `req_min_directx` | ordinal (en brut) | F2 | Requisit mínim: versió de DirectX | Versión 11 |
| `req_min_storage` | numèrica (en brut) | F2 | Requisit mínim: espai al disc | 45 GB de espacio disponible |
| `req_min_network` | text | F2 | Requisit mínim: connexió a internet | Conexión de banda ancha a Internet |
| `req_min_notes` | text | F2 | Requisit mínim: notes addicionals | SSD is highly recommended or expect longer than average l… |
| `req_rec_os` | categòrica (en brut) | F2 | Requisit recomanat: sistema operatiu | Windows 11 64bit |
| `req_rec_cpu` | text | F2 | Requisit recomanat: processador | AMD Ryzen 7 3700X or Intel® Core i7-6700K |
| `req_rec_ram` | numèrica (en brut) | F2 | Requisit recomanat: memòria RAM | 16 GB de RAM |
| `req_rec_gpu` | text | F2 | Requisit recomanat: targeta gràfica | AMD Radeon RX 6600XT, NVIDIA GeForce RTX 3060, Intel Arc … |
| `req_rec_directx` | ordinal (en brut) | F2 | Requisit recomanat: versió de DirectX | Versión 12 |
| `req_rec_storage` | numèrica (en brut) | F2 | Requisit recomanat: espai al disc | 45 GB de espacio disponible |
| `req_rec_network` | text | F2 | Requisit recomanat: connexió a internet | Conexión de banda ancha a Internet |
| `req_rec_notes` | text | F2 | Requisit recomanat: notes addicionals | SSD Required |
| `requires_64bit` | booleana | F2 | Els requisits demanen un sistema de 64 bits | True |
| `has_recommended_reqs` | booleana | F2 | La fitxa indica requisits recomanats | True |

## 9. Multimèdia i metadades (6 columnes)

| Columna | Tipus | Fase | Descripció | Exemple |
|---|---|---|---|---|
| `n_screenshots` | numèrica | F2 | Nombre de captures de pantalla | 33 |
| `n_trailers` | numèrica | F2 | Nombre de tràilers | 4 |
| `header_img_url` | URL | F2 | Imatge de capçalera de la fitxa | https://shared.fastly.steamstatic.com/store_item_assets/s… |
| `capsule_img_url` | URL | F1 | Imatge petita del llistat de la cerca | https://shared.fastly.steamstatic.com/store_item_assets/s… |
| `http_status` | numèrica | P | Codi HTTP de la descàrrega de la fitxa | 200 |
| `scraped_at` | data | P | Moment (UTC) en què es va llegir la fitxa per generar el CSV | 2026-11-02T22:59:15+00:00 |

## Notes

- **Etiquetes de valoració (ordinal, de pitjor a millor):** Extremadamente negativas < Muy negativas < Negativas < Mayormente negativas < Variadas < Mayormente positivas < Positivas < Muy positivas < Extremadamente positivas. Els jocs amb menys de 10 ressenyes no tenen etiqueta, només nombre.
- **Àmbit de la valoració:** Steam calcula la nota amb les ressenyes en castellà només quan n'hi ha prou (`reviews_lang_filtered` = True); si no, mostra la de totes les ressenyes.
- **Característiques:** les columnes `feat_*` es construeixen amb l'identificador numèric de Steam, que no depèn de l'idioma. La compatibilitat amb mando, la RV i el VAC es llegeixen del JSON del catàleg incrustat a la pàgina, perquè l'HTML de la fitxa ja no les mostra.
- **Jocs no publicats:** no tenen preu ni ressenyes i la data de llançament és un text ("Próximamente", "2027"...).
- **Constants per disseny:** `es_interface` sempre és True (tots els jocs estan traduïts al castellà).
- **Fase 3:** la mostra audiovisual no afegeix columnes al dataset; els fitxers i el seu registre (`data/media/media_sample.csv`) es guarden només en local.
