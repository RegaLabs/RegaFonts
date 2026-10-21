"""Rega Type digits, punctuation and symbols, in the same monoline pen as the letters.

Kurdish digits ٠-٩ (and the Persian code points, which share them), English
digits 0-9, the punctuation used in Kurdish and English text, and the few
symbols the apps use (… · • → © ...).
"""
from glyphs import BASE, CMAP, HH, HV, MARK_W, SOFT, letter
from skeleton import W_H, W_V, Line, ellipse, ox, oy, poly

# Pens heavier than Rega Type Bold (Rega Payam Bold): symbols built from strokes
# side by side (« " =) get more room, so the strokes never run together
HEAVY = W_V > 262

AR_TOP = 1268 - SOFT     # Kurdish digits
LAT_TOP = 1440           # English digits (outer top; round ones overshoot it a little)
ROUND_CY, ROUND_RY = 720, oy(650)   # centre line of a full-height round English digit
DOT_Y = 114              # a dot sitting on the baseline (., :, !, ?)
MARK = dict(w=MARK_W)


def mirror(fn, adv):
    """The same glyph turned right-for-left (؟ from ?)."""
    def mirrored():
        _, lines, dots = fn()
        for line in lines:
            line.path = line.path.transform(scaleX=-1, translateX=adv)
        return adv, lines, [(adv - x, y) for x, y in dots]
    return mirrored


# Kurdish digits ٠-٩

@letter('zero_ar', 0x0660)
def zero_ar():
    # a solid round disc, a little bigger in Bold
    return 633, [], [(316, 404, 320 + 2 * HV - 174)]


@letter('one_ar', 0x0661)
def one_ar():
    return 553, [Line(276, SOFT).to(276, AR_TOP)], []


ARM_Y = 1040             # the arm of ٢ and ٣


@letter('two_ar', 0x0662)
def two_ar():
    x = 250
    return 948, [poly([(x, SOFT), (x, ARM_Y), (x + 440, ARM_Y), (x + 440, AR_TOP)], r=[170, 90])], []


@letter('three_ar', 0x0663)
def three_ar():
    x, step = 230, 315
    return 1033, [poly([(x, SOFT), (x, ARM_Y), (x + step, ARM_Y), (x + step, AR_TOP)], r=[170, 80]),
                  poly([(x + step, ARM_Y), (x + 2 * step, ARM_Y), (x + 2 * step, AR_TOP)], r=[0, 80])], []


@letter('four_ar', 0x0664)
def four_ar():
    # a small c over a larger one, both open to the right
    head = Line(700, 1150).arc(470, 1010, ox(245), oy(215), 35, 270)
    body = (Line(470, 795).curve(250, 795, 150, 640, 150, 450)
            .curve(150, 190, 340, BASE, 590, BASE).to(780, BASE))
    return 838, [head, body], []


@letter('five_ar', 0x0665)
def five_ar():
    return 1033, [ellipse(516, 618, ox(345), oy(534))], []


@letter('six_ar', 0x0666)
def six_ar():
    x = 690
    return 885, [poly([(180, 1120), (x, AR_TOP), (x, SOFT)], r=[0, 200])], []


@letter('seven_ar', 0x0667)
def seven_ar():
    return 922, [poly([(130, AR_TOP), (461, SOFT + 40), (792, AR_TOP)], r=70)], []


@letter('eight_ar', 0x0668)
def eight_ar():
    return 922, [poly([(130, SOFT), (461, AR_TOP - 40), (792, SOFT)], r=70)], []


@letter('nine_ar', 0x0669)
def nine_ar():
    xs, rx, ry, cy = 730, ox(260), oy(240), 990
    return 922, [ellipse(xs - rx, cy, rx, ry), Line(xs, cy).to(xs, SOFT)], []


for i, name in enumerate(('zero_ar', 'one_ar', 'two_ar', 'three_ar', 'four_ar',
                          'five_ar', 'six_ar', 'seven_ar', 'eight_ar', 'nine_ar')):
    CMAP[0x06F0 + i] = name   # Persian digits share the Kurdish shapes


# English digits 0-9 (all 1139 wide, so columns of numbers line up)

DW = 1139


@letter('zero', 0x30)
def zero():
    return DW, [ellipse(570, ROUND_CY, ox(383), ROUND_RY)], []


@letter('one', 0x31)
def one():
    return DW, [poly([(300, 1150), (650, LAT_TOP - SOFT), (650, SOFT)], r=[40])], []


@letter('two', 0x32)
def two():
    line = (Line(205, 1150).arc(570, 1040, 380, 384, 163, -35)
            .to(175, BASE).to(1000 - SOFT, BASE))
    return DW, [line], []


@letter('three', 0x33)
def three():
    top = Line(210, 1250).arc(560, 1095, 350, 345, 154, -90)
    bottom = Line(560, 750).arc(560, 405, 420, 345, 90, -150)
    return DW, [top, bottom], []


