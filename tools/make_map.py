"""Draw the game's two maps from OpenStreetMap data (tools/osm/, see fetch_osm.py):

    game/art/map_city.png      the whole city, from the airport to Xochimilco
    game/art/map_centre.png    the Centro Histórico, street by street
    game/art/map_coyoacan.png  Coyoacán and Ciudad Universitaria
    game/art/pin_<place>.png   round thumbnails of each place's illustration
    game/data/map.json         the projection, so the game can turn lat/lon into pixels

    python -X utf8 tools/make_map.py

All maps are 860x720 game pixels, drawn at twice that so they stay sharp when
the window is enlarged. Map data (c) OpenStreetMap contributors, ODbL.
"""

import json
import math
import pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
OSM = ROOT / "tools" / "osm"
ART = ROOT / "game" / "art"
W, H, SS = 860, 720, 2
KX = 111.32 * math.cos(math.radians(19.40))    # km per degree of longitude here
KY = 111.2

LAND = "#F3E6C6"
OLD_TOWN = "#ECD6A8"
BLOCK = "#EAD8B2"
PARK = "#B7D69C"
PARK_EDGE = "#9CC383"
WATER = "#9FD0DD"
BEACH = "#F8E2A4"
ROAD = "#FFFDF6"
ROAD_EDGE = "#D9C49A"
BIG_ROAD = "#F7D58E"
PLAZA = "#FFF4D8"
BUILDING = "#DDBE8E"
BUILDING_EDGE = "#B6935A"
INK = "#1F3A4D"
MUTED = "#8A7A55"
METRO = "#B8402A"
TRAM = "#2E6F8E"

FONT_DIR = ROOT / "game" / "fonts"          # the game's own open-licence fonts
FONTS = {"regular": ("SourceSans3.ttf", 400), "bold": ("SourceSans3.ttf", 700),
         "italic": ("SourceSans3-Italic.ttf", 400)}

VIEWS = {
    "city": {"lat0": 19.3680, "lon0": -99.1350, "scale": 25.7},
    "centre": {"lat0": 19.4372, "lon0": -99.1365, "scale": 500.0},
    "coyoacan": {"lat0": 19.3300, "lon0": -99.1740, "scale": 100.0},
}
# The close-ups, framed on the city view: (view, name shown on the frame, caption side)
ZOOMS = [("centre", "Centro Histórico", "bottom"), ("coyoacan", "Coyoacán y CU", "bottom")]

SHORT = [("Avenida ", "Av. "), ("Calzada ", "Calz. "), ("Calle ", "C. "), ("Paseo ", "Pº "),
         ("Boulevard ", "Blvd. "), ("Circuito ", "Cto. "), ("Anillo Periférico", "Periférico")]
UNIVERSITY = "#E6D7B8"
AIRPORT = "#E2D9C6"
URBAN_EDGE = "#C9B48A"


def font(kind, size):
    name, weight = FONTS[kind]
    f = ImageFont.truetype(str(FONT_DIR / name), int(size * SS * 1.06))
    f.set_variation_by_axes([weight])
    return f


