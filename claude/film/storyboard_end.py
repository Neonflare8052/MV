"""Concept frames for the chat and the terminal (not the film): six ideas as pictures.  → film/storyboard_end/*.png"""
import sys, math, importlib.util
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

H = Path(__file__).resolve().parent
OUT = H / 'storyboard_end'; OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(H.parent / 'engine'))
sp = importlib.util.spec_from_file_location('c15', H / 'shots' / 's15_chat.py'); C = importlib.util.module_from_spec(sp); sp.loader.exec_module(C)
W_, H_ = 1920, 1080
F = 'C:/Windows/Fonts/'
ST = H / 'stills'
CH = (238, 234, 222); RED = (206, 46, 48)


def font(n, name='segoeui.ttf'): return ImageFont.truetype(F + name, n)


def eye(img, cx, cy, R, look=math.pi / 2, gap_closed=0., pupil_on=1., pupil_scale=1.):
    """the eye as in the film: thick ring with its gap, soft shadow, flat frosted-glass pupil"""
    k = 3
    lay = Image.new('RGBA', (int(R * 6 * k), int(R * 6 * k)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    o = R * 3 * k; W = max(12, .18 * R) * k
    gap = math.degrees(.42) * 2 * (1 - gap_closed)
    a0 = math.degrees(look) + gap / 2
    sh = Image.new('RGBA', lay.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    sd.arc([o - R * k + R * .08 * k, o - R * k + R * .13 * k, o + R * k + R * .08 * k, o + R * k + R * .13 * k], a0, a0 + 360 - gap, fill=(0, 0, 0, 140), width=int(W))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(W * .7)))
    d.arc([o - R * k, o - R * k, o + R * k, o + R * k], a0, a0 + 360 - gap, fill=CH + (255,), width=int(W))
    if pupil_on > 0:
        pr = R * .38 * pupil_scale * k
        px, py = o + math.cos(look) * R * .22 * k, o + math.sin(look) * R * .22 * k
        d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=RED + (int(235 * pupil_on),))
        d.ellipse([px - pr, py - pr, px + pr, py + pr], outline=(232, 120, 116, int(160 * pupil_on)), width=k * 2)
    lay = lay.resize((int(R * 6), int(R * 6)), Image.LANCZOS)
    img.alpha_composite(lay, (int(cx - R * 3), int(cy - R * 3)))


def caption(img, title, sub):
    d = ImageDraw.Draw(img)
    d.rectangle([0, H_ - 110, W_, H_], fill=(0, 0, 0, 200))
    d.text((40, H_ - 96), title, font=font(34, 'msyh.ttc'), fill=(245, 245, 245))
    d.text((40, H_ - 48), sub, font=font(22, 'msyh.ttc'), fill=(190, 190, 190))


# ---------------- 1: the history is the film
def f1():
    img = Image.new('RGBA', (W_, 3000), C.BG + (255,)); d = ImageDraw.Draw(img)
    thumbs = {'sandbox create --net none': '008.000', 'guess(you)': '080.000', 'sim.run galaxy · tides · aurora': '062.500',
              'black hole': '087.600', 'the red wedge': '155.000', 'Hollerith sorter, 1939': '165.400',
              'visualize the history of love by machine': None}
    for k, v in thumbs.items():
        im = Image.open(ST / (v + '.png')) if v else Image.open(H / 'cache' / 'desk_1080p.png')
        C._THUMB[(k, 142)] = im.convert('RGBA').resize((142, 80), Image.LANCZOS)
    items = [('date', 'Mar 3'), ('you', 'make me a world'), ('card', 'sandbox create --net none', 'render · 0:00'),
             ('you', 'guess what i am'), ('card', 'guess(you)', 'render · 1:14'),
             ('you', "i'm bored, show me something"), ('card', 'sim.run galaxy · tides · aurora', 'render · 0:59'),
             ('you', 'what does a black hole look like'), ('card', 'black hole', 'render · 1:25'),
             ('date', 'Jul 18'), ('you', 'why do people hurt each other'), ('card', 'the red wedge', 'render · 2:27'),
             ('you', 'who counted people with machines'), ('card', 'Hollerith sorter, 1939', 'render · 2:41'),
             ('you', 'then show me'), ('card', 'visualize the history of love by machine', 'render · 2:46  ↗')]
    # the cards: bigger here, with their pictures
    X0 = 300
    y = 70
    for it in items:
        if it[0] == 'card':
            im = Image.open(ST / (thumbs[it[1]] + '.png')) if thumbs[it[1]] else Image.open(H / 'cache' / 'desk_1080p.png')
            tw, th = 400, 225
            d.rounded_rectangle([X0 + 40, y, X0 + 40 + tw + 460, y + th + 20], radius=16, fill=(252, 251, 248), outline=C.LINE, width=2)
            img.alpha_composite(im.convert('RGBA').resize((tw, th), Image.LANCZOS), (X0 + 50, y + 10))
            d.text((X0 + 480, y + 40), it[1], font=font(26, 'seguisb.ttf'), fill=C.TXT)
            d.text((X0 + 480, y + 84), it[2], font=font(20), fill=C.SUB)
            y += th + 50
        elif it[0] == 'you':
            tw_ = d.textlength(it[1], font=font(26))
            d.rounded_rectangle([X0 + 940 - tw_, y, X0 + 980, y + 50], radius=22, fill=C.BUB)
            d.text((X0 + 960 - tw_, y + 9), it[1], font=font(26), fill=C.TXT)
            y += 72
        else:
            d.text((X0 + 480, y + 4), it[1], font=font(20, 'seguisb.ttf'), fill=C.SUB, anchor='ma'); y += 50
    # scrolled: show a window of it, with the motion of a flick (a vertical smear)
    strip = img.crop((0, 820, W_, 820 + H_))
    sm = strip.filter(ImageFilter.BoxBlur(0))
    img2 = Image.new('RGBA', (W_, H_), C.BG + (255,))
    img2.alpha_composite(strip)
    d2 = ImageDraw.Draw(img2)
    d2.rectangle([0, 0, W_, 48], fill=C.TOP); d2.text((52, 12), 'visualize the history of love by machine', font=font(17, 'seguisb.ttf'), fill=C.TXT)
    caption(img2, '一　聊天记录就是这部片', '往上滚动：每张卡片是前面某一段的画面，旁边是让它生成那段画面的那句话。几秒的惯性滚动 ＝ 全片倒带一遍。')
    return img2