@letter('four', 0x34)
def four():
    return DW, [poly([(800, SOFT), (800, LAT_TOP - SOFT), (120, 470), (1060 - SOFT, 470)], r=[60, 40])], []


@letter('five', 0x35)
def five():
    line = (poly([(990, LAT_TOP - HH), (290, LAT_TOP - HH), (250, 820)], r=[60])
            .curve(420, 900, 990, 870, 990, 450)
            .curve(990, 110, 720, 70, 560, 70)
            .curve(380, 70, 210, 130, 140, 260))
    return DW, [line], []


@letter('six', 0x36)
def six():
    loop = ellipse(570, 460, ox(400), oy(390))
    rise = Line(170, 460).to(170, 760).curve(170, 1200, 470, 1356, 880, 1356)
    return DW, [loop, rise], []


@letter('seven', 0x37)
def seven():
    return DW, [poly([(140, LAT_TOP - HH), (1000, LAT_TOP - HH), (430, SOFT)], r=[60])], []


@letter('eight', 0x38)
def eight():
    return DW, [ellipse(570, 1090, ox(340), oy(290)), ellipse(570, 445, ox(400), oy(375))], []


@letter('nine', 0x39)
def nine():
    loop = ellipse(570, 980, ox(400), oy(390))
    fall = Line(970, 980).to(970, 680).curve(970, 240, 670, 70, 260, 70)
    return DW, [loop, fall], []


# Punctuation

@letter('period', 0x2E)
def period():
    return 569, [], [(284, DOT_Y)]


@letter('comma', 0x2C)
def comma():
    tail = Line(330, 110, **MARK).curve(330, -60, 280, -180, 190, -270)
    return 569, [tail], [(284, DOT_Y)]


@letter('colon', 0x3A)
def colon():
    return 569, [], [(284, DOT_Y), (284, 760)]


@letter('semicolon', 0x3B)
def semicolon():
    _, tail, _ = comma()
    return 569, tail, [(284, DOT_Y), (284, 760)]


@letter('exclam', 0x21)
def exclam():
    return 530, [Line(265, 440).to(265, 1446 - SOFT)], [(265, DOT_Y)]


@letter('question', 0x3F)
def question():
    hook = Line(190, 1170).arc(570, 1100, 380, 330, 160, -60).curve(620, 760, 570, 700, 570, 450)
    return 1139, [hook], [(570, DOT_Y)]


letter('question_ar', 0x061F)(mirror(question, 1176))


@letter('comma_ar', 0x060C)
def comma_ar():
    # the Kurdish comma: a dot with its tail turned upward
    tail = Line(300, 120, **MARK).curve(300, 280, 340, 400, 430, 500)
    return 709, [tail], [(330, DOT_Y)]


@letter('semicolon_ar', 0x061B)
def semicolon_ar():
    tail = Line(300, 600, **MARK).curve(300, 760, 340, 880, 430, 980)
    return 705, [tail], [(330, DOT_Y), (330, 594)]


@letter('decimal_ar', 0x066B)
def decimal_ar():
    return 420, [Line(250, 380, **MARK).to(170, SOFT + 40)], []


@letter('thousands_ar', 0x066C)
def thousands_ar():
    return 420, [Line(250, 560, **MARK).to(170, 240)], []


@letter('percent_ar', 0x066A)
def percent_ar():
    return 1233, [Line(1020, 1200).to(210, 60)], [(330, 1000), (900, 270)]


@letter('percent', 0x25)
def percent():
    return 1560, [ellipse(400, 1090, 190, 260), ellipse(1160, 350, 190, 260),
                  Line(1150, LAT_TOP - SOFT).to(410, SOFT)], []


@letter('parenleft', 0x28)
def parenleft():
    return 530, [Line(470, 1480).curve(250, 1210, 200, 900, 200, 545).curve(200, 190, 250, -120, 470, -390)], []


letter('parenright', 0x29)(mirror(parenleft, 530))


@letter('bracketleft', 0x5B)
def bracketleft():
    return 530, [poly([(470, 1480), (200, 1480), (200, -390), (470, -390)], r=0)], []


letter('bracketright', 0x5D)(mirror(bracketleft, 530))


def _chevron(x, w=300, h=330):
    return poly([(x + w, 528 + h), (x, 528), (x + w, 528 - h)], r=40)


GUILLEMET_STEP = round(1.5 * W_V + 90) if HEAVY else 380    # from one chevron to the next
GUILLEMET_ADV = 1139 + GUILLEMET_STEP - 380


@letter('guillemetleft', 0xAB)
def guillemetleft():
    return GUILLEMET_ADV, [_chevron(180), _chevron(180 + GUILLEMET_STEP)], []


