# 2D 合成层：背景、HUD 标注、字幕
import math, re, numpy as np, vtk
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from vtk.util.numpy_support import numpy_to_vtk
W, H = 1920, 1080
import os
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '字体') + '/'
def font(name, size): return ImageFont.truetype(F + name, size)
SERIF = 'NotoSerifCJKsc-Black.otf'; SERIFB = 'NotoSerifSC-Bold.otf'; SANS = 'NotoSansSC-Bold.otf'; SANSK = 'NotoSansSC-Black.otf'
GOLD = (240, 196, 110); GOLD2 = (255, 222, 150); CYAN = (120, 220, 255); RED = (235, 90, 70); WHITE = (246, 240, 228)

def env_tex(warm=1.0):
    h, w = 256, 512
    y, x = np.mgrid[0:h, 0:w] / np.array([h, w])[:, None, None]
    img = np.zeros((h, w, 3)) + (0.05 + 0.10 * (1 - y))[..., None] * np.array([0.55, 0.6, 0.9])
    def soft(cx, cy, sx, sy, col, k):
        dx = np.minimum(abs(x - cx), 1 - abs(x - cx))
        m = np.exp(-((dx / sx) ** 6 + ((y - cy) / sy) ** 6)); img[:] += m[..., None] * np.array(col) * k
    soft(0.15, 0.22, 0.10, 0.08, (1, 0.78, 0.5), 3.5 * warm)
    soft(0.62, 0.28, 0.07, 0.06, (0.55, 0.75, 1.0), 1.6)
    soft(0.40, 0.08, 0.25, 0.04, (1, 0.93, 0.8), 2.2)
    soft(0.90, 0.35, 0.05, 0.12, (1, 0.7, 0.45), 1.5 * warm)
    img[y > 0.55] = img[y > 0.55] * 0.35 + np.array([0.06, 0.045, 0.03])
    a = (np.clip(img, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8)
    vi = vtk.vtkImageData(); vi.SetDimensions(w, h, 1)
    arr = numpy_to_vtk(np.flipud(a).reshape(-1, 3).copy(), deep=1); arr.SetNumberOfComponents(3); vi.GetPointData().SetScalars(arr)
    t = vtk.vtkTexture(); t.SetInputData(vi); t.SetColorModeToDirectScalars(); t.MipmapOn(); t.InterpolateOn(); t.SetUseSRGBColorSpace(True)
    return t

def background(center=(960, 470), mood='warm', t=0.0, seed=3):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    if mood == 'warm':
        top, bot, glow = np.array([10, 14, 28]), np.array([30, 20, 14]), np.array([120, 70, 30])
    elif mood == 'cold':
        top, bot, glow = np.array([8, 12, 18]), np.array([16, 22, 26]), np.array([40, 70, 80])
    else:
        top, bot, glow = np.array([6, 10, 24]), np.array([12, 16, 34]), np.array([40, 60, 140])
    u = (y / H)[..., None]
    img = top * (1 - u) + bot * u
    d = np.sqrt((x - center[0]) ** 2 + ((y - center[1]) * 1.15) ** 2)[..., None]
    img = img + glow * np.exp(-(d / 520) ** 2) * 0.9
    img = np.clip(img, 0, 255).astype(np.uint8)
    im = Image.fromarray(img).convert('RGBA')
    d = ImageDraw.Draw(im, 'RGBA')
    r = np.random.default_rng(seed)
    for i in range(260):
        sx, sy = r.random() * W, r.random() * H * 0.75
        tw = 0.5 + 0.5 * math.sin(t * 2.5 + i)
        a = int((40 + 120 * r.random()) * tw)
        rr = 0.6 + 1.4 * r.random()
        d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], fill=(230, 220, 200, a))
    # 背景纹样：宝相花式同心环
    cx, cy = center
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(lay)
    col = (230, 180, 100, 34) if mood != 'cold' else (140, 200, 210, 26)
    for R in (430, 470, 640):
        g.ellipse([cx - R, cy - R, cx + R, cy + R], outline=col, width=2)
    for k in range(24):
        a0 = k * 15 + t * 3
        p1 = (cx + 470 * math.cos(math.radians(a0)), cy + 470 * math.sin(math.radians(a0)))
        p2 = (cx + 640 * math.cos(math.radians(a0)), cy + 640 * math.sin(math.radians(a0)))
        g.line([p1, p2], fill=col, width=1)
        g.arc([p2[0] - 40, p2[1] - 40, p2[0] + 40, p2[1] + 40], 0, 360, fill=col, width=1)
    im.alpha_composite(lay)
    return im

