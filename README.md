# CDMX: Un semestre de intercambio

A Spanish practice game (Mexican Spanish) for a student about to spend a semester at the
UNAM in Mexico City, living with a host family in Coyoacán. Two parts, both open from the
start:

- **Parte 1 · El viaje** (A2–B1) – twelve places, twenty-four voiced conversations:
  from the airport taxi counter to a farewell with the mariachis in Plaza Garibaldi, by
  way of the host family's table, the corner shop, the Metro, the market, a taquería, the
  pharmacy, Xochimilco and the Day of the Dead.
- **Parte 2 · La historia** (B1–B2) – ten real historical sites in chronological order,
  twenty reading passages of 320–370 words: Cuicuilco, Teotihuacan, the Templo Mayor,
  Tlatelolco (1521 and 1968), the Villa de Guadalupe, the Cathedral and the sinking city,
  Chapultepec, Bellas Artes, the Casa Azul and Ciudad Universitaria.

Double-click `Jugar.cmd` to play. It runs offline: every spoken line is pre-recorded.

The player is a generic exchange student, not a named character. Characters speak to the
player in gender-neutral Spanish; where the player's own typed answer needs agreement
("estoy cansado/a") both forms are accepted.

## How it plays

The game is built on the same engine as *Valencia: Camino a EUROCALL*:

- **Map** – real Mexico City from OpenStreetMap, in three views: the whole city, the
  Centro Histórico street by street, and Coyoacán with Ciudad Universitaria (click a
  framed area to zoom in). Teotihuacan lies off the map; its pin sits at the edge with an
  arrow.
- **Scenes** – a voiced conversation. You answer comprehension questions, choose the most
  appropriate reply, and type what you would say.
- **Readings** (part 2) – a short voiced exchange with el profesor Salgado, Valeria,
  Diego or Rocío, then a passage to read at your own pace, then questions on it.
- **Tap any word** for an English gloss; looked-up words and the key phrases in red go
  into the **cuaderno** (spaced repetition, printable flashcards).
- **Hoja de frases / Lecturas para imprimir** on each place's card.
- **Grabar / Mi voz / Comparar**, **Modo escucha**, pinch-zoom and + / − as in Valencia.

## Building

Same pipeline as Valencia (see `tools/build_content.py` for the script format):

    python -X utf8 tools/build_content.py     # content/*.txt -> game/data/content.json
    python -X utf8 tools/tts_generate.py      # voice new lines (qwen-tts-studio must be running)
    python -X utf8 tools/make_captions.py     # Ideogram captions for the illustrations
    python -X utf8 tools/make_map.py          # maps and pins (after the illustrations)
    python -X utf8 tools/web_build.py         # web version into web/
    python -X utf8 tools/web_deploy.py        # publish web/ to GitHub Pages
    python -X utf8 tools/status.py            # progress bars

`tools/fetch_osm.py` downloads the map data once. Machine-specific paths and hosts go in
`tools/local.json` (not in git; copy `tools/local.example.json`).

An answer line in a script may write a gendered word as `cansado/a`, `listos/as` or
`profesor/a`: both forms are accepted, the slash is shown in the model answer, and the
recording uses the form that matches the YO voice (`"gender"` in `content/cast.json`).

## Facts and sources

The practical details (Metro fare 5 pesos, Movilidad Integrada card 15 pesos, prepaid
airport taxis priced by zone, the trajinera rate per boat and hour, registering a phone
line with a passport since 2026) were checked in October 2026 and will change; the scenes
say so where it matters. Historical dates were checked against reference sources, and the
texts hedge where historians disagree (the Xitle eruption, the Guadalupe apparition, the
number of victims in 1968, the Niños Héroes).

The illustrations were made with Ideogram 4 (non-commercial licence).
Map data © OpenStreetMap contributors, available under the Open Database Licence.
