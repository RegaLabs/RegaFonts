"""The Rega Type letters, drawn as centre lines (see skeleton.py).

Units: 2048 per em. x grows to the right; a letter that joins the next one
(to its left in Kurdish) ends its stroke at x = -OV, a letter that joins the
previous one starts its stroke at x = advance.

Numbers below are centre-line positions. A stroke's edge lies half a stroke
away (HV for vertical strokes, HH for horizontal ones), and every free end
grows by SOFT, so ends that must land on a guide line stop SOFT short of it.

Each form returns (advance, centre lines, dots). Dots are (x, y) centres;
the dot shape is chosen at build time. Letters that differ only by dots or
marks (ب ت ث پ, ح ج چ خ, ...) share one skeleton function.
"""
from skeleton import (BASE, DOT_GAP, DOT_STACK, EYE, MARK, OV, SOFT, W_H, W_V, Line, ellipse,
                      ox, oy, poly)

HV, HH = W_V / 2, W_H / 2
ALEF_TOP = 1429 - SOFT   # alef, lam, tah
KAF_TOP = 1389 - SOFT
TOOTH = 788 - SOFT       # teeth, reh, the right arm of noon
TOP = 817 - HH           # centre of the top stroke of ح, ع, ی
ARM = 520 - SOFT         # the short upturn at the left end of beh, kaf, lam
DESC = -442 + HH         # centre of a tail that ends level (reh, waw)
DROP = -442 + SOFT       # end of a tail that ends straight down (meem)
L = 50 + HV              # centre of a letter's leftmost stroke when nothing joins on the left

DOT_BELOW = -330         # centre of the (upper row of) dots under a letter
DOT_OVER_BOWL = 1010     # dots over a low letter body (ت, ة, ع)
DOT_OVER_TOOTH = 1132    # dots over a tooth (ن, ت at the start)
MARK_W = MARK           # the pen of the small marks (v, hamza, madda)

GLYPHS = {}              # glyph name -> function returning (advance, lines, dots)
CMAP = {}                # code point -> glyph name
FORMS = {}               # glyph name -> {'init': ..., 'medi': ..., 'fina': ...}
LIGATURES = []           # ([glyph, glyph], ligature glyph) for the 'rlig' feature


def letter(name, code=None, form=None):
    def register(fn):
        gname = name if form is None else f'{name}.{form}'
        GLYPHS[gname] = fn
        if form is None and code is not None:
            CMAP[code] = gname
        if form is not None:
            FORMS.setdefault(name, {})[form] = gname
        return fn
    return register


def family(base_fn, members):
    """Register letters that share one skeleton.

    base_fn(form) -> (advance, lines, info); members maps a glyph name to
    (code point or None, marks), where marks(form, info) -> (extra lines, dots).
    """
    forms = base_fn.forms
    for name, (code, marks) in members.items():
        for form in forms:
            def fn(form=form, marks=marks):
                adv, lines, info = base_fn(form)
                extra, dots = marks(form, info)
                return adv, lines + extra, dots
            letter(name, code if form == 'isol' else None, None if form == 'isol' else form)(fn)


def forms(*names):
    def mark(fn):
        fn.forms = names
        return fn
    return mark


def none(form, info):
    return [], []


def dots(n, x, y, below=False):
    """One, two (side by side) or three (a pair plus one above, or below) dots."""
    if n == 1:
        return [(x, y)]
    pair = [(x - DOT_GAP / 2, y), (x + DOT_GAP / 2, y)]
    if n == 2:
        return pair
    return pair + [(x, y - DOT_STACK if below else y + DOT_STACK)]


def vmark(x, top, w=560, h=250):
    """The small v of ڕ ڵ ۆ ێ; `top` is the top of its arms."""
    return poly([(x - w / 2, top - SOFT), (x, top - h), (x + w / 2, top - SOFT)], r=50, w=MARK_W)


def hamza(x, y, s=1.0):
    """ء: a small open c with a tail sweeping down to the left; (x, y) is the c's centre."""
    rx, ry = 120 * s, 105 * s
    c = Line(x + rx * 0.82, y + ry * 0.57, w=MARK_W).arc(x, y, rx, ry, 35, 270).to(x + 90 * s, y - ry)
    tail = Line(x + 90 * s, y - ry, w=MARK_W).to(x - 170 * s, y - ry - 170 * s)
    return [c, tail]


