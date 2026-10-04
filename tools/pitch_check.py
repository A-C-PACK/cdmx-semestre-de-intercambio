"""Find voice lines that drifted away from their character's voice: each line is
cloned from one locked reference clip, but now and then a take wanders (a
woman's line comes out in a man's voice, or the reverse).

    python -X utf8 tools/pitch_check.py              # every speaker
    python -X utf8 tools/pitch_check.py YO           # one speaker
    python -X utf8 tools/pitch_check.py --ids        # print only the flagged ids, comma-separated
    python -X utf8 tools/pitch_check.py --all        # also list lines merely higher/lower than usual

Each line's pitch is compared with the character's reference clip
(samples/reparto/<WHO>.wav, the clip the voice was cloned from). A line is
flagged when its median pitch is far from the reference's, or when far more of
it sits in the other register (below 165 Hz for a high voice, above 165 Hz for
a low one). Pitch cannot hear accents: those still need a human ear.
"""

import json
import pathlib
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import find_peaks

ROOT = pathlib.Path(__file__).resolve().parent.parent
VOICE = ROOT / "audio_src" / "voice"
REFS = ROOT / "samples" / "reparto"
MANIFEST = ROOT / "tools" / "tts_manifest.json"
CAST = ROOT / "content" / "cast.json"
SPLIT = 165.0          # Hz: roughly where typical men's and women's speaking pitch part


def frame_pitches(path):
    """Pitch in Hz of every clearly voiced 40 ms frame (autocorrelation)."""
    rate, data = wavfile.read(path)
    if data.ndim > 1:
        data = data.mean(axis=1)
    data = data.astype(np.float64)
    data /= np.max(np.abs(data)) or 1.0
    frame, hop = int(0.04 * rate), int(0.01 * rate)
    lo, hi = int(rate / 400), int(rate / 70)
    quiet = 0.3 * np.sqrt(np.mean(data ** 2))
    out = []
    for start in range(0, len(data) - frame, hop):
        x = data[start:start + frame]
        if np.sqrt(np.mean(x ** 2)) < quiet:
            continue
        x = x - x.mean()
        ac = np.correlate(x, x, "full")[frame - 1:]
        if ac[0] <= 0:
            continue
        seg = ac[lo:hi] / ac[0]
        peaks, _ = find_peaks(seg)
        if not len(peaks) or seg[peaks].max() < 0.45:
            continue
        # the shortest lag whose peak is nearly as strong as the best one, so a
        # multiple of the true period is not mistaken for it
        lag = lo + peaks[np.argmax(seg[peaks] >= 0.9 * seg[peaks].max())]
        out.append(rate / lag)
    return np.array(out)


def profile(path):
    f = frame_pitches(path)
    if len(f) < 10:
        return None
    return float(np.median(f)), float((f < SPLIT).mean())


def is_male(spec):
    """From the cast's voice description ("a Mexican man…", "una joven mexicana…")."""
    text = " " + spec["voice"].lower().replace(",", " ") + " "
    female = any(w in text for w in (" woman ", " female ", " mujer ", " mexicana ",
                                      " femenina ", " policewoman ", " girl ", " waitress "))
    return not female and spec.get("gender", "o") != "a"


def check(who, lines, male):
    ref = profile(REFS / f"{who}.wav")
    if ref is None:
        return []
    ref_f0, ref_low = ref
    low_voice = male
    flagged = []
    for line in lines:
        wav = VOICE / f"{line['id']}.wav"
        if not wav.exists():
            continue
        got = profile(wav)
        if got is None:
            continue
        f0, low = got
        # Only drift toward the other register counts: an excited line in the same
        # voice can come out higher (or a calm one lower) without being wrong.
        if low_voice:
            drifted = f0 > max(ref_f0 * 1.30, 200) or (1 - low) - (1 - ref_low) > 0.35
        else:
            drifted = f0 < ref_f0 * 0.85 or low - ref_low > 0.12
        if drifted or ("--all" in sys.argv and abs(f0 - ref_f0) / ref_f0 > 0.22):
            flagged.append((line, f0, low))
    return ref_f0, flagged


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cast = json.loads(CAST.read_text(encoding="utf-8"))
    by_who = {}
    for line in manifest:
        if not args or line["who"] in args:
            by_who.setdefault(line["who"], []).append(line)
    ids = []
    for who, lines in sorted(by_who.items()):
        result = check(who, lines, is_male(cast[who]))
        if not result:
            continue
        ref_f0, flagged = result
        ids += [l["id"] for l, _, _ in flagged]
        if "--ids" in sys.argv:
            continue
        print(f"{who:<11} {len(lines):>3} lines, reference {ref_f0:5.0f} Hz"
              + (f", {len(flagged)} off" if flagged else ""))
        for line, f0, low in flagged:
            print(f"    {line['id']}  {f0:5.0f} Hz  {low:4.0%} low   {line['text'][:60]}")
    print(",".join(ids) if "--ids" in sys.argv else f"{len(ids)} lines flagged")


if __name__ == "__main__":
    main()
