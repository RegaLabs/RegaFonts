"""Rega Type's Latin letters: geometric, monoline, the same pen as the Kurdish letters.

A-Z, a-z, the Kurdish Latin letters (ç ê î ş û), the common accented letters,
and the rest of the keyboard symbols. Round letters are near-circles and share
their stems with their bowls, so a bowl never doubles the ink of its stem.
"""
from glyphs import BASE, HH, HV, MARK_W, SOFT, letter, madda
from skeleton import Line, ellipse, ox, oy, poly
from signs import HEAVY, mirror

XH = 1010                # x-height (outer)
CAP = 1430               # capitals (outer)
ASC = 1460               # b d f h k l
DSC = -440               # g j p q y
TOP = XH - SOFT          # where a lowercase stem stops
CTOP = CAP - SOFT
CBAR = CAP - HH          # centre of a capital's top bar
XBAR = XH - HH           # centre of a lowercase top stroke (f, t, z)
RX, RY, CY = ox(405), oy(435), 505   # lowercase bowl (overshoots the baseline and x-height by 14)
X0 = 90 + HV             # a left stem
DOT = 1300               # the dot of i and j


def bowl(cx):
    return ellipse(cx, CY, RX, RY)


def arch(x0, x1, top=XBAR, spring=560):
    """The shoulder of n, h, m: up from the stem at x0, over, and down the stem at x1."""
    r = (x1 - x0) / 2
    return Line(x0, spring).arc(x0 + r, spring, r, top - spring, 180, 0).to(x1, SOFT)


# lowercase

@letter('a', 0x61)
def a():
    return 1144, [bowl(582), Line(987, TOP).to(987, SOFT)], []


@letter('b', 0x62)
def b():
    return 1164, [Line(X0, ASC - SOFT).to(X0, SOFT), bowl(X0 + RX)], []


@letter('c', 0x63)
def c():
    return 1100, [Line(582 + RX * 0.743, CY + RY * 0.669).arc(582, CY, RX, RY, 42, 318)], []


@letter('d', 0x64)
def d():
    return 1144, [bowl(582), Line(987, ASC - SOFT).to(987, SOFT)], []


@letter('e', 0x65)
def e():
    return 1164, [Line(582 - RX, CY).to(582 + RX, CY).arc(582, CY, RX, RY, 0, 325)], []


@letter('f', 0x66)
def f():
    stem = Line(330, SOFT).to(330, 1150).curve(330, 1340, 430, ASC - HH, 580, ASC - HH).to(700 - SOFT, ASC - HH)
    return 700, [stem, Line(110, XBAR).to(640, XBAR)], []


@letter('g', 0x67)
def g():
    tail = Line(987, TOP).to(987, 0).curve(987, -300, 800, DSC + HH, 560, DSC + HH).to(260, DSC + HH)
    return 1144, [bowl(582), tail], []


@letter('h', 0x68)
def h():
    return 1074, [Line(X0, ASC - SOFT).to(X0, SOFT), arch(X0, 897)], []


@letter('i', 0x69)
def i():
    return 400, [Line(200, TOP).to(200, SOFT)], [(200, DOT)]


@letter('dotlessi', 0x131)
def dotlessi():
    return 400, [Line(200, TOP).to(200, SOFT)], []


@letter('j', 0x6A)
def j():
    return 480, [Line(320, TOP).to(320, -100).curve(320, -300, 240, DSC + HH, 60, DSC + HH)], [(320, DOT)]


@letter('k', 0x6B)
def k():
    return 900, [Line(X0, ASC - SOFT).to(X0, SOFT), Line(740, TOP).to(X0, 360), Line(400, 540).to(790, SOFT)], []


@letter('l', 0x6C)
def l():
    return 400, [Line(200, ASC - SOFT).to(200, SOFT)], []


@letter('m', 0x6D)
def m():
    return 1554, [Line(X0, TOP).to(X0, SOFT), arch(X0, 777), arch(777, 1377)], []


