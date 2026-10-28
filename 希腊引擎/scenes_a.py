# ======== 百眼巨人阿耳戈斯：场景 ========
HERA = dict(kind='gf', dress=G['blue'], dress2=G['blue2'], himation=G['purple'], himation2=G['purple2'], trim=G['gold'], skin=G['skin'], skin2=G['skin2'],
            necklace=True, band=G['gold'], bracelet=True, hair_c=rgb('2a1d16'))
ZEUS = dict(kind='gm', long=True, beard=True, wreath=True, dress=G['white'], dress2=G['cream2'], himation=G['saff'], himation2=G['saff2'], trim=G['gold'],
            skin=G['skin'], skin2=G['skin2'], hair_c=rgb('4a3a30'), hair_c2=rgb('6a5444'))
IO = dict(kind='nymph', dress=G['white'], dress2=G['cream2'], himation=G['rose'], himation2=G['rose2'], trim=G['gold'], skin=G['pale'], skin2=G['pale2'],
          flower=G['rose'], necklace=True, hair_c=rgb('3a2418'), hair_c2=rgb('5a3a28'))
HERM = dict(kind='gm', long=False, dress=G['saff'], dress2=G['saff2'], trim=G['red'], himation=G['red'], himation2=G['red2'], skin=G['skin'], skin2=G['skin2'],
            hair_c=rgb('3a2418'), hair_c2=rgb('5a3a28'), belt=G['gold'])
SHEP = dict(kind='gm', long=False, dress=rgb('8a6a44'), dress2=rgb('6e5234'), trim=rgb('4a3420'), skin=G['skin'], skin2=G['skin2'], hair_c=rgb('3a2418'), hair_c2=rgb('5a3a28'), belt=rgb('4a3420'))
ARG = dict(kind='gm', long=False, beard=True, dress=rgb('5a6a3a'), dress2=rgb('46542c'), trim=G['gold'], skin=rgb('c8946a'), skin2=rgb('a87850'),
           hair_c=rgb('2a1d16'), hair_c2=rgb('4a3324'), belt=G['bronze'], himation=rgb('7a4a2a'), himation2=rgb('5e3820'))

def hera(c, x, h, pose, face, y=GY, **k): return fig(c, x, y, h, pose, face, **{**HERA, **k})
def zeus(c, x, h, pose, face, y=GY, **k): return fig(c, x, y, h, pose, face, **{**ZEUS, **k})
def io(c, x, h, pose, face, y=GY, **k): return fig(c, x, y, h, pose, face, **{**IO, **k})

# ---------- 头部坐标系 ----------
def head_map(o):
    A = np.array([[10, -150, 1], [50, -70, 1], [30, -112, 1]], float)
    B = np.array([o['head'], o['face'], o['brow']], float)
    M = np.linalg.solve(A, B)
    return lambda x, y: tuple(np.array([x, y, 1.0]) @ M), math.hypot(*(np.array(o['face']) - np.array(o['head']))) / 89.4
def mouth_pt(o):
    f, s = head_map(o); return f(50, -38)
def petasos(c, o, wing=0.0):
    f, s = head_map(o)
    brim = [f(-70, -122), f(-30, -140), f(30, -140), f(76, -124), f(30, -112), f(-30, -112)]
    dome = [f(-36, -130), f(-26, -170), f(10, -184), f(36, -166), f(40, -132)]
    for sg, px in ((-1, -40), (1, -10)):
        a = 0.25 * math.sin(wing)
        wpts = [f(px, -150), f(px - 30, -200 - 20 * a), f(px - 70, -214 - 30 * a), f(px - 56, -188), f(px - 80, -184 - 10 * a), f(px - 50, -164), f(px - 66, -156), f(px - 10, -140)]
        shape(c, wpts, G['white'], 2.4)
    shape(c, dome, G['gold'], 2.6); shape(c, brim, G['gold2'], 2.6)
def straw_hat(c, o):
    f, s = head_map(o)
    shape(c, [f(-84, -118), f(-30, -138), f(30, -138), f(90, -120), f(30, -108), f(-30, -108)], rgb('d8b870'), 2.4)
    shape(c, [f(-34, -128), f(-20, -168), f(20, -172), f(40, -130)], rgb('c8a458'), 2.4)
    for k in range(4): line(c, [f(-60 + k * 40, -116), f(-50 + k * 40, -126)], rgb('a8843c'), 1.6)
def helmet(c, o, crest=None):
    f, s = head_map(o)
    shape(c, [f(-50, -100), f(-44, -150), f(-6, -176), f(40, -164), f(58, -130), f(60, -96), f(40, -96), f(36, -116), f(10, -124), f(-20, -110), f(-24, -60), f(-44, -50)], G['bronze'], 2.6)
    cr = [f(-50, -150), f(-40, -210), f(0, -232), f(40, -214), f(50, -170), f(10, -184), f(-24, -176)]
    shape(c, cr, crest or G['red'], 2.4)
def syrinx(c, x, y, s, a=1.0):
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(0.1)
    for k in range(6): shape(c, [(-30 + k * 10, 0), (-21 + k * 10, 0), (-21 + k * 10, 30 + k * 12), (-30 + k * 10, 30 + k * 12)], rgb('d8c07a'), 1.6, t=0)
    line(c, [(-32, 14), (32, 14)], rgb('8a5a26'), 4)
    c.restore()
def harpe(cc):
    line(cc, [(0, 30), (0, 80)], rgb('5a3a1e'), 12)
    shape(cc, [(-6, 30), (6, 30), (8, -120), (40, -200), (90, -210), (60, -186), (30, -150), (24, -60), (14, 30)], rgb('d8dee6'), 2.6)
def caduceus(cc):
    line(cc, [(0, -260), (0, 240)], G['gold'], 7)
    for sg in (-1, 1):
        pts = [(sg * 18 * math.sin(i * 0.6), -200 + i * 14) for i in range(26)]
        line(cc, pts, G['green2'], 4)
    shape(cc, [(-40, -250), (0, -270), (40, -250), (0, -240)], G['white'], 2)
def club(cc):
    shape(cc, [(-8, 60), (8, 60), (24, -280), (0, -320), (-24, -280)], rgb('6a4a2a'), 3)
def phone(cc): shape(cc, [(-10, 30), (12, 30), (12, 70), (-10, 70)], rgb('2a2a30'), 2)
def jar_head(cc): jar(cc, 0, -20, 0.8)

# ---------- 百眼 ----------
_r = np.random.default_rng(100)
TORSO = [(-50 + cx * 21 + (ry % 2) * 10 + _r.uniform(-3, 3), -244 + ry * 35 + _r.uniform(-4, 4)) for ry in range(11) for cx in range(6)][:62]
SHOULD = [(-60 + k * 18, -262 + (k % 2) * 10) for k in range(8)]
LEGS = [(side, d) for side in (0, 1) for d in (60, 110, 230, 280, 330, 360, 160, 200)]
HEADE = [(-40, -120), (-10, -135), (20, -128), (-50, -86), (-55, -40), (-30, -20), (0, -150), (-24, -100), (-62, -110), (12, -14), (-40, 4), (-60, 12)]
RANK = list(_r.permutation(98) + 2)   # 0,1 为脸上那双主眼
def eye_g(c, x, y, r, op=1.0, lx=0.0, ly=0.0, ang=0.0, glowa=0.0, col=None):
    c.save(); c.translate(x, y); c.rotate(ang)
    if glowa > 0 and op > 0.2: glow(c, 0, 0, r * 3, (0.5, 0.95, 0.85), glowa * op)
    if op > 0.05:
        h = r * 0.62 * op
        c.new_path(); c.move_to(-r, 0); c.curve_to(-r * 0.4, -h * 1.5, r * 0.4, -h * 1.5, r, 0); c.curve_to(r * 0.4, h * 1.5, -r * 0.4, h * 1.5, -r, 0); c.close_path()
        c.set_source_rgb(*rgb('f6efdd')); c.fill_preserve(); c.set_source_rgb(*LINE); c.set_line_width(max(1.2, r * 0.14)); c.stroke_preserve()
        c.save(); c.clip()
        ix, iy = lx * r * 0.4, ly * h * 0.4
        circ(c, ix, iy, r * 0.5, col or rgb('2f8a7a')); circ(c, ix, iy, r * 0.24, LINE); circ(c, ix - r * 0.14, iy - r * 0.14, r * 0.09, (1, 1, 1))
        c.restore()
    else:
        c.new_path(); c.move_to(-r, 0); c.curve_to(-r * 0.4, r * 0.55, r * 0.4, r * 0.55, r, 0); c.set_source_rgb(*LINE); c.set_line_width(max(1.4, r * 0.16)); c.stroke()
        for k in (-0.5, 0, 0.5): line(c, [(k * r, r * 0.4), (k * r * 1.2, r * 0.75)], LINE, max(1, r * 0.1))
    c.restore()
def eye_open(i, closed):   # 第 i 只（按 RANK）的睁开度
    rk = i if i < 2 else RANK[i - 2]
    return float(np.clip(1 - (closed - rk), 0, 1))
def argus(c, x, h, pose, face, closed=0.0, look=(0.0, 0.0), glowa=0.0, y=GY, legs=True, twitch=0.0, t=0.0, opfn=None, **k):
    eye_open_ = (lambda i, cl: opfn(i)) if opfn else eye_open
    h = h * 0.86
    p = dict(nsh=0.12, nel=0.18, fsh=-0.1, fel=0.18, nhip=0.04, nkn=-0.03, fhip=-0.06, fkn=0.02, body=0.0); p.update(pose)
    def jit(i): return twitch * 0.5 * (1 + math.sin(t * 23 + i * 1.7)) if twitch else 0
    idx = [2]
    def mark(cc):
        for j, (ex, ey) in enumerate(TORSO + SHOULD):
            i = 2 + j; op = eye_open_(i, closed); op = max(0, op - jit(i)) if op > 0 else op
            eye_g(cc, ex, ey, 9.5, op, look[0], look[1], 0.0, glowa)
        if legs:
            for j, (side, d) in enumerate(LEGS):
                hx = -14 if side == 0 else 14; a1 = (p['fhip'] if side == 0 else p['nhip']) - p['body']; a2 = (p['fhip'] + p['fkn'] if side == 0 else p['nhip'] + p['nkn']) - p['body']
                if d < 205: px, py = hx - d * math.sin(a1), d * math.cos(a1)
                else: kx, ky = hx - 205 * math.sin(a1), 205 * math.cos(a1); dd = d - 205; px, py = kx - dd * math.sin(a2), ky + dd * math.cos(a2)
                if py < 155 and d < 205: continue
                i = 2 + 70 + j; op = eye_open_(i, closed); op = max(0, op - jit(i)) if op > 0 else op
                eye_g(cc, px, py, 9, op, look[0], look[1], 0.0, glowa)
    face = dict(face); face['eye'] = min(face.get('eye', 1.0), eye_open_(0, closed))
    o = fig(c, x, y, h, p, face, mark=mark, **{**ARG, **k})
    f, s = head_map(o)
    for j, (hx, hy) in enumerate(HEADE):
        i = 2 + 86 + j; op = eye_open_(i, closed); op = max(0, op - jit(i)) if op > 0 else op
        ex, ey = f(hx, hy); eye_g(c, ex, ey, 10 * s * 1.18, op, look[0] * (-1 if k.get('flip') else 1), look[1], 0.0, glowa)
    return o
def eye_dots(c, o_pts, a, col=(0.5, 1.0, 0.9)):
    for (x, y) in o_pts: glow(c, x, y, 18, col, a); circ(c, x, y, 3, col, a)

# ---------- 动物 ----------
def cow(c, x, y, s, t=0.0, flip=False, graze=0.0):
    bull(c, x, y + 8 * graze * s, s, t * 0.3, rgb('fbf6ea'), flip)
    sg = -1 if flip else 1
    for k in range(5): circ(c, x + sg * (150 + k * 9) * s, y - (100 - k * 6 + 30 * graze) * s, 6 * s, [G['rose'], G['saff'], G['white']][k % 3])
def sheep(c, x, y, s, t=0.0, ph=0.0, flip=False, lie=0.0, graze=0.0):
    c.save(); c.translate(x, y); c.scale(-s if flip else s, s)
    if lie < 0.5:
        for k, lx in enumerate((-40, -24, 30, 46)):
            a = 0.2 * math.sin(t * 6 + ph + k * 1.6) if graze == 0 else 0
            with J(c, lx, -40, a) as cl: shape(cl, taper(44, 7, 5), LINE, 1)
    by = -60 + 34 * lie
    for k in range(9):
        ang = k / 9 * 2 * math.pi; circ(c, 30 * math.cos(ang), by + 18 * math.sin(ang), 22, rgb('f0e8d4'))
    for k in range(9):
        ang = k / 9 * 2 * math.pi; ring_stroke(c, 30 * math.cos(ang), by + 18 * math.sin(ang), 22, LINE, 2)
    circ(c, 0, by, 30, rgb('f0e8d4'))
    hy = by - 12 + 30 * graze + 3 * math.sin(t * 2 + ph)
    shape(c, [(44, hy - 14), (70, hy - 16), (84, hy + 4), (70, hy + 16), (48, hy + 10)], rgb('2a2420'), 2)
    circ(c, 68, hy - 4, 2.4, (1, 1, 1))
    shape(c, [(52, hy - 14), (40, hy - 26), (58, hy - 18)], rgb('2a2420'), 1.6)
    c.restore()
