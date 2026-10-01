"""Turing's papers as they lie on the desk (s14e): an atlas of seven pages, ink in colour on transparent.

Only short, verified lines are set legibly (title pages, the question, the verdict, the table, the specimen answers,
Lovelace's sentence as Turing quotes it).  Everything else is typesetting texture: pseudo-words set to the journal's
measure, justified, with running heads, folios, footnotes — the look of the page, not its text.  (The 1936 and 1950
papers are public domain in the UK and China but probably not yet in the US; the manuscript and the letter are
unpublished and protected in the UK until 2039.  So: key lines only.)"""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

F = 'C:/Windows/Fonts/'
W, H = 1000, 1414                               # one page (A4-ish), px
PRINT = (24, 20, 18, 255)                       # letterpress black
PRINT2 = (40, 36, 34, 255)
PEN = (28, 34, 70, 255)                         # blue-black ink
PENCIL = (92, 90, 88, 170)
_F = {}


def font(name, size):
    k = (name, size)
    if k not in _F: _F[k] = ImageFont.truetype(F + name, size)
    return _F[k]


# ---------------- pseudo-text: the grain of English, not its words
LET = 'eeeeeeeeeeeettttttttaaaaaaaaooooooooiiiiiiinnnnnnnsssssshhhhhhrrrrrrdddddllllluuuucccmmmwwffggyyppbbvkjxqz'


def pword(r):
    n = r.choice([1, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 7, 7, 8, 9, 10, 11])
    w = ''.join(r.choice(LET) for _ in range(n))
    if n == 1: w = r.choice('aaaI')
    return w


def para(d, r, x0, y, width, lead, fnt, fi=None, n_lines=6, indent=30, fill=PRINT, gothic=None, last=True):
    """a justified paragraph of pseudo-words; returns y after it"""
    for li in range(n_lines):
        x = x0 + (indent if li == 0 else 0)
        words = []
        cw = 0
        while True:
            w = pword(r)
            if r.random() < .06: w = w.capitalize()
            if r.random() < .09: w += r.choice([',', ',', '.', ';', ':'])
            f = fi if (fi and r.random() < .05) else fnt
            if gothic and r.random() < .03: w, f = r.choice('MDUHK'), gothic
            ww = d.textlength(w, font=f)
            sp = d.textlength(' ', font=fnt)
            if cw + ww + (sp if words else 0) > width - (x - x0): break
            words.append((w, f, ww)); cw += ww + (sp if len(words) > 1 else 0)
        final = last and li == n_lines - 1
        if final: words = words[:max(2, int(len(words) * r.uniform(.35, .8)))]
        tot = sum(w[2] for w in words)
        gaps = len(words) - 1
        g = ((width - (x - x0)) - tot) / gaps if gaps and not final else d.textlength(' ', font=fnt)
        for w, f, ww in words:
            d.text((x, y), w, font=f, fill=fill)
            x += ww + g
        y += lead
    return y


def wrap_real(d, x, y, text, fnt, width, lead, fill=PRINT, indent=0, runs=None):
    """a real sentence, set to the measure (ragged last line), justified"""
    words = text.split(' ')
    lines, cur = [], []
    for w in words:
        t = ' '.join(cur + [w])
        if d.textlength(t, font=fnt) > width - (indent if not lines else 0) and cur: lines.append(cur); cur = [w]
        else: cur.append(w)
    lines.append(cur)
    for i, ln in enumerate(lines):
        xx = x + (indent if i == 0 else 0)
        wid = width - (indent if i == 0 else 0)
        tot = sum(d.textlength(w, font=fnt) for w in ln)
        g = (wid - tot) / (len(ln) - 1) if len(ln) > 1 and i < len(lines) - 1 else d.textlength(' ', font=fnt)
        for w in ln:
            d.text((xx, y), w, font=fnt, fill=fill); xx += d.textlength(w, font=fnt) + g
        y += lead
    return y