def madda(x, y):
    """The wave of آ."""
    return [Line(x - 230, y - 30, w=MARK_W).curve(x - 130, y + 100, x - 50, y + 70, x, y)
            .curve(x + 50, y - 70, x + 130, y - 100, x + 230, y + 30)]


def entry(adv, x, up=None):
    """The joining stroke coming in from the previous letter (on the right).

    With `up`, it turns up into the stem at x with a rounded corner (an arch under a tooth).
    """
    if up is None:
        return Line(adv, BASE).to(x, BASE)
    return poly([(adv, BASE), (x, BASE), (x, up)], r=110)


def exit_(x):
    """The joining stroke going out to the next letter (on the left)."""
    return Line(x, BASE).to(-OV, BASE)


def bar(adv):
    """A joining stroke straight through the letter."""
    return Line(adv, BASE).to(-OV, BASE)


def teeth(xs, exit=True, adv=None):
    """Teeth standing on the joining stroke, right to left, with arches between them."""
    lines = [poly([(a, TOOTH), (a, BASE), (b, BASE), (b, TOOTH)], r=110) for a, b in zip(xs, xs[1:])]
    if exit:
        lines.append(poly([(xs[-1], TOOTH), (xs[-1], BASE), (-OV, BASE)], r=110))
    if adv is not None:
        lines.append(entry(adv, xs[0], TOOTH))
    return lines


def closed_poly(points, r):
    """A closed outline through `points` with rounded corners (started mid-edge, so no corner is lost).

    The radii go with points[1], points[2], ..., points[0].
    """
    a, b = points[0], points[1]
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    return poly([mid] + points[1:] + [a, mid], r=r).close()


# ـ tatweel

@letter('tatweel', 0x0640)
def tatweel():
    return 263, [bar(263)], []


# ا alef, أ إ آ

ALEF_X = 140 + HV


@forms('isol', 'fina')
def _alef(form):
    if form == 'isol':
        return 454, [Line(ALEF_X, SOFT).to(ALEF_X, ALEF_TOP)], ALEF_X
    return 463, [poly([(463, BASE), (ALEF_X, BASE), (ALEF_X, ALEF_TOP)], r=150)], ALEF_X


MARK_OVER_ALEF = ALEF_TOP + 230

family(_alef, {
    'alef': (0x0627, none),
    'alef_hamza': (0x0623, lambda f, x: (hamza(x + 20, MARK_OVER_ALEF, 0.62), [])),
    'alef_hamza_below': (0x0625, lambda f, x: (hamza(x + 20, -240, 0.62), [])),
    'alef_madda': (0x0622, lambda f, x: (madda(x, MARK_OVER_ALEF), [])),
})


# The tooth at the start or in the middle of a word: ب ت ث پ ن ی ي ى ێ ئ

TOOTH_X = 487 - HV


@forms('init', 'medi')
def _tooth(form):
    if form == 'init':
        return 627, teeth([TOOTH_X]), TOOTH_X
    return 680, teeth([TOOTH_X], adv=680), TOOTH_X


def _below(n):
    return lambda f, x: ([], dots(n, x - 30, DOT_BELOW, below=True))


def _above(n):
    return lambda f, x: ([], dots(n, x, DOT_OVER_TOOTH))


V_OVER_TOOTH = 1209
HAMZA_OVER_TOOTH = 1270

family(_tooth, {
    'beh': (None, _below(1)),
    'teh': (None, _above(2)),
    'theh': (None, _above(3)),
    'peh': (None, _below(3)),
    'noon': (None, _above(1)),
    'yeh': (None, _below(2)),
    'yeh_ar': (None, _below(2)),
    'alef_maksura': (None, none),
    'yeh_v': (None, lambda f, x: ([vmark(x, V_OVER_TOOTH)], dots(2, x - 30, DOT_BELOW))),
    'yeh_hamza': (None, lambda f, x: (hamza(x - 20, HAMZA_OVER_TOOTH), [])),
})


# ب ت ث پ alone and at the end: a long flat body

def _beh_body(xr):
    return poly([(xr, TOOTH), (xr, BASE), (L, BASE), (L, ARM)], r=[100, 190])


@forms('isol', 'fina')
def _beh(form):
    if form == 'isol':
        return 1845, [_beh_body(1705 - HV)], 901
    xr = 1740 - HV
    return 1890, [_beh_body(xr), entry(1890, xr)], 920


