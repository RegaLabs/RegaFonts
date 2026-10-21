"""Centre-line drawing for the RegaFonts typefaces (by RegaLabs).

Every letter is drawn once, as centre lines (skeletons). Each family then
writes those skeletons with its own pen and proportions:

  - Rega Type:  tall teeth, flat ends (the text face);
  - Rega Aso:   low and wide, round ends, very soft corners (calm, modern);
  - Rega Payam: a tall body, short tails, heavy, round ends (soft headlines).

All shapes are built here from points, lines, rounded corners and ellipse
arcs; nothing is traced from another font.

Two optical details make the strokes look even rather than mechanical:
  - vertical strokes are a little thicker than horizontal ones (W_V vs W_H),
    because the eye reads equal-thickness horizontals as heavier;
  - every outer corner is softened by SOFT units.
"""
import math

import pathops

OV = 40            # how far a joining stroke reaches into the next letter (no hairline gaps)
SOFT = 16          # corner softening: strokes are drawn this much thinner, then grown back round

# One drawing, several pens. A heavier pen keeps every shape's outer edge where
# Rega Type Regular has it (see ox/oy) and lets the inside shrink.
#   cap:     'butt' (flat stroke ends) or 'round'
#   body:    height of the teeth and bowls above the line, as a share of Rega Type's
#   ascend:  how far alef, lam and kaf rise above the dots over the teeth, as a share of Rega Type's
#   descend: depth of the tails and bowls below the line, as a share of Rega Type's
#   stretch: the skeleton is widened by this much before it is stroked (the pen stays the same)
#   lean:    degrees the letters lean the way they are written (Kurdish tops to the left, Latin to the right)
#   corner:  scales the radius of every rounded corner
#   grow:    share of the extra weight by which loops grow outward (0: the inside takes it all)
#   XSCALE:  the finished letter is widened by this much (the strokes widen with it)
# Proportions, width and lean move the skeleton before it is stroked, so strokes stay even.
FAMILIES = {
    # tall teeth, flat ends: the text face
    'Rega Type': dict(dots='round', weights={
        'Regular': dict(W_V=174, W_H=168, MARK=116, EYE=124, DOT=217, DOT_GAP=266, DOT_STACK=246,
                        XSCALE=1.0, CLASS=400),
        'Bold': dict(W_V=262, W_H=240, MARK=168, EYE=172, DOT=292, DOT_GAP=338, DOT_STACK=310,
                     XSCALE=1.04, CLASS=700),
    }),
    # soft and wide: low teeth, wide letters, shallow tails, very round corners, round ends
    'Rega Aso': dict(dots='round', cap='round', body=0.84, descend=0.8, stretch=1.12, corner=1.6, weights={
        'Light': dict(W_V=112, W_H=112, MARK=92, EYE=96, DOT=190, DOT_GAP=240, DOT_STACK=225,
                      XSCALE=1.0, CLASS=300),
        'Regular': dict(W_V=160, W_H=160, MARK=112, EYE=120, DOT=212, DOT_GAP=262, DOT_STACK=242,
                        XSCALE=1.0, CLASS=400),
        'Bold': dict(W_V=240, W_H=232, MARK=156, EYE=162, DOT=280, DOT_GAP=328, DOT_STACK=300,
                     XSCALE=1.0, CLASS=700),
    }),
    # soft and bold: a tall body, short ascenders and tails, compact and heavy, round ends;
    # loops grow so the counters stay open
    'Rega Payam': dict(dots='round', cap='round', body=1.1, ascend=0.8, descend=0.78, stretch=0.94,
                       corner=1.4, grow=0.5, weights={
        'Regular': dict(W_V=220, W_H=214, MARK=146, EYE=150, DOT=266, DOT_GAP=316, DOT_STACK=296,
                        XSCALE=1.03, CLASS=400),
        'Bold': dict(W_V=310, W_H=300, MARK=196, EYE=196, DOT=340, DOT_GAP=392, DOT_STACK=360,
                     XSCALE=1.07, CLASS=700),
    }),
}
# heights in the drawing (Rega Type): the top of the teeth, where ascenders rise above the dots,
# and the top of alef and lam (marks above it keep their distance from it)
TEETH, RISE, STEM = 788, 1150, 1429
_REG = FAMILIES['Rega Type']['weights']['Regular']