def peacock(c, x, y, s, t=0.0, fan=1.0, eyes=1.0, glowa=0.0, flip=False, wing=0.0, eye_lids=1.0, n_spots=100, walk_=0.0):
    c.save(); c.translate(x, y); c.scale(-s if flip else s, s)
    rx, ry = -30, -150
    rows = [(150, 20), (230, 32), (310, 48)]
    span = lerp(0.18, 1.0, fan) * math.pi * 1.05; ctr = lerp(math.pi - 0.15, -math.pi / 2 - 0.12, fan)
    R = rows[-1][0] + 40
    # 羽轴
    nsh = 48
    for i in range(nsh):
        u = i / (nsh - 1); ang = ctr - span / 2 + span * u + 0.02 * math.sin(t * 2 + i)
        ex, ey = rx + math.cos(ang) * R * lerp(0.6, 1.0, fan), ry + math.sin(ang) * R * lerp(0.6, 1.0, fan)
        line(c, [(rx, ry), (ex, ey)], rgb('3a6a4a'), 3)
        for q in range(6):
            uu = 0.25 + q * 0.13; px, py = rx + (ex - rx) * uu, ry + (ey - ry) * uu
            for sg in (-1, 1): line(c, [(px, py), (px + 14 * math.cos(ang + sg * 1.2), py + 14 * math.sin(ang + sg * 1.2))], rgb('5a9a5a'), 2)
    cnt = 0
    for (rr, n) in rows:
        for i in range(n):
            if cnt >= n_spots: break
            u = (i + 0.5) / n; ang = ctr - span / 2 + span * u + 0.02 * math.sin(t * 2 + i + rr)
            rr2 = rr * lerp(0.6, 1.0, fan); px, py = rx + math.cos(ang) * rr2, ry + math.sin(ang) * rr2
            sz = 15 + rr / 40
            gw = glowa * (0.6 + 0.4 * math.sin(t * 3 + cnt))
            if gw > 0: glow(c, px, py, sz * 2.6, (0.4, 0.95, 0.85), gw)
            c.save(); c.translate(px, py); c.rotate(ang + math.pi / 2); c.scale(1, 1.35)
            circ(c, 0, 0, sz, rgb('c8a43a')); circ(c, 0, 0, sz * 0.74, rgb('2f8a6a')); circ(c, 0, 0, sz * 0.5, rgb('2a5a9a')); ring_stroke(c, 0, 0, sz, LINE, 1.4)
            if eyes > 0.02:
                op = eye_lids if eyes >= 1 else eyes
                if op > 0.3: circ(c, 0, 0, sz * 0.28 * op, rgb('101828'))
                if op > 0.6: circ(c, -sz * 0.1, -sz * 0.12, sz * 0.08, (1, 1, 1))
            c.restore()
            cnt += 1
    # 身体
    if walk_ > 0 or True:
        for k, lx in enumerate((-10, 12)):
            a = 0.3 * math.sin(t * 6 + k * 3) * walk_
            with J(c, lx, -40, a) as cl: line(cl, [(0, 0), (0, 70), (16, 76)], rgb('8a7a6a'), 5)
    body = [(-60, -150), (-30, -186), (20, -170), (44, -120), (30, -60), (-10, -40), (-50, -70)]
    shape(c, body, rgb('2a5aa8'), 3)
    wa = 0.5 * math.sin(wing) if wing else 0
    shape(c, [(-40, -150), (0, -168), (30, -120), (0, -80 - 40 * wa), (-40, -90 - 60 * wa)], rgb('8a7a5a'), 2.4)
    for k in range(4): line(c, [(-30 + k * 12, -140), (-24 + k * 10, -96 - 40 * wa)], rgb('5a4a3a'), 1.6)
    neck = [(10, -170), (24, -220), (30, -270), (52, -286), (64, -270), (50, -250), (42, -200), (40, -150)]
    shape(c, neck, rgb('2a5aa8'), 3)
    shape(c, [(60, -282), (82, -276), (62, -268)], rgb('8a8a7a'), 2)
    circ(c, 50, -277, 6, (1, 1, 1)); circ(c, 52, -277, 3, LINE)
    for k in range(3): line(c, [(40 + k * 6, -288), (34 + k * 9, -316)], rgb('2a5aa8'), 2); circ(c, 34 + k * 9, -318, 5, rgb('2a8a9a'))
    c.restore()

# ---------- 云、鸟、天空 ----------
def cloud(c, x, y, s, col=(0.97, 0.95, 0.9), a=1.0, line_=True, seed=0):
    r = np.random.default_rng(seed)
    pts = [(-120, 0), (-90, -40), (-40, -60), (10, -80), (60, -56), (110, -40), (140, 0)]
    c.push_group()
    for (px, py) in pts: circ(c, x + px * s, y + py * s * 0.8, (50 + 10 * (seed % 3)) * s, col)
    rect(c, x - 140 * s, y - 10 * s, 290 * s, 40 * s, col)
    c.pop_group_to_source(); c.paint_with_alpha(a)
    if line_:
        for (px, py) in pts[1:-1]:
            c.new_path(); c.arc(x + px * s, y + py * s * 0.8, (50 + 10 * (seed % 3)) * s, math.pi * 1.05, math.pi * 1.95); c.set_source_rgba(*LINE, 0.5 * a); c.set_line_width(2.2); c.stroke()
        for k in range(3): line(c, [(x - 80 * s + k * 60 * s, y - 10 * s), (x - 30 * s + k * 60 * s, y - 14 * s)], tuple(v * 0.85 for v in col), 2)
def drift_clouds(c, t, n=6, y0=-200, y1=200, col=(0.97, 0.95, 0.9), a=0.9, seed=7, spd=12, s=1.0):
    r = np.random.default_rng(seed)
    for i in range(n):
        x = (r.uniform(-300, SW + 300) + t * spd * r.uniform(0.6, 1.4)) % (SW + 600) - 300
        cloud(c, x, r.uniform(y0, y1), s * r.uniform(0.6, 1.2), col, a, True, i)
def birds(c, t, n=6, y=60, seed=3, a=0.9, spd=60):
    r = np.random.default_rng(seed)
    for i in range(n):
        x = (r.uniform(0, SW) + t * spd) % (SW + 200) - 100; yy = y + r.uniform(-60, 60) + 8 * math.sin(t * 2 + i)
        w = 12 + 6 * math.sin(t * 9 + i)
        line(c, [(x - 16, yy - w * 0.5), (x - 6, yy - 2), (x, yy), (x + 6, yy - 2), (x + 16, yy - w * 0.5)], (0.15, 0.12, 0.1), 2.4)
def fireflies(c, t, n=30, y0=300, y1=760, seed=9, a=1.0):
    r = np.random.default_rng(seed)
    for i in range(n):
        x = r.uniform(0, SW) + 40 * math.sin(t * 0.7 + i); y = r.uniform(y0, y1) + 30 * math.sin(t * 0.9 + i * 2)
        b = 0.5 + 0.5 * math.sin(t * 3 + i * 1.3); glow(c, x, y, 18, (0.9, 1.0, 0.5), 0.6 * b * a); circ(c, x, y, 2.4, (1, 1, 0.7), b * a)
def rain(c, t, a=1.0, n=160, seed=4, ang=0.25):
    r = np.random.default_rng(seed)
    for i in range(n):
        x0 = r.uniform(-200, SW + 200); y = (r.uniform(-300, 900) + t * 1400) % 1200 - 300; x = x0 + (y + 300) * ang
        line(c, [(x, y), (x + 14 * ang * 3, y + 42)], (0.75, 0.82, 0.95), 1.6)
def lightning(c, x, y0, y1, seed, a=1.0):
    if a <= 0: return
    r = np.random.default_rng(seed); pts = [(x, y0)]; yy = y0; xx = x
    while yy < y1: yy += r.uniform(40, 90); xx += r.uniform(-50, 50); pts.append((xx, yy))
    glow(c, x, (y0 + y1) / 2, 300, (0.8, 0.85, 1.0), 0.4 * a)
    line(c, pts, (0.95, 0.97, 1.0), 6 * a + 1)
def sun_disc(c, x, y, r, col=(1, 0.9, 0.6), a=1.0):
    glow(c, x, y, r * 4, col, 0.4 * a); circ(c, x, y, r, col, a)
def moon(c, x, y, r, a=1.0):
    glow(c, x, y, r * 4, (0.85, 0.9, 1.0), 0.3 * a); circ(c, x, y, r, (0.95, 0.94, 0.86), a); circ(c, x - r * 0.3, y - r * 0.2, r * 0.18, (0.82, 0.8, 0.72), a); circ(c, x + r * 0.25, y + r * 0.3, r * 0.12, (0.82, 0.8, 0.72), a)
def swirl_fx(c, x, y, t, a, R=220, col=(1, 0.85, 0.4)):
    if a <= 0: return
    for k in range(40):
        ang = t * 4 + k * 0.5; rr = R * ((k / 40 + t * 0.6) % 1.0)
        px, py = x + rr * math.cos(ang), y + rr * 0.7 * math.sin(ang)
        circ(c, px, py, 5, col, a * (1 - rr / R)); glow(c, px, py, 18, col, 0.3 * a * (1 - rr / R))
    glow(c, x, y, R, col, 0.3 * a)
def haze(c, t, x, y, a, dirx=1, col=(0.7, 0.55, 0.95)):
    if a <= 0: return
    for k in range(8):
        ph = (t * 0.25 + k / 8) % 1.0; px = x + dirx * ph * 700; py = y - 40 + 60 * math.sin(ph * 6 + k)
        glow(c, px, py, 70 + 80 * ph, col, 0.35 * a * math.sin(math.pi * ph))
def zzz(c, x, y, t, a=1.0):
    for k in range(3):
        ph = (t * 0.4 + k / 3) % 1.0; s_ = 18 + 22 * ph; px = x + 60 * ph + 10 * math.sin(t * 2 + k); py = y - 120 * ph
        line(c, [(px - s_ / 2, py - s_ / 2), (px + s_ / 2, py - s_ / 2), (px - s_ / 2, py + s_ / 2), (px + s_ / 2, py + s_ / 2)], (0.95, 0.95, 1.0), 3.4 * a * math.sin(math.pi * ph) + 0.1)
def alarm_rays(c, x, y, t, a):
    if a <= 0: return
    for k in range(16):
        ang = k / 16 * 2 * math.pi + t * 0.5; L = 300 + 60 * math.sin(t * 10 + k)
        line(c, [(x + 80 * math.cos(ang), y + 80 * math.sin(ang)), (x + L * math.cos(ang), y + L * math.sin(ang))], (0.9, 0.2, 0.15), 6 * a)
    glow(c, x, y, 400, (1, 0.25, 0.2), 0.35 * a * (0.6 + 0.4 * math.sin(t * 14)))
def orb(c, x, y, r, a=1.0):
    glow(c, x, y, r * 3.5, (0.4, 1.0, 0.85), 0.5 * a); eye_g(c, x, y, r, 1.0, 0, 0, 0, 0)
def petals(c, t, a, x0=0, x1=SW, seed=5, n=40, cols=None):
    if a <= 0: return
    r = np.random.default_rng(seed); cols = cols or [G['rose'], G['white'], G['saff']]
    for i in range(n):
        x = r.uniform(x0, x1) + 80 * math.sin(t + i); y = (r.uniform(-300, 800) + t * 90) % 1100 - 300
        c.save(); c.translate(x, y); c.rotate(t * 2 + i); shape(c, [(-8, 0), (0, -5), (8, 0), (0, 5)], cols[i % len(cols)], 1.2); c.restore()

# ---------- 背景（多层） ----------
PALS = dict(day=['8fb6cf', 'a8c8d6', 'c4d8d6', 'e0e0c8', 'ecdcb4'], dusk=['2a2a4e', '5a3a5e', 'a0505a', 'd8784a', 'f0b060'],
            night=['070c1e', '0c1430', '121c3e', '18264e', '20305a'], storm=['1e2028', '2a2c36', '363a44', '444852', '52565e'],
            gold=['e8c88a', 'f0d8a0', 'f6e6c0', 'f8eed6', 'fbf4e4'], red=['2a0c10', '4e1416', '7e2418', 'b0401e', 'd8702e'], noon=['6aa0d0', '86b6dc', 'a4cae2', 'c6dce6', 'e6e8dc'])
TINT = dict(day=None, noon=None, gold=None, dusk=((0.55, 0.22, 0.2), 0.32), night=((0.04, 0.07, 0.2), 0.6), storm=((0.12, 0.13, 0.18), 0.5), red=((0.4, 0.05, 0.03), 0.5))
def sky(c, pal, y1=620): bands(c, [rgb(h) for h in PALS[pal]], -BO, y1)
def tinted(c, pal, fn):
    tn = TINT[pal]
    if not tn: fn(); return
    c.push_group(); fn(); pat = c.pop_group(); c.set_source(pat); c.paint(); c.set_source_rgba(*tn[0], tn[1]); c.mask(pat)
def mountains(c, y, h, col, seed, snow=True, n=7):
    r = np.random.default_rng(seed); pts = [(-300, y + 200), (-300, y)]; peaks = []
    for i in range(n + 1):
        x = -300 + (SW + 600) * i / n; px = x + r.uniform(-60, 60); py = y - h * r.uniform(0.5, 1.0); pts.append((px, py)); peaks.append((px, py))
        pts.append((px + (SW + 600) / n / 2, y - h * r.uniform(0.1, 0.35)))
    pts.append((SW + 300, y + 200)); shape(c, pts, col, 3, t=0.2)
    if snow:
        for (px, py) in peaks: shape(c, [(px - 50, py + 50), (px, py), (px + 50, py + 50), (px + 22, py + 40), (px, py + 56), (px - 24, py + 40)], rgb('f2eee6'), 2, t=0)
def cypress(c, x, y, s, col=None):
    col = col or rgb('2e4a2e'); shape(c, [(x, y - 260 * s), (x + 34 * s, y - 120 * s), (x + 30 * s, y), (x - 30 * s, y), (x - 34 * s, y - 120 * s)], col, 2.4)
    for k in range(5): line(c, [(x - 20 * s, y - 40 * s - k * 40 * s), (x, y - 60 * s - k * 40 * s), (x + 20 * s, y - 40 * s - k * 40 * s)], tuple(v * 0.75 for v in col), 1.6)
