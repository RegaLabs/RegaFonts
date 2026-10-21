"""Shape every Sorani letter alone, at the start, middle and end of a word, plus real text, in every font.

    python checks/shape_check.py [font_dir]      (default: dist)

Fails if any letter falls back to .notdef, misses its joining form, the لا ligature
is missing, or vowel marks are not positioned.
"""
import glob
import os
import sys

import uharfbuzz as hb

LETTERS = 'ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنوۆهھەیێ'
DUAL = set('ئبپتجچحخسشعغفڤقکگلڵمنهھیێ')     # letters that join on both sides
TEXT = ['کوردستان', 'لاوەکان', 'ڵا', 'سڵاو', 'بەخێربێن', 'هەڵبژاردن', 'گەنجینە', 'ئێمە',
        'اَلْعَرَبِيَّة', 'مُحَمَّد', 'ژیان', 'ڤیان', 'قوتابخانە', '٠١٢٣٤٥٦٧٨٩', 'RegaLabs 2026']


def shape(font, text):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {'kern': True, 'liga': True})
    return [font.glyph_to_string(i.codepoint) for i in buf.glyph_infos], buf.glyph_positions


bad = 0
folder = sys.argv[1] if len(sys.argv) > 1 else 'dist'
for path in sorted(glob.glob(folder + '/*.ttf')):
    if not any(s in path for s in ('Rega_Type-', 'Rega_Aso-', 'Rega_Payam-')):
        continue
    blob = hb.Blob.from_file_path(path)
    font = hb.Font(hb.Face(blob))
    problems = []
    for ch in LETTERS:
        cases = {'isol': ch, 'fina': 'ب' + ch}
        if ch in DUAL:
            cases.update(init=ch + 'ب', medi='ب' + ch + 'ب')
        for form, text in cases.items():
            names, _ = shape(font, text)
            if '.notdef' in names:
                problems.append(f'{ch} {form}: notdef')
            # in RTL output the glyph order is visual (left to right): the letter is
            # last for init, first for fina, in the middle for medi
            idx = {'isol': 0, 'init': -1, 'fina': 0, 'medi': 1}[form]
            g = names[idx]
            if form != 'isol' and not g.endswith('.' + form) and not g.startswith('lam_'):
                problems.append(f'{ch} {form}: got {g}')
    for t in TEXT:
        names, pos = shape(font, t)
        if '.notdef' in names:
            problems.append(f'{t}: notdef {names}')
    lam_alef, _ = shape(font, 'لا')
    if not any(n.startswith('lam_alef') for n in lam_alef):
        problems.append(f'لا ligature missing: {lam_alef}')
    marks, pos = shape(font, 'بَ')
    if pos[0].x_offset == 0 and pos[0].y_offset == 0 and pos[1].x_offset == 0 and pos[1].y_offset == 0:
        problems.append('fatha not positioned by the mark feature')
    bad += len(problems)
    print(f"{os.path.basename(path):28} {'OK' if not problems else 'PROBLEMS: ' + '; '.join(problems[:6])}")
sys.exit(1 if bad else 0)