def set_style(family, weight):
    """Choose the family and pen. Call before glyphs.py is imported: its constants are built from these."""
    global FAMILY, WEIGHT, DOTS, CAP, GROW, STRETCH, CORNER, BODY, ASCEND, DESCEND, LEAN, \
        RESHAPE, W_V, W_H, W, BASE, MARK, EYE, DOT, DOT_GAP, DOT_STACK, XSCALE, CLASS, _K
    FAMILY, WEIGHT = family, weight
    f = FAMILIES[family]
    p = f['weights'][weight]
    DOTS, CAP, GROW = f['dots'], f.get('cap', 'butt'), f.get('grow', 0)
    STRETCH, CORNER = f.get('stretch', 1.0), f.get('corner', 1.0)
    BODY, ASCEND, DESCEND, LEAN = f.get('body', 1.0), f.get('ascend', 1.0), f.get('descend', 1.0), f.get('lean', 0)
    RESHAPE = (STRETCH, BODY, ASCEND, DESCEND, LEAN) != (1.0, 1.0, 1.0, 1.0, 0)
    W_V, W_H, MARK, EYE, DOT = p['W_V'], p['W_H'], p['MARK'], p['EYE'], p['DOT']
    DOT_GAP, DOT_STACK, XSCALE, CLASS = p['DOT_GAP'], p['DOT_STACK'], p['XSCALE'], p['CLASS']
    W = W_V
    BASE = W_H / 2     # centre of the joining stroke; its bottom edge sits on the baseline
    # strokes are drawn in a space stretched by _K vertically, then squeezed back;
    # the softening rim adds the same 2 * SOFT both ways, so it is left out of the ratio
    _K = (W_V - 2 * SOFT) / (W_H - 2 * SOFT)


set_style('Rega Type', 'Regular')


def ox(r):
    """A horizontal radius drawn for Regular, adjusted so the outer edge stays put in this weight
    (or, with GROW, moves out by that share of the extra weight, so heavy counters stay open)."""
    return r + (_REG['W_V'] - W_V) / 2 * (1 - GROW)


def oy(r):
    """A vertical radius drawn for Regular, adjusted like ox()."""
    return r + (_REG['W_H'] - W_H) / 2 * (1 - GROW)


def place(x, y, latin=False):
    """Where a point of the drawing lands in this family: its proportions, width and lean.

    Latin keeps its own proportions and is scaled with the body, so its x-height stays
    in step with the Kurdish teeth; it leans the other way, the way Latin is written.
    """
    if latin:
        x, y = x * BODY, y * BODY
    else:
        y = _height(y)
    # lean around the middle of the body, so a letter stays centred in its width
    slope = math.tan(math.radians(-LEAN if latin else LEAN))
    return x * STRETCH - (y - TEETH * BODY / 2) * slope, y


def _height(y):
    """The family's proportions: the body (baseline to teeth), the ascenders above the dots
    over the teeth, and the descenders, each scaled on its own. The joining stroke stays put,
    and so does the room between a tooth and the dots over it, or a stem and the mark over it."""
    top = TEETH * BODY
    if y <= 0:
        return y * DESCEND
    if y <= BASE:
        return y
    if y <= TEETH:
        return BASE + (y - BASE) * (top - BASE) / (TEETH - BASE)
    if y <= RISE:
        return top + y - TEETH
    rise = top + RISE - TEETH
    if y <= STEM:
        return rise + (y - RISE) * ASCEND
    return rise + (STEM - RISE) * ASCEND + y - STEM


