"""Build the RegaFonts families (by RegaLabs): Rega Type, Rega Aso, Rega Payam.

    python build.py [out_dir] [--family "Rega Aso"|all] [--weight Regular|Bold|...|all] [--dots round|square|diamond] [--install DIR]

Needs Python 3.10+ with fonttools, skia-pathops, brotli and ttfautohint-py.
Every outline comes from glyphs.py, signs.py and latin.py, written with the
family's pen from skeleton.py: RegaLabs' own drawings, owned by RegaLabs.
"""
import argparse
import importlib
import io
import os
import sys
import unicodedata

import ttfautohint
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.misc.timeTools import timestampNow
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

import skeleton
import spacing

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, 'dist')
VERSION = '0.300'
UPM = 2048
# Same line box as the font the site's layouts were tuned on, so nothing moves.
ASC, DESC, WIN_DESC = 1955, 1040, 1000
RIBBI = ('Regular', 'Bold')
# older file names that apps already load
ALIASES = {('Rega Type', 'Regular'): ['rega-type-reg']}


def draw(path):
    pen = TTGlyphPen(None)
    path.draw(Cu2QuPen(pen, max_err=1.0, reverse_direction=False))
    return pen.glyph()


def empty():
    return TTGlyphPen(None).glyph()


def notdef():
    pen = TTGlyphPen(None)
    for box in (((80, 0), (80, 1400), (900, 1400), (900, 0)),
                ((200, 120), (780, 120), (780, 1280), (200, 1280))):
        pen.moveTo(box[0])
        for pt in box[1:]:
            pen.lineTo(pt)
        pen.closePath()
    return pen.glyph()


def features(font):
    lines = ['languagesystem DFLT dflt;', 'languagesystem arab dflt;', 'languagesystem latn dflt;']
    for form in ('init', 'medi', 'fina'):
        subs = [f'    sub {base} by {forms[form]};'
                for base, forms in glyphs.FORMS.items()
                if form in forms and base in glyphs.GLYPHS]
        lines += [f'feature {form} {{', *subs, f'}} {form};']
    ligs = [f'    sub {" ".join(parts)} by {lig};' for parts, lig in glyphs.LIGATURES]
    lines += ['feature rlig {', *ligs, '} rlig;']
    # marks are classed as marks, so they keep zero width and attach to the letter before them
    bases = [g for g in font.getGlyphOrder() if g not in glyphs.MARKS and g != '.notdef']
    lines.append(f'table GDEF {{ GlyphClassDef [{" ".join(bases)}], , [{" ".join(sorted(glyphs.MARKS))}], ; }} GDEF;')

    data = spacing.ink(font)
    lines.append(spacing.mark_features(data, glyphs.MARKS))
    kern, n_ltr, n_rtl = spacing.kern_features(data, *kerning_sets())
    lines.append(kern)
    print(f'  {skeleton.FAMILY} {skeleton.WEIGHT}: {n_ltr} Latin and {n_rtl} Kurdish/Arabic kerning pairs')
    return '\n'.join(lines)


def kerning_sets():
    """Which glyphs take part in kerning (see spacing.kern_features)."""
    latin = list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
    latin_marks = ['period', 'comma', 'colon', 'semicolon', 'hyphen', 'quoteright',
                   'quotedblright', 'exclam', 'question', 'parenright']
    letters = {g for c, g in glyphs.CMAP.items()
               if 0x0600 <= c <= 0x06FF and unicodedata.category(chr(c)) == 'Lo'}
    letters |= {g for g in glyphs.GLYPHS if g.startswith('lam_') and 'alef' in g and '.' not in g}
    forms = lambda g: glyphs.FORMS.get(g, {})
    right_joining = sorted(g for g in letters if 'init' not in forms(g))
    first = [n for g in right_joining for n in (g, forms(g).get('fina')) if n]
    second = sorted({n for g in letters for n in (g, forms(g).get('init')) if n})
    ends = sorted({n for g in letters for n in (g, forms(g).get('fina')) if n})
    arabic_marks = ['period', 'comma_ar', 'colon', 'question_ar', 'exclam', 'semicolon_ar']
    return latin, latin_marks, first, second, ends, arabic_marks