@letter('n', 0x6E)
def n():
    return 1074, [Line(X0, TOP).to(X0, SOFT), arch(X0, 897)], []


@letter('o', 0x6F)
def o():
    return 1164, [bowl(582)], []


@letter('p', 0x70)
def p():
    return 1164, [Line(X0, TOP).to(X0, DSC + SOFT), bowl(X0 + RX)], []


@letter('q', 0x71)
def q():
    return 1144, [bowl(582), Line(987, TOP).to(987, DSC + SOFT)], []


@letter('r', 0x72)
def r():
    shoulder = Line(X0, 560).curve(X0, 860, 300, XBAR, 520, XBAR).to(680 - SOFT, XBAR)
    return 720, [Line(X0, TOP).to(X0, SOFT), shoulder], []


def _s(cx, top, bottom, rx_t, rx_b, split):
    """Two arcs: a smaller one on top turning left, a larger one below turning right."""
    cy_t, cy_b = (top + split) / 2, (split + bottom) / 2
    ry_t, ry_b = (top - split) / 2, (split - bottom) / 2
    upper = Line(cx + rx_t * 0.906, cy_t + ry_t * 0.423).arc(cx, cy_t, rx_t, ry_t, 25, 270)
    lower = Line(cx, split).arc(cx, cy_b, rx_b, ry_b, 90, -155)
    return [upper, lower]


@letter('s', 0x73)
def s():
    return 1000, _s(500, XH + 14 - HH, -14 + HH, 300, 330, 580), []


@letter('t', 0x74)
def t():
    stem = Line(330, 1250).to(330, 300).curve(330, 140, 420, BASE, 600, BASE).to(700 - SOFT, BASE)
    return 720, [stem, Line(110, XBAR).to(640, XBAR)], []


@letter('u', 0x75)
def u():
    left = Line(X0, TOP).to(X0, 450).arc(537, 450, 360, 450 - BASE, 180, 360)
    return 1074, [left, Line(897, TOP).to(897, SOFT)], []


@letter('v', 0x76)
def v():
    return 1040, [poly([(110, TOP), (520, SOFT + 30), (930, TOP)], r=40)], []


@letter('w', 0x77)
def w():
    return 1440, [poly([(90, TOP), (400, SOFT + 30), (720, TOP), (1040, SOFT + 30), (1350, TOP)], r=40)], []


@letter('x', 0x78)
def x():
    return 1020, [Line(120, TOP).to(900, SOFT), Line(900, TOP).to(120, SOFT)], []


@letter('y', 0x79)
def y():
    return 1040, [Line(110, TOP).to(520, 40), Line(930, TOP).to(330, DSC + SOFT)], []


@letter('z', 0x7A)
def z():
    return 1060, [poly([(150, XBAR), (900, XBAR), (150, BASE), (930, BASE)], r=30)], []


# capitals

CX, CRX, CRY, CCY = 790, ox(630), oy(631), 715    # the round capitals (O, C, G, Q)


@letter('A', 0x41)
def A():
    return 1400, [poly([(90, SOFT), (700, CTOP), (1310, SOFT)], r=40), Line(330, 480).to(1070, 480)], []


@letter('B', 0x42)
def B():
    top = Line(X0, CBAR).to(650, CBAR).arc(650, (CBAR + 760) / 2, 290, (CBAR - 760) / 2, 90, -90).to(X0, 760)
    low = Line(X0, 760).to(680, 760).arc(680, (760 + BASE) / 2, 340, (760 - BASE) / 2, 90, -90).to(X0, BASE)
    return 1150, [Line(X0, CBAR).to(X0, BASE), top, low], []


@letter('C', 0x43)
def C():
    start = (CX + CRX * 0.707, CCY + CRY * 0.707)
    return 1440, [Line(*start).arc(CX, CCY, CRX, CRY, 45, 315)], []


@letter('D', 0x44)
def D():
    side = Line(X0, CBAR).to(560, CBAR).arc(560, (CBAR + BASE) / 2, 600, (CBAR - BASE) / 2, 90, -90).to(X0, BASE)
    return 1350, [Line(X0, CBAR).to(X0, BASE), side], []