family(_beh, {
    'beh': (0x0628, lambda f, x: ([], dots(1, x, DOT_BELOW))),
    'teh': (0x062A, lambda f, x: ([], dots(2, x, DOT_OVER_BOWL))),
    'theh': (0x062B, lambda f, x: ([], dots(3, x, DOT_OVER_BOWL))),
    'peh': (0x067E, lambda f, x: ([], dots(3, x, DOT_BELOW + 13, below=True))),
})


# ن noon alone and at the end

def _noon_bowl(xr, top_r, top_l, bottom, cy=250):
    rx = (xr - L) / 2
    cx = L + rx
    return cx, Line(xr, top_r).to(xr, cy).arc(cx, cy, rx, cy - bottom, 0, -180).to(L, top_l)


@letter('noon', 0x0646)
def noon():
    _, bowl = _noon_bowl(1174 - HV, TOOTH, 560, -248 + HH)
    return 1314, [bowl], [(619, 863)]


@letter('noon', form='fina')
def noon_fina():
    xr = 1290
    _, bowl = _noon_bowl(xr, 686 - SOFT, 520, DESC, cy=200)
    return 1357, [bowl, entry(1357, xr)], [(629, 730)]


# ی ي ى ێ ئ alone and at the end: a hook flowing into a wide bowl

@forms('isol', 'fina')
def _yeh(form):
    if form == 'isol':
        line = (Line(1469 - SOFT, TOP).to(1100, TOP)
                .curve(880, TOP, 880, 420, 1080, 330)
                .curve(1250, 255, 1349, 170, 1349, 0)
                .curve(1349, -200, 1200, -381 + HH, 950, -381 + HH)
                .to(500, -381 + HH)
                .curve(250, -381 + HH, L, -200, L, 50)
                .to(L, 430))
        return 1559, [line], -381
    # the joining stroke turns down on a round corner into a wide bowl whose left arm
    # rises straight; a short diagonal leans up and back from the joint, like a flag
    xr = 1377
    bottom = -343 + HH
    turn, heel = 420, 380    # the round turns into and out of the bottom
    bowl = (poly([(1504, BASE), (xr, BASE), (xr, 0)], r=120)
            .arc(xr - turn, 0, turn, -bottom, 0, -90)
            .to(L + heel, bottom)
            .arc(L + heel, bottom + heel, heel, heel, -90, -180)
            .to(L, 447 - SOFT))
    flag = Line(xr - 30, BASE + 10).to(910, 420 - SOFT)
    return 1504, [bowl, flag], -343


family(_yeh, {
    'yeh': (0x06CC, none),
    'yeh_ar': (0x064A, lambda f, low: ([], dots(2, 757, low - 157))),
    'alef_maksura': (0x0649, none),
    'yeh_v': (0x06CE, lambda f, low: ([vmark(520, 990)], [])),
    'yeh_hamza': (0x0626, lambda f, low: (hamza(330, 760), [])),
})


# ح ج چ خ: a flat head turning down into the line, and alone or at the end a bowl below it

HAH_X = 954              # the head's right side (alone, at the end)


@forms('isol', 'init', 'medi', 'fina')
def _hah(form):
    if form in ('isol', 'fina'):
        line = (poly([(292, TOP), (HAH_X, TOP), (HAH_X, BASE), (520, BASE)], r=[260, 140])
                .arc(520, (BASE + DESC - 77) / 2, 383, (BASE - DESC + 77) / 2, 90, 270).to(760, DESC - 77))
        if form == 'isol':
            return 1234, [line], 'bowl'
        return 1240, [line, entry(1240, HAH_X)], 'bowl'
    xr = 900
    head = poly([(166, TOP), (xr, TOP), (xr, BASE), (-OV, BASE)], r=[260, 140])
    if form == 'init':
        return 1107, [head], 'tooth'
    return 1113, [head, entry(1113, xr)], 'tooth'


def _hah_dots(n, above=False):
    def marks(form, where):
        if above:
            return [], dots(n, 600 if where == 'bowl' else 530, 1100)
        if where == 'bowl':
            return [], dots(n, 900, -150, below=True) if n == 3 else dots(1, 840, -210)
        return [], dots(n, 480, DOT_BELOW, below=True)
    return marks


family(_hah, {
    'hah': (0x062D, none),
    'jeem': (0x062C, _hah_dots(1)),
    'tcheh': (0x0686, _hah_dots(3)),
    'khah': (0x062E, _hah_dots(1, above=True)),
})