def contact_shadow(im, pts2d, alpha=150, blur=40):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.polygon(pts2d, fill=(0, 0, 0, alpha))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(blur)))

def glow_from(rgba, thresh=225, rad=18, k=0.6):
    a = rgba.astype(np.float32)
    lum = a[..., :3].max(-1)
    m = np.clip((lum - thresh) / (255 - thresh), 0, 1)[..., None] * a[..., 3:4] / 255
    g = Image.fromarray((a[..., :3] * m).astype(np.uint8)).filter(ImageFilter.GaussianBlur(rad))
    return np.asarray(g).astype(np.float32) * k

def compose(bg, rgba, glow=True):
    im = bg.copy(); im.alpha_composite(Image.fromarray(rgba))
    if glow:
        g = glow_from(rgba)
        arr = np.asarray(im).astype(np.float32); arr[..., :3] = 255 - (255 - arr[..., :3]) * (1 - g / 255)
        im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    return im

def vignette(im, k=0.55):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
    m = np.clip(1 - k * np.clip(d - 0.55, 0, 1) ** 1.5, 0, 1)[..., None]
    a = np.asarray(im).astype(np.float32); a[..., :3] *= m
    return Image.fromarray(a.astype(np.uint8))

def rich_parts(s):
    # 〖金〗 【红】 「青」
    out = []; i = 0
    for m in re.finditer(r'〖(.+?)〗|【(.+?)】|「(.+?)」', s):
        if m.start() > i: out.append((s[i:m.start()], WHITE))
        if m.group(1): out.append((m.group(1), GOLD2))
        elif m.group(2): out.append((m.group(2), RED))
        else: out.append((m.group(3), CYAN))
        i = m.end()
    if i < len(s): out.append((s[i:], WHITE))
    return out

def subtitle(im, s, a=1.0, y=972, size=54):
    if not s: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    g = np.zeros((H, W, 4), np.uint8); ys = np.arange(H)
    ramp = np.clip((ys - (H - 250)) / 250, 0, 1) ** 1.3
    g[..., 3] = (ramp[:, None] * 200 * a).astype(np.uint8)
    im.alpha_composite(Image.fromarray(g))
    lines = s.split('|')
    f = font(SERIF, size)
    for li, line in enumerate(lines):
        parts = rich_parts(line)
        tw = sum(d.textlength(t, font=f) for t, _ in parts)
        x = W / 2 - tw / 2; yy = y - (len(lines) - 1 - li) * (size + 14)
        for t, c in parts:
            d.text((x + 3, yy + 3), t, font=f, fill=(0, 0, 0, int(200 * a)), anchor='ls')
            d.text((x, yy), t, font=f, fill=c + (int(255 * a),), anchor='ls')
            x += d.textlength(t, font=f)
    im.alpha_composite(lay)

def callout(im, p, label, sub=None, dx=180, dy=-90, a=1.0, idx=None, col=GOLD):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x, y = p; ex, ey = x + dx, y + dy
    sgn = 1 if dx >= 0 else -1
    f = font(SANSK, 34); fs = font(SANS, 24)
    tw = d.textlength(label, font=f); sw = d.textlength(sub, font=fs) if sub else 0
    L = max(tw, sw) + 30 + (44 if idx else 0)
    hx = ex + sgn * L
    ca = col + (int(255 * a),)
    d.ellipse([x - 7, y - 7, x + 7, y + 7], outline=ca, width=3); d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=ca)
    d.line([(x, y), (ex, ey), (hx, ey)], fill=ca, width=3)
    tx = min(ex, hx) + 14
    if idx:
        d.ellipse([tx, ey - 52, tx + 36, ey - 16], fill=ca)
        d.text((tx + 18, ey - 34), str(idx), font=font(SANSK, 24), fill=(20, 16, 10, int(255 * a)), anchor='mm')
        tx += 46
    d.text((tx + 2, ey - 12 + 2), label, font=f, fill=(0, 0, 0, int(180 * a)), anchor='ls')
    d.text((tx, ey - 12), label, font=f, fill=WHITE + (int(255 * a),), anchor='ls')
    if sub:
        d.text((tx - (46 if idx else 0), ey + 32), sub, font=fs, fill=(220, 205, 180, int(230 * a)), anchor='ls')
    im.alpha_composite(lay)