@letter('E', 0x45)
def E():
    return 1100, [poly([(1000 - SOFT, CBAR), (X0, CBAR), (X0, BASE), (1000 - SOFT, BASE)], r=0), Line(X0, 740).to(900, 740)], []


@letter('F', 0x46)
def F():
    return 1060, [poly([(1000 - SOFT, CBAR), (X0, CBAR), (X0, SOFT)], r=0), Line(X0, 740).to(900, 740)], []


@letter('G', 0x47)
def G():
    start = (CX + CRX * 0.766, CCY + CRY * 0.643)
    return 1480, [Line(*start).arc(CX, CCY, CRX, CRY, 40, 360).to(CX + 80, CCY)], []


@letter('H', 0x48)
def H():
    return 1300, [Line(X0, CTOP).to(X0, SOFT), Line(1123, CTOP).to(1123, SOFT), Line(X0, 760).to(1123, 760)], []


@letter('I', 0x49)
def I():
    return 400, [Line(200, CTOP).to(200, SOFT)], []


@letter('J', 0x4A)
def J():
    return 880, [Line(700, CTOP).to(700, 420).curve(700, 120, 560, BASE, 400, BASE).curve(230, BASE, 120, 140, 110, 300)], []


@letter('K', 0x4B)
def K():
    return 1180, [Line(X0, CTOP).to(X0, SOFT), Line(1050, CTOP).to(X0, 500), Line(480, 790).to(1100, SOFT)], []


@letter('L', 0x4C)
def L():
    return 1020, [poly([(X0, CTOP), (X0, BASE), (960 - SOFT, BASE)], r=0)], []


@letter('M', 0x4D)
def M():
    return 1560, [poly([(140, SOFT), (250, CTOP), (780, 250), (1310, CTOP), (1420, SOFT)], r=40)], []


@letter('N', 0x4E)
def N():
    return 1300, [poly([(X0, SOFT), (X0, CTOP), (1123, SOFT), (1123, CTOP)], r=0)], []


@letter('O', 0x4F)
def O():
    return 1580, [ellipse(CX, CCY, CRX, CRY)], []


def _p_bowl(right=640):
    return Line(X0, CBAR).to(right, CBAR).arc(right, 1000, 360, CBAR - 1000, 90, -90).to(X0, 2000 - CBAR)


@letter('P', 0x50)
def P():
    return 1140, [Line(X0, CBAR).to(X0, SOFT), _p_bowl()], []


@letter('Q', 0x51)
def Q():
    return 1580, [ellipse(CX, CCY, CRX, CRY), Line(1010, 330).to(1420, SOFT)], []


@letter('R', 0x52)
def R():
    return 1160, [Line(X0, CBAR).to(X0, SOFT), _p_bowl(), Line(620, 2000 - CBAR).to(1080, SOFT)], []


@letter('S', 0x53)
def S():
    return 1260, _s(640, CAP + 14 - HH, -14 + HH, 430, 470, 766), []


@letter('T', 0x54)
def T():
    return 1200, [Line(80, CBAR).to(1120, CBAR), Line(600, CBAR).to(600, SOFT)], []


@letter('U', 0x55)
def U():
    return 1300, [Line(X0, CTOP).to(X0, 560).arc(650, 560, 473, 560 - BASE, 180, 360).to(1123, CTOP)], []


@letter('V', 0x56)
def V():
    return 1360, [poly([(80, CTOP), (680, SOFT + 30), (1280, CTOP)], r=40)], []


@letter('W', 0x57)
def W():
    return 1860, [poly([(70, CTOP), (470, SOFT + 30), (930, CTOP), (1390, SOFT + 30), (1790, CTOP)], r=40)], []


@letter('X', 0x58)
def X():
    return 1300, [Line(100, CTOP).to(1200, SOFT), Line(1200, CTOP).to(100, SOFT)], []