letter('guillemetright', 0xBB)(mirror(guillemetleft, GUILLEMET_ADV))


@letter('hyphen', 0x2D)
def hyphen():
    return 797, [Line(130, 570).to(667, 570)], []


@letter('endash', 0x2013)
def endash():
    return 1024, [Line(60, 570).to(964, 570)], []


@letter('emdash', 0x2014)
def emdash():
    return 2048, [Line(60, 540).to(1988, 540)], []


@letter('slash', 0x2F)
def slash():
    return 682, [Line(620, 1480).to(60, -20)], []


@letter('quotesingle', 0x27)
def quotesingle():
    return 569, [Line(285, 960).to(285, 1446 - SOFT)], []


QUOTE_STEP = W_V + 150 if HEAVY else 272


@letter('quotedbl', 0x22)
def quotedbl():
    x = 300 + QUOTE_STEP
    return 600 + QUOTE_STEP, [Line(300, 960).to(300, 1446 - SOFT), Line(x, 960).to(x, 1446 - SOFT)], []


def _turned_comma(x, y):
    return Line(x, y + 40, **MARK).curve(x - 10, y + 200, x + 40, y + 320, x + 120, y + 400)


@letter('quotedblleft', 0x201C)
def quotedblleft():
    return 760, [_turned_comma(220, 1030), _turned_comma(470, 1030)], [(250, 1080), (500, 1080)]


@letter('quotedblright', 0x201D)
def quotedblright():
    _, lines, dots = quotedblleft()
    for line in lines:
        line.path = line.path.transform(scaleX=-1, scaleY=-1, translateX=760, translateY=2430)
    return 760, lines, [(760 - x, 2430 - y) for x, y in dots]


@letter('plus', 0x2B)
def plus():
    return 1229, [Line(614, 150).to(614, 936), Line(180, 543).to(1048, 543)], []


EQUAL_GAP = W_H + 150 if HEAVY else 326   # between the centres of the two bars


@letter('equal', 0x3D)
def equal():
    low, high = 543 - EQUAL_GAP / 2, 543 + EQUAL_GAP / 2
    return 1229, [Line(180, low).to(1048, low), Line(180, high).to(1048, high)], []


@letter('multiply', 0xD7)
def multiply():
    return 1229, [Line(260, 180).to(968, 888), Line(260, 888).to(968, 180)], []


@letter('quoteleft', 0x2018)
def quoteleft():
    return 420, [_turned_comma(180, 1030)], [(210, 1080)]


@letter('quoteright', 0x2019)
def quoteright():
    _, lines, dots = quoteleft()
    for line in lines:
        line.path = line.path.transform(scaleX=-1, scaleY=-1, translateX=420, translateY=2430)
    return 420, lines, [(420 - x, 2430 - y) for x, y in dots]


@letter('minus', 0x2212)
def minus():
    return 1229, [Line(180, 543).to(1048, 543)], []


@letter('plusminus', 0xB1)
def plusminus():
    lift = 120 if HEAVY else 0     # the plus moves up, clear of the heavy bar under it
    return 1229, [Line(614, 330 + lift).to(614, 1060 + lift), Line(180, 695 + lift).to(1048, 695 + lift),
                  Line(180, 160).to(1048, 160)], []


@letter('ellipsis', 0x2026)
def ellipsis():
    return 1500, [], [(250, DOT_Y), (750, DOT_Y), (1250, DOT_Y)]


@letter('periodcentered', 0xB7)
def periodcentered():
    return 569, [], [(284, 560)]


@letter('bullet', 0x2022)
def bullet():
    return 800, [], [(400, 560, 300 + 2 * HV - 174)]


@letter('degree', 0xB0)
def degree():
    grow = HV - 87   # keep the ring open in Bold
    return 680, [ellipse(340, 1220, 150 + grow, 150 + grow)], []


@letter('copyright', 0xA9)
def copyright_():
    c = Line(1030, 920, **MARK).arc(780, 720, 270, 280, 40, 320)
    return 1560, [ellipse(780, 720, 620, 620), c], []


def _arrow():
    shaft = Line(150, 560).to(1300, 560)
    head = poly([(980, 900), (1310, 560), (980, 220)], r=40)
    return [shaft, head]


@letter('arrowright', 0x2192)
def arrowright():
    return 1460, _arrow(), []


letter('arrowleft', 0x2190)(mirror(arrowright, 1460))


@letter('arrowup', 0x2191)
def arrowup():
    return 1100, [Line(550, SOFT).to(550, 1420), poly([(210, 1100), (550, 1430), (890, 1100)], r=40)], []


@letter('arrowdown', 0x2193)
def arrowdown():
    _, lines, _ = arrowup()
    for line in lines:
        line.path = line.path.transform(scaleY=-1, translateY=1446)
    return 1100, lines, []
