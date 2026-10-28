# ======== 俄耳甫斯：场景 ========
def tag(zh, pt, side='R'): return ('tag', zh, '', pt, side)
def note(zh, side='TR', t0=0.4, t1=99): return ('note', zh, '', side, t0, t1, None)
def num(txt, x, y, sz, a, col=(240, 214, 140)): return ('num', txt, x, y, sz, a, col)
INK = (0.05, 0.04, 0.06)
VOID = rgb('07080e')

ORPH = dict(kind='gm', long=True, dress=G['white'], dress2=G['cream2'], himation=G['blue'], himation2=G['blue2'], trim=G['gold'],
            skin=G['skin'], skin2=G['skin2'], hair_c=rgb('5a3a1e'), hair_c2=rgb('7a5434'), wreath=True, bracelet=True)
EURY = dict(kind='nymph', dress=G['rose'], dress2=G['rose2'], himation=G['white'], himation2=G['cream2'], trim=G['gold'],
            skin=G['pale'], skin2=G['pale2'], flower=G['white'], necklace=True, hair_c=rgb('3a2418'), hair_c2=rgb('5a3a28'))
HADES = dict(kind='gm', long=True, beard=True, crown=True, dress=rgb('2a2228'), dress2=rgb('1a1418'), himation=G['purple'], himation2=G['purple2'],
             hair_c=rgb('1a1414'), hair_c2=rgb('3a3030'), trim=G['gold'], skin=rgb('b8aa9c'), skin2=rgb('988a7c'), belt=G['gold'])
PERSE = dict(kind='gf', dress=G['purple'], dress2=G['purple2'], himation=G['saff'], himation2=G['saff2'], trim=G['gold'], skin=G['pale'], skin2=G['pale2'], necklace=True, band=G['gold'], bracelet=True)
CHARON = dict(kind='gm', long=True, beard=True, dress=rgb('3a3a40'), dress2=rgb('2a2a30'), himation=rgb('4e4c56'), himation2=rgb('3a3842'),
              hair_c=G['whitehair'], hair_c2=rgb('c8c2b6'), skin=rgb('a89a88'), skin2=rgb('8a7c6c'), trim=rgb('1e1e24'))

def orph(c, x, h, pose, face, y=GY, **k): return fig(c, x, y, h, pose, face, **{**ORPH, **k})
def eury(c, x, h, pose, face, y=GY, **k): return fig(c, x, y, h, pose, face, **{**EURY, **k})

def ghost(c, draw, a, tint=(0.78, 0.9, 1.0), flat=0.45):
    if a <= 0: return {}
    c.push_group(); o = draw(); pat = c.pop_group()
    c.set_source(pat); c.paint_with_alpha(a * (1 - flat))
    c.set_source_rgba(*tint, a * flat); c.mask(pat)
    return o
def sil(c, draw, col=INK, a=1.0):
    c.push_group(); o = draw(); pat = c.pop_group(); c.set_source_rgba(*col, a); c.mask(pat); return o

# ---------- 道具 ----------
def lyre7(cc, s=1.0, pluck=0.0, t=0.0):
    cc.save(); cc.scale(s, s)
    # 龟甲音箱
    shell = [(-46, 30), (0, 18), (46, 30), (54, 70, 'c'), (0, 104, 'c'), (-54, 70, 'c')]
    shape(cc, shell, rgb('b08a50'), 3)
    cc.save(); clip_shape(cc, shell)
    for k_ in range(-3, 4): line(cc, [(k_ * 16, 20), (k_ * 18, 110)], rgb('8a6a3a'), 2)
    line(cc, [(-60, 60), (60, 60)], rgb('8a6a3a'), 2)
    cc.restore()
    # 两只弯角琴臂 + 横梁
    shape(cc, [(-40, 36), (-58, -20), (-74, -86), (-60, -120), (-46, -112), (-56, -84), (-40, -24), (-28, 34)], rgb('d1a347'), 2.6)
    shape(cc, [(40, 36), (58, -20), (74, -86), (60, -120), (46, -112), (56, -84), (40, -24), (28, 34)], rgb('d1a347'), 2.6)
    shape(cc, [(-70, -96), (70, -96), (70, -82), (-70, -82)], rgb('8a5a26'), 2.4, t=0)
    for k_ in range(7):
        xx = -30 + k_ * 10; vib = 2.5 * pluck * math.sin(t * 60 + k_) if k_ in (2, 3, 4) else 0
        cc.new_path(); cc.move_to(xx, -82); cc.curve_to(xx + vib, -20, xx - vib, 30, xx * 0.9, 84)
        cc.set_source_rgb(*rgb('f4ead0')); cc.set_line_width(1.8); cc.stroke()
    shape(cc, [(-34, 78), (34, 78), (34, 88), (-34, 88)], rgb('5a3a1e'), 2, t=0)
    cc.restore()