def _placed(path, latin):
    """A centre line moved by place()."""
    if not RESHAPE:
        return path
    out = pathops.Path()
    for verb, pts in path.segments:
        pts = [place(x, y, latin) for x, y in pts]
        if verb == 'moveTo':
            out.moveTo(*pts[0])
        elif verb == 'lineTo':
            out.lineTo(*pts[0])
        elif verb == 'curveTo':
            out.cubicTo(*pts[0], *pts[1], *pts[2])
        elif verb == 'closePath':
            out.close()
    return out


class Line:
    """One centre line: straight segments, cubic curves and ellipse arcs."""

    def __init__(self, x, y, w=None):
        self.path = pathops.Path()
        self.path.moveTo(x, y)
        self.pt = (x, y)
        self.w = w  # own thickness (thin inner strokes); None = the normal stroke

    def to(self, x, y):
        self.path.lineTo(x, y)
        self.pt = (x, y)
        return self

    def curve(self, x1, y1, x2, y2, x, y):
        self.path.cubicTo(x1, y1, x2, y2, x, y)
        self.pt = (x, y)
        return self

    def arc(self, cx, cy, rx, ry, a0, a1):
        """Follow an ellipse from angle a0 to a1 (degrees; a1 > a0 turns anticlockwise)."""
        start = _on_ellipse(cx, cy, rx, ry, a0)
        if math.dist(start, self.pt) > 0.5:
            self.to(*start)
        steps = max(1, math.ceil(abs(a1 - a0) / 90))
        span = math.radians(a1 - a0) / steps
        k = 4 / 3 * math.tan(span / 4)
        t = math.radians(a0)
        for _ in range(steps):
            t2 = t + span
            x0, y0 = cx + rx * math.cos(t), cy + ry * math.sin(t)
            x3, y3 = cx + rx * math.cos(t2), cy + ry * math.sin(t2)
            self.curve(x0 - k * rx * math.sin(t), y0 + k * ry * math.cos(t),
                       x3 + k * rx * math.sin(t2), y3 - k * ry * math.cos(t2), x3, y3)
            t = t2
        return self

    def close(self):
        self.path.close()
        return self


def _on_ellipse(cx, cy, rx, ry, a):
    t = math.radians(a)
    return cx + rx * math.cos(t), cy + ry * math.sin(t)


def _bezier(c, t):
    s = 1 - t
    return (s ** 3 * c[0][0] + 3 * s * s * t * c[1][0] + 3 * s * t * t * c[2][0] + t ** 3 * c[3][0],
            s ** 3 * c[0][1] + 3 * s * s * t * c[1][1] + 3 * s * t * t * c[2][1] + t ** 3 * c[3][1])


def _split(c, t):
    """de Casteljau: the two halves of a cubic at t."""
    lerp = lambda p, q: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    p01, p12, p23 = lerp(c[0], c[1]), lerp(c[1], c[2]), lerp(c[2], c[3])
    p012, p123 = lerp(p01, p12), lerp(p12, p23)
    mid = lerp(p012, p123)
    return [c[0], p01, p012, mid], [mid, p123, p23, c[3]]


def ellipse(cx, cy, rx, ry=None):
    """A closed ellipse (a ring once stroked)."""
    ry = rx if ry is None else ry
    return Line(cx + rx, cy).arc(cx, cy, rx, ry, 0, 360).close()


def poly(points, r=150, w=None):
    """Straight segments through `points`, every corner rounded with radius r.

    r may be a list with one radius per corner; w is an own stroke thickness.
    """
    radii = r if isinstance(r, (list, tuple)) else [r] * (len(points) - 2)
    line = Line(*points[0], w=w)
    for i in range(1, len(points) - 1):
        p0, p1, p2 = points[i - 1], points[i], points[i + 1]
        d1 = _unit(p0, p1)
        d2 = _unit(p1, p2)
        turn = math.acos(max(-1.0, min(1.0, d1[0] * d2[0] + d1[1] * d2[1])))
        rad = radii[i - 1] * CORNER
        if rad <= 0 or turn < 1e-3:
            line.to(*p1)
            continue
        cut = min(rad * math.tan(turn / 2), math.dist(p0, p1) * 0.5, math.dist(p1, p2) * 0.5)
        rad = cut / math.tan(turn / 2)
        a = (p1[0] - d1[0] * cut, p1[1] - d1[1] * cut)
        b = (p1[0] + d2[0] * cut, p1[1] + d2[1] * cut)
        h = 4 / 3 * math.tan(turn / 4) * rad
        line.to(*a)
        line.curve(a[0] + d1[0] * h, a[1] + d1[1] * h, b[0] - d2[0] * h, b[1] - d2[1] * h, *b)
    line.to(*points[-1])
    return line


