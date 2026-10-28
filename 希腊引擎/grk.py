# 希腊陶瓶画木偶库：希腊服饰、发型、头盔、老妇、仙女、蜘蛛、织机、群像 —— 纯 cairo 矢量
import math, numpy as np, cairocffi as cairo
from puppet import shape, line, smooth, clip_shape, J, taper, rgb, LINE
import egy
from egy import circ, ring_stroke, eye_e, brow_e, mouth_e, fx_face, P_, walk, hop, blink, breathe, E

G = dict(
    terra=rgb('c8692e'), terra2=rgb('a4521f'), black=rgb('1c1714'), cream=rgb('efe2c4'), cream2=rgb('d9c8a2'),
    purple=rgb('6e2b4f'), purple2=rgb('521d3a'), olive=rgb('6b7a3a'), olive2=rgb('505c2a'), sea=rgb('2f5f7a'), sea2=rgb('224a60'),
    gold=rgb('d1a347'), gold2=rgb('a97e2c'), bronze=rgb('b07a3a'), bronze2=rgb('8a5a26'), white=rgb('f6efdd'), grey=rgb('8a8580'), grey2=rgb('6a6560'),
    skin=rgb('e0a878'), skin2=rgb('c88e60'), pale=rgb('f0d2b0'), pale2=rgb('d8b490'), dark=rgb('a8693e'), dark2=rgb('8a5530'),
    hair=rgb('2a1d16'), hair2=rgb('4a3324'), blond=rgb('c99a45'), blond2=rgb('a87a30'), whitehair=rgb('e8e2d6'), red=rgb('a8432b'), red2=rgb('7d2f1e'),
    blue=rgb('3a5a8c'), blue2=rgb('2a4470'), green=rgb('4f7a45'), green2=rgb('3a5c33'), rose=rgb('c9707a'), rose2=rgb('a85560'), saff=rgb('d9a440'), saff2=rgb('b8862c'),
    silk=rgb('e8eef6'))
LW = 4.2

def meander(c, x0, x1, y, h, col, bg=None, lw=2.4):
    if bg: c.rectangle(x0, y, x1 - x0, h); c.set_source_rgb(*bg); c.fill()
    u = h / 5.0; x = x0
    c.new_path()
    while x + 5 * u <= x1 + 0.1:
        pts = [(x, y + 4 * u), (x + 4 * u, y + 4 * u), (x + 4 * u, y + u), (x + u, y + u), (x + u, y + 3 * u), (x + 3 * u, y + 3 * u), (x + 3 * u, y + 2 * u), (x + 2 * u, y + 2 * u)]
        c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]
        c.move_to(x + 4 * u, y + 4 * u); c.line_to(x + 5 * u, y + 4 * u)
        x += 5 * u
    c.set_source_rgb(*col); c.set_line_width(lw); c.set_line_cap(cairo.LINE_CAP_SQUARE); c.stroke()

def wave_band(c, x0, x1, y, h, col, lw=2.4):
    c.new_path(); n = int((x1 - x0) / h)
    for i in range(n):
        x = x0 + i * h
        c.move_to(x, y + h); c.curve_to(x + h * 0.2, y, x + h * 0.9, y, x + h * 0.7, y + h * 0.45); c.curve_to(x + h * 0.6, y + h * 0.6, x + h * 0.4, y + h * 0.5, x + h * 0.5, y + h * 0.35)
    c.set_source_rgb(*col); c.set_line_width(lw); c.stroke()