def hand(d, r, x0, y, width, lead, n, fnt, fill=PEN, slope=0.):
    """handwriting texture: pseudo-words in a script face, uneven baseline, some words struck out"""
    for li in range(n):
        x = x0 + r.uniform(-4, 10)
        while x < x0 + width - 40:
            w = pword(r)
            ww = d.textlength(w, font=fnt)
            if x + ww > x0 + width: break
            yy = y + r.uniform(-2, 2) + (x - x0) * slope
            d.text((x, yy), w, font=fnt, fill=fill)
            if r.random() < .035:
                d.line([(x - 2, yy + lead * .38), (x + ww + 2, yy + lead * .34)], fill=fill, width=3)
            x += ww + d.textlength(' ', font=fnt) * r.uniform(.9, 1.6)
        y += lead
    return y


def _cr(pts, n=6):
    """Catmull-Rom through pts"""
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1])
    return out


def cursive_word(r, x, y, xh, slant=.28):
    """one joined-up word that is not a word: arches, loops, the odd ascender and descender; returns (points, width)"""
    pts = [(x, y - xh * .1)]
    cx = x
    for _ in range(r.randint(2, 8)):
        kind = r.choice('nnmuueeeoollitaa')
        w = xh * r.uniform(.55, .85)
        if kind in 'nm':
            for _ in range(1 if kind == 'n' else 2):
                pts += [(cx + w * .15, y - xh), (cx + w * .5, y - xh * 1.05), (cx + w * .85, y)]; cx += w
        elif kind == 'u':
            pts += [(cx + w * .1, y - xh), (cx + w * .45, y), (cx + w * .9, y - xh)]; cx += w
        elif kind in 'eo':
            pts += [(cx + w * .7, y - xh * .75), (cx + w * .35, y - xh * .95), (cx + w * .2, y - xh * .4), (cx + w * .6, y), (cx + w, y - xh * .3)]; cx += w
        elif kind in 'lt':
            hgt = xh * r.uniform(2., 2.5)
            pts += [(cx + w * .5, y - hgt), (cx + w * .25, y - hgt * .8), (cx + w * .45, y), (cx + w * .8, y - xh * .2)]; cx += w * .8
        elif kind == 'i':
            pts += [(cx + w * .3, y - xh), (cx + w * .5, y)]; cx += w * .5
        else:
            pts += [(cx + w * .8, y - xh), (cx + w * .2, y - xh * .6), (cx + w * .4, y), (cx + w * .8, y - xh), (cx + w, y)]; cx += w
    if r.random() < .25:                                            # a descender
        pts += [(cx + xh * .3, y + xh * 1.2), (cx - xh * .1, y + xh * .9), (cx + xh * .4, y)]; cx += xh * .4
    pts = [(px + (y - py) * slant, py) for px, py in pts]
    return _cr(pts), cx - x


def cursive(d, r, x0, y, width, lead, n, xh=12, fill=(28, 34, 70, 215), w=2):
    """lines of joined-up handwriting nobody can read"""
    for li in range(n):
        x = x0 + r.uniform(0, 12)
        xe = x0 + width - (r.uniform(60, 300) if r.random() < .15 else 0)
        while x < xe - xh * 3:
            pts, ww = cursive_word(r, x, y + r.uniform(-2, 2), xh * r.uniform(.9, 1.1))
            if x + ww > xe: break
            d.line(pts, fill=fill, width=w, joint='curve')
            if r.random() < .03: d.line([(x - 3, y - xh * .5), (x + ww + 3, y - xh * .6)], fill=fill, width=w)
            x += ww + xh * r.uniform(1.1, 1.8)
        y += lead
    return y


# ---------------- the pages
def p_spirit(r):
    """c. 1932, Nature of Spirit: a manuscript on ruled paper (King's College, AMT/C/29)"""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i in range(34):                                                  # the ruling, faint blue; a red margin
        d.line([(0, 150 + i * 36), (W, 150 + i * 36)], fill=(120, 150, 190, 70), width=2)
    d.line([(110, 0), (110, H)], fill=(190, 80, 80, 80), width=2)
    d.text((W / 2, 86), 'Nature of Spirit', font=font('Inkfree.ttf', 52), fill=PEN, anchor='mm')
    d.line([(W / 2 - 190, 118), (W / 2 + 180, 114)], fill=PEN, width=3)
    y = cursive(d, r, 128, 150 + 26, W - 200, 36, 11)
    y = wrap_real(d, 128, y + 2, 'Personally, I think that spirit is really eternally connected with matter but certainly not always by the same kind of body.',
                  font('Inkfree.ttf', 36), W - 200, 54, fill=(20, 26, 64, 255))
    y = cursive(d, r, 128, y + 30, W - 200, 36, 12)
    d.ellipse([W - 260, 1090, W - 226, 1116], fill=(28, 34, 70, 120))     # a blot
    return im