def _unit(p, q):
    dx, dy = q[0] - p[0], q[1] - p[1]
    n = math.hypot(dx, dy)
    return dx / n, dy / n


def dot(cx, cy, size, style):
    """One dot (nuqta) of the given ink width: 'round', 'diamond' (the Hambana emblem) or 'square'."""
    p = pathops.Path()
    if style == 'diamond':
        h = size / 2 * 1.25  # same ink as the round dot
        p.moveTo(cx, cy - h)
        p.lineTo(cx + h, cy)
        p.lineTo(cx, cy + h)
        p.lineTo(cx - h, cy)
        p.close()
        return p
    if style == 'round':
        h = size / 2
        k = h * 0.5523
        p.moveTo(cx + h, cy)
        p.cubicTo(cx + h, cy + k, cx + k, cy + h, cx, cy + h)
        p.cubicTo(cx - k, cy + h, cx - h, cy + k, cx - h, cy)
        p.cubicTo(cx - h, cy - k, cx - k, cy - h, cx, cy - h)
        p.cubicTo(cx + k, cy - h, cx + h, cy - k, cx + h, cy)
        p.close()
        return p
    h = size / 2 * 0.89  # same ink as the round dot
    c = h * 0.32
    k = c * 0.5523
    p.moveTo(cx - h + c, cy - h)
    p.lineTo(cx + h - c, cy - h)
    p.cubicTo(cx + h - c + k, cy - h, cx + h, cy - h + c - k, cx + h, cy - h + c)
    p.lineTo(cx + h, cy + h - c)
    p.cubicTo(cx + h, cy + h - c + k, cx + h - c + k, cy + h, cx + h - c, cy + h)
    p.lineTo(cx - h + c, cy + h)
    p.cubicTo(cx - h + c - k, cy + h, cx - h, cy + h - c + k, cx - h, cy + h - c)
    p.lineTo(cx - h, cy - h + c)
    p.cubicTo(cx - h, cy - h + c - k, cx - h + c - k, cy - h, cx - h + c, cy - h)
    p.close()
    return p