# ع غ: a small open c on the line; in the middle of a word a closed loop

def _ain_bowl(x, end):
    return Line(x, BASE).arc(x, (BASE + DESC - 77) / 2, x - L, (BASE - DESC + 77) / 2, 90, 270).to(end, DESC - 77)


def _ain_loop(cx):
    return closed_poly([(cx - 321, TOP - 4), (cx + 322, TOP - 4), (cx, BASE)], r=[120, 150, 120])


@forms('isol', 'init', 'medi', 'fina')
def _ain(form):
    if form == 'isol':
        head = Line(877 - SOFT, TOP).to(620, TOP).arc(620, (TOP + BASE) / 2, ox(300), (TOP - BASE) / 2, 90, 270)
        base = Line(990 - SOFT, BASE).to(470, BASE)
        return 1066, [head, base, _ain_bowl(470, 760)], 590
    if form == 'init':
        head = Line(820 - SOFT, TOP).to(560, TOP).arc(560, (TOP + BASE) / 2, ox(300), (TOP - BASE) / 2, 90, 270)
        return 978, [head, Line(908 - SOFT, BASE).to(-OV, BASE)], 500
    if form == 'medi':
        return 1077, [_ain_loop(550), bar(1077)], 550
    return 1041, [_ain_loop(515), entry(1041, 515), Line(515, BASE).to(400, BASE), _ain_bowl(400, 700)], 515


family(_ain, {
    'ain': (0x0639, none),
    'ghain': (0x063A, lambda f, x: ([], dots(1, x, 1100 if f in ('isol', 'init') else DOT_OVER_BOWL))),
})


# س ش: three teeth; alone and at the end the last one drops into a bowl

def _seen_bowl(x):
    rx = (x - L) / 2
    return Line(x, TOOTH).to(x, 200).arc(L + rx, 200, rx, 200 - DESC, 0, -180).to(L, ARM - 40)


SEEN_TEETH = {'isol': [2163, 1646, 1087], 'fina': [2203, 1686, 1127],
              'init': [1427, 911, 352], 'medi': [1460, 944, 385]}


@forms('isol', 'init', 'medi', 'fina')
def _seen(form):
    xs = SEEN_TEETH[form]
    if form == 'isol':
        return 2390, teeth(xs, exit=False) + [_seen_bowl(xs[-1])], xs[1]
    if form == 'fina':
        return 2436, teeth(xs, exit=False, adv=2436) + [_seen_bowl(xs[-1])], xs[1]
    if form == 'init':
        return 1654, teeth(xs), xs[1]
    return 1700, teeth(xs, adv=1700), xs[1]


family(_seen, {
    'seen': (0x0633, none),
    'sheen': (0x0634, lambda f, x: ([], dots(3, x, DOT_OVER_TOOTH))),
})


# ص ض ط ظ: a loop with a sloping back; ص adds a tooth, ط a tall stem

SLOPE = 448              # how far right the loop's back leans between the line and its top


def _loop(x0, xr):
    """The ص/ط loop: flat bottom on the line, upright right side, back sloping up from x0."""
    # corners in order: top right, top left, bottom left, bottom right
    return closed_poly([(xr, BASE), (xr, TOP), (x0 + SLOPE, TOP), (x0, BASE)], r=[260, 180, 120, 260])


@forms('isol', 'init', 'medi', 'fina')
def _sad(form):
    if form in ('isol', 'fina'):
        tooth = 1087
        lines = [_seen_bowl(tooth), Line(tooth, BASE).to(1500, BASE), _loop(1400, 2498)]
        if form == 'isol':
            return 2707, lines, 2150
        return 2752, lines + [entry(2752, 2498)], 2150
    tooth = 355
    lines = teeth([tooth]) + [Line(tooth, BASE).to(700, BASE), _loop(586, 1685)]
    if form == 'init':
        return 1882, lines, 1130
    return 1930, lines + [entry(1930, 1685)], 1130


family(_sad, {
    'sad': (0x0635, none),
    'dad': (0x0636, lambda f, x: ([], dots(1, x, DOT_OVER_BOWL))),
})


TAH_STEM = 344