class View:
    def __init__(self, name):
        self.name = name
        self.lat0, self.lon0, self.scale = (VIEWS[name][k] for k in ("lat0", "lon0", "scale"))
        self.img = Image.new("RGB", (W * SS, H * SS), LAND)
        self.d = ImageDraw.Draw(self.img)
        self.boxes = []      # label bounding boxes already used

    def xy(self, lat, lon):
        return ((W / 2 + (lon - self.lon0) * KX * self.scale) * SS,
                (H / 2 - (lat - self.lat0) * KY * self.scale) * SS)

    def pts(self, geometry):
        return [self.xy(p["lat"], p["lon"]) for p in geometry]

    def inside(self, p, margin=0):
        return -margin <= p[0] <= W * SS + margin and -margin <= p[1] <= H * SS + margin

    def polygon(self, geometry, fill, outline=None, width=1):
        pts = self.pts(geometry)
        if len(pts) >= 3:
            self.d.polygon(pts, fill=fill, outline=outline, width=int(width * SS))

    def line(self, pts, fill, width):
        if len(pts) >= 2:
            self.d.line(pts, fill=fill, width=max(1, int(round(width * SS))), joint="curve")

    def dashed(self, pts, fill, width, dash=7, gap=5):
        dash, gap = dash * SS, gap * SS
        on, left = True, dash
        for a, b in zip(pts, pts[1:]):
            seg = math.dist(a, b)
            pos = 0.0
            while pos < seg:
                step = min(left, seg - pos)
                if on:
                    t0, t1 = pos / seg, (pos + step) / seg
                    self.d.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0),
                                 (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)],
                                fill=fill, width=int(width * SS))
                pos += step
                left -= step
                if left <= 0:
                    on = not on
                    left = dash if on else gap

    def label(self, xy, text, size, fill, kind="regular", angle=0.0, halo=LAND, force=False,
              spacing=0):
        """Draw text centred on xy, optionally rotated. Skips it (returns False)
        if it would sit on top of an earlier label, unless forced."""
        f = font(kind, size)
        if spacing:
            text = (" " * spacing).join(text)
        l, t, r, b = f.getbbox(text, stroke_width=2 * SS)
        tile = Image.new("RGBA", (r - l + 8, b - t + 8), (0, 0, 0, 0))
        ImageDraw.Draw(tile).text((4 - l, 4 - t), text, font=f, fill=fill,
                                  stroke_width=int(1.5 * SS), stroke_fill=halo)
        if angle:
            tile = tile.rotate(angle, expand=True, resample=Image.BICUBIC)
        x, y = int(xy[0] - tile.width / 2), int(xy[1] - tile.height / 2)
        box = (x, y, x + tile.width, y + tile.height)
        if not force:
            pad = 6 * SS
            for o in self.boxes:
                if box[0] < o[2] + pad and box[2] > o[0] - pad and box[1] < o[3] + pad \
                        and box[3] > o[1] - pad:
                    return False
            if box[0] < 0 or box[1] < 0 or box[2] > W * SS or box[3] > H * SS:
                return False
        self.img.paste(tile, (x, y), tile)
        self.boxes.append(box)
        return True

    def save(self, path):
        self.img.save(path, optimize=True)


def load(name):
    return json.loads((OSM / f"{name}.json").read_text(encoding="utf-8"))["elements"]


def stitch(ways):
    """Join way geometries end to end into the longest chains they form."""
    key = lambda p: (round(p["lat"], 7), round(p["lon"], 7))
    left = [list(w) for w in ways if len(w) >= 2]
    chains = []
    while left:
        chain = left.pop()
        grew = True
        while grew:
            grew = False
            for i, w in enumerate(left):
                if key(w[0]) == key(chain[-1]):
                    chain += w[1:]
                elif key(w[-1]) == key(chain[-1]):
                    chain += w[-2::-1]
                elif key(w[-1]) == key(chain[0]):
                    chain = w[:-1] + chain
                elif key(w[0]) == key(chain[0]):
                    chain = w[::-1][:-1] + chain
                else:
                    continue
                left.pop(i)
                grew = True
                break
        chains.append(chain)
    return chains


def areas(elements, test):
    """Closed outlines of every way/relation whose tags pass `test`."""
    out = []
    for e in elements:
        if not test(e.get("tags", {})):
            continue
        if e["type"] == "way" and "geometry" in e:
            out.append(e["geometry"])
        elif e["type"] == "relation":
            outer = [m["geometry"] for m in e.get("members", [])
                     if m["type"] == "way" and m.get("role") != "inner" and m.get("geometry")]
            out += stitch(outer)
    return out