def outline(lines, extra=(), adv=None, latin=False):
    """Stroke the centre lines with the family's pen and merge everything into one clean outline.

    `extra` are ready-made shapes (dots, already placed); they are grown by SOFT like the strokes.
    `adv` is the letter's advance: strokes that join the next letter at its edges keep flat ends.
    `latin` places the lines as Latin (see place()).
    """
    total = pathops.Path()
    for p in _strokes(lines, adv, latin):
        total.addPath(p.transform(scaleY=1 / _K))
    for p in extra:
        total.addPath(p)
    total.simplify(clockwise=True)
    rim = pathops.Path()
    rim.addPath(total)
    rim.stroke(2 * SOFT, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    rim.convertConicsToQuads()
    return pathops.op(total, rim, pathops.PathOp.UNION, clockwise=True)


def _straight(p, q):
    """A straight segment as a cubic, so lines and curves go through the same code."""
    return [p, (p[0] + (q[0] - p[0]) / 3, p[1] + (q[1] - p[1]) / 3),
            (p[0] + (q[0] - p[0]) * 2 / 3, p[1] + (q[1] - p[1]) * 2 / 3), q]


# --- stroke ends ---------------------------------------------------------------------

def _strokes(lines, adv, latin):
    """The strokes, in the space squeezed by _K (see set_style).

    With CAP == 'round' every free end is rounded: the stroke is cut back by half its
    width and a disc put on the new end, so the letter keeps its size. An end that joins the
    next letter (on the baseline at the letter's edge) or runs on into another stroke stays
    flat, so joins never pinch.
    """
    k, soft = _K, SOFT
    paths, strokes = [], []
    for line in lines:
        path = _placed(line.path, latin)
        p = path.transform(scaleY=k)
        s = path.transform(scaleY=k)
        s.stroke((line.w or W_V) - 2 * soft, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        s.convertConicsToQuads()
        paths.append(p)
        strokes.append(s)
    if CAP == 'butt':
        return strokes
    out = []
    for i, (line, p) in enumerate(zip(lines, paths)):
        chain = _cubics(p)
        if not chain or any(verb == 'closePath' for verb, _ in p.segments):
            out.append(strokes[i])
            continue
        r = ((line.w or W_V) - 2 * soft) / 2
        others = [o for j, o in enumerate(strokes) if j != i]
        drawn = _cubics(line.path)
        free = [_free_end(chain, drawn, start, others, adv) for start in (True, False)]
        trimmed = _trim(chain, r if free[0] else 0, r if free[1] else 0) if any(free) else None
        if trimmed is None:
            out.append(strokes[i])
            continue
        c = pathops.Path()
        c.moveTo(*trimmed[0][0])
        for seg in trimmed:
            c.cubicTo(*seg[1], *seg[2], *seg[3])
        c.stroke(2 * r, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        c.convertConicsToQuads()
        for at_start, is_free in zip((True, False), free):
            if is_free:
                end = trimmed[0][0] if at_start else trimmed[-1][3]
                c.addPath(dot(end[0], end[1], 2 * r, 'round'))
        out.append(c)
    return out


def _cubics(path):
    """An open centre line as a chain of cubics (straight segments included)."""
    chain, cur = [], None
    for verb, pts in path.segments:
        if verb == 'moveTo':
            cur = pts[0]
        elif verb == 'lineTo':
            if math.dist(cur, pts[0]) > 0.01:
                chain.append(_straight(cur, pts[0]))
            cur = pts[0]
        elif verb == 'curveTo':
            chain.append([cur, *pts])
            cur = pts[-1]
    return chain


def _free_end(chain, drawn, at_start, others, adv):
    """Whether this end of a stroke is free (not a join, not running on into another stroke).

    `chain` is the stroke as placed and squeezed, `drawn` the same stroke as drawn in glyphs.py.
    """
    c = chain[0] if at_start else chain[-1][::-1]
    pt = c[0]
    inner = next((q for q in c[1:] if math.dist(q, pt) > 0.01), None)
    if inner is None:
        return False
    x, y = drawn[0][0] if at_start else drawn[-1][3]
    if adv is not None and abs(y - BASE) < 2 and (x < 1 or x > adv - 1):
        return False
    d = math.dist(pt, inner)
    probe = (pt[0] + (pt[0] - inner[0]) / d * 3, pt[1] + (pt[1] - inner[1]) / d * 3)
    return not any(o.contains(probe) for o in others)


def _seg_length(c, n=24):
    pts = [_bezier(c, i / n) for i in range(n + 1)]
    return sum(math.dist(p, q) for p, q in zip(pts, pts[1:]))


def _trim_start(chain, d):
    chain = list(chain)
    while chain and d > 0:
        c = chain[0]
        length = _seg_length(c)
        if length <= d:
            d -= length
            chain.pop(0)
            continue
        lo, hi = 0.0, 1.0
        for _ in range(30):
            mid = (lo + hi) / 2
            if _seg_length(_split(c, mid)[0], 12) < d:
                lo = mid
            else:
                hi = mid
        chain[0] = _split(c, (lo + hi) / 2)[1]
        d = 0
    return chain


def _trim(chain, a, b):
    """The chain with arc length a cut from its start and b from its end (None if too short)."""
    if a + b >= sum(_seg_length(c) for c in chain) - 1:
        return None
    reverse = lambda ch: [c[::-1] for c in reversed(ch)]
    return reverse(_trim_start(reverse(_trim_start(chain, a)), b))
