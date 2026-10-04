"""Recast a character whose voice is wrong: throw away their recordings and make
candidate voices to choose from by ear.

    python -X utf8 tools/recast.py WHO                 # discard WHO's lines, audition candidates
    python -X utf8 tools/recast.py WHO --pick B2       # lock candidate B2 as WHO's voice

Candidates come from the descriptions listed for WHO in content/recast.json (each
voiced with a random seed and with seed 4242) and land in
samples/<who>_candidatos/. Their ids are kept in samples/candidatos.json. After
--pick, run tools/tts_generate.py to record WHO's lines in the new voice.
"""

import json
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tts_generate as tts
from local_config import get

ROOT = pathlib.Path(__file__).resolve().parent.parent
STUDIO = pathlib.Path(get("studio_projects"))     # qwen-tts-studio's projects folder
CANDIDATES = ROOT / "samples" / "candidatos.json"


def discard(who, state):
    manifest = json.loads(tts.MANIFEST.read_text(encoding="utf-8"))
    ids = [l["id"] for l in manifest if l["who"] == who]
    gone = 0
    for i in ids:
        wav = tts.OUT / f"{i}.wav"
        if wav.exists():
            wav.unlink()
            gone += 1
        (ROOT / "game" / "audio" / "voice" / f"{i}.ogg").unlink(missing_ok=True)
        state["rows"].pop(i, None)
    state["chars"].pop(who, None)
    tts.save_state(state)
    print(f"{who}: {len(ids)} lines, {gone} recordings discarded")


def audition(who, state):
    cast = json.loads(tts.CAST.read_text(encoding="utf-8"))
    specs = json.loads((ROOT / "content" / "recast.json").read_text(encoding="utf-8"))[who]
    out = ROOT / "samples" / f"{who.lower()}_candidatos"
    out.mkdir(parents=True, exist_ok=True)
    cand = json.loads(CANDIDATES.read_text(encoding="utf-8")) if CANDIDATES.exists() else {}
    cand[who] = {}
    slug = state["slug"]
    for k, spec in zip("ABCDE", specs):
        for n, seed in enumerate([None, 4242], 1):
            ch = tts.call(f"/api/projects/{slug}/characters",
                          {"name": f"{who}_{k}{n}", "source": "design", "design_instruct": spec})
            body = {"text": cast[who]["ref"], "language": tts.LANG}
            if seed:
                body["seed"] = seed
            aud = tts.call(f"/api/projects/{slug}/characters/{ch['id']}/audition", body)["audition"]
            shutil.copy(STUDIO / slug / aud["file"], out / f"{k}{n}.wav")
            cand[who][f"{k}{n}"] = [ch["id"], aud["id"], spec]
            print(f"  {k}{n}")
    CANDIDATES.write_text(json.dumps(cand, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"candidates in {out}")


def pick(who, label, state):
    cast = json.loads(tts.CAST.read_text(encoding="utf-8"))
    entry = json.loads(CANDIDATES.read_text(encoding="utf-8"))[who][label]
    char_id, aud_id = entry[:2]
    spec = entry[2] if len(entry) > 2 else None
    tts.call(f"/api/projects/{state['slug']}/characters/{char_id}/lock",
             {"audition_id": aud_id, "ref_text": cast[who]["ref"]})
    state["chars"][who] = char_id
    tts.save_state(state)
    # keep the description in the cast, so a rebuild from scratch casts the same kind of voice
    if spec:
        cast[who]["voice"] = spec
    tts.CAST.write_text(json.dumps(cast, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.copy(ROOT / "samples" / f"{who.lower()}_candidatos" / f"{label}.wav",
                ROOT / "samples" / "reparto" / f"{who}.wav")
    print(f"{who} is now {label}")


def main():
    who = sys.argv[1]
    state = tts.load_state()
    if "--pick" in sys.argv:
        pick(who, sys.argv[sys.argv.index("--pick") + 1], state)
    else:
        discard(who, state)
        audition(who, state)


if __name__ == "__main__":
    main()
