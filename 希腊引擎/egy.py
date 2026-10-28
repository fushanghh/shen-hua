# 埃及壁画木偶库：带表情的头部、兽首、冠冕、走路循环 —— 纯 cairo 矢量
import math, numpy as np, cairocffi as cairo
from puppet import shape, line, smooth, clip_shape, J, taper, rgb, LINE

def circ(c, x, y, r, col, a=1.0): c.new_path(); c.arc(x, y, r, 0, 7); c.set_source_rgba(*col, a); c.fill()
def ring_stroke(c, x, y, r, col, lw, a=1.0): c.new_path(); c.arc(x, y, r, 0, 7); c.set_source_rgba(*col, a); c.set_line_width(lw); c.stroke()

P = dict(
    skin=rgb('c27a4a'), skin2=rgb('a8653b'), fskin=rgb('dba673'), fskin2=rgb('c28c5c'),
    linen=rgb('f1e7cf'), linen2=rgb('d8cbab'), gold=rgb('d1a347'), gold2=rgb('a97e2c'),
    lapis=rgb('26407d'), lapis2=rgb('192c4e'), turq=rgb('3f8f8a'), turq2=rgb('2d6b67'),
    red=rgb('a8432b'), red2=rgb('7d2f1e'), green=rgb('4f7a45'), green2=rgb('3a5c33'),
    black=rgb('1e1a17'), white=rgb('f6efdd'), wig=rgb('1f2742'), wig2=rgb('2f3b63'),
    nut=rgb('2a4a8c'), nut2=rgb('1d3566'), geb=rgb('5f8a46'), geb2=rgb('476b34'), osir=rgb('5d8c5a'),
    silver=rgb('cfd8e3'), silver2=rgb('9fb0c4'), pink=rgb('e58a7a'), tear=rgb('8fc6e8'), ibis=rgb('2a2522'), falcon=rgb('3b4a5a'),
    setc=rgb('9a5a3a'), white2=rgb('e4dcc8'))

LW = 4.2