def p_1936_title(r):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    fr, fi, fb = font('BOD_R.TTF', 25), font('BOD_I.TTF', 25), font('BOD_B.TTF', 27)
    L, R_ = 110, W - 110
    d.text((L, 70), '230', font=font('BOD_R.TTF', 22), fill=PRINT2)
    d.text((W / 2, 70), 'A. M. TURING', font=font('BOD_R.TTF', 22), fill=PRINT2, anchor='ma')
    d.text((R_, 70), '[Nov. 12,', font=font('BOD_R.TTF', 22), fill=PRINT2, anchor='ra')
    d.text((W / 2, 170), 'ON COMPUTABLE NUMBERS, WITH AN APPLICATION TO', font=fb, fill=PRINT, anchor='ma')
    d.text((W / 2, 208), 'THE ENTSCHEIDUNGSPROBLEM', font=fb, fill=PRINT, anchor='ma')
    d.text((W / 2, 268), 'By A. M. Turing.', font=font('BOD_R.TTF', 25), fill=PRINT, anchor='ma')
    d.text((W / 2, 312), '[Received 28 May, 1936.—Read 12 November, 1936.]', font=font('BOD_I.TTF', 22), fill=PRINT, anchor='ma')
    y = wrap_real(d, L, 372, 'The "computable" numbers may be described briefly as the real numbers whose expressions as a decimal are calculable by finite means.',
                  fr, R_ - L, 36, indent=30)
    y = para(d, r, L, y, R_ - L, 36, fr, fi, 12, indent=0)
    y = para(d, r, L, y, R_ - L, 36, fr, fi, 8)
    y = para(d, r, L, y, R_ - L, 36, fr, fi, 5)
    d.line([(L, y + 14), (L + 180, y + 14)], fill=PRINT, width=2)       # footnote rule
    para(d, r, L, y + 28, R_ - L, 26, font('BOD_R.TTF', 18), None, 2, indent=20)
    return im


def p_1936_table(r):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    fr, fi = font('BOD_R.TTF', 25), font('BOD_I.TTF', 25)
    L, R_ = 110, W - 110
    d.text((L, 70), '1936.]', font=font('BOD_R.TTF', 22), fill=PRINT2)
    d.text((W / 2, 70), 'ON COMPUTABLE NUMBERS.', font=font('BOD_R.TTF', 22), fill=PRINT2, anchor='ma')
    d.text((R_, 70), '233', font=font('BOD_R.TTF', 22), fill=PRINT2, anchor='ra')
    d.text((W / 2, 130), 'Circular and circle-free machines.', font=fi, fill=PRINT, anchor='ma')
    y = para(d, r, L, 172, R_ - L, 36, fr, fi, 7)
    d.text((W / 2, y + 16), '3.  Examples of computing machines.', font=fi, fill=PRINT, anchor='ma')
    y = wrap_real(d, L, y + 66, 'I. A machine can be constructed to compute the sequence 010101....', fr, R_ - L, 36, indent=30)
    y = para(d, r, L, y, R_ - L, 36, fr, fi, 6)
    # the table
    x0, x1, x2, x3, x4 = 170, 330, 470, 660, 840
    ty = y + 26
    d.text(((x0 + x2) / 2, ty), 'Configuration', font=fi, fill=PRINT, anchor='ma')
    d.text(((x2 + x4) / 2, ty), 'Behaviour', font=fi, fill=PRINT, anchor='ma')
    d.line([(x0 - 20, ty + 36), (x4 + 20, ty + 36)], fill=PRINT, width=2)
    for x, h_ in ((x0, 'm-config.'), (x1, 'symbol'), (x2, 'operations'), (x3, 'final m-config.')):
        d.text((x, ty + 46), h_, font=font('BOD_I.TTF', 21), fill=PRINT)
    d.line([(x0 - 20, ty + 80), (x4 + 20, ty + 80)], fill=PRINT, width=2)
    for x in (x1 - 20, x2 - 20, x3 - 20): d.line([(x, ty), (x, ty + 300)], fill=PRINT, width=2)
    for i, row in enumerate([('b', 'None', 'P0, R', 'c'), ('c', 'None', 'R', 'e'), ('e', 'None', 'P1, R', 'f'), ('f', 'None', 'R', 'b')]):
        yy = ty + 100 + i * 50
        for x, v, f in zip((x0 + 20, x1, x2, x3 + 40), row, (font('BOD_I.TTF', 28), fr, fr, font('BOD_I.TTF', 28))):
            d.text((x, yy), v, font=f, fill=PRINT)
    y = para(d, r, L, ty + 330, R_ - L, 36, fr, fi, 8)
    return im