def mini_temple(c, x, y, s, col=None):
    col = col or rgb('ece2ca'); rect(c, x - 100 * s, y - 10 * s, 200 * s, 14 * s, col)
    for k in range(6): rect(c, x - 88 * s + k * 34 * s, y - 110 * s, 14 * s, 100 * s, col)
    shape(c, [(x - 110 * s, y - 110 * s), (x, y - 160 * s), (x + 110 * s, y - 110 * s)], col, 2, t=0)
def house(c, x, y, s, wall=None, roof=None):
    wall = wall or rgb('f2eadc'); roof = roof or G['terra']
    shape(c, [(x - 50 * s, y), (x - 50 * s, y - 60 * s), (x + 50 * s, y - 60 * s), (x + 50 * s, y)], wall, 2, t=0)
    shape(c, [(x - 60 * s, y - 56 * s), (x, y - 92 * s), (x + 60 * s, y - 56 * s)], roof, 2, t=0)
    rect(c, x - 10 * s, y - 34 * s, 20 * s, 34 * s, rgb('6a4a2a'))
def flowers(c, seed, y0, y1, n=160, cols=None, x0=0, x1=SW):
    r = np.random.default_rng(seed); cols = cols or [G['white'], G['saff'], G['rose'], rgb('c8a0d8')]
    for i in range(n):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1); col = cols[i % len(cols)]
        line(c, [(x, y + 6), (x - 4, y + 22)], rgb('3a5a2a'), 2)
        for j in range(5): circ(c, x + 5 * math.cos(j * 1.256), y + 5 * math.sin(j * 1.256), 3.4, col)
def grass_tufts(c, seed, y0, y1, n=80, col=None):
    r = np.random.default_rng(seed); col = col or rgb('4a6a2a')
    for i in range(n):
        x, y = r.uniform(0, SW), r.uniform(y0, y1)
        for k in range(5): line(c, [(x + k * 4, y), (x + k * 4 + (k - 2) * 5, y - 22 - 6 * (k % 2))], col, 2)
def big_olive(c, x, y, s):
    shape(c, [(x - 40 * s, y), (x - 26 * s, y - 160 * s), (x - 80 * s, y - 260 * s), (x - 50 * s, y - 270 * s), (x - 6 * s, y - 200 * s), (x + 30 * s, y - 290 * s), (x + 64 * s, y - 280 * s), (x + 26 * s, y - 160 * s), (x + 40 * s, y)], rgb('6a4a2a'), 3)
    for k in range(4): line(c, [(x - 20 * s + k * 12 * s, y - 10 * s), (x - 16 * s + k * 10 * s, y - 150 * s)], rgb('4a321c'), 2)
    r = np.random.default_rng(int(x))
    for i in range(46):
        px = x + r.uniform(-260, 260) * s; py = y - r.uniform(260, 470) * s
        circ(c, px, py, r.uniform(40, 70) * s, [rgb('6b7a3a'), rgb('7a8a46'), rgb('5a6a30')][i % 3])
    for i in range(80):
        px = x + r.uniform(-260, 260) * s; py = y - r.uniform(250, 480) * s
        c.save(); c.translate(px, py); c.rotate(r.uniform(0, 3)); shape(c, [(-10, 0), (0, -4), (10, 0), (0, 4)], rgb('a8b878'), 1); c.restore()
def land_pasture(c):
    mountains(c, 430, 260, rgb('8a9ab0'), 11)
    mountains(c, 500, 180, rgb('7a8a7a'), 12, False, 9)
    shape(c, [(-300, 700), (-300, 520), (200, 480), (600, 530), (1000, 470), (1400, 520), (1800, 480), (2220, 510), (2220, 700)], rgb('8aa070'), 3, t=0)
    mini_temple(c, 420, 492, 0.45); house(c, 1600, 500, 0.4); house(c, 1680, 506, 0.36, roof=G['red'])
    r = np.random.default_rng(3)
    for i in range(40): olive_tree(c, r.uniform(-50, SW + 50), r.uniform(520, 580), r.uniform(0.3, 0.45))
    for x in (120, 180, 1760, 1830): cypress(c, x, 600, 0.9)
    for k in range(3): line(c, [(-300, 600 + k * 24), (500, 590 + k * 20), (1300, 610 + k * 18), (2220, 596 + k * 22)], rgb('a89a7a'), 3)
    shape(c, [(-300, 700), (-300, 600), (400, 580), (900, 620), (1400, 590), (2220, 610), (2220, 700)], rgb('6f8a56'), 3, t=0)
    rect(c, -10, 690, SW + 20, BH, rgb('5e7a44')); rect(c, -10, 686, SW + 20, 5, LINE)
    big_olive(c, 1460, 700, 1.0)
    rock(c, 240, 740, 1.2); rock(c, 1760, 760, 0.9, 0.2)
    flowers(c, 31, 700, 1100); grass_tufts(c, 4, 700, 1100)
def make_pasture(pal):
    def f(c):
        sky(c, pal); tinted(c, pal, lambda: land_pasture(c))
    return f
def land_temple(c):
    mountains(c, 420, 240, rgb('9aa0b4'), 21)
    for x in (80, 180, 1740, 1840): cypress(c, x, 640, 1.2)
    for x in (300, 1620): cypress(c, x, 640, 0.9)
    rect(c, -10, 640, SW + 20, 60, rgb('d8ccb0'))
    for j in range(4): rect(c, 360 - j * 30, 600 + j * 22, 1200 + j * 60, 22, rgb('e6dcc4')); c.rectangle(360 - j * 30, 600 + j * 22, 1200 + j * 60, 22); c.set_source_rgb(*LINE); c.set_line_width(2); c.stroke()
    for k in range(8): ionic(c, 440 + k * 148, 160, 600, 74)
    rect(c, 390, 130, 1140, 36, rgb('efe2c4')); meander(c, 390, 1530, 136, 22, G['terra'])
    pediment(c, 370, 1550, 130, 130)
    for k in range(5): circ(c, 760 + k * 100, 70, 12, rgb('2f8a6a')); ring_stroke(c, 760 + k * 100, 70, 12, LINE, 2)
    rect(c, 560, 200, 800, 400, rgb('3a2a2a'))
    for k in range(8): ionic(c, 440 + k * 148, 160, 600, 74)
    for sx in (250, 1670):
        rect(c, sx - 60, 470, 120, 170, rgb('d8ccb0')); c.rectangle(sx - 60, 470, 120, 170); c.set_source_rgb(*LINE); c.set_line_width(2); c.stroke()
        sil(c, lambda: fig(c, sx, 470, 380, P_(nsh=1.4, nel=0.2), dict(eye=1), kind='gf', himation=G['grey']), rgb('e8e0cc'))
    floor_tiles(c, 700, rgb('cbbd9a'), rgb('b4a684'))
    flowers(c, 9, 720, 760, 40, x0=0, x1=300); flowers(c, 10, 720, 760, 40, x0=1620, x1=SW)
def bg_temple(c): sky(c, 'gold'); land_temple(c)
def land_river(c):
    mountains(c, 420, 200, rgb('8a9ab0'), 31)
    shape(c, [(-300, 640), (-300, 480), (300, 440), (800, 500), (1300, 450), (1800, 480), (2220, 470), (2220, 640)], rgb('8aa070'), 3, t=0)
    r = np.random.default_rng(8)
    for i in range(14): house(c, 1100 + i * 60 + r.uniform(-20, 20), 470 + r.uniform(-10, 30), r.uniform(0.35, 0.5), roof=[G['terra'], G['red']][i % 2])
    mini_temple(c, 1500, 440, 0.4)
    for i in range(18): olive_tree(c, r.uniform(-50, 1000), r.uniform(490, 560), r.uniform(0.3, 0.5))
    shape(c, [(-300, 700), (-300, 580), (2220, 560), (2220, 700)], rgb('6f8a56'), 3, t=0)
    shape(c, [(-300, 640), (2220, 610), (2220, 690), (-300, 720)], rgb('4a7aa0'), 3, t=0)
    for k in range(5): wave_band(c, -300 + k * 60, SW + 300, 624 + k * 16, 14, rgb('8ab8d8'))
    rect(c, -10, 700, SW + 20, BH, rgb('5e7a44')); rect(c, -10, 696, SW + 20, 5, LINE)
    for x in range(-20, SW, 46): line(c, [(x, 700), (x + 6, 640), (x + 12, 600)], rgb('5a7a32'), 3); shape(c, [(x + 8, 606), (x + 16, 590), (x + 14, 620)], rgb('8a6a3a'), 1.4)
    cypress(c, 80, 720, 1.3); cypress(c, 1850, 720, 1.3); olive_tree(c, 260, 720, 1.3); olive_tree(c, 1680, 720, 1.2)
    flowers(c, 13, 720, 1100)
def bg_river(c): sky(c, 'day'); land_river(c)
def bg_river_s(c): sky(c, 'storm'); tinted(c, 'storm', lambda: land_river(c))
def bg_olympus(c):
    sky(c, 'gold', 700)
    for k in range(9): glow(c, 960, 100, 900 - k * 60, (1, 0.95, 0.8), 0.06)
    mountains(c, 520, 300, rgb('c8c0d0'), 41)
    shape(c, [(560, 520), (760, 260), (960, 200), (1160, 260), (1360, 520)], rgb('b8b0c4'), 3, t=0.2)
    shape(c, [(840, 300), (960, 200), (1080, 300), (1020, 290), (960, 320), (900, 290)], rgb('f4f0ea'), 2, t=0)
    rect(c, 700, 230, 520, 18, rgb('f6eedc'))
    for k in range(7): ionic(c, 730 + k * 76, 120, 232, 30, rgb('f6eedc'))
    pediment(c, 690, 1230, 120, 70, rgb('f6eedc'))
    for k in range(3): cloud(c, 300 + k * 660, 600, 2.2, (0.98, 0.96, 0.92), 1.0, True, k)
    for k in range(4): cloud(c, 60 + k * 600, 720, 2.6, (1, 0.98, 0.95), 1.0, True, k + 3)
    rect(c, -10, 740, SW + 20, BH, rgb('fbf6ee'))
def land_cliff(c):
    mountains(c, 500, 220, rgb('7a7a9a'), 51)
    rect(c, -10, 520, SW + 20, 300, rgb('4a6a8a'))
    for k in range(6): wave_band(c, -300, SW + 300, 540 + k * 30, 16, rgb('6a8aaa'))
    shape(c, [(-300, 1200), (-300, 640), (400, 620), (900, 640), (1180, 660), (1230, 760), (1260, 1200)], rgb('8a7a5a'), 3)
    for k in range(8): line(c, [(1180 + k * 6, 660 + k * 60), (1230 - k * 2, 700 + k * 60)], rgb('6a5a3a'), 2)
    rect(c, -300, 640, 1500, 14, rgb('6f8a56'))
    grass_tufts(c, 6, 650, 690, 30)
    olive_tree(c, 200, 650, 1.4); rock(c, 1000, 660, 0.9)
def bg_cliff(c): sky(c, 'dusk'); tinted(c, 'dusk', lambda: land_cliff(c))
def bg_cliff_n(c): sky(c, 'night'); tinted(c, 'night', lambda: land_cliff(c))
def bg_cliff_r(c): sky(c, 'red'); tinted(c, 'red', lambda: land_cliff(c))
def land_valley(c):
    shape(c, [(-300, 900), (-300, -300), (500, -300), (600, 200), (520, 500), (700, 760), (-300, 760)], rgb('7a6a4e'), 3)
    shape(c, [(2220, 900), (2220, -300), (1500, -300), (1400, 200), (1500, 500), (1300, 760), (2220, 760)], rgb('6e5e44'), 3)
    for (x0, x1) in ((-300, 600), (1350, 2220)):
        for k in range(12): line(c, [(x0 + 40, -260 + k * 90), ((x0 + x1) / 2, -250 + k * 90 + 14), (x1 - 40, -260 + k * 90 - 8)], rgb('5a4a34'), 3)
    shape(c, [(560, 200), (620, 300), (600, 420), (680, 520), (760, 600), (840, 700), (900, 760)], rgb('9a8a6a'), 3, closed=False)
    for k in range(10): rect(c, 560 + k * 34, 240 + k * 52, 60, 10, rgb('9a8a6a'))
    rect(c, -10, 760, SW + 20, BH, rgb('4e4232')); rect(c, -10, 756, SW + 20, 5, LINE)
    r = np.random.default_rng(2)
    for i in range(14): rock(c, r.uniform(0, SW), r.uniform(770, 900), r.uniform(0.4, 0.9), r.uniform(-0.4, 0.4))
def bg_valley(c): sky(c, 'storm', 400); tinted(c, 'storm', lambda: land_valley(c))
def bg_valley_n(c): sky(c, 'night', 400); tinted(c, 'night', lambda: land_valley(c))
def land_garden(c):
    mountains(c, 400, 160, rgb('9aa8c0'), 61)
    for k in range(12):
        x = 40 + k * 168; ionic(c, x, 240, 620, 50)
        if k < 11: c.new_path(); c.arc(x + 84, 260, 84, math.pi, 2 * math.pi); c.set_source_rgb(*rgb('ece2ca')); c.set_line_width(16); c.stroke()
    rect(c, -10, 160, SW + 20, 30, rgb('efe2c4')); meander(c, -10, SW, 164, 22, G['terra'])
    for x in (150, 500, 1420, 1770): cypress(c, x, 660, 1.1)
    rect(c, -10, 620, SW + 20, 100, rgb('8aa070'))
    for k in range(10): circ(c, 100 + k * 200, 640, 50, rgb('5a7a3a')); flowers(c, 70 + k, 610, 650, 10, [G['rose'], G['red'], G['white']], 60 + k * 200, 140 + k * 200)
    shape(c, [(860, 680), (880, 600), (1040, 600), (1060, 680)], rgb('e6dcc4'), 3)
    shape(c, [(780, 700), (1140, 700), (1110, 740), (810, 740)], rgb('e6dcc4'), 3)
    floor_tiles(c, 740, rgb('d8ccb0'), rgb('c4b696'))