# ---------------- 头部 ----------------
def head_g(c, kind, L, o):
    L = dict(L or {}); out = {}
    hc = o.get('hair_c', G['hair']); hc2 = o.get('hair_c2', G['hair2'])
    skin = o.get('skin', G['skin']); skin2 = o.get('skin2', G['skin2'])
    sway = o.get('hair_sway', 0.0)
    if kind in ('gf', 'athena', 'nymph', 'arachne'):
        if kind == 'nymph' or kind == 'arachne':   # 长披发
            pts = [(-10, -136), (34, -130), (30, -100), (-4, -90), (-2, -30), (10, 60), (4, 150 + 10 * sway), (-30, 170 + 14 * sway), (-70, 120 + 10 * sway), (-74, 0), (-66, -90), (-46, -128)]
            if kind == 'arachne': pts = [(-10, -136), (34, -130), (30, -100), (-4, -90), (-2, -30), (6, 40), (-6, 100 + 8 * sway), (-34, 112 + 10 * sway), (-64, 80 + 8 * sway), (-72, 0), (-66, -90), (-46, -128)]
            shape(c, pts, hc, LW)
            c.save(); clip_shape(c, pts)
            for k in range(-6, 6): line(c, [(-60 + k * 10, -120), (-50 + k * 11 + 6 * sway, 60), (-56 + k * 12 + 12 * sway, 180)], hc2, 2.2)
            c.restore()
        else:   # 发髻
            circ(c, -52, -104, 30, hc); ring_stroke(c, -52, -104, 30, LINE, 3)
            for k in range(3): c.new_path(); c.arc(-52, -104, 10 + k * 7, 0.5, 5.5); c.set_source_rgb(*hc2); c.set_line_width(2); c.stroke()
            shape(c, [(-10, -138), (30, -134), (40, -110), (-4, -96), (-10, -40), (-40, -36), (-62, -80), (-50, -124)], hc, LW)
        egy.head(c, 'human', L, dict(skin=skin, skin2=skin2, wig=None))
        # 前额发际 + 发带
        shape(c, [(-36, -104), (-12, -140), (30, -138), (46, -118), (30, -110), (14, -112), (0, -100), (-14, -70), (-34, -66)], hc, LW)
        for k in range(4): c.new_path(); c.arc(30 - k * 12, -112 + k * 2, 6, 0, math.pi); c.set_source_rgb(*hc2); c.set_line_width(2); c.stroke()
        if kind != 'athena':
            line(c, [(-36, -100), (-4, -132), (38, -126)], o.get('band', G['gold']), 6)
        if kind == 'nymph':
            for k in range(5):
                fx, fy = -34 + k * 16, -134 + abs(k - 2) * 5
                for j in range(5): circ(c, fx + 6 * math.cos(j * 1.256), fy + 6 * math.sin(j * 1.256), 4, o.get('flower', G['rose']))
                circ(c, fx, fy, 3, G['saff'])
        circ(c, 0, -52, 5, G['gold'])   # 耳环
        out['eye'] = (30, -86)
    elif kind == 'gm':
        shape(c, [(-36, -100), (-14, -142), (30, -136), (46, -116), (-6, -98), (-20, -40), (-40, -50)], hc, LW)
        egy.head(c, 'human', L, dict(skin=skin, skin2=skin2, wig=None))
        shape(c, [(-36, -100), (-14, -144), (32, -140), (48, -118), (26, -112), (0, -104), (-16, -66), (-38, -64)], hc, LW)
        r_ = np.random.default_rng(3)
        for k in range(12): c.new_path(); c.arc(r_.uniform(-34, 34), r_.uniform(-136, -76), 5, 0, 6); c.set_source_rgb(*hc2); c.set_line_width(2); c.stroke()
        if o.get('beard'):
            shape(c, [(-14, -40), (24, -20), (48, -24), (56, -34), (58, -4), (40, 18), (10, 22), (-14, 4)], hc, LW)
            for k in range(5): c.new_path(); c.arc(10 + k * 9, -2 + (k % 2) * 6, 5, 0, 6); c.set_source_rgb(*hc2); c.set_line_width(2); c.stroke()
        if o.get('crown'):
            cr = [(-34, -128), (-38, -170), (-22, -150), (-8, -182), (6, -152), (22, -186), (34, -154), (48, -172), (46, -124)]
            shape(c, cr, G['gold'], LW)
            line(c, [(-34, -134), (46, -130)], G['gold2'], 4)
            for k in range(3): circ(c, -16 + k * 26, -140, 5, [G['red'], G['blue'], G['red']][k])
        if o.get('wreath'):
            for k in range(7): shape(c, [(-30 + k * 10, -136 + abs(k - 3) * 3), (-24 + k * 10, -150 + abs(k - 3) * 3), (-18 + k * 10, -136 + abs(k - 3) * 3)], G['olive'], 1.6)
        out['eye'] = (30, -86)
    elif kind == 'old':
        # 灰色头巾披到背后
        shape(c, [(-20, -150), (36, -144), (54, -110), (40, -96), (0, -100), (-10, -40), (6, 40), (-30, 120), (-84, 110), (-80, -40), (-60, -120)], o.get('veil', G['grey']), LW)
        c.save(); clip_shape(c, [(-20, -150), (36, -144), (54, -110), (40, -96), (0, -100), (-10, -40), (6, 40), (-30, 120), (-84, 110), (-80, -40), (-60, -120)])
        for k in range(6): line(c, [(-70 + k * 14, -130), (-60 + k * 12, 120)], G['grey2'], 2)
        c.restore()
        face = [(-30, -100), (-8, -128), (34, -122), (50, -100), (56, -90), (76, -60, 'c'), (58, -54), (56, -46), (50, -40), (52, -32), (44, -14), (26, -2), (-14, 4), (-30, -40)]
        shape(c, face, skin, LW)
        for k in range(3): line(c, [(4, -70 + k * 10), (14, -66 + k * 10)], skin2, 1.6)
        line(c, [(40, -40), (36, -30)], skin2, 1.8); line(c, [(18, -100), (40, -102)], skin2, 1.6)
        # 白发露出额前
        shape(c, [(-30, -100), (-6, -124), (34, -120), (42, -108), (6, -104), (-16, -86), (-30, -80)], G['whitehair'], 3)
        for k in range(4): line(c, [(-20 + k * 14, -118), (-26 + k * 14, -92)], rgb('c8c0b0'), 1.6)
        shape(c, [(-20, -150), (36, -144), (54, -110), (46, -104), (30, -124), (-6, -128), (-30, -104), (-36, -120)], o.get('veil', G['grey']), 3)
        ex, ey = 30, -84
        eye_e(c, ex, ey, 10, L.get('eye', 1.0) * 0.7, L.get('look', 0), L.get('happy', False), kohl=False)
        brow_e(c, 16, 46, -98, L.get('brow', 0.0), G['whitehair'], 3.6)
        mouth_e(c, 50, -38, L.get('mouth', 'n'), 0.9)
        out['eye'] = (ex, ey); fx_face(c, L, ex, ey)
    # 雅典娜：科林斯头盔推到头顶 + 高羽冠
    if kind == 'athena':
        hp = [(-44, -110), (-40, -150), (-10, -178), (34, -172), (56, -146), (60, -122), (40, -114), (10, -126), (-20, -112)]
        shape(c, hp, o.get('helm', G['bronze']), LW)
        shape(c, [(40, -114), (60, -122), (72, -104), (56, -96)], o.get('helm2', G['bronze2']), 3)
        line(c, [(-30, -132), (0, -150), (44, -140)], G['gold'], 3)
        cr = [(-56, -146), (-46, -200), (-10, -236), (36, -228), (58, -196), (52, -170), (30, -190), (-6, -196), (-36, -168)]
        shape(c, cr, o.get('crest', G['red']), LW)
        c.save(); clip_shape(c, cr)
        for k in range(14): line(c, [(-60 + k * 9, -240), (-50 + k * 9, -150)], o.get('crest2', G['red2']), 2.2)
        c.restore()
        line(c, [(-40, -150), (-4, -184), (40, -176)], G['black'], 4)
    return out