@forms('isol', 'init', 'medi', 'fina')
def _tah(form):
    lines = [poly([(TAH_STEM, ALEF_TOP), (TAH_STEM, BASE), (900, BASE)], r=120), _loop(300, 1315)]
    if form in ('init', 'medi'):
        lines.append(exit_(TAH_STEM))
    if form in ('medi', 'fina'):
        return 1580, lines + [entry(1580, 1315)], 950
    return 1546, lines, 950


family(_tah, {
    'tah': (0x0637, none),
    'zah': (0x0638, lambda f, x: ([], dots(1, x, DOT_OVER_BOWL))),
})


# ف ڤ ق: a loop on the line; ف alone has a long flat body, ق alone a deep bowl

FEH_LOOP = (ox(308), oy(326.5), 412.5)   # rx, ry, centre y


@forms('isol', 'init', 'medi', 'fina')
def _feh(form):
    rx, ry, cy = FEH_LOOP
    if form in ('isol', 'fina'):
        cx = 1584
        lines = [ellipse(cx, cy, rx, ry), poly([(cx, BASE), (L, BASE), (L, ARM)], r=190)]
        if form == 'isol':
            return 2101, lines, cx
        return 2124, lines + [entry(2124, cx)], cx
    cx = 587
    lines = [ellipse(cx, cy, rx, ry), exit_(cx)]
    if form == 'init':
        return 1104, lines, cx
    return 1128, lines + [entry(1128, cx)], cx


family(_feh, {
    'feh': (0x0641, lambda f, x: ([], dots(1, x, DOT_OVER_TOOTH))),
    'veh': (0x06A4, lambda f, x: ([], dots(3, x, DOT_OVER_TOOTH))),
})


@forms('init', 'medi')
def _qaf_joined(form):
    return _feh(form)


family(_qaf_joined, {'qaf': (None, lambda f, x: ([], dots(2, x, DOT_OVER_TOOTH)))})


@forms('isol', 'fina')
def _qaf(form):
    cx, cy, rx, ry = 1014, 409.5, ox(315), oy(329.5)
    xs = cx + rx
    brx = (xs - L) / 2
    bowl = Line(xs, cy).to(xs, 150).arc(L + brx, 150, brx, 150 - DESC, 0, -180).to(L, 420)
    lines = [ellipse(cx, cy, rx, ry), bowl]
    if form == 'isol':
        return 1536, lines, cx
    return 1557, lines + [entry(1557, cx)], cx


family(_qaf, {'qaf': (0x0642, lambda f, x: ([], dots(2, x, DOT_OVER_TOOTH)))})


# ە ae (Kurdish "e"), ه heh where it looks the same (alone, at the end), ة

@forms('isol', 'fina')
def _ae(form):
    if form == 'isol':
        # 10 units below the baseline: round letters overshoot to look as big as flat ones
        return 954, [ellipse(437, 403.5, 407 - HV, 413.5 - HH)], 437
    # one bowl resting on the joining stroke; its flat right side is the stem, which
    # runs on down into the joining stroke (no ring stacked on a stem, no double ink)
    cx, rx = 400, ox(290)
    top, bottom = 915 - HH, 172 + HH          # centre lines of the bowl's top and bottom
    cy, ry = (top + bottom) / 2, (top - bottom) / 2
    xs = cx + rx
    bowl = poly([(xs, cy), (xs, top), (cx, top)], r=110).arc(cx, cy, rx, ry, 90, 270).to(xs, bottom)
    stem = poly([(xs, cy), (xs, BASE), (969, BASE)], r=170)
    return 969, [bowl, stem], 450


family(_ae, {
    'ae': (0x06D5, none),
    'heh': (0x0647, none),
    'teh_marbuta': (0x0629, lambda f, x: ([], dots(2, x, DOT_OVER_BOWL if f == 'isol' else DOT_OVER_TOOTH))),
})


HEH_XL, HEH_XR, HEH_TOP = 171 + HV, 1177 - HV, 824 - HH


def _heh_dome(start):
    """ھ: a wide dome, round on the right and square on the left; a thinner inner
    stroke bows to the right, so the left eye is a soft D and the right one a crescent.
    The joining stroke and the right wall are one stroke, turning on a rounded corner."""
    xl, xr, top = HEH_XL, HEH_XR, HEH_TOP
    shoulder, corner = 480, 50
    dome = (poly([(start, BASE), (xr, BASE), (xr, top - shoulder)], r=60)
            .arc(xr - shoulder, top - shoulder, shoulder, shoulder, 0, 90)
            .to(xl + corner, top)
            .arc(xl + corner, top - corner, corner, corner, 90, 180)
            .to(xl, BASE))
    xe = 640
    eye = Line(xe, top, w=EYE).curve(xe + 120, top - 210, xe + 120, BASE + 210, xe, BASE)
    return [dome, eye]