def road_label_spots(view, elements, classes, limit, min_size=9.5):
    """Pick the longest on-screen stretch of each named street for its label."""
    best = {}
    for e in elements:
        t = e.get("tags", {})
        if e["type"] != "way" or t.get("highway") not in classes or "name" not in t:
            continue
        pts = [p for p in view.pts(e["geometry"]) if view.inside(p, -30 * SS)]
        if len(pts) < 2:
            continue
        length = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
        cur = best.get(t["name"])
        total = (cur[0] if cur else 0) + length
        if cur is None or length > cur[1]:
            best[t["name"]] = (total, length, pts)
        else:
            best[t["name"]] = (total, cur[1], cur[2])
    ranked = sorted(best.items(), key=lambda kv: -kv[1][0])[:limit]
    for name, (_, length, pts) in ranked:
        for a, b in SHORT:
            name = name.replace(a, b)
        # the point half-way along, and the direction of the street there
        half, run = length / 2, 0.0
        for a, b in zip(pts, pts[1:]):
            seg = math.dist(a, b)
            if run + seg >= half:
                t = (half - run) / seg if seg else 0
                mid = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                break
            run += seg
        a, b = pts[0], pts[-1]
        angle = -math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        if angle > 90:
            angle -= 180
        if angle < -90:
            angle += 180
        width = font("regular", min_size).getlength(name)
        if width < length * 1.15:
            view.label(mid, name, min_size, MUTED, "regular", angle)


def credit(view):
    view.label((W * SS - 118 * SS, H * SS - 12 * SS), "© colaboradores de OpenStreetMap", 9.5,
               MUTED, "italic", force=True)


# ----------------------------------------------------------------------- city