# ---------------- 全身木偶（希腊服饰） ----------------
def fig(c, x, y, h, pose=None, look=None, kind='gf', **o):
    p = dict(nsh=0.12, nel=0.18, fsh=-0.1, fel=0.18, nhip=0.04, nkn=-0.03, fhip=-0.06, fkn=0.02, head=0.0, body=0.0, bob=0.0, breathe=0.0)
    p.update(pose or {})
    u = h / 800.0; out = {}
    c.save(); c.translate(x, y + p['bob'] * h / 600)
    if o.get('flip'): c.scale(-1, 1)
    c.scale(u, u)
    lw = LW / u * 0.95; lw = min(max(lw, 2.4), 7.0)
    skin = o.get('skin', G['skin']); skin2 = o.get('skin2', G['skin2'])
    female = kind in ('gf', 'athena', 'nymph', 'old', 'arachne')
    long_ = female or o.get('long', False)
    dcol = o.get('dress', G['cream']); dcol2 = o.get('dress2', G['cream2']); trim = o.get('trim', G['black'])
    c.translate(0, -400); c.rotate(-p['body'])
    def leg(hx, a1, a2, near):
        col = skin if near else skin2
        with J(c, hx, 0, a1) as c1:
            shape(c1, taper(205, 30, 21), col, lw)
            with J(c1, 0, 205, a2 - a1) as c2:
                shape(c2, taper(185, 21, 12), col, lw)
                with J(c2, 0, 185, -a2 - p['body']) as c3:
                    shape(c3, [(-20, -8), (20, -10), (78, 6), (90, 16, 'c'), (86, 20, 'c'), (-24, 20, 'c'), (-28, 4)], o.get('sandal', skin) if not near else skin, lw)
                    line(c3, [(-18, 18), (86, 18)], rgb('5a3a1e'), 5)
                    line(c3, [(-10, -6), (30, 10)], rgb('5a3a1e'), 3)
    def arm(sx, a1, a2, near, prop=None):
        col = skin if near else skin2
        with J(c, sx, -240, a1) as c1:
            shape(c1, taper(150, 22, 16), col, lw)
            with J(c1, 0, 150, a2 - a1) as c2:
                shape(c2, taper(132, 16, 11), col, lw)
                if o.get('bracelet'): line(c2, [(-14, 112), (14, 112)], G['gold'], 6)
                with J(c2, 0, 134, o.get('wrist', 0.0)) as c3:
                    hand = [(-14, 0), (14, 0), (20, 26), (28, 40), (30, 46, 'c'), (18, 44), (15, 50), (11, 80), (5, 84, 'c'), (-4, 80), (-11, 68), (-15, 30)]
                    shape(c3, hand, col, lw * 0.9)
                    m = c3.get_matrix(); out['hand_n' if near else 'hand_f'] = m.transform_point(0, 50)
                    if prop: prop(c3)
            # 袖子
            if o.get('sleeve', True):
                shape(c1, [(-26, -10), (26, -10), (30, 60), (-30, 64)], dcol if near else dcol2, lw * 0.9)
                line(c1, [(-30, 62), (30, 58)], trim, 3)
    if o.get('cape_back'): o['cape_back'](c)
    bd = p['body']
    leg(-14, p['fhip'] - bd, p['fhip'] + p['fkn'] - bd, False)
    arm(-58, p['fsh'], p['fsh'] + p['fel'], False, o.get('prop_f'))
    leg(14, p['nhip'] - bd, p['nhip'] + p['nkn'] - bd, True)
    br = 1 + 0.02 * p['breathe']
    c.save(); c.scale(br, 1)
    shape(c, [(-70, -252), (-30, -270), (40, -270), (78, -252), (66, -200), (50, -120), (40, -46), (46, 0, 'c'), (-46, 0, 'c'), (-40, -46), (-48, -120), (-62, -200)], skin, lw)
    if long_:
        # 长希顿：随步伐摆动的下摆
        sw = (p['nhip'] - p['fhip']) * 60
        dress = [(-62, -250), (-24, -262), (36, -262), (70, -246), (56, -150), (46, -60), (62 + sw * 0.6, 120), (84 + sw, 384, 'c'), (-70 + sw * 0.4, 384, 'c'), (-58, 120), (-48, -60), (-56, -170)]
        if p.get('kneel'): dress = [(-62, -250), (-24, -262), (36, -262), (70, -246), (56, -150), (46, -60), (120, 60), (160, 190, 'c'), (-70, 190, 'c'), (-58, 60), (-48, -60), (-56, -170)]
        shape(c, dress, dcol, lw)
        c.save(); clip_shape(c, dress)
        for k in range(-5, 7): line(c, [(k * 14, -150), (k * 15 + sw * 0.3, 120), (k * 17 + sw * 0.8, 390)], dcol2, 2.2)
        if o.get('hem', True):
            hy = 352 if not p.get('kneel') else 160
            c.rectangle(-120, hy, 260, 36); c.set_source_rgb(*trim); c.fill()
            meander(c, -110, 150, hy + 6, 22, dcol, lw=2.2)
        # 腰带 + 上身折叠
        shape(c, [(-58, -140, 'c'), (58, -140, 'c'), (66, -90), (-60, -86)], dcol, lw * 0.8, t=0)
        line(c, [(-60, -88), (66, -92)], trim, 3)
        line(c, [(-50, -130), (52, -134)], o.get('belt', G['gold']), 6)
        c.restore()
        if o.get('himation'):   # 斜披外袍
            hm = [(-66, -250), (-20, -262), (20, -180), (70, -40), (76, 140), (20, 170), (-56, 140), (-66, -40)]
            shape(c, hm, o['himation'], lw)
            c.save(); clip_shape(c, hm)
            for k in range(6): line(c, [(-60 + k * 20, -240), (-30 + k * 22, 160)], o.get('himation2', dcol2), 2.2)
            c.restore()
            line(c, [(-56, 140), (20, 170), (76, 140)], trim, 4)
    else:
        tun = [(-62, -250), (-24, -262), (36, -262), (70, -246), (58, -150), (52, -40), (66, 150, 'c'), (-62, 150, 'c'), (-52, -40), (-56, -170)]
        shape(c, tun, dcol, lw)
        c.save(); clip_shape(c, tun)
        for k in range(-4, 6): line(c, [(k * 14, -60), (k * 17, 160)], dcol2, 2.2)
        c.rectangle(-100, 128, 200, 24); c.set_source_rgb(*trim); c.fill()
        c.restore()
        line(c, [(-54, -40), (54, -42)], o.get('belt', rgb('5a3a1e')), 6)
        if o.get('himation'):
            hm = [(-66, -250), (-20, -262), (30, -150), (66, 0), (60, 120), (-60, 100), (-60, -40)]
            shape(c, hm, o['himation'], lw)
    if o.get('aegis'):   # 雅典娜的神盾披肩
        ag = [(-64, -254), (-20, -266), (40, -266), (74, -248), (60, -190), (20, -168), (-30, -170), (-60, -196)]
        shape(c, ag, G['saff'], lw)
        c.save(); clip_shape(c, ag)
        for yy in range(-266, -160, 14):
            for xx in range(-70, 80, 16): c.new_path(); c.arc(xx + (yy // 14 % 2) * 8, yy, 8, 0, math.pi); c.set_source_rgb(*G['saff2']); c.set_line_width(1.6); c.stroke()
        c.restore()
        for k in range(9):
            a = math.pi * (0.05 + 0.9 * k / 8); sx_, sy_ = 6 + 64 * math.cos(a), -232 + 62 * math.sin(a)
            line(c, [(sx_, sy_), (sx_ + 6 * math.cos(a), sy_ + 14), (sx_ - 2, sy_ + 22)], G['green2'], 3)
        circ(c, 10, -214, 15, rgb('e8d0b0')); ring_stroke(c, 10, -214, 15, LINE, 2.4)
        circ(c, 6, -218, 2.5, LINE); circ(c, 14, -218, 2.5, LINE); line(c, [(4, -207), (16, -207)], LINE, 2)
    if o.get('necklace'): c.new_path(); c.arc(6, -268, 34, 0.15 * math.pi, 0.85 * math.pi); c.set_source_rgb(*G['gold']); c.set_line_width(5); c.stroke()
    if o.get('mark'): o['mark'](c)
    c.restore()
    shape(c, [(-14, -262), (-12, -300), (24, -300), (28, -262)], skin, lw)
    if o.get('rope'):   # 颈上绳
        line(c, [(-16, -282), (26, -284)], rgb('b49a6a'), 9)
    with J(c, 6, -296, p['head']) as ch:
        ch.scale(1.18, 1.18)
        hk = o.get('head_kind', kind if kind in ('gf', 'athena', 'nymph', 'old', 'arachne', 'gm') else 'gm')
        ho = head_g(ch, hk, look, dict(skin=skin, skin2=skin2, hair_c=o.get('hair_c', G['hair']), hair_c2=o.get('hair_c2', G['hair2']), beard=o.get('beard'), wreath=o.get('wreath'),
                                          crown=o.get('crown'), band=o.get('band', G['gold']), flower=o.get('flower', G['rose']), veil=o.get('veil', G['grey']), crest=o.get('crest', G['red']), crest2=o.get('crest2', G['red2']),
                                          hair_sway=o.get('hair_sway', 0.0)))
        m = ch.get_matrix()
        out['head'] = m.transform_point(10, -150); out['face'] = m.transform_point(50, -70); out['brow'] = m.transform_point(30, -112)
        if 'eye' in ho: out['eye'] = m.transform_point(*ho['eye'])
    arm(70, p['nsh'], p['nsh'] + p['nel'], True, o.get('prop_n'))
    c.restore()
    inv = c.get_matrix(); inv.invert()
    for k_, v_ in list(out.items()):
        if isinstance(v_, tuple) and len(v_) == 2: out[k_] = inv.transform_point(*v_)
    out['u'] = u
    return out

# ---------------- 道具（手部局部坐标：手心约 (0,50)，手指向 +y） ----------------
def spear(cc, L=900):
    line(cc, [(0, 50 - L * 0.55), (0, 50 + L * 0.45)], rgb('6a4a2a'), 10)
    shape(cc, [(-12, 50 - L * 0.55), (0, 50 - L * 0.55 - 90), (12, 50 - L * 0.55)], G['bronze'], 3)
def cane(cc):
    line(cc, [(0, 40), (0, 470)], rgb('6a4a2a'), 10); c_ = cc; c_.new_path(); c_.arc(-14, 40, 14, math.pi, 2 * math.pi); c_.set_source_rgb(*rgb('6a4a2a')); c_.set_line_width(10); c_.stroke()
def shuttle(cc, glow_=0.0):
    shape(cc, [(-6, 20), (6, 20), (12, 60), (6, 110, 'c'), (-6, 110, 'c'), (-12, 60)], rgb('d9b06a'), 2.4)
    line(cc, [(0, 40), (0, 90)], rgb('8a5a2e'), 2)
def owl(c, x, y, s, flap=0.0, eye=1.0, flip=False):
    c.save(); c.translate(x, y); c.scale(-s if flip else s, s)
    for sg in (-1, 1):
        a = flap * sg
        c.save(); c.rotate(a * 0.8)
        shape(c, [(0, -20), (sg * 60, -40 - 30 * abs(flap)), (sg * 90, -10), (sg * 50, 20), (0, 20)], rgb('7a6a54'), 2.6)
        for k in range(3): line(c, [(sg * (20 + k * 20), -10), (sg * (30 + k * 20), 12)], rgb('5a4a38'), 2)
        c.restore()
    shape(c, [(-30, -40), (-34, -64), (-14, -54), (14, -54), (34, -64), (30, -40), (34, 10), (16, 40), (-16, 40), (-34, 10)], rgb('8a7a62'), 2.8)
    for k in range(4): c.new_path(); c.arc(0, -10 + k * 10, 14, 0.3, math.pi - 0.3); c.set_source_rgb(*rgb('5a4a38')); c.set_line_width(1.6); c.stroke()
    for sx in (-12, 12):
        circ(c, sx, -38, 11, rgb('f0e0b0')); ring_stroke(c, sx, -38, 11, LINE, 2)
        if eye > 0.2: circ(c, sx, -38, 5, LINE)
        else: line(c, [(sx - 8, -38), (sx + 8, -38)], LINE, 2)
    shape(c, [(-4, -30), (4, -30), (0, -20)], G['saff'], 1.4)
    c.restore()

def loom(c, x, y, w, h, prog=1.0, cloth=None, t=0.0, weave_x=None, col=None):
    """希腊竖立式经线吊坠织机：(x,y)=左下地面点，cloth(c,x0,y0,w,h) 画已织部分"""
    wood = rgb('7a5230'); wood2 = rgb('5a3a1e')
    shape(c, [(x, y), (x + 18, y - h - 40), (x + 38, y - h - 40), (x + 26, y)], wood, 3, t=0)
    shape(c, [(x + w, y), (x + w - 18, y - h - 40), (x + w - 38, y - h - 40), (x + w - 26, y)], wood, 3, t=0)
    shape(c, [(x - 10, y - h - 10, 'c'), (x + w + 10, y - h - 10, 'c'), (x + w + 10, y - h + 14, 'c'), (x - 10, y - h + 14, 'c')], wood2, 3, t=0)
    top = y - h + 14; cx0 = x + 40; cx1 = x + w - 40
    ch = (y - 120 - top) * prog
    if cloth and ch > 2:
        c.save(); c.rectangle(cx0, top, cx1 - cx0, ch); c.clip(); cloth(c, cx0, top, cx1 - cx0, y - 120 - top); c.restore()
        c.rectangle(cx0, top, cx1 - cx0, ch); c.set_source_rgb(*LINE); c.set_line_width(2.4); c.stroke()
    n = int((cx1 - cx0) / 14)
    for i in range(n + 1):
        xx = cx0 + i * (cx1 - cx0) / n
        line(c, [(xx, top + ch), (xx + (i % 2 - 0.5) * 6, y - 60)], rgb('e8dcc0'), 1.4)
        if i % 2 == 0:
            wy = y - 50 + 4 * math.sin(t * 3 + i)
            shape(c, [(xx - 9, wy - 6, 'c'), (xx + 9, wy - 6, 'c'), (xx + 11, wy + 16, 'c'), (xx - 11, wy + 16, 'c')], rgb('a87850'), 1.6, t=0)
    line(c, [(cx0 - 10, top + ch + 4), (cx1 + 10, top + ch + 4)], wood, 7)
    if weave_x is not None:
        sx = cx0 + (cx1 - cx0) * weave_x
        shape(c, [(sx - 30, top + ch - 2), (sx + 30, top + ch - 2), (sx + 22, top + ch + 10), (sx - 22, top + ch + 10)], rgb('d9b06a'), 2)
        line(c, [(cx0, top + ch + 2), (sx, top + ch + 2)], col or G['red'], 3)
    return dict(top=top, cy=top + ch, x0=cx0, x1=cx1)

def spider(c, x, y, s, t=0.0, legs=1.0, body=1.0, col=None, glow_=0.0, eyes=True, wig=0.0):
    col = col or G['black']
    if glow_ > 0:
        g = cairo.RadialGradient(x, y, 1, x, y, 80 * s); g.add_color_stop_rgba(0, 0.85, 0.9, 1, 0.6 * glow_); g.add_color_stop_rgba(1, 0.85, 0.9, 1, 0); c.set_source(g); c.arc(x, y, 80 * s, 0, 7); c.fill()
    if legs > 0:
        for sg in (-1, 1):
            for k in range(4):
                a0 = (-0.9 + k * 0.55) + 0.12 * math.sin(t * 6 + k * 1.3 + sg) * wig
                L1 = 34 * s * legs; L2 = 40 * s * legs
                bx = x + sg * 10 * s; by = y + (k - 1.5) * 6 * s
                kx = bx + sg * L1 * math.cos(a0 - 0.7); ky = by + L1 * math.sin(a0 - 0.7) - 14 * s * legs
                fx = kx + sg * L2 * math.cos(a0 + 0.9); fy = ky + L2 * math.sin(a0 + 0.9)
                c.new_path(); c.move_to(bx, by); c.line_to(kx, ky); c.line_to(fx, fy); c.set_source_rgb(*col); c.set_line_width(max(1.5, 4 * s)); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()
                for j in range(3):   # 毛刺
                    u = 0.3 + j * 0.25; hx, hy = kx + (fx - kx) * u, ky + (fy - ky) * u
                    line(c, [(hx, hy), (hx + sg * 5 * s, hy - 4 * s)], col, max(1, 1.5 * s))
    if body > 0:
        circ(c, x, y + 20 * s * body, 22 * s * body, col); circ(c, x, y - 4 * s * body, 12 * s * body, col)
        c.new_path(); c.arc(x, y + 20 * s * body, 22 * s * body, 0, 7); c.set_source_rgba(*G['purple'], 0.5); c.set_line_width(2); c.stroke()
        if eyes:
            for ex in (-4, 4): circ(c, x + ex * s, y - 8 * s, 2.4 * s, rgb('d04a3a'))
        # 背上紫纹（她的紫色长裙）
        line(c, [(x, y + 6 * s), (x - 8 * s, y + 20 * s), (x, y + 34 * s), (x + 8 * s, y + 20 * s), (x, y + 6 * s)], G['purple'], max(1.5, 2.5 * s))

def web(c, cx, cy, R, a=1.0, n=14, rings=11, t=0.0, col=(0.9, 0.93, 1.0), lw=1.6, prog=1.0):
    if a <= 0: return
    c.set_line_width(lw)
    for i in range(n):
        ang = i * 2 * math.pi / n + 0.1
        c.new_path(); c.move_to(cx, cy); c.line_to(cx + R * math.cos(ang), cy + R * math.sin(ang)); c.set_source_rgba(*col, a * 0.8); c.stroke()
    nr = int(rings * prog)
    for j in range(1, nr + 1):
        r = R * j / (rings + 1)
        c.new_path()
        for i in range(n + 1):
            ang = i * 2 * math.pi / n + 0.1; rr = r * (0.94 + 0.06 * math.sin(i * 1.7 + j))
            px, py = cx + rr * math.cos(ang), cy + rr * math.sin(ang) + 0.02 * r * math.sin(t + j)
            c.line_to(px, py) if i else c.move_to(px, py)
        c.set_source_rgba(*col, a * (0.55 + 0.35 * math.sin(t * 2 + j) ** 2)); c.stroke()

# ---------------- 群像生成 ----------------
SKINS = [(G['skin'], G['skin2']), (G['pale'], G['pale2']), (G['dark'], G['dark2']), (rgb('d49a6a'), rgb('b88050'))]
DRESS = [(G['cream'], G['cream2']), (G['terra'], G['terra2']), (G['sea'], G['sea2']), (G['olive'], G['olive2']), (G['rose'], G['rose2']), (G['saff'], G['saff2']), (G['blue'], G['blue2']), (rgb('8a6a9a'), rgb('6a4a7a'))]
HAIRS = [(G['hair'], G['hair2']), (G['blond'], G['blond2']), (rgb('6a3a20'), rgb('8a5a34')), (rgb('3a2a20'), rgb('5a4434'))]

def make_crowd(seed, n, x0, x1, ys, hs, kinds=('gf', 'gm', 'nymph'), flip_to=None):
    r = np.random.default_rng(seed); people = []
    for i in range(n):
        layer = int(r.integers(0, len(ys)))
        kd = kinds[int(r.integers(0, len(kinds)))]
        sk = SKINS[int(r.integers(0, len(SKINS)))]; dr = DRESS[int(r.integers(0, len(DRESS)))]; hr = HAIRS[int(r.integers(0, len(HAIRS)))]
        x = r.uniform(x0, x1)
        fl = (x > flip_to) if flip_to is not None else bool(r.integers(0, 2))
        people.append(dict(x=x, layer=layer, y=ys[layer] + r.uniform(-8, 8), h=hs[layer] * r.uniform(0.88, 1.06), kind=kd, skin=sk, dress=dr, hair=hr,
                           flip=fl, ph=r.uniform(0, 6.3), act=r.choice(['cheer', 'clap', 'sway', 'point', 'whisper', 'watch']), beard=bool(r.integers(0, 3) == 0),
                           himation=DRESS[int(r.integers(0, len(DRESS)))][0] if r.integers(0, 3) == 0 else None, child=bool(r.integers(0, 6) == 0)))
    people.sort(key=lambda p: -p['layer'])
    return people

def crowd_pose(p, t, mood):
    ph = p['ph']; act = p['act'] if mood == 'normal' else mood
    if act == 'cheer': a = 0.5 + 0.5 * math.sin(t * 6 + ph); return P_(nsh=2.6 + 0.3 * a, nel=0.2, fsh=2.4 + 0.3 * a, fel=0.3, bob=-8 * a, head=-0.1), dict(mouth='open', happy=True)
    if act == 'clap': a = abs(math.sin(t * 7 + ph)); return P_(nsh=0.8, nel=0.8 + 0.35 * a, fsh=0.7, fel=0.9 + 0.3 * a), dict(mouth='smile')
    if act == 'sway': return P_(body=0.05 * math.sin(t * 2 + ph), head=0.06 * math.sin(t * 2 + ph + 1), nsh=0.2, fsh=-0.1), dict(mouth='smile')
    if act == 'point': return P_(nsh=1.5 + 0.1 * math.sin(t * 3 + ph), nel=0.05, head=-0.15), dict(mouth='O')
    if act == 'whisper': return P_(head=0.25 + 0.05 * math.sin(t * 5 + ph), nsh=0.6, nel=2.2, body=-0.08), dict(mouth='smile' if int(t * 2 + ph) % 2 else 'n')
    if act == 'gasp': return P_(nsh=0.5, nel=2.4, fsh=0.3, fel=0.5, head=-0.12, body=0.06), dict(mouth='O', eye=1.0, brow=0.5)
    if act == 'kneel': return dict(P_(nsh=1.2, nel=0.4, fsh=1.1, fel=0.5, head=0.3, body=-0.3, nhip=0.25, nkn=-1.85, fhip=0.15, fkn=-1.75, bob=135), kneel=True), dict(mouth='n', eye=0.0)
    if act == 'fear': return P_(nsh=1.0, nel=1.8, fsh=0.9, fel=1.9, body=0.08 + 0.02 * math.sin(t * 30 + ph), head=-0.1), dict(mouth='O', brow=0.8, sweat=1, sweat_ph=t + ph)
    if act == 'giggle': return P_(nsh=0.5, nel=2.4, body=0.06 * math.sin(t * 9 + ph), head=0.1), dict(mouth='grin', happy=True)
    if act == 'silent': return P_(head=0.05), dict(mouth='tight', eye=1.0)
    return P_(head=0.04 * math.sin(t + ph)), dict(mouth='n')

def draw_crowd(c, people, t, mood='normal', ydim=None, mood_fn=None):
    for p in people:
        md = mood_fn(p) if mood_fn else mood
        pose, face = crowd_pose(p, t, md)
        face.setdefault('eye', blink(t, int(p['ph'] * 10)))
        face['look'] = face.get('look', 0.2)
        h = p['h'] * (0.72 if p['child'] else 1.0)
        kd = p['kind']
        kw = dict(skin=p['skin'][0], skin2=p['skin'][1], dress=p['dress'][0], dress2=p['dress'][1], hair_c=p['hair'][0], hair_c2=p['hair'][1], flip=p['flip'],
                  himation=p['himation'], beard=(p['beard'] and kd == 'gm' and not p['child']), hair_sway=math.sin(t * 2 + p['ph']) * 0.5)
        if kd == 'nymph': kw['flower'] = [G['rose'], G['white'], G['saff'], rgb('9a7ac8')][int(p['ph'] * 10) % 4]
        fig(c, p['x'], p['y'], h, pose, face, kind=kd, **kw)
        if ydim is not None and p['layer'] > 0:
            pass

# ---------------- 动物（陶瓶画风） ----------------
def bull(c, x, y, s, t=0.0, col=None, flip=False):
    col = col or G['white']
    c.save(); c.translate(x, y); c.scale(-s if flip else s, s)
    for k, (lx, ph) in enumerate(((-90, 0), (-60, 3.1), (70, 1.5), (100, 4.6))):
        a = 0.35 * math.sin(t * 5 + ph)
        with J(c, lx, -10, a) as cl: shape(cl, taper(110, 14, 9), col if k % 2 else tuple(v * 0.88 for v in col), 3)
    body = [(-130, -40), (-100, -90), (40, -96), (110, -110), (150, -90), (130, -20), (60, 10), (-100, 10), (-140, -10)]
    shape(c, body, col, 3.4)
    shape(c, [(110, -110), (150, -150), (196, -140), (214, -110), (200, -90), (160, -80)], col, 3.2)
    for sg in (0, 1): line(c, [(150 + sg * 14, -150), (140 + sg * 20, -186), (170 + sg * 20, -196)], G['gold'], 6)
    circ(c, 184, -126, 4, LINE)
    line(c, [(-130, -40), (-170, -10), (-176, 40)], col, 6); circ(c, -176, 44, 8, LINE)
    for k in range(5): circ(c, -60 + k * 30, -50 + (k % 2) * 16, 6, G['gold2'], 0.6)
    c.restore()
def swan(c, x, y, s, t=0.0, flap=0.0, flip=False):
    c.save(); c.translate(x, y); c.scale(-s if flip else s, s)
    wa = 0.5 + 0.5 * math.sin(t * 4) if flap else 0.2
    shape(c, [(-20, -30), (-120, -120 - 60 * wa), (-180, -60 - 50 * wa), (-90, -10)], G['white'], 3)
    for k in range(4): line(c, [(-40 - k * 30, -30 - k * 10), (-70 - k * 30, -80 - k * 20 - 40 * wa)], G['cream2'], 2)
    shape(c, [(-90, 0), (-40, -40), (40, -40), (90, -20), (60, 20), (-60, 24)], G['white'], 3.2)
    line(c, [(60, -30), (80, -90), (70, -150), (90, -170)], G['white'], 18); line(c, [(60, -30), (80, -90), (70, -150), (90, -170)], LINE, 2)
    shape(c, [(88, -178), (118, -168), (90, -160)], G['saff'], 2)
    circ(c, 86, -172, 3, LINE)
    c.restore()
def horse(c, x, y, s, t=0.0, col=None):
    col = col or G['grey']
    c.save(); c.translate(x, y); c.scale(s, s)
    for k, (lx, ph) in enumerate(((-80, 0), (-60, 2), (70, 1), (90, 3))):
        with J(c, lx, -10, 0.3 * math.sin(t * 4 + ph)) as cl: shape(cl, taper(120, 12, 8), col, 3)
    shape(c, [(-110, -40), (-80, -90), (60, -96), (120, -120), (170, -180), (200, -170), (210, -140), (170, -120), (130, -40), (60, 0), (-100, 0)], col, 3.2)
    line(c, [(120, -120), (150, -170), (180, -190)], G['black'], 10)
    line(c, [(-110, -40), (-150, 0), (-150, 60)], G['black'], 8)
    c.restore()
def olive_tree(c, x, y, s, t=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    shape(c, [(-14, 0), (-10, -120), (-40, -200), (-20, -206), (0, -150), (20, -210), (40, -200), (12, -120), (14, 0)], rgb('6a4a2a'), 3)
    r = np.random.default_rng(4)
    for k in range(40):
        a = r.uniform(0, 2 * math.pi); rr = r.uniform(20, 110); lx, ly = rr * math.cos(a), -240 + rr * 0.6 * math.sin(a)
        c.save(); c.translate(lx, ly); c.rotate(a + 0.2 * math.sin(t + k)); shape(c, [(-14, 0), (0, -5), (14, 0), (0, 5)], G['olive'] if k % 2 else G['olive2'], 1.4); c.restore()
    for k in range(8): circ(c, r.uniform(-90, 90), -240 + r.uniform(-50, 50), 5, G['black'])
    c.restore()

def spear_w(c, hx, hy, h, a=0.0):
    """世界坐标长矛：过手点，竖直（a 倾角），h=人物高"""
    L = h * 1.25; ux, uy = math.sin(a), -math.cos(a)
    x0, y0 = hx - ux * L * 0.35, hy - uy * L * 0.35; x1, y1 = hx + ux * L * 0.65, hy + uy * L * 0.65
    line(c, [(x0, y0), (x1, y1)], rgb('6a4a2a'), max(3, h * 0.012))
    s = h / 800
    c.save(); c.translate(x1, y1); c.rotate(a); shape(c, [(-12 * s, 0), (0, -90 * s), (12 * s, 0)], G['bronze'], 2.6); c.restore()
    return (x1, y1)
def cane_w(c, hx, hy, gy, h):
    line(c, [(hx, hy - h * 0.02), (hx + h * 0.02, gy)], rgb('6a4a2a'), max(3, h * 0.014))
    c.new_path(); c.arc(hx - h * 0.02, hy - h * 0.02, h * 0.02, math.pi, 2 * math.pi); c.set_source_rgb(*rgb('6a4a2a')); c.set_line_width(max(3, h * 0.014)); c.stroke()