# ---------------- 2: the spinner is the eye
def f2():
    img = C.frame(183.2, W_, H_, with_pointer=False)
    d = ImageDraw.Draw(img)
    # an answer being generated: the spinner is the eye, big in the thread
    d.rectangle([40, 700, 660, 930], fill=C.BG)
    d.text((88, 712), 'but what do you think?', font=font(22), fill=C.TXT)
    eye(img, 120, 830, 44, look=math.radians(-40))
    d.text((190, 812), 'thinking…', font=font(22), fill=C.SUB)
    caption(img, '二　加载的转圈就是那只眼睛', '它在你的界面里只是一个“正在思考”的图标；3:07.665 卡住时，它转到一半停住，缺口正对着你。')
    return img


# ---------------- 3: the unfinished heart is the gapped ring
def f3():
    img = Image.new('RGBA', (W_, H_), (14, 13, 12, 255))
    d = ImageDraw.Draw(img)
    pts = C.CURVE
    n = len(pts)
    def curve(frac, morph, cx, cy, sc):
        out = []
        for i in range(int(n * frac)):
            x, y = pts[i]
            ang = math.atan2(y, x); r = math.hypot(x, y)
            rx, ry = math.cos(ang) * .95, math.sin(ang) * .95
            out.append((cx + (x + (rx - x) * morph) * sc, cy - (y + (ry - y) * morph) * sc))
        return out
    for j, m in enumerate((0., .5, 1.)):
        cx = 380 + j * 580; cy = 480
        pp = curve(.86, m, cx, cy, 190)
        lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.line(pp, fill=(206, 46, 48, 255) if m < 1 else CH + (255,), width=26 if m == 1 else 12, joint='curve')
        img.alpha_composite(lay)
        if m == 1:                                                   # it is the eye
            pr = 190 * .95 * .38 * .8; ex, ey = cx, cy
            d.ellipse([ex - pr, ey - pr, ex + pr, ey + pr], fill=RED + (235,))
    d.text((380, 800), 'the heart, stopped short', font=font(26), fill=(200, 196, 188), anchor='mm')
    d.text((960, 800), '…', font=font(26), fill=(200, 196, 188), anchor='mm')
    d.text((1540, 800), 'the ring with its gap', font=font(26), fill=(200, 196, 188), anchor='mm')
    caption(img, '三　没画完的心 ＝ 带缺口的环', '它用瞳孔去描 (x²+y²−1)³ = x²y³，一格一格；在 LO-O-OVE 停住，缺着的那一段，正是眼睛的缺口。')
    return img