def bg_garden(c): sky(c, 'day', 400); land_garden(c)
def land_park(c):
    for i, x in enumerate(range(-40, SW + 60, 90)):
        h = 120 + (i * 37) % 140; rect(c, x, 520 - h, 80, h, [rgb('c8ccd4'), rgb('b4bcc8'), rgb('d8dce0')][i % 3])
        for wy in range(int(520 - h + 14), 510, 26):
            for wx in range(int(x + 10), int(x + 70), 18): rect(c, wx, wy, 8, 12, rgb('8aa0b8'))
    mountains(c, 520, 120, rgb('8aa8a0'), 71, False)
    rect(c, -10, 540, SW + 20, 200, rgb('7aa060'))
    r = np.random.default_rng(5)
    for i in range(16): olive_tree(c, r.uniform(0, SW), 580 + r.uniform(-20, 20), r.uniform(0.6, 0.8))
    for x in (300, 1600): rect(c, x, 650, 160, 10, rgb('6a4a2a')); rect(c, x + 10, 660, 8, 30, rgb('3a3a3a')); rect(c, x + 140, 660, 8, 30, rgb('3a3a3a'))
    rect(c, -10, 690, SW + 20, BH, rgb('6a9050')); rect(c, -10, 686, SW + 20, 5, LINE)
    shape(c, [(700, 1100), (860, 690), (1060, 690), (1220, 1100)], rgb('d8ccb0'), 2, t=0)
    flowers(c, 77, 700, 1100, 120)
def bg_park(c): sky(c, 'noon', 540); land_park(c)
def land_town(c):
    rect(c, -10, 420, SW + 20, 400, rgb('3a7aa8'))
    for k in range(6): wave_band(c, -300, SW + 300, 430 + k * 30, 16, rgb('5a9ac8'))
    shape(c, [(-300, 760), (-300, 520), (300, 470), (800, 520), (1300, 480), (2220, 520), (2220, 760)], rgb('c8b48a'), 3, t=0)
    r = np.random.default_rng(13)
    for i in range(46): house(c, r.uniform(-40, SW + 40), r.uniform(520, 640), r.uniform(0.35, 0.6), roof=[rgb('2a5aa8'), G['terra'], rgb('f2eadc')][i % 3])
    shape(c, [(1300, 760), (1340, 640), (1600, 600), (1900, 620), (2220, 640), (2220, 760)], rgb('7a9a5a'), 3, t=0)
    rect(c, -10, 740, SW + 20, BH, rgb('6a8a4a')); rect(c, -10, 736, SW + 20, 5, LINE)
def bg_town(c): sky(c, 'dusk', 440); tinted(c, 'dusk', lambda: land_town(c))

def sky_cycle(c, u):   # u: 0 白天 → 1 夜（动态天空）
    A = [np.array(rgb(h)) for h in PALS['day']]; Bm = [np.array(rgb(h)) for h in PALS['dusk']]; N_ = [np.array(rgb(h)) for h in PALS['night']]
    if u < 0.5: cols = [tuple(a * (1 - u * 2) + b * u * 2) for a, b in zip(A, Bm)]
    else: cols = [tuple(b * (2 - u * 2) + n * (u * 2 - 1)) for b, n in zip(Bm, N_)]
    bands(c, cols, -BO, 620)
LANDC = {}
def land_layer(name, fn):
    if name not in LANDC:
        s, cc = surf(SW, BH); cc.translate(0, BO); fn(cc); s.flush(); LANDC[name] = s
    return LANDC[name]
def pasture_cycle(c, u, t):
    sky_cycle(c, u)
    if u < 0.75: sun_disc(c, lerp(200, 1700, min(1, u / 0.7)), 300 - 260 * math.sin(math.pi * min(1, u / 0.7)), 50, (1, 0.9 - 0.3 * u, 0.6 - 0.3 * u), 1 - seg(u, 0.6, 0.75))
    stars(c, t, 120, 4, -250, 400, seg(u, 0.6, 0.95))
    if u > 0.55: moon(c, lerp(1700, 1200, seg(u, 0.55, 1)), lerp(380, 0, seg(u, 0.55, 1)), 40, seg(u, 0.55, 0.8))
    c.set_source_surface(land_layer('pd', land_pasture), 0, -BO); c.paint()
    nt = seg(u, 0.3, 1.0)
    c.save(); c.set_source_surface(land_layer('pd', land_pasture), 0, -BO); c.paint()   # (保持层次)
    c.restore()
    if nt > 0:
        c.set_source_rgba(0.04, 0.07, 0.2, 0.6 * nt); c.mask_surface(land_layer('pd', land_pasture), 0, -BO)
    if 0.2 < u < 0.7: c.set_source_rgba(0.55, 0.22, 0.2, 0.3 * math.sin(math.pi * (u - 0.2) / 0.5)); c.mask_surface(land_layer('pd', land_pasture), 0, -BO)

def pasture(c, pal, t, clouds=True, bird=True):
    paintbg(c, 'past_' + pal, make_pasture(pal))
    if pal == 'day':
        sun_disc(c, 1700, 120, 44); 
        if clouds: drift_clouds(c, t, 5, -180, 160, seed=7)
        if bird: birds(c, t, 6, 80)
    elif pal == 'night':
        stars(c, t, 140, 4, -250, 380, 1.0); moon(c, 1650, 60, 42); fireflies(c, t, 28)
    elif pal == 'dusk':
        sun_disc(c, 1500, 470, 60, (1, 0.6, 0.35)); drift_clouds(c, t, 4, -180, 120, (0.9, 0.6, 0.6), 0.6, 8)

# ---------- 镜头 ----------
def s_hook(c, lt, d, k, loop=False):
    paintbg(c, 'cliff_n', bg_cliff_n); stars(c, lt, 140, 4, -250, 400); moon(c, 1600, 20, 50)
    drift_clouds(c, lt, 3, -200, 80, (0.4, 0.45, 0.6), 0.5, 3)
    o = argus(c, 820, 940, P_(nsh=0.4, nel=0.5, fsh=0.3, fel=0.6, head=0.05), dict(eye=1, mouth='tight', brow=-0.6, look=0.0), closed=0, look=(math.sin(lt * 2), 0.3 * math.cos(lt * 3)), glowa=0.6, y=GY + 120, t=lt, prop_n=club)
    sh = sil(c, lambda: fig(c, 1360, GY + 60, 560, P_(nsh=2.8, nel=0.3, fsh=0.6, fel=0.8, head=-0.1), dict(eye=1), flip=True, prop_n=harpe, **HERM), INK, 0.95)
    if 2.2 < lt < 2.6: cross_star(c, sh['hand_n'][0] - 60, sh['hand_n'][1] - 200, 80, 1.0)
    vignette(c, 0.5)
    return [] if loop else [tag("阿耳戈斯", o['head'], 'L')]
def s_loop(c, lt, d, k): return s_hook(c, lt, d, k, True)
def s_title(c, lt, d, k):
    rect(c, -10, -300, SW + 20, 1500, rgb('0a1020')); stars(c, lt, 140, 4, -250, 700)
    peacock(c, 1100, GY + 40, 1.4, lt, 1.0, 1.0, 0.5 + 0.3 * math.sin(lt * 2))
    vignette(c, 0.4)
    return [('title', seg(lt, 0.2, 0.9))]
GUARDS = make_crowd(601, 12, 120, 1800, [700, 690, 680], [420, 380, 340], kinds=('gm',))
GUARDS = [p for p in GUARDS if not (700 < p['x'] < 1220)]
PRIEST = make_crowd(602, 8, 300, 1600, [620], [300], kinds=('gf', 'nymph'))
PRIEST = [p for p in PRIEST if not (760 < p['x'] < 1160)]
def s_temple(c, lt, d, k):
    paintbg(c, 'temple', bg_temple)
    drift_clouds(c, lt, 3, -200, 40, (1, 0.97, 0.9), 0.7, 11); birds(c, lt, 5, 20)
    for x in (480, 1440): brazier(c, x, 420, lt, False, 0.9)
    draw_crowd(c, PRIEST, lt, mood_fn=lambda p: 'sway')
    oh = hera(c, 960, 360, P_(nsh=0.4, nel=0.6), dict(eye=blink(lt, 3), mouth='smile', look=0.0), y=600)
    o = argus(c, 960, 780, P_(nsh=0.2, nel=0.3, fsh=0.15, fel=0.4, head=0.0), dict(eye=1, mouth='tight', brow=-0.4, look=0.0), closed=0, look=(math.sin(lt * 1.5), 0.2), y=GY + 40, t=lt, prop_f=spear)
    for p in GUARDS:
        og = fig(c, p['x'], p['y'] + 60, p['h'], P_(nsh=0.1, nel=0.1, head=0.02 * math.sin(lt + p['ph'])), dict(eye=blink(lt, int(p['ph'] * 9))), kind='gm', long=False, flip=p['x'] > 960,
                 dress=G['red'], dress2=G['red2'], trim=G['black'], skin=p['skin'][0], skin2=p['skin'][1], beard=p['beard'], prop_n=spear)
        helmet(c, og)
    motes(c, lt, 0, 0, SW, 700, 30, (1, 0.85, 0.45), 3, 0.5, 30)
    vignette(c, 0.25)
    return [tag("阿耳戈斯", o['head'], 'L'), tag("赫拉", oh['head'], 'R')]
def s_eyes(c, lt, d, k):
    paintbg(c, 'temple', bg_temple)
    for x in (480, 1440): brazier(c, x, 420, lt, False, 0.9)
    cl = 100 * (1 - seg(lt, 0.3, 3.4))
    o = argus(c, 960, 1100, P_(nsh=0.6, nel=0.4, fsh=0.5, fel=0.5, head=0.0), dict(eye=1, mouth='tight', look=0.0), closed=cl, look=(math.sin(lt * 2.5), 0.3 * math.sin(lt * 3)), glowa=0.3 * seg(lt, 3.0, 4.0), y=GY + 300, t=lt)
    if 0.3 < lt < 3.6: sparks(c, 960, 300, (lt * 3) % 0.9, 10, seed=int(lt * 3))
    vignette(c, 0.35)
    return [num(str(int(100 - cl)), 1500, 160, 120, seg(lt, 0.3, 0.6), (120, 220, 200)), note("阿耳戈斯·潘诺普忒斯\n“全视者”，赫拉的守卫", 'TR', 0.8)]
def s_sleep(c, lt, d, k):
    pasture(c, 'night', lt)
    cow(c, 1500, GY + 10, 1.0, lt, True)
    rock(c, 860, GY - 20, 1.8)
    sc = k == 1
    o = argus(c, 900, 700, dict(P_(nhip=1.45, nkn=-1.45, fhip=1.35, fkn=-1.4, bob=154, nsh=0.4, nel=1.2, fsh=0.3, fel=1.0, head=0.25 + 0.03 * math.sin(lt))),
              dict(eye=0.0, mouth='n', look=0.0), closed=2, look=((math.sin(lt * 1.3 + 1) if sc else 0.4 * math.sin(lt)), 0.2 * math.sin(lt * 2)), glowa=0.5, legs=False, t=lt, prop_n=club)
    zzz(c, o['head'][0] + 40, o['head'][1] - 20, lt)
    marks = []
    if k == 0: marks.append(num("2", 600, 150, 110, seg(lt, 1.2, 1.6), (240, 214, 140)))
    else:
        marks.append(num("98", 1400, 150, 110, seg(lt, 0.4, 0.8), (120, 220, 200)))
        ow = (lt * 260) % 2400 - 200; owl(c, ow, 200 + 30 * math.sin(lt * 2), 0.8, math.sin(lt * 10), 1.0)
        for ex, ey in ((o['head'][0] + 20, o['head'][1] + 120), (o['head'][0], o['head'][1] + 250)):
            c.new_path(); c.move_to(ex, ey); c.line_to(ow - 40, 180); c.line_to(ow + 40, 230); c.close_path(); c.set_source_rgba(0.5, 1, 0.85, 0.08); c.fill()
    vignette(c, 0.45)
    return marks
MAIDS = make_crowd(611, 9, 80, 1840, [690, 680], [380, 330], kinds=('nymph', 'gf'))
MAIDS = [p for p in MAIDS if not (600 < p['x'] < 1400)]
def s_river(c, lt, d, k):
    paintbg(c, 'river', bg_river); drift_clouds(c, lt, 5, -180, 140, seed=13); birds(c, lt, 7, 40)
    for i, p in enumerate(MAIDS):
        fig(c, p['x'], p['y'], p['h'], P_(nsh=2.6, nel=0.6, fsh=2.5, fel=0.7, head=0.03 * math.sin(lt + i)), dict(eye=blink(lt, i), mouth='smile', look=0.2), kind=p['kind'], flip=p['flip'],
            dress=p['dress'][0], dress2=p['dress'][1], skin=p['skin'][0], skin2=p['skin'][1], hair_c=p['hair'][0], hair_c2=p['hair'][1], himation=None)
        egy.jar(c, p['x'] + (-1 if p['flip'] else 1) * 6, p['y'] - p['h'] * 1.08, 0.8 * p['h'] / 380)
    oi = io(c, 820, 560, P_(nsh=0.5, nel=1.8, fsh=0.3, fel=0.4, head=0.1), dict(eye=blink(lt, 2), mouth='smile', look=0.0, happy=True), hair_sway=math.sin(lt * 2) * 0.5)
    zx = lerp(1500, 1180, seg(lt, 0, 2.5))
    oz = zeus(c, zx, 640, walk(lt * 3, 0.25, 0.1) if lt < 2.5 else P_(nsh=1.2, nel=0.4, head=-0.05), dict(eye=1, mouth='grin', happy=True, look=0.0), flip=True)
    for j in range(4): heart(c, (oi['head'][0] + oz['head'][0]) / 2 + 30 * math.sin(lt * 2 + j), oi['head'][1] - 40 - ((lt * 50 + j * 40) % 160), 1.4, G['rose'], 0.8 * seg(lt, 2.4, 3.0) * (1 - ((lt * 50 + j * 40) % 160) / 160))
    petals(c, lt, 0.5)
    vignette(c, 0.2)
    return [tag("宙斯", oz['head'], 'R'), tag("伊俄", oi['head'], 'L')] if lt > 1.0 else []