def chrome(im, tag='唐 · 开元十三年（725）', series='VIBE 知识 · 古代黑科技', a=1.0):
    d = ImageDraw.Draw(im, 'RGBA')
    f = font(SANSK, 26)
    d.rectangle([56, 52, 62, 92], fill=GOLD + (int(255 * a),))
    d.text((76, 72), series, font=f, fill=(235, 225, 205, int(230 * a)), anchor='lm')
    fw = d.textlength(tag, font=font(SANS, 28))
    d.rounded_rectangle([W - 80 - fw - 30, 48, W - 64, 96], 24, outline=GOLD + (int(220 * a),), width=2)
    d.text((W - 64 - 15 - fw, 72), tag, font=font(SANS, 28), fill=GOLD2 + (int(255 * a),), anchor='lm')

def bignum(im, txt, x, y, size=150, col=GOLD2, a=1.0, label=None, anchor='mm'):
    d = ImageDraw.Draw(im, 'RGBA'); f = font(SANSK, size)
    d.text((x + 4, y + 5), txt, font=f, fill=(0, 0, 0, int(160 * a)), anchor=anchor)
    d.text((x, y), txt, font=f, fill=col + (int(255 * a),), anchor=anchor)
    if label:
        d.text((x, y + size * 0.62), label, font=font(SANS, 30), fill=(225, 210, 185, int(240 * a)), anchor='mm' if anchor == 'mm' else 'lm')

def title(im, main, sub, sub2=None, a=1.0, y=170, cx=W / 2):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = font(SERIF, 150)
    tw = d.textlength(main, font=f)
    # 金属渐变字
    mask = Image.new('L', (W, H), 0); ImageDraw.Draw(mask).text((cx, y), main, font=f, fill=255, anchor='mm')
    gy = np.linspace(0, 1, H)[:, None]
    grad = np.zeros((H, W, 4), np.uint8)
    c1, c2, c3 = np.array([255, 236, 180]), np.array([226, 160, 70]), np.array([255, 214, 130])
    t = np.clip((gy - (y - 75) / H) * H / 150, 0, 1)
    col = np.where(t < 0.5, c1 * (1 - t * 2) + c2 * t * 2, c2 * (1 - (t - 0.5) * 2) + c3 * (t - 0.5) * 2)
    grad[..., :3] = np.broadcast_to(col[:, None, :], (H, W, 3)); grad[..., 3] = (np.asarray(mask) * a).astype(np.uint8)
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((cx + 5, y + 7), main, font=f, fill=(0, 0, 0, int(200 * a)), anchor='mm')
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    im.alpha_composite(Image.fromarray(grad))
    d2 = ImageDraw.Draw(im, 'RGBA')
    d2.line([(cx - tw / 2, y + 95), (cx + tw / 2, y + 95)], fill=GOLD + (int(200 * a),), width=2)
    d2.text((cx, y + 135), sub, font=font(SANSK, 40), fill=WHITE + (int(255 * a),), anchor='mm')
    if sub2: d2.text((cx, y + 185), sub2, font=font(SANS, 28), fill=(220, 200, 165, int(230 * a)), anchor='mm')

def ring_burst(im, p, r, a, col=GOLD2, n=3):
    d = ImageDraw.Draw(im, 'RGBA')
    for k in range(n):
        rr = r * (1 + 0.35 * k)
        d.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], outline=col + (int(255 * a * (1 - k / n)),), width=4)

def onomat(im, txt, p, size=90, a=1.0, col=GOLD2, rot=-8):
    lay = Image.new('RGBA', (600, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = font(SERIF, size)
    d.text((300, 150), txt, font=f, fill=(20, 10, 5, int(255 * a)), anchor='mm', stroke_width=8, stroke_fill=(20, 10, 5, int(255 * a)))
    d.text((300, 150), txt, font=f, fill=col + (int(255 * a),), anchor='mm')
    lay = lay.rotate(rot, resample=Image.BICUBIC)
    im.alpha_composite(lay, (int(p[0] - 300), int(p[1] - 150)))

def quote_card(im, lines, src, a=1.0, x=120, y=330):
    d = ImageDraw.Draw(im, 'RGBA')
    f = font(SERIFB, 46)
    for i, l in enumerate(lines):
        d.text((x, y + i * 70), l, font=f, fill=(235, 225, 205, int(255 * a)), anchor='ls')
    d.line([(x - 30, y - 50), (x - 30, y + (len(lines) - 1) * 70 + 10)], fill=GOLD + (int(230 * a),), width=4)
    d.text((x, y + len(lines) * 70 + 4), src, font=font(SANS, 26), fill=(200, 180, 140, int(230 * a)), anchor='ls')