def draw_city():
    v = View("city")
    els = load("city")
    tag = lambda **kw: (lambda t: all(t.get(k) in (val if isinstance(val, tuple) else (val,))
                                      for k, val in kw.items()))

    for ring in areas(els, tag(aeroway="aerodrome")):
        v.polygon(ring, AIRPORT)
    for ring in areas(els, lambda t: t.get("amenity") == "university"):
        v.polygon(ring, UNIVERSITY)
    for ring in areas(els, tag(leisure=("park", "garden"))):
        v.polygon(ring, PARK)
    for ring in areas(els, tag(landuse="cemetery")):
        v.polygon(ring, PARK_EDGE)
    for ring in areas(els, tag(natural="water")):
        v.polygon(ring, WATER)
    for e in els:
        if e["type"] == "way" and e.get("tags", {}).get("waterway") == "canal":
            v.line(v.pts(e["geometry"]), WATER, 1.2)

    # the alcaldías, faintly: they are how people say where things are
    for e in els:
        t = e.get("tags", {})
        if e["type"] == "relation" and t.get("boundary") == "administrative":
            for m in e.get("members", []):
                if m["type"] == "way" and m.get("geometry"):
                    v.dashed(v.pts(m["geometry"]), URBAN_EDGE, 0.9, 4, 4)

    widths = {"primary": 1.3, "trunk": 2.4, "trunk_link": 1.2, "motorway": 3.0,
              "motorway_link": 1.4}
    roads = [e for e in els if e["type"] == "way" and e.get("tags", {}).get("highway") in widths]
    for casing in (True, False):
        for cls in widths:
            for e in roads:
                if e["tags"]["highway"] != cls:
                    continue
                big = cls.startswith(("trunk", "motorway"))
                if casing:
                    v.line(v.pts(e["geometry"]), ROAD_EDGE, widths[cls] + 1.2)
                else:
                    v.line(v.pts(e["geometry"]), BIG_ROAD if big else ROAD, widths[cls])

    for e in els:
        kind = e.get("tags", {}).get("railway")
        if e["type"] == "way" and kind == "subway":
            v.dashed(v.pts(e["geometry"]), METRO, 1.5, 6, 4)
        elif e["type"] == "way" and kind in ("light_rail", "tram"):
            v.dashed(v.pts(e["geometry"]), TRAM, 1.5, 6, 4)

    # Labels, most important first: they claim their space before street names.
    for name, lat, lon, size, colour, halo in [
            ("Aeropuerto (AICM)", 19.4480, -99.0640, 10.5, "#6B5A3A", AIRPORT),
            ("Bosque de Chapultepec", 19.4100, -99.2050, 10, "#3C6B33", PARK),
            ("Ciudad Universitaria", 19.3150, -99.1990, 10, "#8A6A2F", LAND),
            ("Canales de Xochimilco", 19.2700, -99.0700, 10, "#3E7F95", LAND)]:
        v.label(v.xy(lat, lon), name, size, colour, "italic", halo=halo)
    for name, lat, lon in [("CUAUHTÉMOC", 19.4440, -99.1600), ("COYOACÁN", 19.3300, -99.1300),
                           ("BENITO JUÁREZ", 19.3840, -99.1600), ("MIGUEL HIDALGO", 19.4400, -99.2150),
                           ("ÁLVARO OBREGÓN", 19.3700, -99.2350), ("IZTAPALAPA", 19.3550, -99.0750),
                           ("IZTACALCO", 19.3950, -99.0950), ("TLALPAN", 19.2780, -99.1750),
                           ("XOCHIMILCO", 19.2450, -99.1300), ("GUSTAVO A. MADERO", 19.4950, -99.0950),
                           ("AZCAPOTZALCO", 19.4850, -99.1900), ("VENUSTIANO CARRANZA", 19.4200, -99.1050),
                           ("ROMA", 19.4150, -99.1560), ("CONDESA", 19.4110, -99.1780)]:
        v.label(v.xy(lat, lon), name, 8.5, "#8A7A55", "bold")

    road_label_spots(v, els, ("trunk", "motorway"), 14, 8.5)
    credit(v)

    # Legend
    x0, y0 = 12 * SS, (H - 62) * SS
    v.d.rounded_rectangle((x0, y0, x0 + 196 * SS, y0 + 50 * SS), 6 * SS, fill="#FFFAF0",
                          outline=ROAD_EDGE, width=SS)
    v.dashed([(x0 + 12 * SS, y0 + 16 * SS), (x0 + 52 * SS, y0 + 16 * SS)], METRO, 2)
    v.dashed([(x0 + 12 * SS, y0 + 35 * SS), (x0 + 52 * SS, y0 + 35 * SS)], TRAM, 2)
    f = font("regular", 11)
    v.d.text((x0 + 62 * SS, y0 + 8 * SS), "Metro", font=f, fill=INK)
    v.d.text((x0 + 62 * SS, y0 + 27 * SS), "Tren Ligero", font=f, fill=INK)
    v.save(ART / "map_city.png")
    return v


# ------------------------------------------------------------------ close-ups

def draw_streets(v, els, widths):
    tags = lambda e: e.get("tags", {})
    for ring in areas(els, lambda t: t.get("amenity") == "university"):
        v.polygon(ring, UNIVERSITY)
    for ring in areas(els, lambda t: t.get("leisure") in ("park", "garden")
                      or t.get("landuse") in ("grass", "forest", "recreation_ground")
                      or t.get("natural") in ("wood", "scrub")):
        v.polygon(ring, PARK)

    # squares and pedestrian areas are surfaces, not lines
    for ring in areas(els, lambda t: t.get("highway") in ("pedestrian", "footway")
                      and t.get("area") == "yes"):
        v.polygon(ring, PLAZA)
    for e in els:
        if e["type"] == "relation" and tags(e).get("highway") == "pedestrian":
            for ring in areas([e], lambda t: True):
                v.polygon(ring, PLAZA)

    roads = [e for e in els if e["type"] == "way" and tags(e).get("highway") in widths
             and tags(e).get("area") != "yes"]
    for casing in (True, False):
        for cls in widths:
            for e in roads:
                if tags(e)["highway"] != cls:
                    continue
                if casing:
                    v.line(v.pts(e["geometry"]), ROAD_EDGE, widths[cls] + 1.4)
                else:
                    big = cls.startswith(("trunk", "motorway"))
                    v.line(v.pts(e["geometry"]), PLAZA if cls in ("pedestrian", "living_street")
                           else BIG_ROAD if big else ROAD, widths[cls])

    for ring in areas(els, lambda t: "building" in t):
        v.polygon(ring, BUILDING, BUILDING_EDGE, 0.5)

    for e in els:
        kind = tags(e).get("railway")
        if e["type"] == "way" and kind == "subway":
            v.dashed(v.pts(e["geometry"]), METRO, 2.2, 9, 6)
        elif e["type"] == "way" and kind in ("tram", "light_rail"):
            v.dashed(v.pts(e["geometry"]), TRAM, 2.2, 9, 6)