def peacock_chariot(c, x, y, s, t, hera_face=None, hera_pose=None):
    for j, dx in enumerate((520, 380)):
        peacock(c, x + dx * s, y - 120 * s + 14 * math.sin(t * 3 + j), 0.6 * s, t, 0.05, 0.0, 0.0, False, t * 8 + j, walk_=0.0)
        line(c, [(x + 120 * s, y - 120 * s), (x + (dx - 20) * s, y - 200 * s)], G['gold'], 3)
    for k_ in range(5): cloud(c, x - 120 * s + k_ * 90 * s, y + 40 * s, 1.1 * s, (0.98, 0.96, 0.92), 1, True, k_)
    oh = hera(c, x, 640 * s, hera_pose or P_(nsh=1.6, nel=0.2, fsh=0.4, fel=0.6), hera_face or dict(eye=1, mouth='smile', look=0.0), y=y + 120 * s)
    car = [(x - 140 * s, y - 120 * s), (x + 130 * s, y - 120 * s), (x + 150 * s, y - 40 * s), (x + 100 * s, y + 20 * s), (x - 130 * s, y + 20 * s)]
    shape(c, car, G['gold'], 3); meander(c, x - 120 * s, x + 110 * s, y - 100 * s, 22 * s, G['gold2'])
    wx, wy, wr = x - 20 * s, y + 20 * s, 70 * s
    circ(c, wx, wy, wr, G['bronze']); ring_stroke(c, wx, wy, wr, LINE, 3)
    for q in range(8): a = q / 8 * math.pi * 2 + t * 4; line(c, [(wx, wy), (wx + wr * math.cos(a), wy + wr * math.sin(a))], G['gold2'], 4)
    circ(c, wx, wy, 14 * s, G['gold'])
    return oh
def s_panic(c, lt, d, k):
    paintbg(c, 'river_s', bg_river_s)
    drift_clouds(c, lt * 3, 7, -220, 160, (0.35, 0.36, 0.42), 0.9, 21, spd=20)
    if int(lt * 2.5) % 4 == 0: lightning(c, 400 + 300 * (int(lt) % 3), -260, 300, int(lt * 7))
    px = lerp(-600, 300, seg(lt, 0, d)); peacock_chariot(c, px, 0, 0.45, lt)
    oi = io(c, 820, 560, P_(nsh=0.6, nel=2.2, fsh=0.5, fel=2.2, head=-0.1), dict(eye=1, mouth='O', look=0.0, brow=0.7))
    oz = zeus(c, 1180, 640, P_(nsh=2.4 + 0.3 * math.sin(lt * 8), nel=0.3, fsh=0.4, fel=0.8, head=-0.15), dict(eye=1, mouth='O', brow=0.7, sweat=1, sweat_ph=lt, look=0.0), flip=True)
    hx, hy = oz['hand_n']; swirl_fx(c, hx, hy, lt, seg(lt, 2.4, 3.6), 120)
    rain(c, lt, 0.4, 60)
    vignette(c, 0.45)
    return [('shake', 0.15 if int(lt * 2.5) % 4 == 0 else 0)]
def s_transform(c, lt, d, k):
    paintbg(c, 'river_s', bg_river_s)
    drift_clouds(c, lt * 3, 7, -220, 160, (0.35, 0.36, 0.42), 0.9, 21, spd=20)
    oz = zeus(c, 1240, 640, P_(nsh=1.6, nel=0.1, fsh=0.4, fel=0.8, head=-0.05), dict(eye=1, mouth='tight', brow=0.4, look=0.0), flip=True)
    u = seg(lt, 1.0, 2.2)
    if u < 1: c.push_group(); io(c, 820, 560, P_(nsh=0.6, nel=2.2, fsh=0.5, fel=2.2, head=-0.1), dict(eye=1, mouth='O', look=0.0)); c.pop_group_to_source(); c.paint_with_alpha(1 - u)
    if u > 0: c.push_group(); cow(c, 820, GY, 1.3, lt, False); c.pop_group_to_source(); c.paint_with_alpha(u)
    hx, hy = oz['hand_n']
    for j in range(16):
        ph = (lt * 0.9 + j / 16) % 1; px = lerp(hx, 820, ph); py = lerp(hy, 500, ph) - 80 * math.sin(math.pi * ph)
        circ(c, px, py, 6, (1, 0.9, 0.5), seg(lt, 0.2, 0.6) * (1 - seg(lt, 2.2, 2.8))); glow(c, px, py, 22, (1, 0.85, 0.4), 0.3)
    swirl_fx(c, 820, 520, lt, seg(lt, 0.4, 1.0) * (1 - seg(lt, 2.0, 3.0)), 300)
    fl = math.exp(-((lt - 1.6) / 0.25) ** 2); rect(c, -10, -300, SW + 20, 1500, (1, 1, 0.95), 0.9 * fl)
    petals(c, lt - 1.6, seg(lt, 1.6, 2.0), 500, 1200, 6, 50, [G['white'], G['rose']]) if lt > 1.6 else None
    vignette(c, 0.4)
    return [tag("伊俄", (820, 500), 'L')] if lt > 2.6 else []
def s_hera_arrive(c, lt, d, k):
    paintbg(c, 'river', bg_river); drift_clouds(c, lt, 5, -180, 140, seed=13)
    for j in range(5): light_beams(c, 600, -260, 0.7, 7, 1400, 0.8, math.pi * 0.5)
    if k == 0:
        u = seg(lt, 0, 2.6); oh = peacock_chariot(c, 520, lerp(-200, 520, u), 0.9, lt, dict(eye=1, mouth='smile', look=0.0), P_(nsh=1.5 * seg(lt, 2.4, 3.2) + 0.3, nel=0.1, fsh=0.4, fel=0.6))
        petals(c, lt, 0.6, 200, 900, 8, 30, [G['white'], G['saff']])
    else:
        oh = peacock_chariot(c, 520, 520, 0.9, lt, dict(eye=1, mouth='open' if int(lt * 4) % 2 else 'smile', look=0.0), P_(nsh=1.5, nel=0.1, fsh=0.4, fel=0.6))
    cow(c, 1180, GY, 1.1, lt, True)
    oz = zeus(c, 1560, 660, P_(nsh=0.5, nel=2.2, fsh=0.4, fel=0.6, head=0.1), dict(eye=1, mouth='tight', brow=0.6, sweat=1, sweat_ph=lt, look=0.0), flip=True)
    vignette(c, 0.25)
    return [tag("赫拉", oh['head'], 'L')] if k == 0 and lt > 2.4 else []
def s_zeus_nod(c, lt, d, k):
    paintbg(c, 'river', bg_river)
    oh = hera(c, 600, 700, P_(nsh=0.8, nel=1.2, fsh=0.4, fel=0.6, head=0.05), dict(eye=1, mouth='smile', look=0.0))
    cow(c, 1000, GY, 1.0, lt, True)
    nod = 0.12 * max(0, math.sin(lt * 4)) * seg(lt, 1.5, 2.0)
    oz = zeus(c, 1400, 900, P_(nsh=0.3, nel=1.8, fsh=0.4, fel=0.6, head=0.1 + nod), dict(eye=1, mouth='tight', brow=0.8, sweat=1, sweat_ph=lt * 1.5, look=0.0), flip=True, y=GY + 120)
    for j in range(3): circ(c, oz['face'][0] + 30 - j * 14, oz['face'][1] - 60 + ((lt * 80 + j * 30) % 120), 7, P['tear'], 0.8)
    vignette(c, 0.3)
    return []
def s_handover(c, lt, d, k):
    paintbg(c, 'past_day', make_pasture('day')); sun_disc(c, 1700, 120, 44); drift_clouds(c, lt, 5, -180, 160, seed=7); birds(c, lt, 5, 80)
    for j, x in enumerate((140, 320, 1800)): peacock(c, x, GY + 20, 0.55, lt, 0.6 + 0.3 * math.sin(lt + j), 0, 0, x > 960, walk_=0.3)
    oh = hera(c, 620, 700, P_(nsh=1.5 if k == 1 else 0.9, nel=0.1 if k == 1 else 0.5, fsh=0.4, fel=0.6, head=0.0), dict(eye=1, mouth=('open' if int(lt * 5) % 2 else 'tight') if k == 1 else 'smile', brow=-0.4 * (k == 1), look=0.0))
    cow(c, 940, GY, 1.0, lt, False)
    o = argus(c, 1320, 820, dict(P_(nsh=1.2, nel=0.6, fsh=0.4, fel=0.4, head=0.15, body=-0.2, nhip=0.25, nkn=-1.85, fhip=0.15, fkn=-1.75, bob=135), kneel=True) if k == 0 else P_(nsh=0.3, nel=0.4, head=0.0),
              dict(eye=1, mouth='tight', look=0.0), closed=0, look=(-1 if k == 1 else -0.6, 0.2), glowa=0.4 * (k == 1), flip=True, legs=k == 1, t=lt, prop_f=club)
    hx, hy = oh['hand_n']
    if k == 0: line(c, [(hx, hy), ((hx + 940) / 2, hy + 80), (1080, GY - 150)], rgb('b49a6a'), 5)
    if k == 1:
        fl = math.exp(-((lt - 1.6) / 0.2) ** 2); glow(c, o['head'][0], o['head'][1] + 300, 500, (0.5, 1, 0.85), 0.6 * fl)
    vignette(c, 0.25)
    return [('shake', 0.1 * math.exp(-((lt - 1.6) / 0.2) ** 2))] if k == 1 else []
def s_watch(c, lt, d, k):
    cyc = (lt / d) * 2.0; u = (cyc % 1.0)
    pasture_cycle(c, 0.98 * (u if int(cyc) % 2 == 0 else 1 - u), lt)
    cow(c, 1300, GY + 10, 1.0, lt, True)
    line(c, [(1460, 560), (1420, 620), (1360, 640)], rgb('b49a6a'), 5)
    ph = lt * 1.6
    def opfn(i): return float(np.clip(0.5 + 1.5 * math.sin(ph + (i % 2) * math.pi), 0, 1))
    o = argus(c, 820, 760, P_(nsh=0.2, nel=0.3, head=0.03 * math.sin(lt)), dict(eye=1, mouth='tight', look=0.0), look=(1, 0.3), glowa=0.4, t=lt, prop_n=club, opfn=opfn)
    night = int(cyc) % 2 == 0 and u > 0.6 or int(cyc) % 2 == 1 and u < 0.4
    vignette(c, 0.3)
    return [num("夜" if night else "日", 1700, 140, 90, 0.8, (240, 214, 140))]
def emblem(c, s):
    c.save(); c.scale(s, s)
    for r_, col in ((60, rgb('c8a43a')), (44, rgb('2f8a6a')), (30, rgb('2a5a9a')), (14, rgb('101828'))): circ(c, 0, 0, r_, col)
    ring_stroke(c, 0, 0, 60, LINE, 3); circ(c, -5, -6, 5, (1, 1, 1))
    c.restore()