def names(family, weight):
    """Name records. Regular and Bold sit in the family itself; any other weight
    is its own small family ("Rega Aso Light") so every app can tell them apart."""
    ps = f'{family.replace(" ", "")}-{weight}'
    ribbi = weight in RIBBI
    rec = {
        'copyright': 'Copyright 2026 RegaLabs (https://regalabs.dev). All rights reserved.',
        'familyName': family if ribbi else f'{family} {weight}',
        'styleName': weight if ribbi else 'Regular',
        'uniqueFontIdentifier': f'{VERSION};REGA;{ps}',
        'fullName': f'{family} {weight}',
        'version': f'Version {VERSION}',
        'psName': ps,
        'manufacturer': 'RegaLabs',
        'designer': 'RegaLabs',
        'vendorURL': 'https://regalabs.dev',
        'designerURL': 'https://regalabs.dev',
    }
    if not ribbi:
        rec.update(typographicFamily=family, typographicSubfamily=weight)
    return rec


def build(dot_style):
    family, weight = skeleton.FAMILY, skeleton.WEIGHT
    stretch = skeleton.STRETCH
    dot_size = skeleton.DOT - 2 * skeleton.SOFT   # ink width of a dot; the outline step grows it by SOFT
    order = ['.notdef', 'space', 'zwnj', 'zwj', 'bidi', *glyphs.GLYPHS]
    shapes = {'.notdef': notdef(), 'space': empty(), 'zwnj': empty(), 'zwj': empty(), 'bidi': empty()}
    metrics = {'.notdef': (980, 80), 'space': (round(640 * stretch), 0), 'zwnj': (0, 0), 'zwj': (0, 0), 'bidi': (0, 0)}
    # Latin, English digits and symbols keep Latin proportions (see skeleton.place)
    latin = {g for c, g in glyphs.CMAP.items() if c < 0x0600 or c >= 0x2000}
    for name, fn in glyphs.GLYPHS.items():
        adv, lines, dots = fn()
        is_latin = name in latin
        if skeleton.KASHIDA and name.endswith(('.init', '.medi')):
            adv, lines, dots = skeleton.lengthen(adv, lines, dots)
        # a dot is (x, y), or (x, y, ink width) for a solid disc of its own size (٠, •);
        # the family's proportions move the dots but keep their size. Latin letters and
        # punctuation keep round dots whatever shape the Kurdish dots take
        style = 'round' if is_latin and dot_style == 'soft' else dot_style
        discs = [skeleton.dot(*skeleton.place(d[0], d[1], is_latin), d[2] - 2 * skeleton.SOFT, 'round')
                 if len(d) > 2 else skeleton.dot(*skeleton.place(d[0], d[1], is_latin), dot_size, style)
                 for d in dots]
        path = skeleton.outline(lines, discs, adv=adv, latin=is_latin)
        adv *= stretch * (skeleton.LATIN if is_latin else 1)
        if skeleton.XSCALE != 1:
            path = path.transform(scaleX=skeleton.XSCALE)   # Bold is a little wider
            adv *= skeleton.XSCALE
        shapes[name] = draw(path)
        metrics[name] = (round(adv), 0)

    cmap = {0x20: 'space', 0xA0: 'space', 0x200C: 'zwnj', 0x200D: 'zwj', **glyphs.CMAP}
    # invisible direction controls get an empty glyph, so the browser never looks for them in another font
    cmap.update({c: 'bidi' for c in (0x061C, 0x200E, 0x200F, *range(0x202A, 0x202F), *range(0x2066, 0x206A), 0xFEFF)})

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(shapes)
    glyf = fb.font['glyf']
    fb.setupHorizontalMetrics({n: (adv, glyf[n].xMin if hasattr(glyf[n], 'xMin') else 0)
                               for n, (adv, _) in metrics.items()})
    fb.setupHorizontalHeader(ascent=ASC, descent=-DESC)
    fb.setupNameTable(names(family, weight))
    fb.setupOS2(sTypoAscender=ASC, sTypoDescender=-DESC, sTypoLineGap=0,
                usWinAscent=ASC, usWinDescent=WIN_DESC, achVendID='REGA',
                usWeightClass=skeleton.CLASS, fsSelection=(1 << 5) if weight == 'Bold' else (1 << 6), fsType=0,
                sxHeight=800, sCapHeight=1430)
    fb.setupPost()
    fb.setupHead(unitsPerEm=UPM, fontRevision=float(VERSION), created=timestampNow(), modified=timestampNow(),
                 macStyle=1 if weight == 'Bold' else 0)
    addOpenTypeFeaturesFromString(fb.font, features(fb.font))
    return fb.font