def landmarks(v, els, names):
    """Highlight these named buildings; every footprint first, then the labels on top."""
    spots = []
    for e in els:
        name = e.get("tags", {}).get("name")
        if name in names and "building" in e.get("tags", {}):
            rings = areas([e], lambda t: True)
            if not rings:
                continue
            for ring in rings:
                v.polygon(ring, "#CFA56A", "#8A6A2F", 1)
            pts = v.pts(max(rings, key=len))
            spots.append(((sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)),
                          names[name]))
    for xy, label in spots:
        v.label(xy, label, 10.5, "#5B3A29", "bold", halo="#F4E4C2")


def stations(v, els, keep=None):
    seen = set()
    for e in els:
        t = e.get("tags", {})
        if e["type"] != "node" or t.get("railway") != "station" or "name" not in t:
            continue
        name = t["name"].split("/")[0]
        if name in seen or (keep and name not in keep):
            continue
        x, y = v.xy(e["lat"], e["lon"])
        if not v.inside((x, y), -20 * SS):
            continue
        seen.add(name)
        r = 8 * SS
        v.d.ellipse((x - r, y - r, x + r, y + r), fill=METRO, outline="white", width=SS)
        v.d.text((x, y), "M", font=font("bold", 10), fill="white", anchor="mm")
        v.label((x, y + 17 * SS), name, 10, METRO, "bold", halo="#FFFAF0", force=True)


def draw_centre():
    v = View("centre")
    v.img.paste(BLOCK, (0, 0, W * SS, H * SS))
    els = load("centre")
    draw_streets(v, els, {"living_street": 3.5, "pedestrian": 4.0, "residential": 4.2,
                          "unclassified": 4.2, "tertiary": 5.5, "tertiary_link": 3.0,
                          "secondary": 7.0, "secondary_link": 3.5, "primary": 8.5,
                          "primary_link": 4.0, "trunk": 9.0, "busway": 3.5})
    landmarks(v, els, {"Catedral Metropolitana de la Ciudad de México": "Catedral",
                       "Palacio de Bellas Artes": "Bellas Artes",
                       "Casa de los Azulejos": "Casa de los Azulejos",
                       "Antiguo Colegio de San Ildefonso": "San Ildefonso",
                       "Palacio Postal": "Correo Mayor", "Torre Latinoamericana": "Torre Latino"})
    v.label(v.xy(19.43265, -99.13319), "ZÓCALO", 12, "#8A6A2F", "bold", halo=PLAZA, spacing=1)
    v.label(v.xy(19.43260, -99.13080), "Palacio Nacional", 10.5, "#5B3A29", "bold", halo="#F4E4C2")
    v.label(v.xy(19.43520, -99.13140), "Templo Mayor", 10.5, "#5B3A29", "bold", halo="#F4E4C2")
    v.label(v.xy(19.43590, -99.14530), "Alameda Central", 11, "#3C6B33", "italic", halo=PARK)
    stations(v, els)
    road_label_spots(v, els, ("primary", "secondary", "tertiary", "residential", "pedestrian"),
                     60, 9.5)
    credit(v)
    v.save(ART / "map_centre.png")
    return v