def p_1936_verdict(r):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    fr, fi, fg = font('BOD_R.TTF', 25), font('BOD_I.TTF', 25), font('OLDENGL.TTF', 26)
    L, R_ = 110, W - 110
    d.text((L, 70), '1936.]', font=font('BOD_R.TTF', 22), fill=PRINT2)
    d.text((W / 2, 70), 'ON COMPUTABLE NUMBERS.', font=font('BOD_R.TTF', 22), fill=PRINT2, anchor='ma')
    d.text((R_, 70), '247', font=font('BOD_R.TTF', 22), fill=PRINT2, anchor='ra')
    y = para(d, r, L, 130, R_ - L, 36, fr, fi, 8, gothic=fg)
    y = para(d, r, L, y, R_ - L, 36, fr, fi, 9, gothic=fg)
    y = para(d, r, L, y, R_ - L, 36, fr, fi, 7, gothic=fg, last=False)
    # the verdicts: set as in the paper, the machine's name in black letter
    x = L
    for w, f in [(s, fr) for s in 'Thus both verdicts are impossible and we conclude that there can be no machine'.split()] + [('D.', fg)]:
        ww = d.textlength(w + ' ', font=f)
        if x + ww > R_: x = L; y += 36
        d.text((x, y), w, font=f, fill=PRINT); x += ww
    d.line([(L - 4, y + 34), (x - 10, y + 32)], fill=PENCIL, width=3)        # someone underlined it, in pencil
    d.line([(L - 4, y - 2), (R_ - 20, y - 4)], fill=PENCIL, width=3)
    y += 36
    y = para(d, r, L, y, R_ - L, 36, fr, fi, 6, gothic=fg)
    d.text((R_ + 30, y - 380), '?', font=font('Inkfree.ttf', 60), fill=PENCIL)  # a pencil query in the margin
    return im


def p_1950_title(r):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    fr, fi = font('GARA.TTF', 27), font('GARAIT.TTF', 27)
    L, R_ = 110, W - 110
    d.text((L, 64), 'VOL. LIX. No. 236.]', font=font('GARA.TTF', 21), fill=PRINT2)
    d.text((R_, 64), '[October, 1950', font=font('GARA.TTF', 21), fill=PRINT2, anchor='ra')
    d.line([(L, 100), (R_, 100)], fill=PRINT, width=2)
    d.text((W / 2, 150), 'M I N D', font=font('GARABD.TTF', 64), fill=PRINT, anchor='mm')
    d.text((W / 2, 208), 'A QUARTERLY REVIEW', font=font('GARA.TTF', 22), fill=PRINT, anchor='mm')
    d.text((W / 2, 238), 'OF', font=font('GARA.TTF', 16), fill=PRINT, anchor='mm')
    d.text((W / 2, 266), 'PSYCHOLOGY AND PHILOSOPHY', font=font('GARA.TTF', 22), fill=PRINT, anchor='mm')
    d.line([(L, 300), (R_, 300)], fill=PRINT, width=2); d.line([(L, 305), (R_, 305)], fill=PRINT, width=1)
    d.text((W / 2, 360), 'I.—COMPUTING MACHINERY AND', font=font('GARA.TTF', 30), fill=PRINT, anchor='mm')
    d.text((W / 2, 398), 'INTELLIGENCE', font=font('GARA.TTF', 30), fill=PRINT, anchor='mm')
    d.text((W / 2, 448), 'By A. M. Turing', font=font('GARA.TTF', 25), fill=PRINT, anchor='mm')
    d.text((W / 2, 510), '1. The Imitation Game.', font=fi, fill=PRINT, anchor='mm')
    y = wrap_real(d, L, 552, 'I propose to consider the question, "Can machines think?"', fr, R_ - L, 38, indent=30)
    y = para(d, r, L, y, R_ - L, 38, fr, fi, 9, indent=0)
    y = para(d, r, L, y, R_ - L, 38, fr, fi, 8)
    y = para(d, r, L, y, R_ - L, 38, fr, fi, 4)
    return im