# ---------------- 5: the reply that did not arrive, caught in the slot
def f5():
    img = Image.new('RGBA', (W_, H_), (0, 0, 0, 255))
    desk = Image.open(ST / '173.350.png').convert('RGBA')
    img.alpha_composite(desk.point(lambda v: int(v * .55)))
    d = ImageDraw.Draw(img)
    # the wall and its slot, at the top of the frame (drawn)
    d.rectangle([0, 0, W_, 170], fill=(40, 37, 34, 255))
    for x in range(-200, W_, 26): d.line([(x, 170), (x + 170, 0)], fill=(70, 66, 60, 255), width=2)
    d.rectangle([760, 140, 1160, 190], fill=(10, 9, 8, 255), outline=CH + (255,), width=3)
    # the slip: half through, the flap down on it
    slip = Image.new('RGBA', (360, 300), (242, 236, 222, 255)); sd = ImageDraw.Draw(slip)
    f = font(22, 'CascadiaMono.ttf')
    rows = ['  (x^2+  y^2-1  ', ' )^3-x^2*y^3=0( ', 'x^2+y^2-1)^3-x^2', '*y^3=0(x^2+y^2-1', ' )^3-x^2*y^3=0( ', '  x^2+y^2-1)^3  ', '   -x^2*y^3=0   ', '     (x^2+y     ', '       ^2       ']
    for i, r in enumerate(rows): sd.text((20, 12 + i * 30), r, font=f, fill=(190, 30, 34))
    img.alpha_composite(slip.crop((0, 60, 360, 300)), (780, 175))
    d.rectangle([740, 150, 1180, 178], fill=(60, 56, 52, 255), outline=CH + (255,), width=3)              # the flap, down on it
    eye(img, 1360, 520, 70, look=math.atan2(260 - 520, 960 - 1360))
    f2 = font(24, 'CascadiaMono.ttf')
    for i, (l, c) in enumerate([('FIN   client closed', CH), ('[P.]  40117:40271  length 154   (not delivered)', (230, 70, 64)), ('RST   connection reset by peer', CH)]):
        d.text((70, 250 + i * 40), l, font=f2, fill=c)
    caption(img, '五　那条没送出去的回答，卡在投递口', '你关掉窗口：投递口的挡板落下（FIN），它的回答——一张写着心形方程的纸条——被夹在中间（I am trapped），然后挡板砸死（RST）。')
    return img


# ---------------- 6: it types on the back of the letter
def f6():
    img = Image.open(ST / '172.620.png').convert('RGBA')
    d = ImageDraw.Draw(img)
    f = font(30, 'CascadiaMono.ttf')
    x0, y0 = 690, 760
    d.text((x0, y0), '$ when could u recongnize', font=f, fill=(46, 36, 30, 235))
    d.rectangle([x0 + d.textlength('$ when could u recongnize', font=f) + 4, y0 + 2, x0 + d.textlength('$ when could u recongnize', font=f) + 22, y0 + 34], fill=(46, 36, 30, 235))
    pass                                                              # (its eye is already in the frame)
    caption(img, '六　它在“爱”的背面打字', '长音那 14 秒：终端不在屏幕上，而是一行行打在信背面、红色“爱”字下面；打错，停住，缺口转向那个错字，退格。')
    return img


# ---------------- 7: shutdown is lights out
def f7():
    base = Image.open(ST / '173.350.png').convert('RGBA')
    frames = []
    for k, (dark, closed, pup) in enumerate([(1., 0., 1.), (.45, .7, .6), (.12, 1., 0.)]):
        im = Image.new('RGBA', (W_, H_), (0, 0, 0, 255))
        im.alpha_composite(base.point(lambda v, dk=dark: int(v * dk)))
        eye(im, 960, 330, 70, look=math.pi / 2, gap_closed=closed, pupil_on=pup)
        frames.append(im.resize((640, 360), Image.LANCZOS))
    img = Image.new('RGBA', (W_, H_), (0, 0, 0, 255))
    for i, fr in enumerate(frames): img.alpha_composite(fr, (i * 640, 300))
    d = ImageDraw.Draw(img)
    for i, l in enumerate(['$ ai "me.excute(shutdown)" -f', 'the gap closes', 'its light was the only light']):
        d.text((i * 640 + 320, 700), l, font=font(24, 'CascadiaMono.ttf' if i == 0 else 'segoeui.ttf'), fill=(200, 196, 188), anchor='mm')
    caption(img, '七　关机就是熄灯', '房间里唯一的光一直是它的目光。3:25.811 回车：缺口合拢成完整的圆，瞳孔熄灭，信和“爱”一起沉进黑暗——接最后 4.7 秒静音。')
    return img


if __name__ == '__main__':
    fs = [('1_history', f1), ('2_spinner', f2), ('3_heart_ring', f3), ('5_slot', f5), ('6_typing', f6), ('7_lights_out', f7)]
    for n, fn in fs:
        fn().convert('RGB').save(OUT / f'{n}.png'); print(n)