def lyre_prop(s=1.6, pluck=0.0, t=0.0):
    def f(cc):
        cc.save(); cc.translate(0, 60); cc.rotate(math.pi); lyre7(cc, s, pluck, t); cc.restore()
    return f
def music_note(c, x, y, s, a, col=(0.98, 0.84, 0.42)):
    if a <= 0: return
    c.save(); c.translate(x, y); c.scale(s, s)
    glow(c, 0, 0, 30, col, 0.35 * a)
    c.new_path(); c.save(); c.scale(1.3, 1); c.arc(0, 0, 8, 0, 7); c.restore(); c.set_source_rgba(*col, a); c.fill()
    line(c, [(9, 0), (9, -38)], col, 3.2); c.new_path(); c.move_to(9, -38); c.curve_to(22, -30, 24, -18, 16, -10); c.set_source_rgba(*col, a); c.set_line_width(3.2); c.stroke()
    c.restore()
def notes_flow(c, t, x, y, a=1.0, n=7, spread=1.0, seed=3, dirx=1.0):
    r = np.random.default_rng(seed)
    for i in range(n):
        ph = (t * 0.35 + i / n) % 1.0; s_ = r.uniform(0.8, 1.4)
        nx = x + dirx * ph * 520 * spread + 30 * math.sin(t * 2 + i); ny = y - ph * 260 * spread + 40 * math.sin(t * 1.6 + i * 2)
        music_note(c, nx, ny, s_, a * math.sin(math.pi * ph))
def rock(c, x, y, s, ang=0.0, tear=0.0, t=0.0, col=None):
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    pts = [(-90, -10), (-70, -38), (-20, -48), (40, -44), (86, -24), (96, 6), (70, 34), (10, 44), (-50, 38), (-88, 18)]
    shape(c, pts, col or rgb('8e887c'), 3.4)
    c.save(); clip_shape(c, pts)
    shape(c, [(-90, 10), (-20, 20), (60, 14), (100, 4), (100, 60), (-100, 60)], tuple(v * 0.82 for v in (col or rgb('8e887c'))), 0, t=0)
    line(c, [(-40, -30), (-20, -6), (-30, 20)], rgb('5e5850'), 2.4); line(c, [(30, -36), (44, -10)], rgb('5e5850'), 2.4)
    c.restore()
    if tear > 0:
        for (ex, ey) in ((-26, -16), (24, -18)):
            shape(c, [(ex - 12, ey), (ex, ey - 6), (ex + 12, ey)], LINE, 2.2, closed=False)
            u = (t * 0.7 + ex * 0.01) % 1.0; ty = ey + 6 + 50 * u
            line(c, [(ex, ey + 4), (ex, ty)], P['tear'], 3)
            shape(c, [(ex, ty - 10), (ex + 6, ty + 2), (ex, ty + 8), (ex - 6, ty + 2)], P['tear'], 1.4)
    c.restore()
