T0 = np.cumsum([0] + [s[0] for s in S]); TOTAL = float(T0[-1])
GRP = []
for i in range(len(S)):
    if i > 0 and S[i][1] is S[i - 1][1]: GRP.append((GRP[-1][0], GRP[-1][1] + 1))
    else: GRP.append((i, 0))
NOSUB = {1: ("希腊神话 · 百眼巨人阿耳戈斯", ""), len(S) - 1: ("· 完 ·", "")}
# ---------------- 外框 / 字幕 / 名牌 / 讲解卡 ----------------
KW = {'b': (30, 72, 160), 'r': (176, 50, 24), 'g': (40, 112, 62), 'n': (24, 14, 4)}
NAMES = re.compile(r'(阿耳戈斯|赫尔墨斯|伊俄|宙斯|赫拉|神王|神后)')
def segs_(s):
    out = []
    for t, cc in segs0_(s):
        if cc != 'n': out.append((t, cc)); continue
        for u in NAMES.split(t):
            if u: out.append((u, 'b' if NAMES.fullmatch(u) else 'n'))
    return out
def segs0_(s):
    out = []; cur = 'n'
    for t in re.split(r'(\[/?[brg]\])', s):
        if not t: continue
        if t.startswith('[/'): cur = 'n'; continue
        if t.startswith('['): cur = t[1]; continue
        out.append((t, cur))
    return out
def kheker(c, y0, h):
    rect(c, 0, y0, OW, h, G['black'])
    rect(c, 0, y0 + 5, OW, h - 10, G['terra'])
    meander(c, 0, OW, y0 + 9, h - 18, G['black'], lw=2.2)
    rect(c, 0, y0, OW, 3, GOLD); rect(c, 0, y0 + h - 3, OW, 3, GOLD)
def winged_sun(c, cx, cy, s):
    c.save(); c.translate(cx, cy); c.scale(s, s)
    shape(c, [(-90, -14, 'c'), (90, -14, 'c'), (90, 14, 'c'), (-90, 14, 'c')], G['black'], 2.4, t=0)
    for sg in (-1, 1):
        c.save(); c.translate(sg * 50, 0); c.scale(0.22, 0.22); emblem(c, 1.0); c.restore()
    circ(c, 0, 0, 11, G['gold']); ring_stroke(c, 0, 0, 11, LINE, 2)
    c.restore()
SX0, SX1, SY0, SY1 = 36, 1404, 852, 1034
TXT = {}
def make_ovl():
    s, c = surf(OW, OH)
    kheker(c, 0, PY); kheker(c, PY + PH, OH - PY - PH)
    c.rectangle(16, PY + 10, OW - 32, PH - 20); c.set_source_rgba(*GOLD, 0.8); c.set_line_width(2.5); c.stroke()
    n = nmap(21, SX1 - SX0, SY1 - SY0, ((6, 1), (20, .5), (60, .25)))
    a = np.array(rgb('f6ecd0'))[None, None] * (1 - n[..., None] * 0.25) + np.array(rgb('e2d0a4'))[None, None] * (n[..., None] * 0.25)
    xs = np.arange(SX1 - SX0)
    a = a * (1 - 0.05 * (np.sin(xs / 3.0) > 0.6))[None, :, None]   # 莎草纸纤维
    c.save(); c.new_path(); r_ = 14; x0, y0, x1, y1 = SX0, SY0, SX1, SY1
    c.move_to(x0 + r_, y0); c.line_to(x1 - r_, y0); c.arc(x1 - r_, y0 + r_, r_, -math.pi / 2, 0); c.line_to(x1, y1); c.line_to(x0, y1); c.line_to(x0, y0 + r_); c.arc(x0 + r_, y0 + r_, r_, math.pi, 1.5 * math.pi); c.close_path()
    path = c.copy_path(); c.clip(); paint_arr(c, a, SX0, SY0); c.restore()
    c.new_path(); c.append_path(path); c.set_source_rgb(*rgb('7d2f1e')); c.set_line_width(4); c.stroke()
    c.new_path(); c.rectangle(SX0 + 9, SY0 + 9, SX1 - SX0 - 18, SY1 - SY0 - 14); c.set_source_rgba(*GOLD, 0.9); c.set_line_width(1.6); c.stroke()
    for xx in (SX0 + 28, SX1 - 28):
        c.save(); c.translate(xx, SY0 + (SY1 - SY0) / 2 - 2); emblem(c, 0.3); c.restore()
    winged_sun(c, OW / 2, PY / 2, 0.55); winged_sun(c, OW / 2, OH - (OH - PY - PH) / 2, 0.5)
    arr = np.ndarray((OH, OW, 4), np.uint8, s.get_data()).copy(); al = arr[..., 3:4].astype(np.float32) / 255
    rgbp = arr[..., [2, 1, 0]].astype(np.float32); rgbs = np.where(al > 0, rgbp / np.maximum(al, 1e-6), 0)
    return rgbs, al
