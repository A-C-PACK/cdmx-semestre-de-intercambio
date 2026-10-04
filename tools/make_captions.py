"""Write one Ideogram caption per location illustration into art/captions/.

Every scene shares one style block so all the places read as one set.
No text elements: signage rendered by the model would be uncontrolled Spanish
sitting next to carefully levelled Spanish, so the scenes stay wordless.

    python tools/make_captions.py
"""

import json
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "art" / "captions"

PALETTE = ["#F6E7C8", "#E8A33D", "#D9622B", "#B8402A", "#2E6F8E", "#7FC4D6",
           "#3F7D4E", "#F2C9A0", "#5B3A29", "#FFFFFF", "#1F3A4D", "#C2477A"]

STYLE = {
    "aesthetics": "Warm, inviting vintage travel-poster illustration of Mexico City; "
                  "simple confident shapes, gentle grain, uncluttered composition, "
                  "no lettering, no signs with words, no captions, no user interface.",
    "lighting": "Bright high-altitude sunlight with soft warm shadows.",
    "medium": "Gouache painting.",
    "art_style": "Mid-century gouache travel poster with flat layered shapes, visible "
                 "brush texture and a limited warm palette.",
    "color_palette": PALETTE,
}

# id: (high level, background, [(bbox, desc, palette), ...])   bbox = [y0, x0, y1, x1]
SCENES = {
    "title": (
        "A tall travel-poster view of Mexico City at golden hour: the white marble Palacio de "
        "Bellas Artes with its orange and gold domes in the foreground, jacaranda trees in "
        "purple bloom, and the two snow-capped volcanoes on the horizon.",
        "A wide glowing sky fading from pale gold near the horizon to soft teal at the top, "
        "above a city of low buildings with two distant snow-capped volcanoes.",
        [([300, 150, 760, 850], "The Palacio de Bellas Artes, a white marble palace with a large "
          "central dome tiled in orange and gold and smaller domes at the corners, seen from the "
          "front.", ["#FFFFFF", "#E8A33D", "#D9622B"]),
         ([160, 0, 360, 1000], "Two distant volcanoes with snowy peaks on the horizon, one a "
          "perfect cone and one long and low.", ["#7FC4D6", "#FFFFFF", "#2E6F8E"]),
         ([740, 0, 1000, 1000], "Foreground jacaranda trees covered in purple blossom framing "
          "the bottom of the picture.", ["#C2477A", "#3F7D4E", "#5B3A29"]),
         ([60, 100, 240, 900], "A few small dark birds wheeling in the open sky.", ["#1F3A4D"])]),
    "aeropuerto": (
        "The taxi rank outside a large modern airport terminal in Mexico City on a sunny "
        "afternoon, with a friendly older taxi driver waiting beside his white and pink taxi.",
        "A long glass-and-steel terminal building under a clear blue sky, with a covered "
        "walkway along the kerb and distant hills.",
        [([430, 60, 900, 740], "A white four-door saloon taxi with bright pink doors parked at "
          "the kerb, seen exactly side-on, every door shut flush with the body, door "
          "handles visible, windows up, nobody touching the car.", ["#FFFFFF", "#C2477A", "#1F3A4D"]),
         ([360, 660, 920, 920], "A man of about sixty-five with grey hair and a grey moustache, a "
          "short-sleeved shirt and a warm smiling face, standing on the pavement a step away "
          "from the closed taxi, with one hand raised in greeting.", ["#F2C9A0", "#F6E7C8", "#5B3A29"]),
         ([760, 260, 960, 520], "Two rolling suitcases standing on the pavement in the "
          "foreground.", ["#B8402A", "#2E6F8E"]),
         ([100, 0, 420, 1000], "The terminal building's long glass facade and roof.",
          ["#7FC4D6", "#E9D3A1"])]),
    "casa": (
        "The front of a charming family house on a quiet street in Coyoacán, Mexico City, with a "
        "warm smiling woman of about fifty opening a green door, bougainvillea spilling over the "
        "wall.",
        "A quiet cobbled street of low colourful houses under a clear sky, with a tree casting "
        "soft shade.",
        [([180, 100, 900, 900], "A two-storey house painted terracotta with a green wooden front "
          "door and a small wrought-iron balcony.", ["#D9622B", "#3F7D4E", "#5B3A29"]),
         ([380, 380, 880, 640], "A woman of about fifty with dark hair tied back and a colourful "
          "embroidered blouse, standing in the doorway with her arms open in welcome.",
          ["#F2C9A0", "#FFFFFF", "#C2477A"]),
         ([100, 0, 520, 380], "Bright magenta bougainvillea cascading over the top of the wall.",
          ["#C2477A", "#3F7D4E"]),
         ([800, 620, 980, 900], "A small friendly brown dog sitting on the pavement.",
          ["#5B3A29", "#E8A33D"])]),
    "tiendita": (
        "A small neighbourhood corner shop in Mexico City with a cheerful shopkeeper in his "
        "sixties behind the counter, shelves of colourful snacks and drinks behind him.",
        "The open front of a little shop on a street corner, its walls painted bright yellow, "
        "with a hand-painted awning and no readable words.",
        [([300, 300, 700, 700], "A cheerful round-faced man of about sixty-five with grey hair, "
          "glasses and an apron over a checked shirt, leaning on the counter and smiling.",
          ["#F2C9A0", "#2E6F8E", "#FFFFFF"]),
         ([0, 0, 560, 1000], "Shelves packed with colourful bottles of soft drinks, bags of "
          "crisps, loaves of bread and sweets, with no readable labels.", ["#B8402A", "#E8A33D", "#2E6F8E"]),
         ([620, 50, 900, 950], "A wooden counter with a glass jar of sweets and a small basket "
          "of bread rolls.", ["#5B3A29", "#E9D3A1"]),
         ([560, 820, 960, 1000], "Stacked crates of glass bottles beside the counter.",
          ["#3F7D4E", "#E9D3A1"])]),
    "metro": (
        "A busy Mexico City metro platform with an orange train arriving and a few passengers "
        "waiting, including an elderly lady with a shopping bag.",
        "A long underground station with a curved pale ceiling, tiled walls and a yellow line "
        "along the platform edge.",
        [([320, 0, 760, 620], "An orange metro train with rounded front and large windows "
          "pulling in along the platform.", ["#D9622B", "#E8A33D", "#1F3A4D"]),
         ([380, 640, 900, 860], "An elderly woman of about seventy-five with grey hair in a bun, "
          "a cardigan and a woven market bag, smiling kindly.", ["#F2C9A0", "#C2477A", "#5B3A29"]),
         ([420, 860, 840, 1000], "A young person with a backpack looking at a colourful metro "
          "map made of coloured lines and round icons, with no readable words.",
          ["#2E6F8E", "#3F7D4E"]),
         ([760, 0, 1000, 1000], "The platform floor with a bold yellow safety stripe.",
          ["#E9D3A1", "#E8A33D"])]),
    "zocalo": (
        "The vast Zócalo square of Mexico City on a bright day with a giant Mexican flag on a "
        "tall pole, the grey stone Metropolitan Cathedral with its bell towers, and a friendly "
        "police officer in a vest.",
        "A huge open paved square under a deep blue sky, with low colonial buildings around it.",
        [([80, 300, 700, 1000], "The Metropolitan Cathedral, a huge grey stone Baroque church with "
          "two tall bell-shaped towers and a central dome.", ["#E9D3A1", "#5B3A29", "#F6E7C8"]),
         ([40, 40, 640, 300], "A very tall flagpole with an enormous green, white and red flag "
          "flying in the wind, with no emblem visible.", ["#3F7D4E", "#FFFFFF", "#B8402A"]),
         ([620, 160, 800, 260], "In the middle distance, a small figure of a woman police "
          "officer in a dark uniform, a bright yellow-green vest and a cap, pointing the way, the "
          "same size as the other people in the square and far smaller than the cathedral.",
          ["#1F3A4D", "#E8A33D", "#F2C9A0"]),
         ([780, 380, 1000, 1000], "People strolling across the square, small in the distance.",
          ["#C2477A", "#2E6F8E", "#D9622B"])]),
    "cu": (
        "The Central Library of the UNAM university in Mexico City, a tall windowless block "
        "covered with colourful stone mosaics, with students on the green lawn in front.",
        "A wide green lawn and pale paved plaza under a clear blue sky, with volcanic stone "
        "walls.",
        [([60, 250, 720, 750], "A tall rectangular library tower whose four walls are covered in "
          "a mosaic of coloured stones in ochre, red, blue and green forming abstract figures and "
          "symbols, with a band of windows at its base.", ["#E8A33D", "#B8402A", "#2E6F8E"]),
         ([620, 40, 960, 420], "A cheerful young woman of about twenty-two with long dark hair "
          "and a denim jacket, waving with a folder under her arm.", ["#F2C9A0", "#2E6F8E", "#5B3A29"]),
         ([720, 0, 1000, 1000], "A wide lawn with students sitting on the grass with books.",
          ["#3F7D4E", "#E9D3A1"]),
         ([600, 700, 900, 1000], "A dark volcanic stone wall with a few small cacti.",
          ["#5B3A29", "#3F7D4E"])]),
    "mercado": (
        "A fruit stall inside a traditional Mexican market in Coyoacán, piled high with mangoes, "
        "papayas, limes and chilies, with a lively woman vendor holding out a slice of mango.",
        "The busy interior of a market hall with strings of colourful papel picado bunting "
        "overhead and piñatas hanging in the distance.",
        [([520, 0, 1000, 1000], "A generous market stall with sloping crates of yellow mangoes, "
          "orange papayas cut in half, green limes, red chilies and tomatoes.",
          ["#E8A33D", "#D9622B", "#3F7D4E"]),
         ([280, 320, 640, 680], "A lively woman of about fifty-five with dark curly hair and a "
          "flowered apron behind the stall, smiling and holding out a slice of mango on a knife.",
          ["#F2C9A0", "#C2477A", "#E8A33D"]),
         ([0, 0, 260, 1000], "Strings of colourful cut-paper bunting crossing under the roof.",
          ["#C2477A", "#2E6F8E", "#E8A33D"]),
         ([260, 0, 520, 300], "Colourful star-shaped piñatas hanging at a neighbouring stall.",
          ["#C2477A", "#E8A33D", "#3F7D4E"])]),
    "taqueria": (
        "A lively Mexico City taco stand at night, with a taco cook slicing meat from a vertical "
        "spit of al pastor pork topped with a pineapple, and young friends eating tacos at the "
        "counter.",
        "A warm glowing taquería open to a night street, with string lights and a dark blue "
        "night sky.",
        [([200, 380, 760, 700], "A tall vertical spit of red marinated pork with a pineapple on "
          "top, glowing in front of a heater.", ["#B8402A", "#E8A33D", "#D9622B"]),
         ([180, 640, 760, 960], "A cheerful fair-haired taco cook of about thirty-five in a white "
          "apron and cap, slicing meat with a long knife.", ["#FFFFFF", "#F2C9A0", "#E8A33D"]),
         ([560, 0, 960, 520], "Two young friends at the counter laughing, holding small tacos "
          "on paper plates.", ["#2E6F8E", "#3F7D4E", "#F2C9A0"]),
         ([800, 400, 1000, 1000], "A counter with bowls of red and green salsa, chopped onion, "
          "coriander and lime halves.", ["#B8402A", "#3F7D4E", "#FFFFFF"])]),
    "farmacia": (
        "The inside of a tidy Mexican pharmacy with a calm woman pharmacist in a white coat at "
        "the counter.",
        "Clean white shelves lined with small plain boxes and bottles behind the counter, and a "
        "door to a small doctor's office at the side.",
        [([260, 320, 700, 690], "A woman pharmacist of about forty-five with shoulder-length dark "
          "hair and an open white coat, standing upright behind the counter, looking straight at "
          "the viewer with open eyes and a warm reassuring smile.", ["#FFFFFF", "#F2C9A0", "#5B3A29"]),
         ([600, 60, 880, 940], "A pale counter with a small paper bag and a bottle of "
          "rehydration drink.", ["#F6E7C8", "#7FC4D6"]),
         ([60, 720, 260, 900], "A glowing green pharmacy cross sign on the wall.",
          ["#3F7D4E", "#FFFFFF"]),
         ([0, 0, 560, 1000], "Tall white shelving with neat rows of small coloured boxes.",
          ["#FFFFFF", "#7FC4D6", "#E8A33D"])]),
    "xochimilco": (
        "Brightly painted flat-bottomed trajinera boats on a green canal in Xochimilco, Mexico "
        "City, with a boatman pushing a long pole and a small canoe selling corn alongside.",
        "A calm green canal lined with tall trees and willows under a bright sky, with more "
        "colourful boats in the distance.",
        [([300, 0, 760, 1000], "A long flat boat with a wooden roof and a front arch painted in "
          "bright red, yellow, blue and pink flowers, with no letters.", ["#B8402A", "#E8A33D", "#C2477A"]),
         ([200, 700, 780, 940], "A friendly boatman of about forty-five in a straw hat standing "
          "at the back of the boat, pushing a long wooden pole into the water.",
          ["#F2C9A0", "#E9D3A1", "#5B3A29"]),
         ([680, 0, 960, 420], "A small wooden canoe with an older woman in a shawl selling "
          "corn on the cob from a steaming pot.", ["#5B3A29", "#E8A33D", "#C2477A"]),
         ([760, 0, 1000, 1000], "Calm green water with reflections.", ["#3F7D4E", "#7FC4D6"])]),
    "jamaica": (
        "A flower stall in Mexico City's Jamaica market piled with bright orange marigolds and "
        "purple cockscomb flowers for the Day of the Dead, with a smiling florist.",
        "The colourful interior of a big flower market, full of buckets of flowers and hanging "
        "papel picado bunting.",
        [([440, 0, 1000, 1000], "Huge bundles of bright orange cempasúchil marigolds and deep "
          "purple cockscomb flowers in buckets.", ["#E8A33D", "#D9622B", "#C2477A"]),
         ([200, 340, 640, 700], "A good-natured man of about fifty-five with a moustache and a "
          "cap, holding out a big bunch of orange marigolds and smiling.",
          ["#F2C9A0", "#2E6F8E", "#E8A33D"]),
         ([0, 0, 220, 1000], "Strings of colourful cut-paper bunting overhead.",
          ["#C2477A", "#E8A33D", "#2E6F8E"]),
         ([220, 0, 520, 300], "A small sugar skull decorated with coloured icing on a shelf.",
          ["#FFFFFF", "#C2477A", "#2E6F8E"])]),
    "garibaldi": (
        "Plaza Garibaldi in Mexico City at night, with a mariachi band in black charro suits "
        "with silver buttons and wide sombreros playing trumpets and violins.",
        "A warm-lit night square with colonial buildings and glowing lamps under a deep blue "
        "night sky.",
        [([200, 100, 860, 900], "A group of five mariachi musicians in black charro suits with "
          "silver buttons and wide sombreros, playing violins, trumpets and a big guitar.",
          ["#1F3A4D", "#E9D3A1", "#FFFFFF"]),
         ([300, 380, 760, 620], "The lead singer, a proud man of about fifty-five with a "
          "moustache, singing with one arm raised.", ["#1F3A4D", "#F2C9A0", "#B8402A"]),
         ([0, 0, 240, 1000], "A deep blue night sky with a few stars and a warm glow from the "
          "lamps.", ["#1F3A4D", "#E8A33D"]),
         ([820, 0, 1000, 1000], "The paved square with people watching.", ["#5B3A29", "#C2477A"])]),
    "cuicuilco": (
        "The round stepped pyramid of Cuicuilco in Mexico City, a wide circular platform of "
        "grey stone and earth among dry grass, black volcanic rock and pepper trees.",
        "A clear blue sky and, far away, a low dark volcanic hill.",
        [([300, 50, 760, 950], "A very wide low circular pyramid of grey stone in several round "
          "tiers, like a truncated cone, with a ramp up one side.", ["#E9D3A1", "#5B3A29", "#F6E7C8"]),
         ([120, 500, 320, 900], "A low dark volcanic hill on the horizon.", ["#5B3A29", "#2E6F8E"]),
         ([760, 0, 1000, 1000], "Black jagged volcanic rock with dry yellow grass and small "
          "succulent plants.", ["#1F3A4D", "#E8A33D", "#3F7D4E"]),
         ([450, 820, 800, 1000], "A feathery pepper tree.", ["#3F7D4E", "#5B3A29"])]),
    "teotihuacan": (
        "The great Pyramid of the Sun at Teotihuacan seen from the long Avenue of the Dead, "
        "with the Pyramid of the Moon in the distance and dry hills under a vast blue sky.",
        "A vast blue sky with a few white clouds over a dry valley and distant hills.",
        [([200, 300, 800, 1000], "A huge stepped stone pyramid with a long staircase, warm grey "
          "and ochre stone.", ["#E9D3A1", "#5B3A29", "#D9622B"]),
         ([380, 0, 700, 320], "A smaller stepped pyramid at the far end of a long straight "
          "avenue.", ["#E9D3A1", "#5B3A29"]),
         ([700, 0, 1000, 1000], "A long wide stone avenue lined with low platforms, with a few "
          "tiny walking figures.", ["#F6E7C8", "#E8A33D", "#5B3A29"]),
         ([780, 0, 1000, 220], "Prickly pear cacti in the foreground.", ["#3F7D4E", "#C2477A"])]),
    "templo_mayor": (
        "The excavated ruins of the Templo Mayor in Mexico City: layered stone walls and "
        "staircases of the Aztec temple, carved serpent heads, and a metal walkway, with the "
        "cathedral towers behind.",
        "A bright sky above old colonial buildings and the bell towers of a grey stone cathedral.",
        [([300, 0, 900, 1000], "Excavated stone ruins with several nested layers of walls and "
          "staircases of grey and reddish volcanic stone.", ["#5B3A29", "#B8402A", "#E9D3A1"]),
         ([620, 380, 860, 640], "A large carved stone serpent head with an open mouth at the foot "
          "of a staircase.", ["#E9D3A1", "#5B3A29"]),
         ([60, 600, 420, 1000], "The bell towers of a grey stone cathedral behind the ruins.",
          ["#E9D3A1", "#5B3A29"]),
         ([440, 0, 600, 1000], "A metal walkway with railings crossing above the ruins, with a "
          "few small visitors.", ["#1F3A4D", "#2E6F8E"])]),
    "tlatelolco": (
        "The Plaza of the Three Cultures in Mexico City: Aztec stone ruins in the foreground, "
        "a grey colonial stone church in the middle, and 1960s modernist apartment blocks and "
        "a tower behind.",
        "A clear blue sky over a wide plaza.",
        [([500, 0, 1000, 1000], "Low excavated stepped stone platforms and walls of an Aztec "
          "temple.", ["#E9D3A1", "#5B3A29", "#B8402A"]),
         ([200, 250, 700, 750], "A sturdy grey stone colonial church with a single bell tower "
          "and a dome.", ["#E9D3A1", "#5B3A29", "#F6E7C8"]),
         ([80, 0, 520, 300], "A tall modernist tower of concrete and glass.", ["#7FC4D6", "#E9D3A1"]),
         ([120, 720, 500, 1000], "Long 1960s apartment blocks with rows of windows.",
          ["#F6E7C8", "#2E6F8E"])]),
    "guadalupe": (
        "The Basilica of Guadalupe in Mexico City with crowds of pilgrims, the modern round "
        "basilica with its sweeping green roof beside the leaning old baroque basilica, and the "
        "Tepeyac hill behind.",
        "A clear sky over a green hill with small chapels on its slope.",
        [([280, 0, 700, 560], "A huge modern round church with a sweeping steep green copper "
          "roof and a tall cross.", ["#3F7D4E", "#E9D3A1", "#FFFFFF"]),
         ([240, 520, 720, 1000], "An old baroque church with a tiled dome and four towers, "
          "leaning slightly.", ["#E9D3A1", "#E8A33D", "#5B3A29"]),
         ([660, 0, 1000, 1000], "A wide plaza full of pilgrims carrying red roses and flowers.",
          ["#B8402A", "#C2477A", "#2E6F8E"]),
         ([60, 300, 300, 1000], "A green hill with small white chapels.", ["#3F7D4E", "#FFFFFF"])]),
    "catedral": (
        "The interior of the Metropolitan Cathedral of Mexico City, a vast stone nave with a "
        "golden baroque altarpiece and a pendulum hanging from the dome.",
        "Tall grey stone columns and vaults in soft light.",
        [([200, 250, 800, 750], "A towering golden baroque altarpiece full of carved columns, "
          "saints and gold leaf.", ["#E8A33D", "#D9622B", "#5B3A29"]),
         ([0, 0, 1000, 220], "Tall grey stone columns and arches.", ["#E9D3A1", "#5B3A29"]),
         ([0, 780, 1000, 1000], "Tall grey stone columns and arches.", ["#E9D3A1", "#5B3A29"]),
         ([480, 440, 880, 560], "A long thin cable hanging from above ending in a metal "
          "pendulum weight just above a round drawing on the stone floor.",
          ["#1F3A4D", "#E9D3A1"])]),
    "chapultepec": (
        "Chapultepec Castle on top of its wooded hill in Mexico City, seen from below through "
        "the trees of the park, with a boating lake in the foreground.",
        "A clear blue sky over a forested hill.",
        [([80, 150, 460, 900], "A pale neoclassical castle with terraces, arches and a small "
          "round tower on top of a hill.", ["#F6E7C8", "#E9D3A1", "#2E6F8E"]),
         ([380, 0, 760, 1000], "Thick green forest of tall cypress and ash trees on the hill.",
          ["#3F7D4E", "#5B3A29"]),
         ([740, 0, 1000, 1000], "A calm lake with small rowing boats and families.",
          ["#7FC4D6", "#2E6F8E", "#C2477A"]),
         ([620, 680, 900, 960], "A young man in a hoodie holding a leaflet and pointing up at the "
          "castle.", ["#3F7D4E", "#F2C9A0", "#1F3A4D"])]),
    "bellas_artes": (
        "The Palacio de Bellas Artes in Mexico City seen from the Alameda park, a white marble "
        "palace with domes tiled in orange and gold.",
        "A bright sky above, with tall modern buildings in the distance.",
        [([150, 100, 780, 900], "A grand white marble palace with a large central dome tiled in "
          "orange and gold, smaller domes and sculpted figures on the facade.",
          ["#FFFFFF", "#E8A33D", "#D9622B"]),
         ([740, 0, 1000, 1000], "A park with fountains and trees and people sitting on benches.",
          ["#3F7D4E", "#7FC4D6", "#E9D3A1"]),
         ([300, 0, 760, 160], "Purple jacaranda trees in bloom.", ["#C2477A", "#3F7D4E"]),
         ([300, 840, 760, 1000], "Purple jacaranda trees in bloom.", ["#C2477A", "#3F7D4E"])]),
    "casa_azul": (
        "The courtyard of the Blue House in Coyoacán, Mexico City, where Frida Kahlo lived: "
        "cobalt-blue walls with red trim, tropical plants, and a small stepped pyramid with "
        "clay figures.",
        "A bright sky above intensely cobalt-blue walls.",
        [([100, 0, 700, 1000], "Intense cobalt-blue walls with red-brown window frames and "
          "green shutters.", ["#2E6F8E", "#B8402A", "#3F7D4E"]),
         ([500, 300, 900, 700], "A small stepped pyramid in the garden with pre-Hispanic clay "
          "figures on its steps.", ["#D9622B", "#5B3A29"]),
         ([400, 0, 1000, 300], "Big tropical plants, cacti and a palm.", ["#3F7D4E", "#E8A33D"]),
         ([780, 600, 1000, 1000], "Pots of red geraniums along a path.", ["#B8402A", "#3F7D4E"])]),
    "ciudad_universitaria": (
        "The Olympic Stadium of the UNAM university in Mexico City, a low curved stadium of "
        "volcanic stone with a colourful stone relief on its facade, under a vast blue sky.",
        "A vast blue sky with a few white clouds over dark volcanic rock and green trees.",
        [([280, 0, 760, 1000], "A wide low curved stadium built of dark volcanic stone, like a "
          "crater, with a colourful stone mosaic relief of figures and an eagle on its outer "
          "wall, with no letters.", ["#5B3A29", "#E8A33D", "#B8402A"]),
         ([740, 0, 1000, 1000], "Dark volcanic rock with succulents and dry grass in the "
          "foreground.", ["#1F3A4D", "#3F7D4E", "#E8A33D"]),
         ([600, 600, 900, 900], "A few students walking with backpacks.",
          ["#2E6F8E", "#C2477A", "#F2C9A0"]),
         ([60, 600, 280, 1000], "Distant mountains.", ["#7FC4D6", "#2E6F8E"])]),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (high, background, elements) in SCENES.items():
        caption = {
            "high_level_description": high,
            "style_description": STYLE,
            "compositional_deconstruction": {
                "background": background,
                "elements": [{"type": "obj", "bbox": b, "desc": d, "color_palette": p}
                             for b, d, p in elements],
            },
        }
        (OUT / f"cdmx_{name}.json").write_text(
            json.dumps(caption, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(SCENES)} captions to {OUT}")


if __name__ == "__main__":
    main()
