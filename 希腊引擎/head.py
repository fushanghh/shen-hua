# 神话风 · 希腊 · 百眼巨人（阿耳戈斯） —— 纯代码剪纸壁画木偶动画
import sys, os, math, re, subprocess, numpy as np, cairocffi as cairo, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from puppet import shape, line, smooth, clip_shape, J, taper, rgb, LINE, wolf
from grk import *
from egy import P
from PIL import Image, ImageDraw, ImageFont

FPS = 24; OW, OH = 1440, 1080; SW, SH = 1920, 800; GY = 760
PY = 40; PH = 1000; K = 0.75; OFF = 250
FZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '字体', 'NotoSerifSC-Bold.otf')
FEB = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
FE = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'

SAND = rgb('e0cca2'); SAND2 = rgb('cbb68f'); SAND3 = rgb('b7a380'); GOLD = rgb('bf9746'); LAP = rgb('26407d'); LAP2 = rgb('192c4e')
RED = rgb('90452a'); TURQ = rgb('416773'); BONE = rgb('efe4c8'); NIGHT = rgb('0f1830')

def seg(t, a, b): return E((t - a) / (b - a)) if b > a else float(t >= a)
def lerp(a, b, u): return a + (b - a) * u
def surf(w, h):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); return s, cairo.Context(s)
def nmap(seed, w, h, scales=((8, 1.0), (24, 0.5), (80, 0.25), (240, 0.12))):
    r = np.random.default_rng(seed); acc = np.zeros((h, w), np.float32)
    for n, a in scales:
        g = r.random((max(2, h * n // w), n)).astype(np.float32); acc += cv2.resize(g, (w, h), interpolation=cv2.INTER_CUBIC) * a
    acc -= acc.min(); return acc / acc.max()
def paint_arr(c, a, x=0, y=0):
    a = (np.clip(a, 0, 1) * 255).astype(np.uint8); h, w = a.shape[:2]
    bgra = np.dstack([a[..., 2], a[..., 1], a[..., 0], np.full((h, w), 255, np.uint8)])
    s = cairo.ImageSurface.create_for_data(bytearray(bgra.tobytes()), cairo.FORMAT_ARGB32, w, h); c.set_source_surface(s, x, y); c.paint()
def glow(c, x, y, r, col, a):
    if a <= 0: return
    g = cairo.RadialGradient(x, y, 1, x, y, r); g.add_color_stop_rgba(0, *col, a); g.add_color_stop_rgba(1, *col, 0); c.set_source(g)
    c.arc(x, y, r, 0, 7); c.fill()
def bands(c, cols, y0, y1, x0=-300, x1=SW + 300):
    h = (y1 - y0) / len(cols)
    for i, col in enumerate(cols): c.rectangle(x0, y0 + i * h, x1 - x0, h + 1); c.set_source_rgb(*col); c.fill()
def rect(c, x, y, w, h, col, a=1): c.rectangle(x, y, w, h); c.set_source_rgba(*col, a); c.fill()

# ---------------- 特效 ----------------
def cross_star(c, x, y, r, a, col=(1, 0.95, 0.75)):
    if a <= 0: return
    glow(c, x, y, r * 1.5, col, 0.55 * a)
    for ang, L in ((0, r), (math.pi / 2, r), (math.pi / 4, r * 0.45), (-math.pi / 4, r * 0.45)):
        dx, dy = math.cos(ang) * L, math.sin(ang) * L
        c.new_path(); c.move_to(x - dx, y - dy); c.line_to(x + dx, y + dy); c.set_source_rgba(1, 0.97, 0.85, a); c.set_line_width(3); c.stroke()
def stars(c, t, n=160, seed=4, ymin=-OFF, ymax=500, a=1.0):
    if a <= 0: return
    r = np.random.default_rng(seed)
    for i in range(n):
        x, y = r.uniform(-100, SW + 100), r.uniform(ymin, ymax); rr = r.uniform(1.2, 3.4); ph = r.uniform(0, 6.3)
        circ(c, x, y, rr, (0.98, 0.9, 0.7), a * (0.3 + 0.6 * (0.5 + 0.5 * math.sin(t * 2.4 + ph))))
def dust(c, x, y, age, n=9, s=1.0, col=None, seed=0):
    if age < 0 or age > 1.6: return
    col = col or rgb('d8c49a'); r = np.random.default_rng(seed + int(x))
    for i in range(n):
        a = r.uniform(math.pi, 2 * math.pi); v = r.uniform(50, 150) * s
        circ(c, x + math.cos(a) * v * age * 1.5, y + math.sin(a) * v * age * 0.5, (14 + age * 30) * s * r.uniform(.6, 1.2), col, max(0, .5 * (1 - age / 1.6)))
def sparks(c, x, y, age, n=14, col=None, seed=0, spd=1.0, life=0.9):
    if age < 0 or age > life: return
    col = col or rgb('f6d070'); r = np.random.default_rng(seed)
    for i in range(n):
        a = r.uniform(0, 2 * math.pi); v = r.uniform(150, 420) * spd
        px = x + math.cos(a) * v * age; py = y + math.sin(a) * v * age + 200 * age * age
        c.move_to(px, py); c.line_to(px - math.cos(a) * 16, py - math.sin(a) * 16); c.set_source_rgba(*col, 1 - age / life); c.set_line_width(3); c.stroke()
def motes(c, t, x0, y0, x1, y1, n=30, col=(1, 0.85, 0.45), seed=1, a=1.0, rise=40):
    if a <= 0: return
    r = np.random.default_rng(seed)
    for i in range(n):
        x = r.uniform(x0, x1); y = r.uniform(y0, y1); ph = r.uniform(0, 6.3); sp = r.uniform(0.5, 1.5)
        yy = y - ((t * rise * sp) % (y1 - y0 + 1)); yy = yy if yy > y0 else yy + (y1 - y0)
        circ(c, x + 14 * math.sin(t * sp + ph), yy, r.uniform(2, 5), col, a * (0.4 + 0.5 * math.sin(t * 3 + ph) ** 2))
def heart(c, x, y, s, col, a):
    if a <= 0: return
    c.save(); c.translate(x, y); c.scale(s, s); c.new_path(); c.move_to(0, 6)
    c.curve_to(-14, -4, -8, -16, 0, -8); c.curve_to(8, -16, 14, -4, 0, 6); c.close_path(); c.set_source_rgba(*col, a); c.fill(); c.restore()
def vignette(c, amt, col=(0.05, 0.03, 0.02)):
    g = cairo.RadialGradient(SW / 2, SH / 2 - 60, 380, SW / 2, SH / 2 - 60, 1250)
    g.add_color_stop_rgba(0, *col, 0); g.add_color_stop_rgba(1, *col, amt); c.set_source(g); c.paint()
def wind(c, t, x, y, L, a, seed=0, col=(0.95, 0.95, 1.0)):
    if a <= 0: return
    r = np.random.default_rng(seed)
    for k in range(6):
        yy = y + r.uniform(-40, 40); ph = r.uniform(0, 6)
        pts = [(x + i * L / 20, yy + 10 * math.sin(i * 0.6 + t * 6 + ph)) for i in range(21)]
        c.new_path(); c.move_to(*pts[0])
        for p_ in pts[1:]: c.line_to(*p_)
        c.set_source_rgba(*col, a * 0.7); c.set_line_width(3); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
def whirl(c, x, y, R, t, a, col=(0.95, 0.97, 1.0)):
    if a <= 0: return
    for k in range(7):
        rr = R * (0.3 + 0.1 * k); a0 = t * (5 - k * 0.3) + k
        c.new_path(); c.arc(x, y - k * R * 0.12, rr, a0, a0 + 4.2)
        c.set_source_rgba(*col, a * (0.8 - k * 0.08)); c.set_line_width(4); c.stroke()
def idea(c, x, y, a, t):
    if a <= 0: return
    cross_star(c, x, y, 40 * a, a)
    for k in range(6):
        ang = k * math.pi / 3 + t; line(c, [(x + math.cos(ang) * 50 * a, y + math.sin(ang) * 50 * a), (x + math.cos(ang) * 74 * a, y + math.sin(ang) * 74 * a)], rgb('f2c95a'), 4)


# ---------------- 背景（缓存） ----------------
BGC = {}; BH = 1460; BO = 300
def bgcache(name, fn):
    if name not in BGC:
        s, c = surf(SW, BH); c.translate(0, BO); fn(c); s.flush(); BGC[name] = s
    return BGC[name]
def paintbg(c, name, fn): c.set_source_surface(bgcache(name, fn), 0, -BO); c.paint()
def mottle(c, c1, c2, seed, y0=-BO, y1=BH - BO):
    n = nmap(seed, SW // 2, (y1 - y0) // 2); n = cv2.resize(n, (SW, y1 - y0))
    a = np.array(c1)[None, None] * (1 - n[..., None]) + np.array(c2)[None, None] * n[..., None]
    paint_arr(c, a, 0, y0)
def cracks(c, seed, n=26, y0=-200, y1=700, col=None):
    r = np.random.default_rng(seed)
    for i in range(n):
        x, y = r.uniform(0, SW), r.uniform(y0, y1); pts = [(x, y)]
        for k in range(r.integers(3, 6)): x += r.uniform(-30, 30); y += r.uniform(10, 40); pts.append((x, y))
        line(c, pts, col or rgb('b8a47e'), 1.4)
def doric(c, x, y0, y1, w=80, col=None):
    col = col or rgb('e6dcc4')
    shape(c, [(x - w / 2, y1, 'c'), (x - w * 0.42, y0 + 40, 'c'), (x + w * 0.42, y0 + 40, 'c'), (x + w / 2, y1, 'c')], col, 3, t=0)
    for k in range(-2, 3): line(c, [(x + k * w * 0.16, y0 + 44), (x + k * w * 0.19, y1 - 4)], rgb('b8ab90'), 2)
    shape(c, [(x - w * 0.62, y0 + 18, 'c'), (x + w * 0.62, y0 + 18, 'c'), (x + w * 0.45, y0 + 40, 'c'), (x - w * 0.45, y0 + 40, 'c')], col, 3, t=0)
    shape(c, [(x - w * 0.7, y0, 'c'), (x + w * 0.7, y0, 'c'), (x + w * 0.7, y0 + 18, 'c'), (x - w * 0.7, y0 + 18, 'c')], col, 3, t=0)
def ionic(c, x, y0, y1, w=70, col=None):
    col = col or rgb('ece2ca')
    shape(c, [(x - w / 2, y1, 'c'), (x - w * 0.42, y0 + 30, 'c'), (x + w * 0.42, y0 + 30, 'c'), (x + w / 2, y1, 'c')], col, 3, t=0)
    for k in range(-2, 3): line(c, [(x + k * w * 0.16, y0 + 34), (x + k * w * 0.18, y1 - 4)], rgb('c0b498'), 2)
    shape(c, [(x - w * 0.8, y0, 'c'), (x + w * 0.8, y0, 'c'), (x + w * 0.8, y0 + 30, 'c'), (x - w * 0.8, y0 + 30, 'c')], col, 3, t=0)
    for sg in (-1, 1): spiral_(c, x + sg * w * 0.75, y0 + 18, 16)
def spiral_(c, cx, cy, r):
    c.new_path()
    for i in range(50):
        u = i / 49; a = u * 4.4 * math.pi; rr = r * (1 - u * 0.85); x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        c.line_to(x, y) if i else c.move_to(x, y)
    c.set_source_rgb(*LINE); c.set_line_width(2.2); c.stroke()
def pediment(c, x0, x1, y, h, col=None):
    col = col or rgb('e6dcc4')
    shape(c, [(x0, y, 'c'), ((x0 + x1) / 2, y - h, 'c'), (x1, y, 'c')], col, 3.4, t=0)
    shape(c, [(x0 + 40, y - 8, 'c'), ((x0 + x1) / 2, y - h + 24, 'c'), (x1 - 40, y - 8, 'c')], G['terra'], 2.4, t=0)
    rect(c, x0 - 10, y, x1 - x0 + 20, 34, col); c.rectangle(x0 - 10, y, x1 - x0 + 20, 34); c.set_source_rgb(*LINE); c.set_line_width(3); c.stroke()
    meander(c, x0, x1, y + 6, 22, G['black'])
def floor_tiles(c, y, col1, col2):
    rect(c, -10, y, SW + 20, BH, col1); rect(c, -10, y - 4, SW + 20, 6, LINE)
    for k in range(-2, 26):
        for j, yy in enumerate((y + 30, y + 90, y + 180, y + 320)):
            x = k * 160 + (j % 2) * 80
            c.rectangle(x, yy, 160, [60, 90, 140, 200][j]); c.set_source_rgba(*col2, 0.45); c.set_line_width(2); c.stroke()
def window_hills(c, x0, y0, x1, y1):
    c.save(); c.rectangle(x0, y0, x1 - x0, y1 - y0); c.clip()
    bands(c, [rgb('9cc0d4'), rgb('b4d0dc'), rgb('d8e0d0'), rgb('e8dcc0')], y0, y1, x0, x1)
    shape(c, [(x0 - 10, y1), (x0 + 60, y0 + 140), (x0 + 160, y0 + 110), (x0 + 260, y0 + 160), (x1 + 10, y0 + 120), (x1 + 10, y1)], rgb('8aa070'), 2.4)
    shape(c, [(x0 - 10, y1), (x0 + 100, y0 + 200), (x0 + 300, y0 + 190), (x1 + 10, y0 + 210), (x1 + 10, y1)], rgb('6f8a56'), 2.4)
    c.restore()
# ======== 克洛诺斯：场景 ========