def s_graze(c, lt, d, k):
    pasture(c, 'day', lt)
    shape(c, [(1000, 800), (1100, 760), (1400, 770), (1700, 750), (2000, 770), (2000, 830), (1000, 830)], rgb('4a7aa0'), 2.4)
    for q in range(3): wave_band(c, 1100, 1900, 770 + q * 14, 12, rgb('8ab8d8'))
    gz = 0.5 + 0.5 * math.sin(lt * 1.5)
    cow(c, 1360, GY + 20, 1.0, lt, False, gz)
    o = argus(c, 700, 720, dict(P_(nsh=1.0, nel=0.8, fsh=0.6, fel=0.8, head=0.2, body=-0.3, nhip=0.25, nkn=-1.85, fhip=0.15, fkn=-1.75, bob=135), kneel=True),
              dict(eye=1, mouth='tight', look=0.0), closed=0, look=(1, 0.6), glowa=0.3, legs=False, t=lt, prop_n=club)
    for j in range(12):
        ex, ey = 700 + (j % 4) * 20, o['head'][1] + 120 + (j // 4) * 120
        line(c, [(ex, ey), (1380 + 30 * math.sin(j), GY - 120 + 20 * (j % 3))], (0.5, 1, 0.85), 1.2)
    vignette(c, 0.25)
    return []
def s_olympus(c, lt, d, k):
    paintbg(c, 'olympus', bg_olympus); drift_clouds(c, lt, 6, 500, 720, (1, 0.98, 0.95), 1.0, 31, spd=15, s=1.6)
    light_beams(c, 960, -260, 0.8, 9, 1400, 1.0, math.pi * 0.5)
    if k == 0:
        oz = zeus(c, 760, 640, P_(nsh=0.3, nel=1.8, fsh=0.2, fel=0.4, head=0.25), dict(eye=1, mouth='tight', brow=0.7, look=0.2), y=GY - 40)
        cx, cy = 1300, 560; c.save(); c.new_path(); c.arc(cx, cy, 170, 0, 7); c.clip(); c.translate(cx - 960 * 0.25, cy - 400 * 0.25); c.scale(0.25, 0.25)
        pasture(c, 'day', lt); cow(c, 1300, GY, 1.0, lt, True); argus(c, 820, 760, P_(), dict(eye=1), look=(1, 0.3), t=lt); c.restore()
        ring_stroke(c, cx, cy, 170, (0.95, 0.9, 0.8), 10); ring_stroke(c, cx, cy, 175, LINE, 3)
        return [tag("宙斯", oz['head'], 'L')]
    oz = zeus(c, 600, 640, P_(nsh=1.6, nel=0.1, fsh=0.4, fel=0.6, head=0.0), dict(eye=1, mouth='open', look=0.0), y=GY - 40)
    u = seg(lt, 1.0, d)
    hx = lerp(900, 2300, u); hy = lerp(GY - 40, 300, u) + 60 * math.sin(u * 6)
    for j in range(20): circ(c, hx - j * 40, hy + 10 * math.sin(lt * 4 + j) + j * 4, 6, (1, 0.85, 0.4), 1 - j / 20); glow(c, hx - j * 40, hy + j * 4, 26, (1, 0.85, 0.4), 0.3 * (1 - j / 20))
    oh = fig(c, hx if u > 0 else 900, hy if u > 0 else GY - 40, 520, P_(nsh=2.6, nel=0.2, fsh=-0.6, fel=0.3, nhip=0.6, nkn=-0.8, fhip=-0.4, fkn=-0.6) if u > 0 else P_(nsh=0.5, nel=0.5), dict(eye=1, mouth='grin', look=0.0), prop_f=caduceus, **HERM)
    petasos(c, oh, lt * 14)
    return [tag("赫尔墨斯", oh['head'], 'L')] if lt < 1.4 else []
def s_alarm(c, lt, d, k):
    pasture(c, 'day', lt)
    cow(c, 1640, GY + 10, 0.9, lt, True)
    pk = seg(lt, 0.6, 1.4) * (1 - seg(lt, 3.2, 3.8))
    oh = fig(c, 380, GY + 120 - 120 * pk, 560, P_(nsh=0.6, nel=1.8, head=-0.05), dict(eye=1, mouth='O' if lt > 1.8 else 'grin', look=0.0, brow=0.6 * (lt > 1.8)), **HERM)
    petasos(c, oh, lt * 10)
    rock(c, 380, GY + 20, 2.6)
    snap = seg(lt, 1.6, 1.9)
    o = argus(c, 1100, 780, P_(nsh=lerp(0.2, 2.6, snap), nel=0.3, head=0.0), dict(eye=1, mouth='open' if snap > 0.5 else 'tight', brow=-0.9 * snap, look=0.0), closed=0, look=(lerp(0.6, -1, snap), lerp(0, -0.2, snap)), glowa=0.6 * snap, flip=True, t=lt, prop_n=club)
    alarm_rays(c, o['head'][0], o['head'][1] + 250, lt, snap * (1 - seg(lt, 3.6, 4.4)) * 0.8)
    vignette(c, 0.3 + 0.2 * snap, (0.15, 0.0, 0.0))
    return [num("！", o['head'][0] - 100, o['head'][1] - 80, 160, snap, (210, 60, 40)), ('shake', 0.25 * math.exp(-((lt - 1.8) / 0.25) ** 2))]
SHEEP = [(x, y, s) for (x, y, s) in [(200 + i * 92 + (i * 37) % 50, GY + 10 + (i % 3) * 26, 0.7 + 0.1 * (i % 3)) for i in range(18)]]
def s_disguise(c, lt, d, k):
    pasture(c, 'day', lt)
    rock(c, 380, GY + 20, 2.6)
    u = seg(lt, 1.6, 2.6)
    if u < 1:
        c.push_group(); oh = fig(c, 700, GY, 600, P_(nsh=0.5, nel=2.4, head=0.1), dict(eye=1, mouth='grin', look=0.0, happy=True), prop_f=caduceus, **HERM); petasos(c, oh, lt * 10); c.pop_group_to_source(); c.paint_with_alpha(1 - u)
        idea(c, oh['head'][0] + 60, oh['head'][1] - 60, seg(lt, 0.4, 1.0), lt)
    if u > 0:
        c.push_group(); oh = fig(c, 700, GY, 600, P_(nsh=0.4, nel=2.8, fsh=0.5, fel=2.6, head=0.0), dict(eye=1, mouth='smile', look=0.0), **SHEP); straw_hat(c, oh); syrinx(c, *mouth_pt(oh), 1.0); c.pop_group_to_source(); c.paint_with_alpha(u)
        for j, (x, y, s) in enumerate(SHEEP[:8]): 
            c.push_group(); sheep(c, 900 + j * 110, y, s, lt, j); c.pop_group_to_source(); c.paint_with_alpha(seg(lt, 2.0 + j * 0.1, 2.6 + j * 0.1))
    swirl_fx(c, 700, GY - 300, lt, seg(lt, 1.2, 1.7) * (1 - seg(lt, 2.4, 3.0)), 320)
    fl = math.exp(-((lt - 2.0) / 0.2) ** 2); rect(c, -10, -300, SW + 20, 1500, (1, 1, 0.95), 0.7 * fl)
    vignette(c, 0.25)
    return []
def hill_slope(c):
    pass
def s_walk(c, lt, d, k):
    pasture(c, 'day', lt)
    u = seg(lt, 0, d); x0 = lerp(-200, 700, u)
    for j, (x, y, s) in enumerate(SHEEP):
        sheep(c, x0 - 120 - (j % 6) * 120 - (j // 6) * 50, y, s, lt, j * 1.3, graze=0.0)
    oh = fig(c, x0 + 120, GY, 600, P_(**walk(lt * 2.6, 0.2, 0.1, nsh=0.4, nel=2.8, fsh=0.5, fel=2.6)), dict(eye=1, mouth='smile', look=0.0), **SHEP)
    straw_hat(c, oh); syrinx(c, *mouth_pt(oh), 1.0)
    notes_flow(c, lt, mouth_pt(oh)[0] + 30, mouth_pt(oh)[1], 0.7, 5)
    o = argus(c, 1500, 640, P_(nsh=0.2, nel=0.3, head=0.0), dict(eye=1, mouth='tight', look=0.0), closed=0, look=(-1, 0.2), flip=True, t=lt, prop_n=club)
    cow(c, 1760, GY + 10, 0.8, lt, True)
    vignette(c, 0.2)
    return []
def s_play(c, lt, d, k):
    pasture(c, 'day' if k < 2 else 'dusk', lt)
    seated = k >= 1
    rock(c, 820, GY - 20, 1.6); rock(c, 1160, GY - 20, 1.8)
    for j, (x, y, s) in enumerate(SHEEP[:10]): sheep(c, 120 + j * 64 + (j % 2) * 20, y + 20, s * 0.9, lt, j, lie=1.0 if lt > 1.5 or k else 0.0, graze=0)
    hp = P_(nsh=0.4, nel=2.8, fsh=0.5, fel=2.6, head=0.02 * math.sin(lt * 2))
    if seated: hp.update(nhip=1.45, nkn=-1.45, fhip=1.35, fkn=-1.4, bob=154)
    oh = fig(c, 820 if seated else 700, GY, 560, hp, dict(eye=0.4 if k else 1, mouth='n', look=0.0), **SHEP)
    straw_hat(c, oh); mx, my = mouth_pt(oh); syrinx(c, mx, my, 1.0)
    notes_flow(c, lt, mx + 30, my, 1.0, 8)
    haze(c, lt, mx + 40, my + 40, 0.9, 1)
    sway = 0.06 * math.sin(lt * 1.5)
    ap = P_(nsh=0.3, nel=0.6, fsh=0.2, fel=0.6, head=0.15 + sway, body=sway * 0.5)
    if k == 1 and lt < 1.6: ap = P_(nsh=1.6, nel=0.6 + 0.6 * math.sin(lt * 6), head=0.05)
    if seated: ap.update(nhip=1.45, nkn=-1.45, fhip=1.35, fkn=-1.4, bob=154)
    cl = 0 if k < 2 else 50 * seg(lt, 0.3, 3.6)
    o = argus(c, 1180, 720, ap, dict(eye=1 if cl < 1 else 0, mouth='smile', look=0.0, happy=True), closed=cl, look=(-0.8, 0.3), flip=True, legs=not seated, t=lt, prop_f=club)
    marks = []
    if k == 2:
        marks.append(num(str(int(cl)), 1600, 150, 120, seg(lt, 0.3, 0.6), (200, 180, 255)))
    vignette(c, 0.3)
    return marks
def s_hold(c, lt, d, k):
    pasture(c, 'dusk', lt)
    rock(c, 1160, GY - 20, 1.8)
    nodd = 0.15 * max(0, math.sin(lt * 2.2)) ** 3
    ap = P_(nsh=0.3, nel=0.6, fsh=0.2, fel=0.6, head=0.25 + nodd, nhip=1.45, nkn=-1.45, fhip=1.35, fkn=-1.4, bob=154)
    o = argus(c, 1080, 900, ap, dict(eye=0, mouth='n', look=0.0), closed=50, look=(math.sin(lt * 9) * 0.6, 0.2), legs=False, twitch=0.8, t=lt, flip=True, y=GY + 140)
    haze(c, lt, 300, 500, 0.8, 1)
    notes_flow(c, lt, 200, 520, 0.6, 5)
    vignette(c, 0.35)
    return [num("50", 1600, 150, 120, 0.9, (120, 220, 200))]
def story_bubble(c, x, y, r, t, kind):
    circ(c, x, y, r, rgb('f6ecd0'), 0.92); ring_stroke(c, x, y, r, LINE, 3)
    c.save(); c.new_path(); c.arc(x, y, r - 4, 0, 7); c.clip()
    if kind == 0:   # 绵羊跳栏
        rect(c, x - r, y + r * 0.35, 2 * r, r, rgb('8aa070')); line(c, [(x - 10, y + r * 0.35), (x - 10, y), (x + 10, y), (x + 10, y + r * 0.35)], rgb('6a4a2a'), 4)
        ph = (t * 0.8) % 1; sheep(c, x - r * 0.8 + ph * r * 1.6, y + r * 0.35 - 60 * math.sin(math.pi * ph), 0.5, t)
    elif kind == 1:   # 星星月亮
        rect(c, x - r, y - r, 2 * r, 2 * r, rgb('1a2648')); moon(c, x + 20, y - 10, 26); stars(c, t, 20, 9, int(y - r), int(y + r), 1.0)
    else:   # 古老的王
        rect(c, x - r, y - r, 2 * r, 2 * r, rgb('e8d8b0')); fig(c, x, y + r * 0.8, 200, P_(), dict(eye=blink(t, 1)), kind='gm', long=True, beard=True, crown=True)
    c.restore()
def s_story(c, lt, d, k):
    pasture(c, 'dusk', lt)
    rock(c, 820, GY - 20, 1.6); rock(c, 1160, GY - 20, 1.8)
    hp = P_(nsh=0.9 + 0.2 * math.sin(lt * 1.2), nel=1.0, fsh=0.4, fel=0.6, head=0.0, nhip=1.45, nkn=-1.45, fhip=1.35, fkn=-1.4, bob=154)
    oh = fig(c, 820, GY, 560, hp, dict(eye=1, mouth='open' if int(lt * 2.5) % 2 else 'n', look=0.0), **SHEP)
    straw_hat(c, oh)
    mx, my = mouth_pt(oh)
    for j in range(6):
        ph = (lt * 0.2 + j / 6) % 1; px = mx + 40 + ph * 300; py = my - 20 + 30 * math.sin(ph * 8 + j)
        line(c, [(px, py), (px + 30, py - 10), (px + 60, py)], (0.9, 0.85, 1.0), 3 * math.sin(math.pi * ph) + 0.1)
    haze(c, lt, mx + 40, my + 40, 0.9, 1, (0.55, 0.45, 0.85))
    if k == 1:
        for j in range(3): story_bubble(c, 980 + j * 240, 160 + 40 * math.sin(lt + j), 100, lt, j) if lt > j * 0.8 else None
    ap = P_(nsh=0.3, nel=0.6, fsh=0.2, fel=0.6, head=0.3 + 0.05 * math.sin(lt), nhip=1.45, nkn=-1.45, fhip=1.35, fkn=-1.4, bob=154)
    o = argus(c, 1180, 720, ap, dict(eye=0, mouth='n', look=0.0), closed=50 + 10 * seg(lt, 0, d) + 10 * k, look=(-0.8, 0.3), flip=True, legs=False, t=lt, prop_f=club)
    zzz(c, o['head'][0] - 40, o['head'][1] - 20, lt, 0.6)
    vignette(c, 0.35)
    return []
def s_dusk(c, lt, d, k):
    u = seg(lt, 0, d) * 0.65 + 0.35
    pasture_cycle(c, u, lt)
    rock(c, 820, GY - 20, 1.6); rock(c, 1160, GY - 20, 1.8)
    hp = P_(nsh=0.9, nel=1.0, fsh=0.4, fel=0.6, nhip=1.45, nkn=-1.45, fhip=1.35, fkn=-1.4, bob=154)
    oh = fig(c, 820, GY, 560, hp, dict(eye=1, mouth='open' if int(lt * 2) % 2 else 'n', look=0.0), **SHEP); straw_hat(c, oh)
    sl = seg(lt, 2.4, 4.4)
    ap = P_(nsh=0.3, nel=0.6, fsh=0.2, fel=0.6, head=0.3 + 0.3 * sl, body=-0.1 * sl, nhip=1.45, nkn=-1.45, fhip=1.35, fkn=-1.4, bob=154)
    cl = 70 + 8 * seg(lt, 0, d)
    o = argus(c, 1180, 720, ap, dict(eye=0, mouth='n', look=0.0), closed=cl, look=(-0.8, 0.3), flip=True, legs=False, t=lt, prop_f=club, glowa=0.3 * u)
    zzz(c, o['head'][0] - 40, o['head'][1] - 20, lt)
    vignette(c, 0.4)
    return [num(str(int(cl)), 1600, 150, 120, 0.9, (200, 180, 255))]
def s_count(c, lt, d, k):
    pasture(c, 'night', lt)
    cl = lerp(79, 99, seg(lt, 0.2, d - 0.3))
    ap = P_(nsh=0.3, nel=0.6, fsh=0.2, fel=0.6, head=0.55, body=-0.15, nhip=1.45, nkn=-1.45, fhip=1.35, fkn=-1.4, bob=154)
    o = argus(c, 1000, 1100, ap, dict(eye=0, mouth='n', look=0.0), closed=cl, look=(0, 0.3), flip=True, legs=False, t=lt, glowa=0.6, y=GY + 260)
    vignette(c, 0.5)
    n_ = int(cl)
    lab = "第%d只" % (80 if n_ < 90 else (90 if n_ < 99 else 99))
    return [num(lab, 1550, 150, 90, 0.9, (200, 180, 255))]
def s_last(c, lt, d, k):
    rect(c, -10, -300, SW + 20, 1500, rgb('0a0e1c')); stars(c, lt, 80, 6, -250, 800, 0.5)
    op = 1 - seg(lt, 0.4, 3.4)
    op2 = op + 0.12 * math.sin(lt * 7) * (op > 0.1) * (1 - op)
    eye_g(c, 960, 360, 260, max(0, op2), 0.0, 0.2, 0, 0.5)
    vignette(c, 0.6)
    return [num("最后一只", 960, 40, 60, 0.7, (200, 180, 255))]
def s_silence(c, lt, d, k):
    pasture(c, 'night', lt, False, False)
    rect(c, -10, -300, SW + 20, 1500, (0.02, 0.03, 0.08), 0.45)
    rock(c, 820, GY - 20, 1.6); rock(c, 1160, GY - 20, 1.8)
    ap = P_(nsh=0.3, nel=0.6, fsh=0.2, fel=0.6, head=0.6, body=-0.15, nhip=1.45, nkn=-1.45, fhip=1.35, fkn=-1.4, bob=154)
    o = argus(c, 1180, 720, ap, dict(eye=0, mouth='n'), closed=100, flip=True, legs=False, t=lt)
    ey = 1.0 if lt > 2.2 else 0.3
    hp = P_(nsh=0.4, nel=0.6, fsh=0.4, fel=0.6, head=0.0, nhip=1.45, nkn=-1.45, fhip=1.35, fkn=-1.4, bob=154)
    oh = fig(c, 820, GY, 560, hp, dict(eye=ey, mouth='tight', look=0.0, brow=-0.6 * (lt > 2.2)), **SHEP); straw_hat(c, oh)
    if 2.2 < lt < 2.6: cross_star(c, oh['eye'][0], oh['eye'][1], 40, 1.0)
    vignette(c, 0.55)
    return [num("0", 1600, 150, 120, 0.9, (120, 220, 200))]
def s_slash(c, lt, d, k):
    sw = seg(lt, 1.6, 1.9)
    paintbg(c, 'cliff_r' if lt > 1.9 else 'cliff_n', bg_cliff_r if lt > 1.9 else bg_cliff_n)
    if lt < 1.9: stars(c, lt, 100, 4, -250, 380); moon(c, 1650, 60, 42)
    ap = P_(nsh=0.3, nel=0.6, fsh=0.2, fel=0.6, head=0.6, body=-0.15, nhip=1.45, nkn=-1.45, fhip=1.35, fkn=-1.4, bob=154)
    if lt < 1.9:
        rock(c, 960, 640, 1.8)
        argus(c, 980, 720, ap, dict(eye=0, mouth='n'), closed=100, flip=True, legs=False, t=lt, y=650)
        oh = fig(c, 620, 650, 600, P_(nsh=lerp(0.4, 3.0, seg(lt, 0.4, 1.4)) - 2.4 * sw, nel=0.2, fsh=0.4, fel=0.8, head=-0.1), dict(eye=1, mouth='tight', brow=-0.9, look=0.0), prop_n=harpe, **HERM)
        if 1.0 < lt < 1.4: cross_star(c, oh['hand_n'][0] + 40, oh['hand_n'][1] - 160, 70, 1.0)
        if sw > 0: c.new_path(); c.arc(800, 300, 300, -1.4, -1.4 + 2.6 * sw); c.set_source_rgba(1, 1, 1, 0.9); c.set_line_width(18); c.stroke()
    else:
        rock(c, 960, 640, 1.8)
        tip = seg(lt, 2.4, 4.0)
        c.save(); c.translate(980, 650); c.rotate(0.9 * tip); c.translate(-980, -650)
        sil(c, lambda: argus(c, 980, 720, ap, dict(eye=0, mouth='n'), closed=100, flip=True, legs=False, t=lt, y=650), INK)
        c.restore()
        sil(c, lambda: fig(c, 620, 650, 600, P_(nsh=0.6, nel=0.2, fsh=0.4, fel=0.8, head=0.0), dict(eye=1), prop_n=harpe, **HERM), INK)
        dust(c, 1000, 650, lt - 2.0, 12, 1.4, rgb('8a3020'))
    fl = math.exp(-((lt - 1.9) / 0.15) ** 2); rect(c, -10, -300, SW + 20, 1500, (1, 1, 1), fl)
    vignette(c, 0.5, (0.15, 0.0, 0.0))
    return [('shake', 0.6 * math.exp(-((lt - 1.95) / 0.2) ** 2))]
def s_fall(c, lt, d, k):
    paintbg(c, 'cliff_r', bg_cliff_r)
    u = seg(lt, 0.3, 3.2)
    x = lerp(1100, 1500, u); y = lerp(560, 1300, u ** 1.6)
    c.save(); c.translate(x, y); c.rotate(u * 5); c.translate(-x, -y)
    sil(c, lambda: argus(c, x, 600, P_(nsh=2.0, nel=0.6, fsh=1.4, fel=0.8, nhip=1.0, nkn=-1.0, head=0.4), dict(eye=0), closed=100, legs=False, t=lt, y=y + 300), INK)
    c.restore()
    for j in range(10):
        rr = (lt * 1.3 + j * 0.13) % 1.4; rock(c, 1200 + j * 30, 600 + rr * 500, 0.25 + 0.05 * (j % 3), rr * 4)
    dust(c, 1230, 680, (lt * 0.8) % 1.6, 12, 1.4, rgb('8a6a4a'))
    vignette(c, 0.5, (0.15, 0.0, 0.0))
    return [('shake', 0.2 * seg(lt, 0.3, 0.6) * (1 - seg(lt, 2.6, 3.2)))]
_rd = np.random.default_rng(55); DOTS = [(_rd.uniform(600, 1350), _rd.uniform(600, 820)) for _ in range(100)]
def s_dark(c, lt, d, k):
    paintbg(c, 'valley_n', bg_valley_n); stars(c, lt, 100, 4, -250, 300, 0.7)
    sil(c, lambda: argus(c, 980, 520, P_(nsh=2.6, nel=0.4, fsh=2.2, fel=0.6, nhip=0.9, nkn=-0.9, head=0.6), dict(eye=0), closed=100, legs=False, t=lt, y=1020), (0.06, 0.05, 0.06))
    for i, (x, y) in enumerate(DOTS):
        a = 1 - seg(lt, 0.4 + i * 0.035, 0.7 + i * 0.035)
        if a > 0: glow(c, x, y, 24, (0.5, 1, 0.85), 0.7 * a); circ(c, x, y, 3, (0.7, 1, 0.9), a)
    vignette(c, 0.6)
    return [num(str(max(0, 100 - int(max(0, lt - 0.55) / 0.035))), 1600, 150, 120, 0.9, (120, 220, 200))]
def s_grief(c, lt, d, k):
    if k == 0:
        paintbg(c, 'cliff_n', bg_cliff_n)
        drift_clouds(c, lt * 3, 8, -240, 200, (0.25, 0.26, 0.32), 0.95, 41, spd=25)
        if int(lt * 2) % 3 == 0: lightning(c, 300 + 400 * (int(lt * 2) % 4), -260, 500, int(lt * 9))
        oh = hera(c, 860, 720, P_(nsh=0.4, nel=2.4, fsh=0.6, fel=2.2, head=0.25), dict(eye=1, mouth='open', brow=1.0, tear=1, tear_ph=lt * 0.8, look=0.0), y=650, hair_sway=math.sin(lt * 4))
        for j, x in enumerate((560, 1120)): peacock(c, x, 660, 0.5, lt, 0.1, 0, 0, x > 860)
        rain(c, lt, 1.0, 200)
        vignette(c, 0.5)
        return [('shake', 0.15 if int(lt * 2) % 3 == 0 else 0)]
    paintbg(c, 'valley', bg_valley); drift_clouds(c, lt * 2, 6, -240, 100, (0.3, 0.3, 0.36), 0.9, 42, spd=20)
    sil(c, lambda: argus(c, 1100, 520, P_(nsh=2.6, nel=0.4, fsh=2.2, fel=0.6, nhip=0.9, nkn=-0.9, head=0.6), dict(eye=0), closed=100, legs=False, t=lt, y=1020), (0.12, 0.1, 0.1))
    oh = hera(c, 760, 640, dict(P_(nsh=1.2, nel=1.6, fsh=0.6, fel=0.6, head=0.3, body=-0.2, nhip=0.25, nkn=-1.85, fhip=0.15, fkn=-1.75, bob=135), kneel=True), dict(eye=1, mouth='tight', brow=0.9, tear=1, tear_ph=lt * 0.8, look=0.0))
    rain(c, lt, 0.7, 140)
    vignette(c, 0.45)
    return []
def s_descend(c, lt, d, k):
    paintbg(c, 'valley', bg_valley); drift_clouds(c, lt * 2, 6, -240, 100, (0.3, 0.3, 0.36), 0.9, 42, spd=20)
    sil(c, lambda: argus(c, 1100, 520, P_(nsh=2.6, nel=0.4, fsh=2.2, fel=0.6, nhip=0.9, nkn=-0.9, head=0.6), dict(eye=0), closed=100, legs=False, t=lt, y=1020), (0.12, 0.1, 0.1))
    u = seg(lt, 0, d)
    hx = lerp(600, 880, u); hy = lerp(300, 760, u)
    glow(c, hx, hy - 200, 300, (1, 0.9, 0.6), 0.4)
    oh = hera(c, hx, 420, walk(lt * 3, 0.24, 0.1), dict(eye=1, mouth='tight', brow=0.5, look=0.0), y=hy)
    for i, (x, y) in enumerate(DOTS[::3]): glow(c, x + 120, y + 60, 16, (0.5, 1, 0.85), 0.3 * u * (0.5 + 0.5 * math.sin(lt * 3 + i)))
    vignette(c, 0.45)
    return []
def s_pluck(c, lt, d, k):
    paintbg(c, 'valley', bg_valley)
    rect(c, -10, -300, SW + 20, 1500, (0.05, 0.05, 0.1), 0.3)
    sil(c, lambda: argus(c, 1150, 520, P_(nsh=2.6, nel=0.4, fsh=2.2, fel=0.6, nhip=0.9, nkn=-0.9, head=0.6), dict(eye=0), closed=100, legs=False, t=lt, y=1020), (0.12, 0.1, 0.1))
    oh = hera(c, 760, 700, P_(nsh=1.2, nel=0.8, fsh=1.0, fel=0.9, head=-0.1), dict(eye=1, mouth='tight', brow=0.6, look=0.0))
    hx, hy = oh['hand_n']; cx, cy = hx + 30, hy - 60
    n = int(100 * seg(lt, 0.2, d - 0.3)) if k == 1 else int(30 * seg(lt, 0.5, d))
    for i in range(n):
        x0, y0 = DOTS[i][0] + 170, DOTS[i][1] + 60
        age = lt * 8 - i * 0.4 if k == 1 else lt * 3 - i * 0.12
        ph = min(1, max(0, (lt - (i * (d - 0.5) / 100 if k == 1 else 0.5 + i * 0.12)) / 0.8))
        ang = i * 2.4 + lt * 1.5; rr = 40 + 50 * ((i * 7) % 10) / 10
        tx, ty = cx + rr * math.cos(ang), cy + rr * 0.6 * math.sin(ang)
        x = lerp(x0, tx, ph); y = lerp(y0, ty, ph) - 120 * math.sin(math.pi * ph)
        orb(c, x, y, 10, 0.9)
    glow(c, cx, cy, 200, (0.5, 1, 0.85), 0.3 + 0.3 * seg(lt, 0, d))
    vignette(c, 0.45)
    return [num(str(n if k == 1 else n), 1600, 150, 110, 0.9, (120, 220, 200))]
def s_garden(c, lt, d, k):
    paintbg(c, 'garden', bg_garden); drift_clouds(c, lt, 4, -200, 60, seed=51); birds(c, lt, 4, 40)
    for j in range(3): fx = 960; c.new_path(); c.move_to(fx, 600); c.curve_to(fx - 60 - j * 30, 480, fx - 120 - j * 40, 520, fx - 140 - j * 40, 690); c.set_source_rgba(0.7, 0.85, 1.0, 0.7); c.set_line_width(4); c.stroke(); c.new_path(); c.move_to(fx, 600); c.curve_to(fx + 60 + j * 30, 480, fx + 120 + j * 40, 520, fx + 140 + j * 40, 690); c.stroke()
    if k == 0:
        pc = peacock(c, 1400, GY + 20, 1.2, lt, 0.15, 0.0, 0.0, True, walk_=0.2)
        oh = hera(c, 520, 700, P_(nsh=1.6, nel=0.2, fsh=0.4, fel=0.6), dict(eye=1, mouth='tight', look=0.0))
        hx, hy = oh['hand_n']
        for i in range(30):
            ph = ((lt * 0.4 + i / 30) % 1.0) * seg(lt, 0.6, 1.4)
            x = lerp(hx + 40, 1560, ph); y = lerp(hy - 40, 480, ph) - 260 * math.sin(math.pi * ph)
            if ph > 0.02: orb(c, x, y, 9, 0.9 * math.sin(math.pi * min(ph * 1.05, 1)))
        return [tag("孔雀", (1440, 420), 'R')] if lt > 1.5 else []
    f = seg(lt, 0.6, 2.6)
    oh = hera(c, 520, 700, P_(nsh=0.6, nel=0.8, fsh=0.4, fel=0.6), dict(eye=1, mouth='smile', look=0.0))
    peacock(c, 1300, GY + 20, 1.3, lt, lerp(0.15, 1.0, f), f, 0.8 * seg(lt, 1.2, 2.0) + 0.2, True)
    sparks(c, 1200, 300, (lt - 2.2) if lt > 2.2 else -1, 30, seed=3, spd=2.0, life=1.2)
    light_beams(c, 1250, 360, seg(lt, 2.0, 3.0), 12, 1400, 2 * math.pi, 0.0)
    fl = math.exp(-((lt - 2.4) / 0.25) ** 2); rect(c, -10, -300, SW + 20, 1500, (0.8, 1, 0.95), 0.5 * fl)
    vignette(c, 0.25)
    return []
TOUR = make_crowd(701, 14, 40, 1880, [700, 690], [380, 340], kinds=('gm', 'gf'))
TOUR = [p for p in TOUR if not (620 < p['x'] < 1300)]
def s_today(c, lt, d, k):
    paintbg(c, 'park', bg_park); drift_clouds(c, lt, 5, -200, 100, seed=61); birds(c, lt, 6, 30)
    sun_disc(c, 1700, 60, 50)
    f = seg(lt, 0.8, 3.2)
    peacock(c, 980, GY + 30, 1.2, lt, f, f, 0.3 * f, False)
    for i, p in enumerate(TOUR):
        cols = [rgb('e04a3a'), rgb('3a7ad0'), rgb('f2c040'), rgb('3aa070'), rgb('ffffff'), rgb('d070a0')]
        oo = fig(c, p['x'], p['y'], p['h'], P_(nsh=2.2 if i % 2 else 0.3, nel=0.9 if i % 2 else 0.2, head=-0.05), dict(eye=1, mouth='O' if f > 0.5 else 'smile', look=0.2, happy=True), kind=p['kind'], long=False,
                 flip=p['x'] > 960, dress=cols[i % 6], dress2=tuple(v * 0.85 for v in cols[i % 6]), trim=cols[(i + 2) % 6], hem=False, sleeve=False, skin=p['skin'][0], skin2=p['skin'][1], hair_c=p['hair'][0], hair_c2=p['hair'][1], prop_n=phone if i % 2 else None)
        if i % 2 and int(lt * 3 + i) % 5 == 0: cross_star(c, oo['hand_n'][0], oo['hand_n'][1] - 50, 40, 1.0)
    vignette(c, 0.15)
    return []
def s_spots(c, lt, d, k):
    paintbg(c, 'park', bg_park)
    rect(c, -10, -300, SW + 20, 1500, (0.05, 0.12, 0.1), 0.25)
    if k == 0:
        op = seg(lt, 1.6, 2.4)
        peacock(c, 900, GY + 820, 3.2, lt * 0.3, 1.0, 1.0, 0.4 + 0.4 * op, False, eye_lids=op)
        for j in range(20): cross_star(c, (j * 397) % SW, (j * 211) % 600, 26, 0.5 + 0.5 * math.sin(lt * 4 + j))
        return []
    u = seg(lt, 0.4, 2.0)
    c.save(); s_ = lerp(1, 3, u); c.translate(960, 380); c.scale(s_, s_); c.translate(-960, -380)
    peacock(c, 900, GY + 820, 3.2, lt * 0.3, 1.0, 1.0, 0.5, False)
    c.restore()
    a = seg(lt, 1.6, 2.6)
    if a > 0:
        rect(c, -10, -300, SW + 20, 1500, (0.02, 0.06, 0.06), 0.5 * a)
        eye_g(c, 960, 380, 220 * a, 1.0 * (0.9 + 0.1 * math.sin(lt * 3)), math.sin(lt), 0.2, 0, 0.6 * a)
        ghost(c, lambda: argus(c, 960, 1000, P_(nsh=0.3, nel=0.4), dict(eye=1, look=0.0), closed=0, look=(0, 0.3), t=lt, y=GY + 100), 0.3 * seg(lt, 2.6, 3.6), (0.6, 1.0, 0.9), 0.6)
    return []
def s_world(c, lt, d, k):
    paintbg(c, 'town', bg_town); sun_disc(c, 1500, 440, 60, (1, 0.6, 0.35)); drift_clouds(c, lt, 4, -200, 120, (0.9, 0.6, 0.6), 0.6, 8); birds(c, lt, 5, 200)
    ghost(c, lambda: argus(c, 960, 1300, P_(nsh=0.4, nel=0.6, fsh=0.3, fel=0.6), dict(eye=1, look=0.0, mouth='n'), closed=0, look=(math.sin(lt * 0.7), 0.6), glowa=0.4, t=lt, y=GY + 500), 0.35, (0.75, 0.95, 1.0), 0.55)
    peacock(c, 1500, GY + 10, 1.0, lt, 1.0, 1.0, 0.5, True)
    vignette(c, 0.35)
    return []
def s_end(c, lt, d, k):
    s_title(c, lt, d, k)
    rect(c, -10, -300, SW + 20, 1500, (0.02, 0.02, 0.04), seg(lt, 1.2, 2.8))
    return []

S = [
    (5.8, s_hook, ("巨人卷入宙斯偷情", "失去了[r]100只眼睛[/r]"), ("", ""), (1.0, 1.08, 960, 300)),
    (4.4, s_title, ("", ""), ("", ""), (1.0, 1.03, 960, 380)),
    (5.2, s_temple, ("他叫阿耳戈斯", "是神后赫拉手下[r]最忠诚的守卫[/r]"), ("", ""), (1.0, 1.06, 960, 380)),
    (5.4, s_eyes, ("他的头上、身上", "密密麻麻长着[r]一百只眼睛[/r]"), ("", ""), (1.0, 1.08, 960, 300)),
    (4.8, s_sleep, ("就算睡觉的时候", "也只闭上[r]两只[/r]"), ("", ""), (1.0, 1.06, 900, 380)),
    (5.2, s_sleep, ("剩下的九十八只眼睛", "依然[r]死死盯着四周[/r]"), ("", ""), (1.05, 1.0, 960, 360)),
    (5.6, s_river, ("有一天 神王宙斯又在人间偷情", "爱上了美丽的少女伊俄"), ("", ""), (1.0, 1.06, 1000, 400)),
    (5.0, s_panic, ("怕被妻子赫拉[r]抓个正着[/r]", "宙斯慌忙挥手"), ("", ""), (1.0, 1.05, 960, 380)),
    (4.8, s_transform, ("把少女变成了", "一头[r]雪白的小母牛[/r]"), ("", ""), (1.0, 1.08, 900, 400)),
    (5.4, s_hera_arrive, ("赫拉[r]早就看穿了一切[/r]", "她指着小母牛 笑着对宙斯说："), ("", ""), (1.0, 1.04, 960, 380)),
    (4.4, s_hera_arrive, ("「这头牛真漂亮」", "「送给我吧」"), ("", ""), (1.04, 1.1, 800, 360)),
    (4.8, s_zeus_nod, ("宙斯[r]骑虎难下[/r]", "只能硬着头皮答应"), ("", ""), (1.0, 1.06, 1200, 360)),
    (5.4, s_handover, ("赫拉一拿到母牛", "立刻交给百眼巨人阿耳戈斯看管："), ("", ""), (1.0, 1.05, 960, 400)),
    (4.6, s_handover, ("「给我盯紧她」", "「[r]一秒钟也别离开视线！[/r]」"), ("", ""), (1.05, 1.12, 1100, 360)),
    (5.8, s_watch, ("巨人把母牛拴在橄榄树上", "一百只眼睛[r]日夜不停[/r]地轮流盯着她"), ("", ""), (1.0, 1.04, 1000, 400)),
    (4.4, s_graze, ("连吃草喝水", "都[r]不放过[/r]"), ("", ""), (1.0, 1.06, 1000, 420)),
    (4.8, s_olympus, ("宙斯心疼情人", "却[r]近不了身[/r]"), ("", ""), (1.0, 1.05, 1000, 400)),
    (5.4, s_olympus, ("只好派最机灵的信使赫尔墨斯", "去偷回母牛"), ("", ""), (1.0, 1.04, 960, 400)),
    (5.6, s_alarm, ("硬抢根本没戏", "只要有一只眼睛醒着 巨人就会[r]报警[/r]"), ("", ""), (1.0, 1.05, 900, 400)),
    (5.4, s_disguise, ("赫尔墨斯想了个主意", "他化身成一个[r]普通的牧羊人[/r]"), ("", ""), (1.0, 1.05, 900, 420)),
    (5.4, s_walk, ("手里拿着一管芦苇排笛", "慢悠悠走到山坡上"), ("", ""), (1.0, 1.04, 960, 420)),
    (5.0, s_play, ("他吹起[r]催眠的曲子[/r]", "巨人听得入了迷"), ("", ""), (1.0, 1.06, 960, 400)),
    (4.6, s_play, ("叫他过来", "坐在身边接着吹"), ("", ""), (1.05, 1.1, 1000, 420)),
    (5.4, s_play, ("吹完一首又一首", "巨人的[r]五十只眼睛[/r]闭上了"), ("", ""), (1.0, 1.06, 1000, 400)),
    (4.6, s_hold, ("还有五十只", "在[r]硬撑[/r]"), ("", ""), (1.0, 1.06, 1000, 360)),
    (4.8, s_story, ("赫尔墨斯又收起笛子", "用低沉缓慢的声音"), ("", ""), (1.0, 1.05, 960, 420)),
    (4.8, s_story, ("给他讲起了", "[r]漫长又无聊[/r]的故事"), ("", ""), (1.04, 1.0, 1000, 380)),
    (5.4, s_dusk, ("从天亮讲到天黑", "巨人终于[r]熬不住了[/r]"), ("", ""), (1.0, 1.06, 1000, 400)),
    (5.4, s_count, ("第八十只、第九十只……", "直到最后那一只眼睛"), ("", ""), (1.0, 1.08, 1000, 300)),
    (4.2, s_last, ("也[r]沉沉地合上了[/r]", ""), ("", ""), (1.0, 1.1, 960, 360)),
    (4.8, s_silence, ("就在一百只眼睛", "[r]全部闭上[/r]的瞬间"), ("", ""), (1.0, 1.08, 820, 360)),
    (5.4, s_slash, ("赫尔墨斯猛地拔出弯刀", "一刀[r]砍下了巨人的头颅[/r]"), ("", ""), (1.0, 1.06, 900, 380)),
    (4.4, s_fall, ("巨人的尸体", "[r]滚落山崖[/r]"), ("", ""), (1.0, 1.04, 1200, 500)),
    (5.0, s_dark, ("一百只眼睛", "从此[r]永远熄灭了[/r]"), ("", ""), (1.0, 1.06, 960, 560)),
    (5.4, s_grief, ("赫拉得知最忠心的部下为自己惨死", "[r]悲痛欲绝[/r]"), ("", ""), (1.0, 1.05, 860, 380)),
    (5.2, s_grief, ("她没有让这双不眠不休的眼睛", "烂在泥土里"), ("", ""), (1.0, 1.05, 900, 500)),
    (5.0, s_descend, ("赫拉走下山崖", "将巨人身上那一百只眼睛"), ("", ""), (1.0, 1.04, 900, 460)),
    (5.2, s_pluck, ("一颗接一颗地", "[r]摘了下来[/r]"), ("", ""), (1.0, 1.08, 900, 420)),
    (5.4, s_garden, ("她把这些眼睛", "全都镶嵌在了自己最心爱的神鸟——"), ("", ""), (1.0, 1.04, 960, 420)),
    (4.6, s_garden, ("[g]孔雀[/g]的尾羽上", ""), ("", ""), (1.0, 1.08, 1200, 380)),
    (5.4, s_today, ("今天 每当孔雀", "展开长长的屏风"), ("", ""), (1.0, 1.05, 960, 400)),
    (5.6, s_spots, ("那一百个闪烁着[g]蓝绿色光芒[/g]的圆斑", "就会在阳光下[r]齐刷刷地睁开[/r]"), ("", ""), (1.0, 1.06, 960, 360)),
    (5.2, s_spots, ("那不是普通的花纹", "那是百眼巨人阿耳戈斯"), ("", ""), (1.0, 1.0, 960, 380)),
    (5.6, s_world, ("跨越了几千年的光阴", "依然在替他的主人 [r]凝视着人间[/r]"), ("", ""), (1.0, 1.05, 960, 380)),
    (5.8, s_loop, ("巨人卷入宙斯偷情", "失去了[r]100只眼睛[/r]"), ("", ""), (1.0, 1.08, 960, 300)),
    (3.0, s_end, ("", ""), ("", ""), (1.0, 1.0, 960, 380)),
]