def p_1950_qa(r):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    fr, fi = font('GARA.TTF', 27), font('GARAIT.TTF', 27)
    L, R_ = 110, W - 110
    d.text((L, 64), '434', font=font('GARA.TTF', 21), fill=PRINT2)
    d.text((W / 2, 64), 'A. M. TURING :', font=font('GARA.TTF', 21), fill=PRINT2, anchor='ma')
    y = para(d, r, L, 120, R_ - L, 38, fr, fi, 9)
    y += 8
    for q, a in [('Please write me a sonnet on the subject of the Forth Bridge.', 'Count me out on this one. I never could write poetry.'),
                 ('Add 34957 to 70764.', '(Pause about 30 seconds and then give as answer) 105621.'),
                 ('Do you play chess?', 'Yes.')]:
        y = wrap_real(d, L + 40, y + 6, 'Q: ' + q, fr, R_ - L - 80, 38)
        y = wrap_real(d, L + 40, y, 'A: ' + a, fr, R_ - L - 80, 38)
    y = para(d, r, L, y + 16, R_ - L, 38, fr, fi, 9)
    return im


def p_1950_lovelace(r):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    fr, fi = font('GARA.TTF', 27), font('GARAIT.TTF', 27)
    L, R_ = 110, W - 110
    d.text((L, 64), '450', font=font('GARA.TTF', 21), fill=PRINT2)
    d.text((W / 2, 64), 'A. M. TURING :', font=font('GARA.TTF', 21), fill=PRINT2, anchor='ma')
    y = para(d, r, L, 120, R_ - L, 38, fr, fi, 8)
    d.text((L + 30, y + 14), "(6) Lady Lovelace's Objection.", font=fi, fill=PRINT)
    x = L + 30 + d.textlength("(6) Lady Lovelace's Objection.  ", font=fi)
    y = para(d, r, L, y + 14 + 38, R_ - L, 38, fr, fi, 2, indent=0, last=False)
    y = wrap_real(d, L, y, '"The Analytical Engine has no pretensions to originate anything. It can do whatever we know how to order it to perform" (her italics).',
                  fr, R_ - L, 38)
    y = para(d, r, L, y, R_ - L, 38, fr, fi, 8, indent=0)
    y = para(d, r, L, y, R_ - L, 38, fr, fi, 7)
    return im


PAGES = [p_spirit, p_1936_title, p_1936_table, p_1936_verdict, p_1950_title, p_1950_qa, p_1950_lovelace]
# paper stock per page: base colour (sRGB), how yellowed, crease (0 none, 1 horizontal fold at 1/3, 2 at 1/2)
STOCK = [((238, 226, 196), .8, 2), ((236, 228, 206), .55, 0), ((236, 228, 206), .55, 1), ((236, 228, 206), .55, 0),
         ((243, 239, 228), .25, 0), ((243, 239, 228), .25, 1), ((243, 239, 228), .25, 0)]


def atlas():
    A = Image.new('RGBA', (W * 4, H * 2), (0, 0, 0, 0))
    for i, fn in enumerate(PAGES):
        im = fn(random.Random(100 + i))
        # printer's ink: a hair of spread, so type sits in the paper rather than on it
        a = im.split()[3].filter(ImageFilter.GaussianBlur(.6))
        im.putalpha(a)
        A.paste(im, ((i % 4) * W, (i // 4) * H))
    return A


if __name__ == '__main__':
    import sys
    A = atlas()
    out = Image.new('RGB', A.size, (240, 232, 214))
    out.paste(A, (0, 0), A)
    out.resize((A.width // 2, A.height // 2), Image.LANCZOS).save(sys.argv[1])