def snake(c, pts, w, col=None, col2=None, a=1.0, head=True, tongue=0.0):
    col = col or rgb('5a6a2a'); col2 = col2 or rgb('d8b040')
    c.push_group()
    n = len(pts)
    for i in range(n - 1):
        u = i / (n - 1); ww = w * (0.35 + 0.65 * math.sin(math.pi * min(1, u * 1.15 + 0.08)))
        c.new_path(); c.move_to(*pts[i]); c.line_to(*pts[i + 1]); c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_source_rgb(*LINE); c.set_line_width(ww + 5); c.stroke()
    for i in range(n - 1):
        u = i / (n - 1); ww = w * (0.35 + 0.65 * math.sin(math.pi * min(1, u * 1.15 + 0.08)))
        c.new_path(); c.move_to(*pts[i]); c.line_to(*pts[i + 1]); c.set_source_rgb(*(col2 if (i // 3) % 3 == 0 else col)); c.set_line_width(ww); c.stroke()
    if head:
        x0, y0 = pts[-2]; x1, y1 = pts[-1]; ang = math.atan2(y1 - y0, x1 - x0)
        c.save(); c.translate(x1, y1); c.rotate(ang)
        shape(c, [(-10, -w * 0.6), (w * 0.9, -w * 0.5), (w * 1.5, 0), (w * 0.9, w * 0.5), (-10, w * 0.6)], col, 2.6)
        circ(c, w * 0.8, -w * 0.22, w * 0.12, rgb('e8c040')); circ(c, w * 0.82, -w * 0.22, w * 0.05, LINE)
        if tongue > 0: line(c, [(w * 1.5, 0), (w * 1.5 + 26 * tongue, 0), (w * 1.5 + 36 * tongue, -8)], rgb('b02a20'), 2.4); line(c, [(w * 1.5 + 26 * tongue, 0), (w * 1.5 + 36 * tongue, 8)], rgb('b02a20'), 2.4)
        c.restore()
    c.pop_group_to_source(); c.paint_with_alpha(a)
def snake_path(x0, y0, L, amp, ph, n=40, ang=0.0, waves=2.0):
    out = []
    for i in range(n):
        u = i / (n - 1); px = u * L; py = amp * math.sin(u * waves * 2 * math.pi + ph)
        out.append((x0 + px * math.cos(ang) - py * math.sin(ang), y0 + px * math.sin(ang) + py * math.cos(ang)))
    return out
def flame(c, x, y, s, t, seed=0, cols=None):
    cols = cols or [rgb('e85a1a'), rgb('f2a030'), rgb('f8e090')]
    for k_ in range(3):
        f = 1 + 0.15 * math.sin(t * 13 + k_ * 2 + seed); col = cols[k_]; w = (40 - k_ * 11) * s; hh = (110 - k_ * 28) * s * f
        shape(c, [(x - w, y), (x - w * 0.6, y - hh * 0.5), (x + 4 * math.sin(t * 9 + seed), y - hh), (x + w * 0.6, y - hh * 0.5), (x + w, y)], col, 0, t=0)
    glow(c, x, y - 40 * s, 220 * s, cols[1], 0.35)
BLUEF = [rgb('2a5a9a'), rgb('4a9ad0'), rgb('bfe8f8')]
def brazier(c, x, y, t, blue=True, s=1.0):
    rect(c, x - 8 * s, y, 16 * s, 220 * s, rgb('3a3036')); shape(c, [(x - 50 * s, y), (x + 50 * s, y), (x + 30 * s, y + 34 * s, 'c'), (x - 30 * s, y + 34 * s, 'c')], G['bronze'], 3)
    flame(c, x, y + 4, s, t, x, BLUEF if blue else None)
def smoke_wisp(c, pts, w, a, col=(0.94, 0.96, 1.0)):
    for i, (x, y) in enumerate(pts):
        u = i / max(1, len(pts) - 1)
        glow(c, x, y, w * (0.6 + 0.8 * u), col, a * (1 - 0.6 * u))
def light_beams(c, x, y, a, n=7, L=1400, spread=0.9, base=-2.4, col=(1, 0.94, 0.72)):
    if a <= 0: return
    for k_ in range(n):
        ang = base + spread * (k_ / (n - 1) - 0.5)
        c.new_path(); c.move_to(x, y); c.line_to(x + math.cos(ang - 0.04) * L, y + math.sin(ang - 0.04) * L); c.line_to(x + math.cos(ang + 0.04) * L, y + math.sin(ang + 0.04) * L); c.close_path()
        c.set_source_rgba(*col, a * 0.07); c.fill()

# ---------- 背景 ----------
def bg_sun(c):
    bands(c, [rgb('f2d48a'), rgb('f0c070'), rgb('e8a85a'), rgb('d8904a'), rgb('c07a46'), rgb('a86a40')], -BO, 700)
    for k_ in range(28):
        a = k_ * math.pi / 14; c.new_path(); c.move_to(960, 300)
        c.line_to(960 + math.cos(a - 0.05) * 1600, 300 + math.sin(a - 0.05) * 1600); c.line_to(960 + math.cos(a + 0.05) * 1600, 300 + math.sin(a + 0.05) * 1600); c.close_path()
        c.set_source_rgba(1, 0.95, 0.75, 0.18); c.fill()
    circ(c, 960, 300, 230, rgb('f8e2a0')); ring_stroke(c, 960, 300, 230, G['gold2'], 6); ring_stroke(c, 960, 300, 200, G['gold'], 3)
    for k_ in range(16):
        a = k_ * math.pi / 8; shape(c, [(960 + math.cos(a - 0.1) * 236, 300 + math.sin(a - 0.1) * 236), (960 + math.cos(a) * 300, 300 + math.sin(a) * 300), (960 + math.cos(a + 0.1) * 236, 300 + math.sin(a + 0.1) * 236)], G['gold'], 2.4, t=0)
    shape(c, [(-300, 700), (-300, 600), (300, 560), (700, 610), (1100, 560), (1500, 600), (2220, 560), (2220, 700)], rgb('8a6a3a'), 3, t=0)
    rect(c, -10, 690, SW + 20, BH, rgb('6a5232')); rect(c, -10, 686, SW + 20, 5, LINE)
    for x in (180, 1740): ionic(c, x, 120, 690, 90, rgb('efe2c4'))
def bg_meadow(c, dusk=False):
    cols = [rgb('8fb6cf'), rgb('a8c8d6'), rgb('c4d8d6'), rgb('e0e0c8'), rgb('ecdcb4')] if not dusk else [rgb('2a2a4e'), rgb('5a3a5e'), rgb('a0505a'), rgb('d8784a'), rgb('f0b060')]
    bands(c, cols, -BO, 560)
    shape(c, [(-300, 640), (-300, 520), (200, 470), (600, 520), (1000, 450), (1400, 510), (1800, 460), (2220, 500), (2220, 640)], rgb('8aa070') if not dusk else rgb('5a4a52'), 3, t=0)
    shape(c, [(-300, 700), (-300, 580), (400, 560), (900, 600), (1400, 560), (2220, 590), (2220, 700)], rgb('6f8a56') if not dusk else rgb('4a3a40'), 3, t=0)
    rect(c, -10, 690, SW + 20, BH, rgb('5e7a44') if not dusk else rgb('3a2e30')); rect(c, -10, 686, SW + 20, 5, LINE)
    r = np.random.default_rng(31)
    for i in range(160):
        x, y = r.uniform(0, SW), r.uniform(700, 1100)
        if not dusk:
            col = [G['white'], G['saff'], G['rose'], rgb('c8a0d8')][i % 4]
            for j in range(5): circ(c, x + 5 * math.cos(j * 1.256), y + 5 * math.sin(j * 1.256), 3.4, col)
        line(c, [(x, y + 6), (x - 4, y + 22)], rgb('3a5a2a') if not dusk else rgb('2a2028'), 2)
def bg_meadow_d(c): bg_meadow(c, True)
def bg_wedding(c):
    bg_meadow(c)
    for x in (200, 520, 1400, 1720): ionic(c, x, 140, 690, 80, rgb('f2e8d2'))
    rect(c, 140, 120, 1640, 30, rgb('efe2c4')); c.rectangle(140, 120, 1640, 30); c.set_source_rgb(*LINE); c.set_line_width(3); c.stroke(); meander(c, 140, 1780, 124, 22, G['terra'])
    for j in range(5):   # 花环
        x0 = 140 + j * 328; c.new_path(); c.move_to(x0, 150); c.curve_to(x0 + 100, 250, x0 + 228, 250, x0 + 328, 150); c.set_source_rgb(*G['green']); c.set_line_width(12); c.stroke()
        for q in range(9):
            u = q / 8; px = x0 + 328 * u; py = 150 + 4 * 75 * u * (1 - u) * 1.33
            circ(c, px, py, 9, [G['rose'], G['white'], G['saff']][q % 3]); ring_stroke(c, px, py, 9, LINE, 1.6)
def bg_forest(c):
    bands(c, [rgb('3a4a5a'), rgb('5a6a62'), rgb('8a8a6a'), rgb('b49a6a'), rgb('d8b070')], -BO, 600)
    for x, s in ((80, 1.5), (360, 1.2), (1560, 1.3), (1840, 1.6), (700, 0.8), (1250, 0.85)):
        olive_tree(c, x, 680, s)
    shape(c, [(-300, 700), (-300, 600), (500, 580), (1000, 620), (1600, 580), (2220, 610), (2220, 700)], rgb('5a6a3a'), 3, t=0)
    rect(c, -10, 690, SW + 20, BH, rgb('4a5a30')); rect(c, -10, 686, SW + 20, 5, LINE)
def bg_gate(c):
    bands(c, [rgb('0e0a18'), rgb('1e1428'), rgb('3a1e34'), rgb('5a2a3a'), rgb('7a3a3a')], -BO, 640)
    r = np.random.default_rng(9)
    for i in range(90): circ(c, r.uniform(0, SW), r.uniform(-BO, 400), r.uniform(0.8, 2.2), (1, 0.9, 0.8), r.uniform(0.2, 0.6))
    cliff = [(-300, 760), (-300, -100), (300, -60), (520, 40), (640, 200), (700, 380), (720, 690), (1200, 690), (1220, 380), (1290, 200), (1420, 40), (1640, -60), (2220, -100), (2220, 760)]
    shape(c, cliff, rgb('2e2630'), 4)
    c.save(); clip_shape(c, cliff); cracks(c, 17, 40, -200, 700, rgb('1e1820')); c.restore()
    shape(c, [(720, 690), (700, 380), (760, 250), (960, 190), (1160, 250), (1220, 380), (1200, 690)], VOID, 4)
    glow(c, 960, 520, 300, (0.35, 0.1, 0.4), 0.35)
    for x in (560, 1380):   # 枯树
        line(c, [(x, 690), (x + 10, 520), (x - 40, 430), (x - 90, 400)], rgb('1a141a'), 14); line(c, [(x + 10, 520), (x + 70, 440), (x + 110, 430)], rgb('1a141a'), 10)
    rect(c, -10, 690, SW + 20, BH, rgb('1e1820')); rect(c, -10, 686, SW + 20, 5, LINE)
    for x in range(-40, SW, 140): shape(c, [(x, 700), (x + 30, 690), (x + 60, 700)], rgb('3a3036'), 2)
def bg_styx(c):
    bands(c, [rgb('06070c'), rgb('0c1018'), rgb('121a24'), rgb('18242e'), rgb('1e2e36')], -BO, 520)
    for x in range(-40, SW + 80, 110):   # 钟乳石
        h = 120 + 90 * math.sin(x * 0.07); shape(c, [(x - 40, -BO), (x, -BO + 160 + h), (x + 40, -BO)], rgb('141a22'), 3, t=0)
    shape(c, [(-300, 560), (-300, 470), (500, 440), (1100, 470), (1600, 430), (2220, 460), (2220, 560)], rgb('1a2228'), 3, t=0)
    rect(c, -10, 520, SW + 20, 260, rgb('1a3a3a'))
    for j in range(8): wave_band(c, -10, SW + 20, 530 + j * 30, 20, rgb('2e5a56'), 2)
    rect(c, -10, 760, SW + 20, BH, rgb('1e1c20')); rect(c, -10, 756, SW + 20, 5, LINE)
def bg_hall_u(c):
    mottle(c, rgb('1a1620'), rgb('120e16'), 77); cracks(c, 5, 18, col=rgb('0e0a10'))
    rect(c, -10, -BO, SW + 20, BO + 40, rgb('0a080e')); rect(c, -10, 40, SW + 20, 34, rgb('3a2a3a')); meander(c, -10, SW + 20, 46, 22, rgb('8a7a5a'))
    for x in (140, 380, 1540, 1780): doric(c, x, 80, 690, 110, rgb('4a4450'))
    for j in range(3): shape(c, [(600 - j * 60, 690 - j * 36, 'c'), (1320 + j * 60, 690 - j * 36, 'c'), (1320 + j * 60, 726 - j * 36, 'c'), (600 - j * 60, 726 - j * 36, 'c')], rgb('2e2832'), 3, t=0)
    for tx in (720, 1060):   # 双宝座
        shape(c, [(tx, 600), (tx, 240), (tx + 30, 200), (tx + 150, 200), (tx + 180, 240), (tx + 180, 600)], rgb('2a2228'), 4)
        shape(c, [(tx + 22, 590), (tx + 22, 260), (tx + 158, 260), (tx + 158, 590)], G['purple2'], 3)
        for k_ in range(5): line(c, [(tx + 30, 280 + k_ * 60), (tx + 150, 280 + k_ * 60)], G['gold2'], 2)
    rect(c, -10, 690, SW + 20, BH, rgb('16121a')); rect(c, -10, 686, SW + 20, 5, LINE)
def bg_stairs(c):
    rect(c, -10, -BO, SW + 20, BH, VOID)
    for i in range(40):
        u = i / 39; x = lerp(-200, 2000, u); y = lerp(1050, -260, u); w_ = 120; h_ = 33
        a = 0.25 + 0.5 * u
        c.new_path(); c.move_to(x, y); c.line_to(x + w_, y); c.line_to(x + w_, y - h_); c.set_source_rgba(0.35, 0.38, 0.5, a); c.set_line_width(3); c.stroke()
        rect(c, x, y, w_ + 2, 1400, (0.07, 0.07, 0.1), 1)
def bg_exit(c):
    rect(c, -10, -BO, SW + 20, BH, VOID)
    # 右上：洞口外的人间
    mouth = [(1060, 760), (1060, 300), (1120, 120), (1300, -60), (1600, -160), (2300, -200), (2300, 760)]
    c.save(); clip_shape(c, mouth, t=0.3)
    bands(c, [rgb('f8f0d0'), rgb('f6e6b0'), rgb('f0d890'), rgb('e8c878'), rgb('d8b468')], -BO, 760, 1000, 2300)
    glow(c, 1700, 100, 900, (1, 0.98, 0.85), 0.8)
    shape(c, [(1000, 760), (1000, 640), (1400, 600), (1800, 640), (2300, 610), (2300, 760)], rgb('b8c880'), 3, t=0)
    c.restore()
    c.new_path(); smooth(c, mouth, True, 0.3); c.set_source_rgb(*LINE); c.set_line_width(5); c.stroke()
    # 岩壁纹
    r = np.random.default_rng(13)
    for i in range(40):
        x, y = r.uniform(0, 1050), r.uniform(-250, 760); line(c, [(x, y), (x + r.uniform(-40, 40), y + r.uniform(20, 70))], rgb('1a1a24'), 2)
    # 地面：左边暗石阶，右边光地
    rect(c, -10, 760, 1070, BH, rgb('121218')); rect(c, 1060, 760, SW, BH, rgb('c8b880'))
    rect(c, -10, 756, SW + 20, 5, LINE)
    for k_ in range(6): line(c, [(1060 - k_ * 170, 760), (1060 - k_ * 170, 1200)], rgb('22222c'), 3)
def edge_x(): return 1060
def bg_mourn(c):
    bg_meadow(c, True)