def draw_coyoacan():
    v = View("coyoacan")
    v.img.paste(BLOCK, (0, 0, W * SS, H * SS))
    els = load("coyoacan")
    draw_streets(v, els, {"residential": 1.0, "unclassified": 1.0, "living_street": 1.0,
                          "pedestrian": 1.2, "tertiary": 1.8, "secondary": 2.6,
                          "secondary_link": 1.4, "primary": 3.4, "primary_link": 1.6,
                          "trunk": 4.2, "trunk_link": 1.8, "motorway": 4.6,
                          "motorway_link": 2.0})
    for name, lat, lon, size, colour, halo in [
            ("COYOACÁN", 19.3500, -99.1590, 12, "#8A6A2F", BLOCK),
            ("CIUDAD UNIVERSITARIA", 19.3210, -99.1840, 12, "#8A6A2F", UNIVERSITY),
            ("COPILCO", 19.3420, -99.1800, 10, "#8A7A55", BLOCK),
            ("SAN ÁNGEL", 19.3470, -99.1940, 10, "#8A7A55", BLOCK),
            ("PEDREGAL", 19.3080, -99.2040, 10, "#8A7A55", BLOCK),
            ("Reserva del Pedregal", 19.3120, -99.1900, 9.5, "#3C6B33", PARK)]:
        v.label(v.xy(lat, lon), name, size, colour, "bold" if name.isupper() else "italic",
                halo=halo, spacing=1 if name.isupper() and size >= 12 else 0)
    stations(v, els, {"Coyoacán", "Viveros-Derechos Humanos", "Miguel Ángel de Quevedo",
                      "Copilco", "Universidad"})
    road_label_spots(v, els, ("trunk", "primary", "secondary"), 16, 9)
    credit(v)
    v.save(ART / "map_coyoacan.png")
    return v


# ----------------------------------------------------------------------- pins

def make_pins():
    content = json.loads((ROOT / "game/data/content.json").read_text(encoding="utf-8"))
    size = 112
    for loc in content["locations"]:
        src = ART / f"cdmx_{loc['id']}.png"
        if not src.exists():
            continue
        img = Image.open(src).convert("RGB")
        side = img.width
        top = int(img.height * 0.14)
        crop = img.crop((0, top, side, top + side)).resize((size * 2, size * 2), Image.LANCZOS)
        mask = Image.new("L", (size * 2, size * 2), 0)
        ImageDraw.Draw(mask).ellipse((2, 2, size * 2 - 3, size * 2 - 3), fill=255)
        pin = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
        pin.paste(crop, (0, 0), mask)
        pin.resize((size, size), Image.LANCZOS).save(ART / f"pin_{loc['id']}.png")
    print(f"pins: {len(content['locations'])}")


def main():
    city = draw_city()
    close = {"centre": draw_centre(), "coyoacan": draw_coyoacan()}
    make_pins()
    # where each close-up sits on the city view, for its "zoom in" frame
    zooms = []
    for name, title, caption in ZOOMS:
        z = close[name]
        half_w = W / 2 / z.scale / KX
        half_h = H / 2 / z.scale / KY
        x0, y0 = city.xy(z.lat0 + half_h, z.lon0 - half_w)
        x1, y1 = city.xy(z.lat0 - half_h, z.lon0 + half_w)
        rect = [x0 / SS, y0 / SS, (x1 - x0) / SS, (y1 - y0) / SS]
        zooms.append({"view": name, "name": title, "caption": caption, "rect": rect})
        print(f"{name} frame on city:", [round(n) for n in rect])
    out = {"kx": KX, "ky": KY, "size": [W, H], "views": VIEWS, "zooms": zooms}
    (ROOT / "game/data/map.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("maps written")


if __name__ == "__main__":
    main()