@letter('heh', form='init')
def heh_init():
    return 1287, _heh_dome(-OV), []


@letter('heh', form='medi')
def heh_medi():
    # an oval resting on the line, and a bowl hanging open from it, set a little to
    # the left so the letter leans forward like the pen that writes it
    rx, ry = ox(267), oy(329)
    upper = ellipse(575, BASE + ry, rx, ry)
    lrx, lry = ox(312), BASE - DESC
    lower = Line(545 + lrx, BASE).arc(545, BASE, lrx, lry, 0, -180)
    return 1061, [upper, lower, bar(1061)], []


# ھ (06BE, the two-eyed h): the dome in every position

@letter('heh_doachashmee', 0x06BE)
def heh_doachashmee():
    return 1287, _heh_dome(HEH_XL), []


@letter('heh_doachashmee', form='fina')
def heh_doachashmee_fina():
    return 1287, _heh_dome(HEH_XL) + [entry(1287, HEH_XR)], []


FORMS['heh_doachashmee'].update(init='heh.init', medi='heh.medi')


# ر ز ژ ڕ, و ۆ ؤ: the descending tail

def _tail(xr, top, end_x):
    span = xr - end_x
    return Line(xr, top).to(xr, 60).curve(xr, -320, xr - span * 0.2, DESC, end_x, DESC)


@forms('isol', 'fina')
def _reh(form):
    if form == 'isol':
        xr = 485 - HV
        return 625, [_tail(xr, TOOTH, 40 + SOFT)], xr
    xr = 520 - HV
    return 671, [_tail(xr, TOOTH, 75 + SOFT), entry(671, xr)], xr


family(_reh, {
    'reh': (0x0631, none),
    'zain': (0x0632, lambda f, x: ([], dots(1, x, DOT_OVER_TOOTH))),
    'jeh': (0x0698, lambda f, x: ([], dots(3, x, DOT_OVER_TOOTH))),
    'reh_v': (0x0695, lambda f, x: ([vmark(x - 100, -560, w=500, h=230)], [])),
})


WAW_HEAD = (512, 409.5, ox(315), oy(329.5))   # centre x, centre y, rx, ry


def _waw_lines(dx=0):
    cx, cy, rx, ry = WAW_HEAD
    return [ellipse(cx + dx, cy, rx, ry), _tail(cx + rx + dx, cy, 120 + SOFT + dx)]


@forms('isol', 'fina')
def _waw(form):
    cx, _, rx, _ = WAW_HEAD
    if form == 'isol':
        return 1035, _waw_lines(), cx
    return 1056, _waw_lines(10) + [entry(1056, cx + rx + 10)], cx + 10


family(_waw, {
    'waw': (0x0648, none),
    'waw_v': (0x06C6, lambda f, x: ([vmark(x, 1330)], [])),
    'waw_hamza': (0x0624, lambda f, x: (hamza(x - 20, 1050, 0.8), [])),
})


# د ذ

def _dal_line(xr, xl):
    return poly([(xl + 120, 760), (xr, 560), (xr, BASE), (xl, BASE)], r=[560, 120])


@forms('isol', 'fina')
def _dal(form):
    if form == 'isol':
        return 927, [_dal_line(816 - HV, 61 + SOFT)], 400
    xr = 850 - HV
    return 979, [_dal_line(xr, 80 + SOFT), entry(979, xr)], 420


family(_dal, {
    'dal': (0x062F, none),
    'thal': (0x0630, lambda f, x: ([], dots(1, x, 1060))),
})


# ک ك گ: a < on a long base; the lower stroke sweeps into the base

KAF_BACK = 520           # how far left the point of the < sits from the base's right end
KAF_MID = 820
KAF_TURN = 250           # radius of the turn from the lower stroke into the base


def _kaf_lines(xr, tail):
    """The < (top stroke, then a lower stroke that bows outward and sweeps into the base)."""
    vx = xr - KAF_BACK
    y = BASE + KAF_TURN
    k = KAF_TURN * 0.5523
    line = (Line(xr - 10, KAF_TOP).to(vx, KAF_MID)
            .curve(vx + 260, KAF_MID - 270, xr, y + 260, xr, y)
            .curve(xr, y - k, xr - KAF_TURN + k, BASE, xr - KAF_TURN, BASE))
    if len(tail) == 1:
        return [line.to(*tail[0])]
    return [line, poly([(xr - KAF_TURN, BASE)] + tail, r=190)]