@letter('Y', 0x59)
def Y():
    return 1280, [Line(80, CTOP).to(640, 700), Line(1200, CTOP).to(640, 700), Line(640, 700).to(640, SOFT)], []


@letter('Z', 0x5A)
def Z():
    return 1300, [poly([(160, CBAR), (1100, CBAR), (160, BASE), (1140 - SOFT, BASE)], r=30)], []


# accents, and the accented letters built from them

def acute(x, y):
    return [Line(x - 70, y, w=MARK_W).to(x + 110, y + 210)], []


def grave(x, y):
    return [Line(x + 70, y, w=MARK_W).to(x - 110, y + 210)], []


def circumflex(x, y):
    return [poly([(x - 180, y), (x, y + 200), (x + 180, y)], r=30, w=MARK_W)], []


def diaeresis(x, y):
    return [], [(x - 160, y + 100), (x + 160, y + 100)]


def tilde(x, y):
    return madda(x, y + 90), []


def cedilla(x, y):
    hook = Line(x, SOFT, w=MARK_W).to(x, -150).curve(x + 150, -150, x + 150, -340, x - 90, -340)
    return [hook], []


LOWER_ACCENT_Y, CAP_ACCENT_Y = 1170, 1590

ACCENTED = {
    # name: (code, base, accent)
    'agrave': (0xE0, 'a', grave), 'aacute': (0xE1, 'a', acute), 'acircumflex': (0xE2, 'a', circumflex),
    'atilde': (0xE3, 'a', tilde), 'adieresis': (0xE4, 'a', diaeresis),
    'ccedilla': (0xE7, 'c', cedilla),
    'egrave': (0xE8, 'e', grave), 'eacute': (0xE9, 'e', acute), 'ecircumflex': (0xEA, 'e', circumflex),
    'edieresis': (0xEB, 'e', diaeresis),
    'igrave': (0xEC, 'dotlessi', grave), 'iacute': (0xED, 'dotlessi', acute),
    'icircumflex': (0xEE, 'dotlessi', circumflex), 'idieresis': (0xEF, 'dotlessi', diaeresis),
    'ntilde': (0xF1, 'n', tilde),
    'ograve': (0xF2, 'o', grave), 'oacute': (0xF3, 'o', acute), 'ocircumflex': (0xF4, 'o', circumflex),
    'otilde': (0xF5, 'o', tilde), 'odieresis': (0xF6, 'o', diaeresis),
    'ugrave': (0xF9, 'u', grave), 'uacute': (0xFA, 'u', acute), 'ucircumflex': (0xFB, 'u', circumflex),
    'udieresis': (0xFC, 'u', diaeresis),
    'scedilla': (0x15F, 's', cedilla),
    'Agrave': (0xC0, 'A', grave), 'Aacute': (0xC1, 'A', acute), 'Acircumflex': (0xC2, 'A', circumflex),
    'Adieresis': (0xC4, 'A', diaeresis), 'Ccedilla': (0xC7, 'C', cedilla),
    'Egrave': (0xC8, 'E', grave), 'Eacute': (0xC9, 'E', acute), 'Ecircumflex': (0xCA, 'E', circumflex),
    'Edieresis': (0xCB, 'E', diaeresis),
    'Iacute': (0xCD, 'I', acute), 'Icircumflex': (0xCE, 'I', circumflex), 'Idieresis': (0xCF, 'I', diaeresis),
    'Ntilde': (0xD1, 'N', tilde),
    'Oacute': (0xD3, 'O', acute), 'Ocircumflex': (0xD4, 'O', circumflex), 'Odieresis': (0xD6, 'O', diaeresis),
    'Uacute': (0xDA, 'U', acute), 'Ucircumflex': (0xDB, 'U', circumflex), 'Udieresis': (0xDC, 'U', diaeresis),
    'Scedilla': (0x15E, 'S', cedilla),
}