def E(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

# ---------------- 表情眼睛 ----------------
def eye_e(c, x, y, w, open_=1.0, look=0.0, happy=False, kohl=True, iris=None):
    if happy:   # 笑眯眼：上弯弧
        line(c, [(x - w, y + 2), (x, y - w * 0.45), (x + w, y + 2)], lw=3.2)
        if kohl: line(c, [(x + w, y + 2), (x + w * 1.7, y + 1)], lw=2.6)
        return
    if open_ < 0.15:
        line(c, [(x - w, y), (x, y + w * 0.22), (x + w, y)], lw=3.0)
        if kohl: line(c, [(x + w, y), (x + w * 1.7, y - 1)], lw=2.6)
        return
    k = open_
    pts = [(x - w, y, 'c'), (x - w * 0.15, y - w * 0.5 * k), (x + w * 0.7, y - w * 0.28 * k), (x + w, y, 'c'), (x + w * 0.1, y + w * 0.36 * k)]
    shape(c, pts, P['white'], 2.2)
    c.save(); clip_shape(c, pts)
    circ(c, x + w * (0.18 + 0.25 * look), y - w * 0.04, w * 0.34, iris or LINE)
    circ(c, x + w * (0.10 + 0.25 * look), y - w * 0.16, w * 0.09, P['white'])
    c.restore()
    line(c, [(x - w * 1.05, y - w * 0.04), (x - w * 0.15, y - w * 0.56 * k), (x + w * 0.75, y - w * 0.3 * k), (x + w * 1.0, y)], lw=3.0)
    if kohl: line(c, [(x + w * 0.95, y), (x + w * 1.8, y - w * 0.06)], lw=2.8)

def brow_e(c, x0, x1, y, b, col=LINE, lw=3.4):
    # b<0 愤怒（前端压低） b>0 忧伤（前端上挑）
    yf = y + 9 * (-b); yb = y - 3 * (-b)
    line(c, [(x0, yb), ((x0 + x1) / 2, min(yb, yf) - 3), (x1, yf)], col, lw)

def mouth_e(c, x, y, kind, s=1.0):
    if kind == 'smile': line(c, [(x - 12 * s, y - 2), (x - 4 * s, y + 3), (x + 4, y - 5 * s)], lw=2.6)
    elif kind == 'grin':
        shape(c, [(x - 14 * s, y - 4, 'c'), (x + 4, y - 9 * s, 'c'), (x + 2, y + 6 * s), (x - 8 * s, y + 6 * s)], P['white'], 2.4)
        line(c, [(x - 12 * s, y), (x + 3, y - 3 * s)], lw=1.4)
    elif kind == 'open': shape(c, [(x - 12 * s, y - 6), (x + 4, y - 8 * s), (x + 4, y + 10 * s), (x - 8 * s, y + 10 * s)], rgb('3a2018'), 2.4)
    elif kind == 'O': shape(c, [(x - 6 * s, y - 6 * s), (x + 3, y - 6 * s), (x + 3, y + 6 * s), (x - 6 * s, y + 6 * s)], rgb('3a2018'), 2.2)
    elif kind == 'frown': line(c, [(x - 12 * s, y + 3), (x - 4 * s, y - 3), (x + 4, y + 4 * s)], lw=2.6)
    elif kind == 'tight': line(c, [(x - 12 * s, y), (x + 4, y)], lw=3.0)
    else: line(c, [(x - 10 * s, y), (x + 3, y - 1)], lw=2.4)

def fx_face(c, L, ex, ey):
    if L.get('blush', 0) > 0:
        g = cairo.RadialGradient(ex + 4, ey + 26, 1, ex + 4, ey + 26, 26); g.add_color_stop_rgba(0, *P['pink'], 0.75 * L['blush']); g.add_color_stop_rgba(1, *P['pink'], 0)
        c.set_source(g); c.arc(ex + 4, ey + 26, 26, 0, 7); c.fill()
    if L.get('tear', 0) > 0:
        u = L.get('tear_ph', 0.0) % 1.0
        tx, ty = ex - 4, ey + 10 + u * 70
        shape(c, [(tx, ty - 12), (tx + 7, ty + 2), (tx, ty + 9), (tx - 7, ty + 2)], P['tear'], 1.6)
        line(c, [(ex - 3, ey + 8), (tx, ty - 10)], P['tear'], 3)
    if L.get('sweat', 0) > 0:
        u = L.get('sweat_ph', 0.0) % 1.0
        sx, sy = ex - 34, ey - 34 + u * 40
        for k_ in range(int(1 + 2 * L['sweat'])):
            xx = sx - k_ * 18; yy = sy + k_ * 12
            shape(c, [(xx, yy - 12), (xx + 7, yy + 3), (xx, yy + 9), (xx - 7, yy + 3)], P['tear'], 1.6)

# ---------------- 头部（局部：下巴约在 y=0，头顶约 y=-130，朝 +x） ----------------
def head(c, kind, L, o):
    L = dict(L or {}); b = L.get('brow', 0.0); eo = L.get('eye', 1.0); mk = L.get('mouth', 'n'); happy = L.get('happy', False); look = L.get('look', 0.0)
    skin = o.get('skin', P['skin'])
    out = {}
    wig = o.get('wig', 'long')
    def wigback(col=P['wig'], col2=P['wig2'], long_=True):
        pts = [(-6, -136), (34, -132), (40, -110), (-6, -96), (-6, -40), (8, 30 if long_ else -10), (-10, 60 if long_ else 0), (-52, 70 if long_ else 4), (-66, -40), (-56, -110)]
        shape(c, pts, col, LW)
        c.save(); clip_shape(c, pts)
        for k_ in range(-6, 8): line(c, [(-80 + k_ * 12, -140), (-80 + k_ * 12, 80)], col2, 2.6)
        c.restore()
        line(c, [(-62, 40 if long_ else -4), (6, 24 if long_ else -12)], o.get('wigband', P['gold']), 6)
    if kind in ('human', 'woman', 'youth'):
        if wig and kind != 'youth': wigback(long_=(wig == 'long'))
        face = [(-30, -100), (-8, -134), (34, -126), (50, -104), (54, -94), (70, -66, 'c'), (56, -58), (58, -50), (54, -42), (56, -34), (50, -16), (28, -2), (-14, 4), (-30, -40)]
        if kind == 'youth':
            shape(c, [(-36, -96), (-10, -138), (36, -128), (40, -100), (-20, -86), (-40, -40)], P['black'], LW)
        shape(c, face, skin, LW)
        if kind == 'youth':   # 侧编发（少年锁）
            pts = [(-30, -70), (-12, -60), (-20, 10), (-12, 60), (-26, 80), (-40, 40), (-44, -40)]
            shape(c, pts, P['black'], LW)
            for k_ in range(6): line(c, [(-38, -40 + k_ * 18), (-18, -30 + k_ * 18)], P['wig2'], 2)
            circ(c, -24, 78, 8, P['gold'])
        if wig and kind != 'youth':   # 前额发际
            shape(c, [(-30, -100), (-8, -138), (36, -132), (44, -114), (14, -108), (-4, -96), (-20, -60), (-34, -60)], P['wig'], LW)
            line(c, [(-26, -70), (-6, -100), (40, -116)], P['wig2'], 2.4)
        ex, ey = 30, -86
        eye_e(c, ex, ey, 12, eo, look, happy)
        brow_e(c, 16, 48, -102, b)
        mouth_e(c, 52, -44, mk)
        line(c, [(40, -66), (32, -58)], o.get('skin2', P['skin2']), 2.2)
        out['eye'] = (ex, ey)
        fx_face(c, L, ex, ey)
        if o.get('beard'):
            shape(c, [(40, -12), (52, -14), (54, 30), (46, 34), (40, 10)], P['black'], 2.6)
            for k_ in range(4): line(c, [(42, k_ * 8), (52, k_ * 8 - 2)], P['gold'], 1.6)
    elif kind == 'falcon':
        wigback(P['lapis'], P['lapis2'])
        fc = o.get('feather', P['falcon'])
        hd = [(-32, -96), (-6, -134), (34, -128), (54, -110), (64, -96), (84, -82), (90, -60, 'c'), (80, -66), (70, -62), (56, -56), (44, -34), (24, -4), (-14, 6), (-34, -40)]
        shape(c, hd, fc, LW)
        shape(c, [(54, -110), (64, -96), (84, -82), (90, -60, 'c'), (80, -66), (70, -62), (58, -70), (56, -92)], P['gold'], 2.8)
        if mk in ('open', 'grin', 'O'):
            shape(c, [(58, -68), (78, -60), (70, -44), (54, -50)], P['gold2'], 2.4)
        shape(c, [(10, -88), (44, -96), (50, -76), (30, -64), (6, -70)], P['white'], 2.0)
        line(c, [(28, -76), (22, -48), (16, -30)], LINE, 5)     # 隼面颊泪纹
        ex, ey = 30, -88
        eye_e(c, ex, ey, 11, eo, look, happy, kohl=False, iris=rgb('3a2a10'))
        brow_e(c, 14, 50, -104, b, lw=4)
        out['eye'] = (ex, ey); fx_face(c, L, ex, ey)
    elif kind == 'ibis':
        wigback(P['wig'], P['wig2'])
        hd = [(-30, -96), (-10, -128), (26, -126), (46, -108), (50, -90), (40, -70), (24, -40), (6, 0), (-20, 6), (-34, -40)]
        shape(c, hd, P['ibis'], LW)
        bo = 0.22 if mk in ('open', 'grin', 'O') else 0.0
        # 长喙：上喙 + 下喙（可张）
        with J(c, 44, -84, 0) as cb:
            up = [(0, -10), (40, -6), (90, 18), (130, 58), (146, 86, 'c'), (126, 66), (82, 32), (36, 10), (0, 6)]
            shape(cb, up, rgb('3a322c'), 3.2)
            with J(cb, 0, 4, -bo) as cl:
                lo = [(0, 0), (36, 10), (80, 34), (122, 70), (140, 92, 'c'), (118, 76), (74, 44), (30, 22), (0, 14)]
                shape(cl, lo, rgb('4a3f36'), 3.0)
            mb = cb.get_matrix(); out['beak'] = mb.transform_point(140, 86)
        ex, ey = 22, -96
        circ(c, ex, ey, 15, rgb('3a332d'))
        eye_e(c, ex, ey, 10, eo, look, happy, kohl=False, iris=rgb('2a2010'))
        brow_e(c, 6, 40, -112, b, P['white2'], 3.4)
        out['eye'] = (ex, ey); fx_face(c, L, ex, ey)
    elif kind == 'set':
        wigback(P['wig'], P['wig2'])
        hd = [(-30, -96), (-10, -128), (30, -122), (60, -100), (96, -74), (110, -50, 'c'), (92, -52), (70, -46), (46, -30), (24, -4), (-14, 6), (-34, -40)]
        shape(c, hd, P['setc'], LW)
        for xx in (-14, 8):   # 方顶长耳
            shape(c, [(xx, -122), (xx - 4, -210), (xx + 18, -214, 'c'), (xx + 16, -124)], P['setc'], 3.4, t=0.2)
        if mk in ('grin', 'open'):
            shape(c, [(60, -52), (106, -52), (96, -38), (64, -34)], P['white'], 2.2)
            for k_ in range(4): line(c, [(68 + k_ * 9, -52), (68 + k_ * 9, -38)], lw=1.4)
        ex, ey = 30, -88
        eye_e(c, ex, ey, 11, eo, look, happy, iris=rgb('7a1a10'))
        brow_e(c, 14, 50, -104, b, lw=4)
        out['eye'] = (ex, ey); fx_face(c, L, ex, ey)
    elif kind == 'jackal':
        wigback(P['wig'], P['wig2'])
        fc = o.get('fur', rgb('1e1a17'))
        hd = [(-30, -96), (-10, -126), (24, -120), (60, -96), (104, -76), (112, -62, 'c'), (96, -56), (66, -48), (44, -30), (24, -4), (-14, 6), (-34, -40)]
        shape(c, hd, fc, LW)
        for xx in (-16, 6):
            shape(c, [(xx, -118), (xx + 6, -200), (xx + 26, -120)], fc, 3.4)
            line(c, [(xx + 8, -128), (xx + 10, -180)], P['gold'], 3)
        ex, ey = 34, -90
        eye_e(c, ex, ey, 11, eo, look, happy, iris=rgb('c99a45'))
        brow_e(c, 18, 52, -106, b, P['gold'], 3)
        out['eye'] = (ex, ey)
    # ---------- 冠冕 ----------
    cr = o.get('crown')
    if cr == 'sun':
        shape(c, [(-4, -132), (8, -150), (22, -132)], P['gold'], 2.6)
        r_ = 46; cx, cy = 8, -150 - r_
        circ(c, cx, cy, r_ + 14, rgb('f3c34a'), 0.0)
        shape(c, [(cx + r_ * math.cos(a), cy + r_ * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)], (o.get('disk') or rgb('d8432a')), 3.4)
        line(c, [(cx + r_ - 2, cy + 30), (cx + r_ + 12, cy + 10), (cx + r_ + 6, cy - 12), (cx + r_ + 16, cy - 22)], P['gold'], 7)
        out['disk'] = (cx, cy, r_)
    elif cr == 'moon':
        r_ = 38; cx, cy = 6, -150 - r_
        c.new_path(); c.arc(cx, cy + 10, r_ + 14, 0.15 * math.pi, 0.85 * math.pi); c.arc_negative(cx, cy - 6, r_ + 4, 0.8 * math.pi, 0.2 * math.pi); c.close_path()
        c.set_source_rgb(*P['silver2']); c.fill_preserve(); c.set_source_rgb(*LINE); c.set_line_width(3); c.stroke()
        shape(c, [(cx + r_ * math.cos(a), cy + r_ * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)], (o.get('disk') or P['silver']), 3.2)
        out['disk'] = (cx, cy, r_)
    elif cr == 'feather':
        shape(c, [(-10, -130), (-30, -270), (-14, -300, 'c'), (4, -260), (6, -130)], P['white'], 3)
        line(c, [(-8, -134), (-16, -286)], LINE, 2)
        for k_ in range(8): line(c, [(-12, -150 - k_ * 17), (-26, -160 - k_ * 17)], P['linen2'], 1.6)
    elif cr == 'goose':
        shape(c, [(-30, -132), (-36, -168), (-10, -180), (30, -176), (48, -188), (58, -210), (72, -214), (80, -204, 'c'), (66, -198), (58, -170), (40, -150), (20, -136)], P['white2'], 3)
        line(c, [(-26, -160), (24, -166)], P['linen2'], 2)
        circ(c, 66, -206, 3, LINE)
    elif cr == 'atef':
        shape(c, [(-30, -128), (-26, -200), (-6, -266), (8, -282, 'c'), (22, -266), (42, -200), (46, -128)], P['white'], 3.2)
        for sx_ in (-1, 1):
            xx = 8 + sx_ * 52
            shape(c, [(8 + sx_ * 30, -140), (xx, -250), (xx + sx_ * 10, -270, 'c'), (8 + sx_ * 34, -180)], P['linen2'], 2.6)
        circ(c, 8, -286, 8, P['gold'])
    elif cr == 'throne':
        shape(c, [(-10, -132), (-10, -150), (30, -150), (30, -132)], P['gold'], 2.6, t=0)
        shape(c, [(-14, -150, 'c'), (-14, -220, 'c'), (6, -220, 'c'), (6, -186, 'c'), (34, -186, 'c'), (34, -150, 'c')], P['lapis'], 3, t=0)
        line(c, [(-8, -160), (28, -160)], P['gold'], 4)
    elif cr == 'house':
        shape(c, [(-10, -132), (-10, -150), (30, -150), (30, -132)], P['gold'], 2.6, t=0)
        shape(c, [(-20, -150, 'c'), (-20, -196, 'c'), (40, -196, 'c'), (40, -150, 'c')], P['red'], 3, t=0)
        shape(c, [(-26, -196), (46, -196), (34, -218), (-14, -218)], P['gold'], 3, t=0.3)
    elif cr == 'pschent':
        shape(c, [(-30, -126), (-30, -180), (30, -170), (40, -230), (52, -228), (50, -150), (56, -126)], P['red'], 3)
        shape(c, [(-20, -160), (-14, -232), (6, -262, 'c'), (24, -232), (30, -168)], P['white'], 3)
    return out

# ---------------- 全身木偶 ----------------
def fig(c, x, y, h, pose=None, look=None, kind='human', **o):
    """h=身高像素，脚底在 y，默认朝右；flip=True 朝左。返回手、头、眼等世界坐标"""
    p = dict(nsh=0.12, nel=0.18, fsh=-0.1, fel=0.18, nhip=0.04, nkn=-0.03, fhip=-0.06, fkn=0.02, head=0.0, body=0.0, bob=0.0, breathe=0.0)
    p.update(pose or {})
    u = h / 800.0; out = {}
    c.save(); c.translate(x, y + p['bob'] * h / 600)
    if o.get('flip'): c.scale(-1, 1)
    c.scale(u, u)
    lw = LW / u * 0.95; lw = min(max(lw, 3.0), 7.0)
    skin = o.get('skin', P['skin']); skin2 = o.get('skin2', P['skin2'])
    female = o.get('female', False)
    c.translate(0, -400); c.rotate(-p['body'])
    def leg(hx, a1, a2, near):
        col = skin if near else skin2
        with J(c, hx, 0, a1) as c1:
            shape(c1, taper(205, 32, 22), col, lw)
            with J(c1, 0, 205, a2 - a1) as c2:
                shape(c2, taper(185, 22, 13), col, lw)
                with J(c2, 0, 185, -a2 + p['body']) as c3:
                    shape(c3, [(-22, -8), (20, -10), (82, 6), (96, 16, 'c'), (90, 20, 'c'), (-26, 20, 'c'), (-30, 4)], col, lw)
                    if o.get('anklet'): line(c3, [(-18, -8), (18, -8)], P['gold'], 6)
    def arm(sx, a1, a2, near, prop=None):
        col = skin if near else skin2
        with J(c, sx, -240, a1) as c1:
            shape(c1, taper(150, 24, 17), col, lw)
            line(c1, [(-18, 30), (18, 30)], P['gold'], 7)
            with J(c1, 0, 150, a2 - a1) as c2:
                shape(c2, taper(132, 17, 12), col, lw)
                line(c2, [(-15, 112), (15, 112)], P['gold'], 8); line(c2, [(-15, 112), (15, 112)], P['lapis'], 3)
                with J(c2, 0, 134, 0) as c3:
                    hand = [(-15, 0), (15, 0), (22, 26), (30, 40), (32, 46, 'c'), (20, 44), (16, 50), (12, 82), (6, 86, 'c'), (-4, 82), (-12, 70), (-16, 30)]
                    shape(c3, hand, col, lw * 0.9)
                    m = c3.get_matrix(); out['hand_n' if near else 'hand_f'] = c.device_to_user(*m.transform_point(0, 50)) if False else m.transform_point(0, 50)
                    if prop: prop(c3)
    leg(-14, p['fhip'], p['fhip'] + p['fkn'], False)
    arm(-58, p['fsh'], p['fsh'] + p['fel'], False, o.get('prop_f'))
    leg(14, p['nhip'], p['nhip'] + p['nkn'], True)
    br = 1 + 0.02 * p['breathe']
    c.save(); c.scale(br, 1)
    torso = [(-74, -252), (-30, -270), (40, -270), (82, -252), (70, -200), (52, -120), (40, -46), (46, 0, 'c'), (-46, 0, 'c'), (-40, -46), (-50, -120), (-66, -200)]
    shape(c, torso, skin, lw)
    if female:
        dcol = o.get('dress', P['red']); dcol2 = o.get('dress2', P['red2'])
        dress = [(-52, -190), (50, -190), (44, -60), (58, 120), (70, 380, 'c'), (-62, 380, 'c'), (-52, 120), (-48, -60)]
        shape(c, dress, dcol, lw)
        c.save(); clip_shape(c, dress)
        pat = o.get('pattern', 'feather')
        if pat == 'feather':
            for yy in range(-180, 400, 34):
                for xx in range(-80, 100, 30): c.new_path(); c.arc(xx + (yy // 34 % 2) * 15, yy, 16, 0, math.pi); c.set_source_rgb(*dcol2); c.set_line_width(2.4); c.stroke()
        elif pat == 'stars':
            r_ = np.random.default_rng(5)
            for k_ in range(40): circ(c, r_.uniform(-70, 80), r_.uniform(-180, 380), r_.uniform(3, 6), P['gold'])
        c.restore()
        line(c, [(-40, -190), (-30, -262)], dcol2, 8); line(c, [(38, -190), (30, -262)], dcol2, 8)
        line(c, [(-52, -186), (50, -186)], P['gold'], 6)
        if o.get('pregnant', 0) > 0:
            pg = o['pregnant']
            shape(c, [(46, -150), (46 + 60 * pg, -100), (50 + 70 * pg, -40), (46 + 40 * pg, 20), (44, 30)], dcol, lw)
            if o.get('glow_belly', 0) > 0:
                g = cairo.RadialGradient(60 + 30 * pg, -60, 2, 60 + 30 * pg, -60, 120)
                g.add_color_stop_rgba(0, 1, 0.92, 0.6, 0.8 * o['glow_belly']); g.add_color_stop_rgba(1, 1, 0.8, 0.4, 0); c.set_source(g); c.arc(60 + 30 * pg, -60, 120, 0, 7); c.fill()
                for k_ in range(5):
                    a_ = k_ * 1.25 + o.get('t', 0) * 0.8
                    circ(c, 60 + 30 * pg + 26 * math.cos(a_), -60 + 26 * math.sin(a_), 6, rgb('fff1b8'), o['glow_belly'])
    else:
        kc = o.get('kilt', P['linen'])
        kilt = [(-52, -12), (48, -12), (64, 150), (-6, 170), (-58, 156)]
        shape(c, kilt, kc, lw)
        c.save(); clip_shape(c, kilt)
        for k_ in range(-6, 8): line(c, [(k_ * 14, -10), (k_ * 18 + 10, 175)], P['linen2'], 2.2)
        c.restore()
        shape(c, [(8, 0), (44, 6), (66, 152), (20, 160)], o.get('apron', P['gold']), lw * 0.8)
        for yy in (40, 80, 120): line(c, [(18, yy), (52, yy + 4)], P['red2'], 3)
        shape(c, [(-54, -26, 'c'), (50, -26, 'c'), (50, -4, 'c'), (-54, -4, 'c')], P['gold'], lw * 0.8, t=0)
        if o.get('tail'): shape(c, [(-52, 0), (-80, 120), (-66, 330), (-56, 330), (-62, 120)], P['gold2'], lw * 0.7)
    # 宽领圈（wesekh）
    cx_, cy_ = 6, -268
    for k_, col in enumerate(o.get('collar', (P['turq'], P['gold'], P['red'], P['lapis'], P['gold']))):
        r1 = 30 + k_ * 13
        c.new_path(); c.arc(cx_, cy_, r1 + 13, 0.04 * math.pi, 0.96 * math.pi); c.arc_negative(cx_, cy_, r1, 0.96 * math.pi, 0.04 * math.pi); c.close_path()
        c.set_source_rgb(*col); c.fill_preserve(); c.set_source_rgb(*LINE); c.set_line_width(1.6); c.stroke()
    if o.get('stars_body'):
        r_ = np.random.default_rng(9)
        for k_ in range(14): circ(c, r_.uniform(-50, 50), r_.uniform(-180, -20), r_.uniform(3, 5), P['gold'])
    c.restore()
    # 颈 + 头
    shape(c, [(-14, -262), (-12, -300), (24, -300), (28, -262)], skin, lw)
    with J(c, 6, -296, p['head']) as ch:
        ch.scale(1.22, 1.22)
        hk = o.get('head_kind', 'woman' if female else 'human')
        ho = head(ch, hk, look, dict(skin=skin, skin2=skin2, crown=o.get('crown'), wig=o.get('wig', 'long'), beard=o.get('beard'), disk=o.get('disk'), wigband=o.get('wigband') or P['gold']))
        m = ch.get_matrix()
        out['head'] = m.transform_point(10, -140); out['face'] = m.transform_point(50, -70)
        if 'eye' in ho: out['eye'] = m.transform_point(*ho['eye'])
        if 'disk' in ho: dx, dy, dr = ho['disk']; out['disk'] = m.transform_point(dx, dy); out['disk_r'] = dr * u * 1.22
        if 'beak' in ho: out['beak'] = m.transform_point(*ho['beak'])
    arm(70, p['nsh'], p['nsh'] + p['nel'], True, o.get('prop_n'))
    c.restore()
    inv = c.get_matrix(); inv.invert()
    for k_, v_ in list(out.items()):
        if isinstance(v_, tuple) and len(v_) == 2: out[k_] = inv.transform_point(*v_)
    out['u'] = u
    return out

# ---------------- 姿势 ----------------
def P_(**k):
    d = dict(nsh=0.12, nel=0.18, fsh=-0.1, fel=0.18, nhip=0.04, nkn=-0.03, fhip=-0.06, fkn=0.02, head=0.0, body=0.0, bob=0.0); d.update(k); return d
def walk(ph, amp=0.36, arm=0.32, **k):
    s_ = math.sin(ph)
    d = dict(nhip=amp * s_, fhip=-amp * s_, nkn=-0.55 * max(0, -math.cos(ph)), fkn=-0.55 * max(0, math.cos(ph)),
             nsh=-arm * s_ + 0.05, fsh=arm * s_ - 0.05, nel=0.22 + 0.1 * max(0, s_), fel=0.22 + 0.1 * max(0, -s_), head=0.02 * math.sin(2 * ph),
             bob=-10 * abs(math.cos(ph)) + 5, body=0.03)
    d.update(k); return d
def hop(ph, **k):   # 轻快踮步
    d = walk(ph, 0.42, 0.4, **k); d['bob'] = -24 * abs(math.sin(ph)); return d
def blink(t, seed=0, period=3.7):
    ph = (t + seed * 1.37) % period
    return 0.0 if ph < 0.12 else 1.0
def breathe(t, seed=0): return math.sin(t * 2.2 + seed)

# ---------------- 道具 ----------------
def senet(c, x, y, w, h, t=0, pieces=None):
    shape(c, [(x, y, 'c'), (x + w, y, 'c'), (x + w, y + h, 'c'), (x, y + h, 'c')], rgb('8a5a2e'), 3.4, t=0)
    c.rectangle(x + 8, y + 8, w - 16, h - 16); c.set_source_rgb(*rgb('d9b06a')); c.fill()
    cw = (w - 16) / 10; chh = (h - 16) / 3
    for i in range(11): line(c, [(x + 8 + i * cw, y + 8), (x + 8 + i * cw, y + h - 8)], rgb('5a3a1e'), 1.8)
    for j in range(4): line(c, [(x + 8, y + 8 + j * chh), (x + w - 8, y + 8 + j * chh)], rgb('5a3a1e'), 1.8)
    for (i, j, col) in (pieces or []):
        px = x + 8 + (i + 0.5) * cw; py = y + 8 + (j + 0.5) * chh
        shape(c, [(px - cw * 0.3, py + chh * 0.3, 'c'), (px - cw * 0.2, py - chh * 0.25), (px, py - chh * 0.4), (px + cw * 0.2, py - chh * 0.25), (px + cw * 0.3, py + chh * 0.3, 'c')], col, 2)
    # 侧面厚度
    shape(c, [(x, y + h, 'c'), (x + w, y + h, 'c'), (x + w, y + h + 18, 'c'), (x, y + h + 18, 'c')], rgb('6a4320'), 2.6, t=0)

def jar(c, x, y, s, glow=0.0):
    shape(c, [(x - 30 * s, y - 80 * s), (x + 30 * s, y - 80 * s), (x + 22 * s, y - 70 * s), (x + 48 * s, y - 30 * s), (x + 40 * s, y + 10 * s), (x, y + 18 * s), (x - 40 * s, y + 10 * s), (x - 48 * s, y - 30 * s), (x - 22 * s, y - 70 * s)], rgb('b5643a'), 3)
    line(c, [(x - 40 * s, y - 40 * s), (x + 40 * s, y - 40 * s)], P['lapis'], 5 * s)
    if glow > 0:
        g = cairo.RadialGradient(x, y - 80 * s, 2, x, y - 80 * s, 120 * s); g.add_color_stop_rgba(0, 0.85, 0.92, 1, 0.9 * glow); g.add_color_stop_rgba(1, 0.7, 0.8, 1, 0)
        c.set_source(g); c.arc(x, y - 80 * s, 120 * s, 0, 7); c.fill()