@forms('isol', 'init', 'medi', 'fina')
def _kaf(form):
    if form == 'isol':
        xr = 1615
        return 1812, _kaf_lines(xr, [(L, BASE), (L, ARM)]), xr
    if form == 'fina':
        xr = 1650
        return 1912, _kaf_lines(xr, [(L, BASE), (L, ARM)]) + [entry(1912, xr - KAF_TURN)], xr
    if form == 'init':
        xr = 700
        return 937, _kaf_lines(xr, [(-OV, BASE)]), xr
    xr = 720
    return 1025, _kaf_lines(xr, [(-OV, BASE)]) + [entry(1025, xr - KAF_TURN)], xr


def _gaf_stroke(form, xr):
    """گ: parallel stroke running above the main slanting stroke."""
    lift = round(104 + W_V)
    vx = xr - KAF_BACK
    return [Line(xr - 10, KAF_TOP + lift).to(vx, KAF_MID + lift)], []


family(_kaf, {
    'kaf': (0x06A9, none),
    'gaf': (0x06AF, _gaf_stroke),
})
CMAP[0x0643] = 'kaf'     # the Arabic kaf shares the Kurdish shapes


# ل ڵ

def _lam_bowl(xr):
    rx = (xr - L) / 2
    cy = 200
    return Line(xr, ALEF_TOP).to(xr, cy).arc(L + rx, cy, rx, cy - DESC, 0, -180).to(L, ARM - 40)


LAM_X = 425 - HV


@forms('isol', 'init', 'medi', 'fina')
def _lam(form):
    if form == 'isol':
        xr = 1174 - HV
        return 1314, [_lam_bowl(xr)], ((L + xr) / 2, 1450)
    if form == 'fina':
        xr = 1275 - HV
        return 1357, [_lam_bowl(xr), entry(1357, xr)], ((L + xr) / 2, 1450)
    stem = poly([(LAM_X, ALEF_TOP), (LAM_X, BASE), (-OV, BASE)], r=110)
    if form == 'init':
        return 565, [stem], (LAM_X - 20, 1880)
    return 626, [stem, entry(626, LAM_X, ALEF_TOP)], (LAM_X - 20, 1880)


family(_lam, {
    'lam': (0x0644, none),
    'lam_v': (0x06B5, lambda f, at: ([vmark(at[0], at[1])], [])),
})


# لا (and with أ إ آ, and ڵا): the lam with a long foot, the alef leaning down onto it

LA_FOOT = 70 + SOFT
LA_ALEF_TOP_X = LA_FOOT + 430


def _lam_alef_lines(xr):
    lam = poly([(xr, ALEF_TOP), (xr, BASE), (LA_FOOT, BASE)], r=150)
    alef = Line(LA_ALEF_TOP_X, ALEF_TOP).to(LA_FOOT + 540, BASE)
    return [lam, alef]


@forms('isol', 'fina')
def _lam_alef(form):
    if form == 'isol':
        xr = 1117 - HV
        return 1257, _lam_alef_lines(xr), xr
    xr = 1150 - HV
    return 1300, _lam_alef_lines(xr) + [entry(1300, xr)], xr


ALEF_MARKS = {
    '': none,
    '_hamza': lambda f, xr: (hamza(LA_ALEF_TOP_X + 20, MARK_OVER_ALEF, 0.62), []),
    '_hamza_below': lambda f, xr: (hamza(LA_FOOT + 560, -240, 0.62), []),
    '_madda': lambda f, xr: (madda(LA_ALEF_TOP_X, MARK_OVER_ALEF), []),
}

for suffix, marks in ALEF_MARKS.items():
    family(_lam_alef, {f'lam_alef{suffix}': (None, marks)})
    LIGATURES.append((['lam.init', f'alef{suffix}.fina'], f'lam_alef{suffix}'))
    LIGATURES.append((['lam.medi', f'alef{suffix}.fina'], f'lam_alef{suffix}.fina'))