def stems(family, weight):
    """File names: Rega_Aso-Light, rega-aso-light, and any older names apps still load."""
    primary = f'{family.replace(" ", "_")}-{weight}'
    return [primary, primary.lower().replace('_', '-'), *ALIASES.get((family, weight), [])]


def load_letters():
    """Import the letter modules afresh: they read the pen's sizes once, when imported."""
    global glyphs
    for name in ('glyphs', 'signs', 'latin'):
        sys.modules.pop(name, None)
    glyphs = importlib.import_module('glyphs')
    importlib.import_module('latin')    # registers the Latin letters (and, through signs, the digits and symbols)
    importlib.import_module('signs')


def make(family, weight, out, dots, install):
    skeleton.set_style(family, weight)
    load_letters()
    font = build(dots or skeleton.DOTS)

    raw = io.BytesIO()
    font.save(raw)
    # hinting snaps stems to the pixel grid, so 14-16px text stays crisp on Windows
    hinted = ttfautohint.ttfautohint(in_buffer=raw.getvalue(), default_script='arab', no_info=True)
    woff = TTFont(io.BytesIO(hinted))
    woff.flavor = 'woff2'
    buf = io.BytesIO()
    woff.save(buf)
    woff2 = buf.getvalue()

    targets = [(out, 'ttf', hinted), (out, 'woff2', woff2)]
    if os.path.abspath(out) == DIST:
        # a release build also refreshes fonts/ttf and fonts/woff2; a trial build elsewhere does not
        targets += [(os.path.join(HERE, 'fonts', 'ttf'), 'ttf', hinted),
                    (os.path.join(HERE, 'fonts', 'woff2'), 'woff2', woff2)]
    names_ = stems(family, weight)
    for folder, ext, data in targets:
        os.makedirs(folder, exist_ok=True)
        for stem in names_:
            with open(os.path.join(folder, f'{stem}.{ext}'), 'wb') as f:
                f.write(data)

    print(f'{names_[0]}.ttf (and aliases)  {len(woff.getGlyphOrder())} glyphs, hinted')
    if install:
        os.makedirs(install, exist_ok=True)
        for stem in names_:
            dest = os.path.join(install, f'{stem}.woff2')
            with open(dest, 'wb') as f:
                f.write(woff2)
            print(f'  installed {dest}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out', nargs='?', default=DIST)
    ap.add_argument('--family', choices=(*skeleton.FAMILIES, 'all'), default='all')
    ap.add_argument('--weight', default='all')
    ap.add_argument('--dots', choices=('round', 'soft', 'square', 'diamond'), help="override the family's dot shape")
    ap.add_argument('--install', metavar='DIR', help="also copy the .woff2 files into this folder (an app's fonts)")
    args = ap.parse_args()
    todo = [(family, weight)
            for family, spec in skeleton.FAMILIES.items() if args.family in ('all', family)
            for weight in spec['weights'] if args.weight in ('all', weight)]
    if not todo:
        sys.exit(f'{args.family} has no {args.weight} weight')
    for family, weight in todo:
        make(family, weight, args.out, args.dots, args.install)

if __name__ == '__main__':
    main()