def text_img(key, lines, w, h):
    if key in TXT: return TXT[key]
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for s, fp, sz, y, dim in lines:
        f = ImageFont.truetype(fp, sz); sg = segs_(s); tw = sum(d.textlength(t, font=f) for t, _ in sg)
        while tw > w - 10 and sz > 14: sz -= 1; f = ImageFont.truetype(fp, sz); tw = sum(d.textlength(t, font=f) for t, _ in sg)
        x = w / 2 - tw / 2
        for t, cc in sg:
            col = KW[cc]
            if dim and cc == 'n': col = (70, 48, 28)
            d.text((x, y), t, font=f, fill=col + (255,)); x += d.textlength(t, font=f)
    TXT[key] = np.array(im); return TXT[key]
SUBW, SUBH = SX1 - SX0 - 150, SY1 - SY0 - 26
def sub_img(i):
    k = ('sub', i)
    if k in TXT: return TXT[k]
    zh = S[i][2]
    im = Image.new('RGBA', (SUBW, SUBH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for r, zs in enumerate(zh):
        zsz = 62
        while True:
            fz = ImageFont.truetype(FZ, zsz); sz_ = segs_(zs); wz = sum(d.textlength(t, font=fz) for t, _ in sz_)
            if wz <= SUBW - 6 or zsz <= 34: break
            zsz -= 1
        x = SUBW / 2 - wz / 2; yb = 4 + r * (SUBH // 2) + 66
        for t, cc in sz_:
            d.text((x, yb), t, font=fz, fill=KW[cc] + (255,), anchor='ls'); x += d.textlength(t, font=fz)
    TXT[k] = np.array(im); return TXT[k]
def tag_img(zh, en):
    k = ('tag', zh, en)
    if k in TXT: return TXT[k]
    fz = ImageFont.truetype(FZ, 28); fe = ImageFont.truetype(FEB, 17)
    tmp = ImageDraw.Draw(Image.new('RGBA', (10, 10)))
    w = int(max(tmp.textlength(zh, font=fz), tmp.textlength(en, font=fe)) + 40); h = 70 if en else 48
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([1, 1, w - 2, h - 2], radius=12, fill=(236, 224, 192, 242), outline=(125, 47, 30, 255), width=3)
    d.rounded_rectangle([6, 6, w - 7, h - 7], radius=8, outline=(191, 151, 70, 200), width=1)
    tw = d.textlength(zh, font=fz); d.text((w / 2 - tw / 2, 5), zh, font=fz, fill=(43, 74, 140, 255))
    if en: tw = d.textlength(en, font=fe); d.text((w / 2 - tw / 2, 42), en, font=fe, fill=(70, 48, 28, 255))
    TXT[k] = np.array(im); return TXT[k]
def icon_draw(c, kind, x, y, s):
    if kind == 'spider': spider(c, x, y - 10, 0.8, 0)
    elif kind == 'senet': pass
    elif kind == 'phases':
        for j in range(5):
            cx = x - 80 * s + j * 40 * s; r = 14 * s; circ(c, cx, y, r, rgb('3a4660')); fr = [0.0, 0.3, 1.0, 0.3, 0.0][j]
            if j == 2: circ(c, cx, y, r, rgb('e8eef6'))
            elif j in (1, 3):
                c.save(); c.new_path(); c.arc(cx, y, r, 0, 7); c.clip(); circ(c, cx + (r if j == 1 else -r) * 0.5, y, r, rgb('e8eef6')); circ(c, cx + (-r if j == 1 else r) * 0.6, y, r, rgb('3a4660')); c.restore()
            ring_stroke(c, cx, y, r, LINE, 1.5)
def note_img(zh, en, icon):
    k = ('note', zh, en, icon)
    if k in TXT: return TXT[k]
    zl = zh.split('\n'); el = en.split('\n') if en else []
    fz = ImageFont.truetype(FZ, 26); fe = ImageFont.truetype(FE, 17)
    tmp = ImageDraw.Draw(Image.new('RGBA', (10, 10)))
    tw = max([tmp.textlength(z, font=fz) for z in zl] + [tmp.textlength(e, font=fe) for e in el])
    iw = 130 if icon else 0
    w = int(min(620, tw) + 44 + iw); lh = len(zl) * 33 + len(el) * 23 + 34; h = max(lh, 84 if icon else 0)
    s, c = surf(w, h)
    c.rectangle(2, 2, w - 4, h - 4); c.set_source_rgba(*rgb('efe2bf'), 0.95); c.fill_preserve(); c.set_source_rgb(*rgb('7d2f1e')); c.set_line_width(3); c.stroke()
    c.rectangle(8, 8, w - 16, h - 16); c.set_source_rgba(*GOLD, 0.9); c.set_line_width(1.2); c.stroke()
    rect(c, 2, 2, 10, h - 4, rgb('7d2f1e'))
    if icon: icon_draw(c, icon, 22 + iw / 2, h / 2, 1.0)
    arr = np.ndarray((h, w, 4), np.uint8, s.get_data())[..., [2, 1, 0, 3]].copy()
    im = Image.fromarray(arr, 'RGBA'); d = ImageDraw.Draw(im)
    y = 14; x0 = 24 + iw
    for z in zl:
        sz = 26; f = fz
        while d.textlength(z, font=f) > w - x0 - 16 and sz > 14: sz -= 1; f = ImageFont.truetype(FZ, sz)
        d.text((x0, y), z, font=f, fill=(34, 19, 5, 255)); y += 33
    y += 2
    for e in el:
        sz = 17; f = fe
        while d.textlength(e, font=f) > w - x0 - 16 and sz > 10: sz -= 1; f = ImageFont.truetype(FE, sz)
        d.text((x0, y), e, font=f, fill=(90, 62, 36, 255)); y += 23
    TXT[k] = np.array(im); return TXT[k]
def title_img():
    k = 'title'
    if k in TXT: return TXT[k]
    w, h = 1080, 360
    s, c = surf(w, h)
    def tab(inset, col, lw, fill=None):
        x0, y0, x1, y1 = inset, inset, w - 60 - inset, h - inset; r_ = 26
        c.new_path(); c.arc(x0 + r_, y0 + r_, r_, math.pi, 1.5 * math.pi); c.arc(x1 - r_, y0 + r_, r_, -math.pi / 2, 0); c.arc(x1 - r_, y1 - r_, r_, 0, math.pi / 2); c.arc(x0 + r_, y1 - r_, r_, math.pi / 2, math.pi); c.close_path()
        if fill: c.set_source_rgba(*fill, 0.97); c.fill_preserve()
        c.set_source_rgb(*col); c.set_line_width(lw); c.stroke()
    tab(8, G['black'], 7, rgb('efe2bf')); tab(20, GOLD, 3)
    rect(c, 40, 30, w - 140, 26, G['terra']); meander(c, 40, w - 100, 33, 20, G['black'])
    rect(c, 40, h - 56, w - 140, 26, G['terra']); meander(c, 40, w - 100, h - 53, 20, G['black'])
    for xx in (100, w - 160):
        c.save(); c.translate(xx + 30, 180); emblem(c, 0.9); c.restore()
    arr = np.ndarray((h, w, 4), np.uint8, s.get_data())[..., [2, 1, 0, 3]].copy()
    im = Image.fromarray(arr, 'RGBA'); d = ImageDraw.Draw(im)
    for txt, fp, sz, y, col in (("百眼巨人[r]阿耳戈斯[/r]", FZ, 88, 64, None), ("一百只眼睛 最后落在了孔雀的尾巴上", FZ, 32, 184, (157, 52, 30)),
                                ("Vibe 希腊神话", FZ, 26, 250, (90, 62, 36))):
        f = ImageFont.truetype(fp, sz); sg = segs_(txt); tw = sum(d.textlength(t, font=f) for t, _ in sg); x = (w - 60) / 2 - tw / 2
        for t, cc in sg:
            d.text((x, y), t, font=f, fill=(col if (col and cc == 'n') else KW[cc]) + (255,)); x += d.textlength(t, font=f)
    TXT[k] = np.array(im); return TXT[k]
def num_img(txt, size, col):
    k = ('num', txt, size, col)
    if k in TXT: return TXT[k]
    fp = FEB if any(0x370 <= ord(ch) <= 0x1fff for ch in txt) else (FZ if any(ord(ch) > 127 for ch in txt) else FEB)
    f = ImageFont.truetype(fp, size); tmp = ImageDraw.Draw(Image.new('RGBA', (10, 10))); tw = int(tmp.textlength(txt, font=f))
    im = Image.new('RGBA', (tw + 20, size + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((10, 6), txt, font=f, fill=col + (255,), stroke_width=max(2, size // 22), stroke_fill=(30, 18, 8, 255))
    TXT[k] = np.array(im); return TXT[k]
def counter_img(n):
    k = ('cnt', n)
    if k in TXT: return TXT[k]
    w, h = 260, 96; s, c = surf(w, h)
    c.rectangle(2, 2, w - 4, h - 4); c.set_source_rgba(*rgb('2a1a2a'), 0.92); c.fill_preserve(); c.set_source_rgb(*GOLD); c.set_line_width(3); c.stroke()
    for j in range(3):
        for i in range(3): rect(c, 20 + i * 18, 18 + j * 22, 14, 18, [G['rose'], G['saff'], G['sea']][(i + j) % 3])
    arr = np.ndarray((h, w, 4), np.uint8, s.get_data())[..., [2, 1, 0, 3]].copy(); im = Image.fromarray(arr, 'RGBA'); d = ImageDraw.Draw(im)
    d.text((90, 8), f"{n} / 21", font=ImageFont.truetype(FEB, 36), fill=(240, 220, 150, 255))
    d.text((92, 56), "桩丑闻 scandals", font=ImageFont.truetype(FZ, 18), fill=(230, 200, 210, 255))
    TXT[k] = np.array(im); return TXT[k]

BASE = None; TEX = None; OVL = None
def render(t):
    global BASE, TEX, OVL
    if BASE is None:
        BASE = np.zeros((OH, OW, 3), np.uint8); BASE[:] = (28, 22, 18)
        n = nmap(5, OW, PH, ((12, 1), (40, .6), (160, .3))); g = np.random.default_rng(5).normal(0, 1, (PH, OW)).astype(np.float32)
        TEX = ((0.965 + 0.07 * n) + g * 0.016)[..., None]; OVL = make_ovl()
    i = int(np.searchsorted(T0, t, side='right') - 1); i = min(i, len(S) - 1); lt_e = t - T0[i]; d, fn, zh, en, cam = S[i]
    g0, kk = GRP[i]; lt = t - T0[g0]; dg = float(T0[i + 1] - T0[g0])
    s, c = surf(OW, PH); c.scale(K, K); c.translate(0, OFF)
    z = lerp(cam[0], cam[1], E(lt_e / d)); fx, fy = cam[2], cam[3]
    c.translate(fx, fy); c.scale(z, z); c.translate(-fx, -fy)
    M = c.get_matrix()
    marks = fn(c, lt_e, d, kk) or []
    s.flush(); pic = np.ndarray((PH, OW, 4), np.uint8, s.get_data())[..., [2, 1, 0]].astype(np.float32)
    tex = np.roll(TEX, int(t * FPS) % 3, axis=1)
    pic = np.clip(pic * tex, 0, 255).astype(np.uint8)
    for m in marks:
        if m[0] == 'shake' and m[1] > 0:
            pic = np.roll(pic, int(16 * m[1] * math.sin(t * 55)), axis=1); pic = np.roll(pic, int(8 * m[1] * math.cos(t * 47)), axis=0)
    out = BASE.copy(); out[PY:PY + PH] = pic
    def blit(img, x, y, alpha):
        h, w = img.shape[:2]; x = int(x); y = int(y)
        x0, y0 = max(0, x), max(PY, y); x1, y1 = min(OW, x + w), min(PY + PH, y + h)
        if x1 <= x0 or y1 <= y0 or alpha <= 0: return
        sub = img[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32); a = sub[..., 3:4] / 255 * min(1, alpha)
        out[y0:y1, x0:x1] = (out[y0:y1, x0:x1] * (1 - a) + sub[..., :3] * a).astype(np.uint8)
    for m in marks:
        if m[0] == 'num':
            _, txt, x, y, sz, a, col = m
            if a <= 0: continue
            px, py = M.transform_point(x, y); im = num_img(txt, int(sz * K * 1.25), col); blit(im, px - im.shape[1] / 2, py + PY - im.shape[0] / 2, a)
        elif m[0] == 'math' and m[1] > 0:
            im = math_img(); blit(im, 60, PY + 330, m[1])
        elif m[0] == 'counter':
            im = counter_img(m[1]); blit(im, OW - im.shape[1] - 40, PY + 28, 1.0)
    o_rgb, o_a = OVL; out[:] = (out * (1 - o_a) + o_rgb * o_a).astype(np.uint8)
    tag_a = seg(lt_e, 0.3, 0.8) * (1 - seg(lt_e, d - 0.35, d))
    for m in marks:
        if m[0] == 'title':
            blit(title_img(), (OW - 1080) / 2 + 30, 300, m[1])
        elif m[0] == 'note':
            _, zz, ee, side, t0_, t1_, icon = m
            a = seg(lt_e, t0_, t0_ + 0.4) * (1 - seg(lt_e, min(t1_, d - 0.3), min(t1_, d - 0.3) + 0.3))
            im = note_img(zz, ee, icon); w = im.shape[1]
            bx = 40 if side == 'TL' else OW - w - 40
            blit(im, bx, PY + 26 + int(10 * (1 - a)), a)
        elif m[0] == 'tag':
            _, zh_, en_, pt, side = m; px, py = M.transform_point(*pt); py += PY
            im = tag_img(zh_, en_); w, h = im.shape[1], im.shape[0]; gap = 60
            if side == 'L' and px - gap - w < 30: side = 'R'
            if side == 'R' and px + gap + w > OW - 30: side = 'L'
            bx = px - gap - w if side == 'L' else px + gap; by = min(max(PY + 24, py - h - 30), SY0 - h - 8)
            ex = bx + w if side == 'L' else bx; ey = by + h / 2
            tx_ = px + (-18 if side == 'L' else 18); ty_ = py - 10
            if tag_a > 0:
                ov = out.copy(); cv2.line(ov, (int(ex), int(ey)), (int(tx_), int(ty_)), (125, 47, 30), 2, cv2.LINE_AA); cv2.circle(ov, (int(tx_), int(ty_)), 5, (125, 47, 30), -1, cv2.LINE_AA)
                out[:] = (out * (1 - tag_a) + ov * tag_a).astype(np.uint8)
            blit(im, bx, by, tag_a)
    a = seg(lt_e, 0, 0.35) * (1 - seg(lt_e, d - 0.3, d))
    # 字幕框在 PY+PH 之外也要画：临时放宽 blit 范围
    def blit2(img, x, y, alpha):
        h, w = img.shape[:2]; x = int(x); y = int(y)
        sub = img.astype(np.float32); al = sub[..., 3:4] / 255 * alpha
        out[y:y + h, x:x + w] = (out[y:y + h, x:x + w] * (1 - al) + sub[..., :3] * al).astype(np.uint8)
    if zh[0] or zh[1]: blit2(sub_img(i), SX0 + 75, SY0 + 13, a)
    else:
        zz, ee = NOSUB.get(i, ("", ""))
        blit2(text_img(('cont', zz), [(zz, FZ, 52, 46, False)], SX1 - SX0 - 110, 150), SX0 + 55, SY0 + 14, seg(lt_e, 0.8, 1.4))
    if lt_e < 0.12 and i > 0 and GRP[i][1] == 0:
        k_ = lt_e / 0.12; out[PY:PY + PH] = (out[PY:PY + PH] * (0.65 + 0.35 * k_) + 255 * 0.35 * (1 - k_)).clip(0, 255).astype(np.uint8)
    return out

if __name__ == '__main__':
    import argparse; ap = argparse.ArgumentParser(); ap.add_argument('--stills'); ap.add_argument('--part', type=int, default=0); ap.add_argument('--parts', type=int, default=1); ap.add_argument('--out', default='out')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    if a.stills:
        for tt in a.stills.split(','): Image.fromarray(render(float(tt))).save(f'{a.out}/s_{float(tt):06.2f}.jpg', quality=85)
    else:
        nf = int(round(TOTAL * FPS)); f0 = nf * a.part // a.parts; f1 = nf * (a.part + 1) // a.parts
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', f'{a.out}/part{a.part}.mp4'], stdin=subprocess.PIPE)
        for f in range(f0, f1):
            p.stdin.write(render(f / FPS).tobytes())
            if f % 48 == 0: print(a.part, f, '/', f1, flush=True)
        p.stdin.close(); p.wait()