family(_lam_alef, {'lam_v_alef': (None, lambda f, xr: ([vmark((LA_FOOT + xr) / 2 + 80, 1700)], []))})
LIGATURES.append((['lam_v.init', 'alef.fina'], 'lam_v_alef'))
LIGATURES.append((['lam_v.medi', 'alef.fina'], 'lam_v_alef.fina'))


# م meem

MEEM_LOOP = (ox(332.5), oy(309.5), 372.5)      # rx, ry, centre y (dips 21 below the baseline)


def _meem_loop(cx):
    rx, ry, cy = MEEM_LOOP
    return ellipse(cx, cy, rx, ry)


def _heel(cx):
    """The loop's left side sweeps down into the joining stroke: a teardrop, not a ring on a line."""
    rx, _, cy = MEEM_LOOP
    x = cx - rx
    return Line(x, cy).curve(x, cy - 0.6 * (cy - BASE), x - 20, BASE, x - 190, BASE)


def _meem_tail(cx):
    rx, _, _ = MEEM_LOOP
    return [_heel(cx), poly([(cx - rx - 190, BASE), (L, BASE), (L, DROP)], r=150)]


@letter('meem', 0x0645)
def meem():
    return 1242, [_meem_loop(711.5)] + _meem_tail(711.5), []


@letter('meem', form='fina')
def meem_fina():
    return 1271, [_meem_loop(711.5), entry(1271, 711.5)] + _meem_tail(711.5), []


@letter('meem', form='init')
def meem_init():
    rx = MEEM_LOOP[0]
    return 1192, [_meem_loop(661.5), _heel(661.5), exit_(661.5 - rx - 190)], []


@letter('meem', form='medi')
def meem_medi():
    rx = MEEM_LOOP[0]
    return 1141, [_meem_loop(581.5), _heel(581.5), exit_(581.5 - rx - 190), entry(1141, 581.5)], []


# ء hamza on its own

@letter('hamza', 0x0621)
def hamza_alone():
    return 760, hamza(400, 520, 1.25), []


# Vowel marks (Arabic text). They take no width; with no positioning table in the
# font, the text engine (HarfBuzz) centres each one over or under its letter.

MARKS = set()


def mark(name, code):
    def register(fn):
        MARKS.add(name)
        return letter(name, code)(fn)
    return register


def _thin(line):
    line.w = MARK_W
    return line


def _stroke(y):
    return Line(-120, y, w=MARK_W).to(120, y + 130)


MARK_GROW = (MARK_W - 116) / 2   # the small loops grow with the pen, so they stay open in Bold


def _damma(x, s=1.0):
    loop = _thin(ellipse(x + 30 * s, 1180, 95 * s + MARK_GROW, 90 * s + MARK_GROW))
    tail = Line(x + 125 * s, 1180, w=MARK_W).curve(x + 125 * s, 1020, x + 40 * s, 950, x - 110 * s, 940)
    return [loop, tail]


@mark('fatha', 0x064E)
def fatha():
    return 0, [_stroke(1060)], []


@mark('fathatan', 0x064B)
def fathatan():
    return 0, [_stroke(1000), _stroke(1200)], []


@mark('kasra', 0x0650)
def kasra():
    return 0, [_stroke(-260)], []


@mark('kasratan', 0x064D)
def kasratan():
    return 0, [_stroke(-220), _stroke(-420)], []


@mark('damma', 0x064F)
def damma():
    return 0, _damma(0), []


@mark('dammatan', 0x064C)
def dammatan():
    return 0, _damma(-170, 0.9) + _damma(170, 0.9), []


@mark('shadda', 0x0651)
def shadda():
    left = poly([(-170, 1260), (-170, 1110), (0, 1110), (0, 1260)], r=50, w=MARK_W)
    right = poly([(0, 1260), (0, 1110), (170, 1110), (170, 1260)], r=50, w=MARK_W)
    return 0, [left, right], []


@mark('sukun', 0x0652)
def sukun():
    return 0, [_thin(ellipse(0, 1160, 100 + MARK_GROW, 100 + MARK_GROW))], []


@mark('alef_above', 0x0670)
def alef_above():
    return 0, [Line(0, 1040, w=MARK_W).to(0, 1300)], []


@mark('madda_above', 0x0653)
def madda_above():
    return 0, madda(0, 1150), []


@mark('hamza_above', 0x0654)
def hamza_above():
    return 0, hamza(0, 1150, 0.62), []


@mark('hamza_below', 0x0655)
def hamza_below():
    return 0, hamza(0, -250, 0.62), []
