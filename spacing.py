"""Spacing worked out from the drawn outlines: vowel-mark anchors and kerning.

Both read each glyph's ink, so they follow any change to the drawings.

Anchors: every letter gets a point above its top and below its bottom; the
vowel marks hang from those points (and from each other, for shadda + vowel).

Kerning: for a pair of letters, the gap between their ink is measured in thin
horizontal bands. A pair that collides is pushed apart. A pair whose closest
point is clearly further apart than ordinary spacing (To, AV, را) is pulled
part of the way in; round letters next to each other (oo) are left alone,
because their closest point is already normal. The pulls are capped, so
Kurdish letters that do not join never look joined.
"""
import statistics

import pathops

BAND = 40
YS = range(-600, 1760, BAND)
MARK_GAP = 70              # air between a letter and a vowel mark

TOP_MARKS = ('fatha', 'fathatan', 'damma', 'dammatan', 'shadda', 'sukun',
             'alef_above', 'madda_above', 'hamza_above')
BOTTOM_MARKS = ('kasra', 'kasratan', 'hamza_below')


def _path(glyphset, name):
    p = pathops.Path()
    glyphset[name].draw(p.getPen())
    return p


def _bounds(p):
    try:
        return p.bounds
    except Exception:
        return None


def ink(font):
    """Per glyph: advance, bounds, and the ink's left and right edge in each band."""
    gs = font.getGlyphSet()
    hmtx = font['hmtx']
    data = {}
    for name in font.getGlyphOrder():
        p = _path(gs, name)
        bounds = _bounds(p) if list(p.contours) else None
        rows = {}
        if bounds:
            for y in YS:
                if y + BAND < bounds[1] or y > bounds[3]:
                    continue
                band = pathops.Path()
                band.moveTo(bounds[0] - 10, y)
                band.lineTo(bounds[2] + 10, y)
                band.lineTo(bounds[2] + 10, y + BAND)
                band.lineTo(bounds[0] - 10, y + BAND)
                band.close()
                cut = pathops.op(p, band, pathops.PathOp.INTERSECTION)
                b = _bounds(cut) if list(cut.contours) else None
                if b:
                    rows[y] = (b[0], b[2])
        data[name] = (hmtx[name][0], bounds, rows)
    return data


# --- vowel marks -----------------------------------------------------------

def _centre(rows, lo, hi):
    """The middle of the ink between heights lo and hi (None if there is none)."""
    edges = [r for y, r in rows.items() if y + BAND >= lo and y <= hi]
    if not edges:
        return None
    return (min(e[0] for e in edges) + max(e[1] for e in edges)) / 2


def mark_features(data, marks):
    top = [m for m in TOP_MARKS if m in marks]
    bottom = [m for m in BOTTOM_MARKS if m in marks]
    lines = []
    for m in top:
        b = data[m][1]
        lines.append(f'markClass {m} <anchor {round((b[0] + b[2]) / 2)} {round(b[1] - MARK_GAP)}> @TOP;')
    for m in bottom:
        b = data[m][1]
        lines.append(f'markClass {m} <anchor {round((b[0] + b[2]) / 2)} {round(b[3] + MARK_GAP)}> @BOTTOM;')
    bases = []
    for name, (_, b, rows) in data.items():
        if b is None or name in marks:
            continue
        # a mark sits over the top of the letter (its tooth, loop or stem), not over the middle of
        # its ink box, which a long joining stroke pulls sideways; below, it hangs from the
        # lowest part when the letter reaches under the line, else under the same spot
        above = _centre(rows, b[3] - 0.35 * max(b[3], 1), b[3]) or (b[0] + b[2]) / 2
        below = (_centre(rows, b[1], b[1] * 0.65) if b[1] < -60 else None) or above
        bases.append(f'    pos base {name} <anchor {round(above)} {round(b[3])}> mark @TOP '
                     f'<anchor {round(below)} {round(b[1])}> mark @BOTTOM;')
    lines += ['feature mark {', *bases, '} mark;']
    # a vowel written with shadda sits on top of the shadda
    stack = []
    for m in top:
        b = data[m][1]
        stack.append(f'    pos mark {m} <anchor {round((b[0] + b[2]) / 2)} {round(b[3])}> mark @TOP;')
    lines += ['feature mkmk {', *stack, '} mkmk;']
    return '\n'.join(lines)


# --- kerning -----------------------------------------------------------------

def _gaps(data, a, b, rtl):
    """The gap between a's ink and b's ink in every band where both have some.

    b's edge is taken over the band and its neighbours, so a diagonal stroke
    cannot slip through between two bands.
    """
    adv_a, _, rows_a = data[a]
    adv_b, _, rows_b = data[b]
    gaps = []
    for y, (a_left, a_right) in rows_a.items():
        near = [rows_b[v] for v in (y - BAND, y, y + BAND) if v in rows_b]
        if not near:
            continue
        b_left = min(r[0] for r in near)
        b_right = max(r[1] for r in near)
        # rtl: a sits on the right, b on its left; ltr: a on the left
        gaps.append(a_left + (adv_b - b_right) if rtl else (adv_a - a_right) + b_left)
    return gaps


# how each script is kerned: a pair is loose when its closest point is more than
# ref * loose apart; it is pulled `share` of the way back to ref, at most `most`;
# smaller kerns are dropped
LTR = dict(least=60, loose=1.4, share=0.7, most=200, smallest=30)
RTL = dict(least=90, loose=1.4, share=0.5, most=90, smallest=25)


def _kern(data, a, b, rtl, ref, least, loose, share, most, smallest):
    gaps = _gaps(data, a, b, rtl)
    if not gaps:
        return 0
    closest = min(gaps)
    if closest < least:
        return round(least - closest)                    # they touch: push apart
    if closest <= ref * loose:
        return 0
    pull = max((ref - closest) * share, -most, least - closest)   # never closer than `least`
    return round(pull) if pull <= -smallest else 0


def kern_features(data, latin, latin_marks, arabic_first, arabic_second, arabic_ends, arabic_marks):
    """latin: Latin letters; latin_marks: punctuation that follows them.
    arabic_first: right-joining letters (a gap always follows them inside a word);
    arabic_second: letters that can start a new piece after them;
    arabic_ends: letters that can end a word (alone or end forms), before arabic_marks."""
    # ordinary spacing: two straight stems side by side
    ltr_ref = min(_gaps(data, 'n', 'n', False))
    rtl_ref = min(_gaps(data, 'alef', 'alef', True))
    ltr, rtl = [], []
    for a in latin:
        for b in latin + latin_marks:
            k = _kern(data, a, b, False, ltr_ref, **LTR)
            if k:
                ltr.append(f'    pos {a} {b} {k};')
    for a in arabic_first:
        for b in arabic_second:
            k = _kern(data, a, b, True, rtl_ref, **RTL)
            if k:
                rtl.append(f'    pos {a} {b} <{k} 0 {k} 0>;')
    for a in arabic_ends:
        for b in arabic_marks:
            k = _kern(data, a, b, True, rtl_ref, **dict(RTL, least=60))
            if k:
                rtl.append(f'    pos {a} {b} <{k} 0 {k} 0>;')
    # in right-to-left text the first glyph sits on the right: moving it (placement)
    # and its advance together brings the pair closer without shifting the rest of the line
    return ('\n'.join(['feature kern {', '    lookupflag IgnoreMarks;', *ltr, *rtl, '} kern;']),
            len(ltr), len(rtl))