BASES = {fn.__name__: fn for fn in (a, c, e, n, o, s, u, dotlessi, A, C, E, I, N, O, S, U)}
CENTRES = {'a': 582, 'c': 582, 'e': 582, 'o': 582, 'u': 537, 'n': 537,
           'A': 700, 'C': CX, 'O': CX, 'E': 560, 'I': 200, 'N': 650, 'U': 650, 'S': 640, 's': 500}

for gname, (code, base, accent) in ACCENTED.items():
    def accented(base=base, accent=accent):
        adv, lines, dts = BASES[base]()
        x = CENTRES.get(base, adv / 2)
        y = CAP_ACCENT_Y if base.isupper() else LOWER_ACCENT_Y
        extra, extra_dots = accent(x, 0 if accent is cedilla else y)
        return adv, lines + extra, dts + extra_dots
    letter(gname, code)(accented)


# the rest of the keyboard

@letter('numbersign', 0x23)
def numbersign():
    return 1200, [Line(470, 1400).to(390, SOFT), Line(870, 1400).to(790, SOFT),
                  Line(150, 960).to(1100, 960), Line(110, 470).to(1060, 470)], []


@letter('dollar', 0x24)
def dollar():
    _, lines, _ = S()
    for line in lines:
        line.path = line.path.transform(scaleX=0.8, scaleY=0.86, translateX=40, translateY=100)
    return 1100, lines + [Line(550, -200).to(550, 1600)], []


@letter('asterisk', 0x2A)
def asterisk():
    cx, cy, r = 360, 1180, 270
    w = MARK_W if HEAVY else None   # six heavy arms this short would fill in
    return 721, [Line(cx, cy - r, w=w).to(cx, cy + r), Line(cx - 234, cy - 135, w=w).to(cx + 234, cy + 135),
                 Line(cx - 234, cy + 135, w=w).to(cx + 234, cy - 135)], []


@letter('less', 0x3C)
def less():
    return 1229, [poly([(1040, 1000), (190, 543), (1040, 86)], r=40)], []


letter('greater', 0x3E)(mirror(less, 1229))


@letter('at', 0x40)
def at():
    ring = Line(1350, 260).curve(1450, 500, 1450, 1000, 1300, 1150).arc(820, 650, 640, 640, 50, 300)
    inner = ellipse(780, 640, 250, 260)
    stem = Line(1030, 900).to(1030, 450).curve(1030, 300, 1110, 240, 1200, 240).curve(1300, 240, 1350, 260, 1350, 260)
    return 1638, [ring, inner, stem], []


@letter('backslash', 0x5C)
def backslash():
    return 682, [Line(60, 1480).to(620, -20)], []


@letter('asciicircum', 0x5E)
def asciicircum():
    return 1000, [poly([(220, 900), (500, 1400), (780, 900)], r=40)], []


@letter('underscore', 0x5F)
def underscore():
    return 1000, [Line(SOFT, -220).to(1000 - SOFT, -220)], []


@letter('grave', 0x60)
def grave_mark():
    lines, _ = grave(400, 1170)
    return 800, lines, []


@letter('braceleft', 0x7B)
def braceleft():
    upper = Line(470, 1480).curve(300, 1480, 300, 1420, 300, 1250).to(300, 800).curve(300, 600, 250, 545, 130, 545)
    lower = Line(130, 545).curve(250, 545, 300, 490, 300, 290).to(300, -160).curve(300, -330, 300, -390, 470, -390)
    return 600, [upper, lower], []


letter('braceright', 0x7D)(mirror(braceleft, 600))


@letter('bar', 0x7C)
def bar_glyph():
    return 560, [Line(280, -400).to(280, 1500)], []


@letter('asciitilde', 0x7E)
def asciitilde():
    return 1100, madda(550, 560), []


@letter('ampersand', 0x26)
def ampersand():
    loop = Line(1150, SOFT + 20).to(450, 860).curve(330, 1000, 330, 1350, 600, 1350).curve(860, 1350, 880, 1050, 680, 900)
    belly = Line(680, 900).to(400, 700).curve(150, 520, 150, 84, 520, 84).curve(800, 84, 960, 300, 1100, 560)
    return 1366, [loop, belly], []

