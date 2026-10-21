"""Compare every RegaFonts outline with other fonts, character by character.

    python checks/provenance.py <folder of other fonts> [our font_dir]     (default: dist)

Prints how many outlines are identical (point for point, any drawing order). An
original font has 0. Copying a font, even renamed, gives near 100%.
"""
import glob
import os
import sys

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont


def shapes(path):
    f = TTFont(path)
    gs = f.getGlyphSet()
    out = {}
    for code, name in f.getBestCmap().items():
        pen = DecomposingRecordingPen(gs)
        gs[name].draw(pen)
        if pen.value:
            # the point set, ignoring drawing order
            out[code] = sorted(p for _, pts in pen.value for p in pts if p is not None)
    return out


others = sys.argv[1]
ours_dir = sys.argv[2] if len(sys.argv) > 2 else 'dist'
refs = {os.path.basename(p): shapes(p) for p in glob.glob(os.path.join(others, '*.[ot]tf'))}
total = 0
for ours in sorted(glob.glob(os.path.join(ours_dir, 'Rega_*.ttf'))):
    mine = shapes(ours)
    shared = sum(1 for r in refs.values() for c in mine if c in r)
    same = sum(1 for r in refs.values() for c, pts in mine.items() if r.get(c) == pts)
    total += same
    print(f'{os.path.basename(ours):26} characters compared: {shared:5}   identical outlines: {same}')
print(f'{len(refs)} other font files. TOTAL identical outlines: {total}')
sys.exit(1 if total else 0)
