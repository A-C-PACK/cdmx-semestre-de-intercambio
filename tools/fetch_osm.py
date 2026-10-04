"""Download the OpenStreetMap data the map is drawn from into tools/osm/.

    python -X utf8 tools/fetch_osm.py           # fetch whatever is missing
    python -X utf8 tools/fetch_osm.py --force   # fetch again

One-off: the game itself never goes online. Data (c) OpenStreetMap contributors,
ODbL. Public Overpass servers are often busy, so each query is tried on several
mirrors in turn.
"""

import json
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

OUT = pathlib.Path(__file__).resolve().parent / "osm"
MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]
AGENT = "CDMXSpanishGame/1.0 (personal offline language-learning project)"

# south, west, north, east -- a little wider than what each view shows
CITY = "19.240,-99.300,19.505,-98.990"
CENTRE = "19.4280,-99.1480,19.4450,-99.1250"
COYOACAN = "19.2900,-99.2200,19.3700,-99.1300"

QUERIES = {
    "city": f"""[out:json][timeout:120][bbox:{CITY}];
(
  way["highway"~"^(motorway|trunk|primary|motorway_link|trunk_link)$"];
  way["aeroway"="aerodrome"];
  way["landuse"="cemetery"];
  way["amenity"="university"]["name"~"Ciudad Universitaria|Universidad Nacional"];
  relation["amenity"="university"]["name"~"Ciudad Universitaria|Universidad Nacional"];
  way["leisure"~"^(park|garden)$"];
  relation["leisure"~"^(park|garden)$"];
  way["natural"="water"];
  relation["natural"="water"];
  way["railway"~"^(subway|tram|light_rail)$"];
  node["railway"~"^(station|tram_stop)$"];
  node["place"~"^(suburb|neighbourhood|quarter)$"];
  relation["boundary"="administrative"]["admin_level"="6"];
  way["waterway"="canal"];
);
out geom;""",
    "centre": f"""[out:json][timeout:120][bbox:{CENTRE}];
(
  way["highway"]["highway"!~"^(footway|steps|cycleway|path|service|construction|proposed|corridor|elevator)$"];
  way["highway"="footway"]["area"="yes"];
  way["highway"="pedestrian"];
  relation["highway"="pedestrian"];
  way["leisure"~"^(park|garden)$"];
  relation["leisure"~"^(park|garden)$"];
  way["building"]["name"];
  relation["building"]["name"];
  way["railway"~"^(subway|tram|light_rail)$"];
  node["railway"~"^(station|tram_stop)$"];
);
out geom;""",
    "coyoacan": f"""[out:json][timeout:180][bbox:{COYOACAN}];
(
  way["highway"~"^(motorway|trunk|primary|secondary|tertiary|residential|unclassified|living_street|pedestrian|motorway_link|trunk_link|primary_link|secondary_link)$"];
  way["leisure"~"^(park|garden|stadium|pitch)$"];
  relation["leisure"~"^(park|garden)$"];
  way["landuse"~"^(grass|forest|recreation_ground)$"];
  way["natural"~"^(wood|scrub|bare_rock)$"];
  relation["natural"~"^(wood|scrub)$"];
  way["amenity"="university"];
  relation["amenity"="university"];
  way["building"]["name"];
  way["railway"~"^(subway|tram|light_rail)$"];
  node["railway"~"^(station|tram_stop)$"];
);
out geom;""",
    # exact positions for the pins, looked up by name rather than trusted from memory
    "places": f"""[out:json][timeout:60][bbox:{CITY}];
(
  nwr["name"~"^(Zócalo|Plaza de la Constitución)$"];
  nwr["name"~"^(Templo Mayor|Museo del Templo Mayor)$"];
  nwr["name"~"^Catedral Metropolitana"];
  nwr["name"~"^Palacio Nacional$"];
  nwr["name"~"^(Palacio de Bellas Artes)$"];
  nwr["name"~"^Plaza Garibaldi$"];
  nwr["name"~"^(Plaza de las Tres Culturas)$"];
  nwr["name"~"^(Mercado de Coyoacán|Mercado de Jamaica|Mercado Jamaica)"];
  nwr["name"~"^(Jardín Centenario|Jardín Hidalgo|Museo Frida Kahlo|Museo Casa de León Trotsky)"];
  nwr["name"~"^(Biblioteca Central|Centro de Enseñanza para Extranjeros|Estadio Olímpico Universitario)"];
  nwr["name"~"^(Castillo de Chapultepec|Museo Nacional de Antropología)"];
  nwr["name"~"Cuicuilco"];
  nwr["name"~"^(Basílica de (Santa María de )?Guadalupe|Insigne y Nacional Basílica)"];
  nwr["name"~"Embarcadero"];
  node["railway"="station"]["name"~"^(Zócalo|Hidalgo|Coyoacán|Viveros|Universidad|Copilco|Bellas Artes|Garibaldi|Jamaica|Terminal Aérea|Xochimilco)"];
  nwr["aeroway"="terminal"]["name"~"Terminal 1|Terminal 2"];
);
out center tags;""",
}


def fetch(name, query):
    body = urllib.parse.urlencode({"data": query}).encode("utf-8")
    for attempt in range(3):
        for url in MIRRORS:
            req = urllib.request.Request(url, data=body, headers={"User-Agent": AGENT})
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    raw = r.read()
                data = json.loads(raw.decode("utf-8"))
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
                print(f"  {name}: {url.split('/')[2]} failed ({str(exc)[:70]})", flush=True)
                continue
            if data.get("elements"):
                (OUT / f"{name}.json").write_bytes(raw)
                print(f"  {name}: {len(data['elements'])} elements, {len(raw) // 1024} KB "
                      f"from {url.split('/')[2]}", flush=True)
                return True
            print(f"  {name}: {url.split('/')[2]} returned nothing "
                  f"({data.get('remark', '')[:70]})", flush=True)
        time.sleep(20)
    return False


def main():
    OUT.mkdir(exist_ok=True)
    ok = True
    for name, query in QUERIES.items():
        if (OUT / f"{name}.json").exists() and "--force" not in sys.argv:
            print(f"  {name}: already downloaded")
            continue
        ok = fetch(name, query) and ok
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
