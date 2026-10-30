# 水运浑天 三维模型（代码建模）
import math, numpy as np, vtk
from g3d import *

TILT = -56          # 极轴倾角（长安纬度约34°）
AXIS = (0, math.cos(math.radians(34)), math.sin(math.radians(34)))
ZB0, ZTOP = -1.6, 0.07   # 柜体底、地平板顶
HALF = 1.8

def sq(t, h=HALF): return h / max(abs(math.cos(t)), abs(math.sin(t)))

def rng(seed): return np.random.default_rng(seed)

def star_field():
    r = rng(7); pts = []
    v = r.normal(size=(240, 3)); v /= np.linalg.norm(v, axis=1)[:, None]
    stars = [sphere(0.011 + 0.008 * r.random(), 8) for _ in range(1)]
    spheres = []
    for p in v * 1.006:
        s = 0.009 + 0.010 * r.random()
        spheres.append(xform(sphere(s, 8), T(('t', *p))))
    # 星官连线：28 组
    lines = []
    for k in range(28):
        th = 2 * np.pi * k / 28 + r.normal() * 0.04; ph = r.uniform(-0.45, 0.45)
        c = np.array([math.cos(ph) * math.cos(th), math.cos(ph) * math.sin(th), math.sin(ph)])
        n = r.integers(3, 6); chain = [c]
        for i in range(n):
            d = r.normal(size=3) * 0.11; q = chain[-1] + d; q /= np.linalg.norm(q); chain.append(q)
        for q in chain: spheres.append(xform(sphere(0.016, 10), T(('t', *(q * 1.008)))))
        seg = []
        for a, b in zip(chain[:-1], chain[1:]):
            for u in np.linspace(0, 1, 6):
                m = a * (1 - u) + b * u; seg.append(m / np.linalg.norm(m) * 1.004)
        lines.append(tube(seg, 0.0035, 6))
    return merge(*spheres), merge(*lines)

def figure(robe='robe_r'):
    """木人（局部坐标：面朝 +x，脚在原点）。返回 [(pd,mat)], 肩部坐标"""
    parts = []
    parts.append((cyl(0.15, 0.05), 'wood'))
    parts.append((xform(cone(0.15, 0.07, 0.36), T(('t', 0, 0, 0.05))), robe))
    parts.append((xform(cyl(0.085, 0.04), T(('t', 0, 0, 0.40))), robe))         # 领
    parts.append((xform(cyl(0.03, 0.05), T(('t', 0, 0, 0.42))), 'skin'))
    parts.append((xform(sphere(0.066, 32), T(('s', 0.92, 0.95, 1.08), ('t', 0, 0, 0.51))), 'skin'))
    # 幞头
    parts.append((xform(sphere(0.07, 24), T(('s', 1.0, 1.0, 0.75), ('t', -0.008, 0, 0.555))), 'black'))
    parts.append((xform(cyl(0.035, 0.06), T(('t', -0.02, 0, 0.57))), 'black'))
    for sgn in (-1, 1):
        parts.append((xform(box(-0.012, 0.012, -0.012, 0.012, -0.11, 0), T(('rx', sgn * 18), ('t', -0.07, sgn * 0.03, 0.56))), 'black'))
    # 眼（两点）
    for sgn in (-1, 1):
        parts.append((xform(sphere(0.008, 8), T(('t', 0.058, sgn * 0.022, 0.52))), 'black'))
    # 腰带
    parts.append((xform(cyl(0.118, 0.025), T(('t', 0, 0, 0.27))), 'gold'))
    return parts, (0.02, -0.09, 0.39)

def arm(tool='mallet'):
    """手臂局部：肩在原点，指向 +x"""
    p = [(tube([(0, 0, 0), (0.12, 0, -0.03), (0.22, 0, 0)], 0.028), 'robe_r'),
         (xform(sphere(0.026, 12), T(('t', 0.23, 0, 0))), 'skin')]
    if tool == 'mallet':
        p.append((tube([(0.23, 0, 0), (0.42, 0, 0.0)], 0.009), 'wood_l'))
        p.append((xform(sphere(0.035, 16), T(('t', 0.43, 0, 0))), 'lacquer'))
    else:  # 撞木
        p.append((tube([(0.20, -0.0, 0), (0.46, 0, 0)], 0.022), 'wood_l'))
    return p

def drum():
    p = [(xform(cyl(0.13, 0.17, 48), T(('t', 0, 0, -0.085), ('ry', 90))), 'lacquer')]
    for sx in (-0.088, 0.088):
        p.append((xform(cyl(0.122, 0.006, 48), T(('t', 0, 0, -0.003), ('ry', 90), ('t', sx, 0, 0))), 'drum'))
        p.append((xform(torus(0.125, 0.008, 48, 8), T(('ry', 90), ('t', sx * 0.98, 0, 0))), 'gold'))
    # 架
    for sy in (-0.15, 0.15):
        p.append((box(-0.015, 0.015, sy - 0.015, sy + 0.015, -0.32, 0.02), 'wood'))
    p.append((box(-0.015, 0.015, -0.15, 0.15, -0.02, 0.0), 'wood'))
    p.append((box(-0.08, 0.08, -0.2, 0.2, -0.33, -0.31), 'wood'))
    return p

def bell():
    prof = [(0.0, 0.0), (0.03, 0.0), (0.06, -0.02), (0.075, -0.08), (0.085, -0.17), (0.105, -0.22), (0.1, -0.225), (0.0, -0.225)]
    p = [(xform(lathe(prof, 48), T(('t', 0, 0, 0.12))), 'bronze')]
    p.append((xform(torus(0.03, 0.008, 24, 8), T(('rx', 90), ('t', 0, 0, 0.14))), 'bronze'))
    for sy in (-0.17, 0.17):
        p.append((box(-0.016, 0.016, sy - 0.016, sy + 0.016, -0.42, 0.18), 'wood'))
    p.append((box(-0.018, 0.018, -0.2, 0.2, 0.16, 0.19), 'lacquer'))
    p.append((box(-0.08, 0.08, -0.22, 0.22, -0.43, -0.41), 'wood'))
    return p

class Device:
    def __init__(self, S):
        self.S = S; A = self.A = {}
        def add(name, pd, mat, **k):
            a = actor(pd, mat, **k); S.add(a); A.setdefault(name, []).append(a); return a
        self.add = add
        # ---- 天（随天旋转的部分）----
        add('sky', sphere(1.0, 128), 'bronze')
        st, ln = star_field()
        add('sky', st, 'gold', emit=(2.2, 1.7, 0.9))
        add('sky', ln, 'gold')
        add('sky', torus(1.006, 0.007, 200, 8), 'gold')                                       # 赤道
        add('sky', xform(torus(1.006, 0.005, 200, 8), T(('rx', 24))), 'gold')                 # 黄道刻线
        for k in range(12):                                                                    # 经线
            add('sky', xform(torus(1.004, 0.003, 160, 6), T(('rx', 90), ('rz', k * 15))), 'bronze2')
        add('sky', xform(cyl(0.035, 3.1), T(('t', 0, 0, -1.55))), 'iron')                    # 极轴
        # 日环、月环
        self.RS, self.RM = 1.15, 1.23
        self.sun_ring = xform(ring_solid(self.RS - 0.02, self.RS + 0.02, -0.012, 0.012, 240), T(('rx', 24)))
        self.moon_ring = xform(ring_solid(self.RM - 0.02, self.RM + 0.02, -0.012, 0.012, 240), T(('rx', 29), ('rz', 40)))
        add('sunring', self.sun_ring, 'gold'); add('moonring', self.moon_ring, 'iron')
        self.sun = add('sun', sphere(0.075, 40), 'gold', emit=(3.0, 1.4, 0.4))
        self.sun_glow = add('sun', sphere(0.11, 32), dict(col=(1, 0.6, 0.2), metal=0, rough=1, op=0.25), emit=(2.0, 0.9, 0.2))
        self.moon = add('moon', sphere(0.06, 40), dict(col=(0.85, 0.88, 0.95), metal=0.0, rough=0.5), emit=(0.6, 0.65, 0.8))
        # ---- 固定框架 ----
        add('frame', xform(ring_solid(1.38, 1.48, -0.045, 0.045, 240), T(('ry', 90))), 'bronze2')   # 子午环
        for k in range(36):
            ang = k * 10
            add('frame', xform(box(-0.05, 0.05, 1.44, 1.485, -0.006, 0.006), T(('ry', 90), ('rx', ang))), 'gold')
        # ---- 木柜地平 ----
        self.cab = []
        self.cab.append(add('cab', box(-HALF + 0.03, HALF - 0.03, -HALF + 0.03, HALF - 0.03, ZB0, -0.03), 'wood'))
        self.cab.append(add('cab', ring_solid(1.045, sq, -0.03, ZTOP, 256), 'lacquer'))
        # 地平刻度圈
        add('cabtop', xform(ring_solid(1.06, 1.16, ZTOP, ZTOP + 0.012, 200), T()), 'gold')
        for k in range(24):
            add('cabtop', xform(box(1.17, 1.3, -0.006, 0.006, ZTOP, ZTOP + 0.01), T(('rz', k * 15))), 'gold')
        # 金边与腿
        e = HALF
        for (x0, x1, y0, y1) in [(-e, e, -e - 0.01, -e + 0.03), (-e, e, e - 0.03, e + 0.01), (-e - 0.01, -e + 0.03, -e, e), (e - 0.03, e + 0.01, -e, e)]:
            self.cab.append(add('cab', box(x0, x1, y0, y1, ZTOP, ZTOP + 0.035), 'gold'))
        for sx in (-1, 1):
            for sy in (-1, 1):
                self.cab.append(add('cab', box(sx * e - 0.08, sx * e + 0.08, sy * e - 0.08, sy * e + 0.08, ZB0, ZTOP), 'lacquer'))
                self.cab.append(add('cab', box(sx * (e - 0.12) - 0.1, sx * (e - 0.12) + 0.1, sy * (e - 0.12) - 0.1, sy * (e - 0.12) + 0.1, ZB0 - 0.18, ZB0), 'wood'))
        # 柜面装饰框
        for face in range(4):
            for (a0, a1, z0, z1) in [(-1.45, -0.1, -1.42, -0.25), (0.1, 1.45, -1.42, -0.25)]:
                pts = [(a0, -e - 0.012, z0), (a1, -e - 0.012, z0), (a1, -e - 0.012, z1), (a0, -e - 0.012, z1), (a0, -e - 0.012, z0)]
                self.cab.append(add('cab', xform(tube(pts, 0.012, 8), T(('rz', face * 90))), 'gold'))
        add('base', box(-2.4, 3.2, -2.2, 2.2, ZB0 - 0.36, ZB0 - 0.18), 'stone')
        # ---- 木人与钟鼓 ----
        self.figs = []
        for side, tool in ((-1, 'mallet'), (1, 'bar')):
            px, py = side * 1.32, -1.25
            yaw = 0 if side < 0 else 180
            parts, sh = figure('robe_r' if side < 0 else 'robe_g')
            base = T(('rz', yaw), ('t', px, py, ZTOP + 0.035))
            for pd, m in parts: add('fig', pd, m, xf=base)
            arms = []
            for pd, m in arm(tool):
                if m == 'robe_r' and side > 0: m = 'robe_g'
                arms.append(add('arm', pd, m))
            self.figs.append(dict(px=px, py=py, yaw=yaw, sh=sh, arms=arms))
            if side < 0:
                for pd, m in drum(): add('drum', pd, m, xf=T(('t', px + 0.5, py, ZTOP + 0.035 + 0.36)))
                self.drum_pos = (px + 0.5 - 0.09, py, ZTOP + 0.035 + 0.36)
            else:
                for pd, m in bell(): add('bell', pd, m, xf=T(('t', px - 0.52, py, ZTOP + 0.035 + 0.42)))
                self.bell_pos = (px - 0.52 + 0.08, py, ZTOP + 0.035 + 0.42 - 0.07)
        # ---- 水力 ----
        self.WX, self.WZ, self.WR = 2.3, -1.15, 0.6
        wheel = []
        wheel.append(xform(ring_solid(self.WR - 0.05, self.WR, -0.06, 0.06, 160), T(('ry', 90))))
        wheel.append(xform(ring_solid(0.07, 0.12, -0.08, 0.08, 48), T(('ry', 90))))
        for k in range(8):
            wheel.append(xform(box(-0.02, 0.02, -0.025, 0.025, 0.1, self.WR - 0.04), T(('rx', k * 45))))
        for k in range(16):
            wheel.append(xform(box(-0.08, 0.08, -0.07, 0.03, self.WR - 0.02, self.WR + 0.1), T(('rx', k * 22.5))))
        self.wheel_pd = merge(*wheel)
        self.wheel = add('wheel', self.wheel_pd, 'wood_l')
        add('shaft', xform(cyl(0.04, self.WX - 0.6 + 0.1), T(('ry', 90), ('t', 0.6, 0, self.WZ))), 'iron')
        # 水柜、水槽、承水池
        add('tank', box(1.95, 2.65, 0.25, 0.95, -0.15, 0.45), 'wood')
        add('tank', box(1.98, 2.62, 0.28, 0.92, 0.36, 0.42), 'water')
        for sx in (2.0, 2.6):
            for sy in (0.3, 0.9):
                add('tank', box(sx - 0.03, sx + 0.03, sy - 0.03, sy + 0.03, ZB0 - 0.18, -0.15), 'wood')
        add('tank', tube([(2.3, 0.3, -0.05), (2.3, 0.22, -0.12), (2.3, 0.4, -0.28)], 0.03), 'bronze2')
        add('pool', box(1.95, 2.65, -0.8, 0.8, ZB0 - 0.18, ZB0 + 0.05), 'wood')
        add('pool', box(1.98, 2.62, -0.77, 0.77, ZB0 - 0.1, ZB0 + 0.0), 'water')
        self.drops = []
        for i in range(14):
            self.drops.append(add('water', sphere(0.028, 12), 'water'))
        self.stream = add('water', tube([(2.3, 0.4, -0.3), (2.3, 0.4, -0.7)], 0.022, 10), 'water')
        # ---- 柜内齿轮（X光可见）----
        G = []
        G.append(('g1', gear(0.3, 24, 0.05, -0.05, 0.05, 0.04), T(('ry', 90), ('t', 1.0, 0, self.WZ)), (1, 0, 0), (1.0, 0, self.WZ)))
        G.append(('g2', gear(0.3, 24, 0.05, -1.51, -1.45, 0.04), T(('t', 0.7, 0, 0)), (0, 0, 1), (0.7, 0, 0)))
        G.append(('g3', gear(0.15, 12, 0.045, -1.18, -1.12, 0.03), T(('t', 0.7, 0, 0)), (0, 0, 1), (0.7, 0, 0)))
        G.append(('g4', gear(0.55, 44, 0.05, -1.18, -1.12, 0.05), T(), (0, 0, 1), (0, 0, 0)))
        G.append(('g5', gear(0.2, 16, 0.045, -1.18, -1.12, 0.03), T(('t', 0, -0.75, 0)), (0, 0, 1), (0, -0.75, 0)))
        self.gears = []
        for name, pd, base, ax, ctr in G:
            a = add('gear', pd, 'bronze', emit=None)
            self.gears.append((a, base, ax, ctr, name))
        add('gear', xform(cyl(0.025, 0.42), T(('t', 0.7, 0, -1.51))), 'iron')
        add('gear', xform(cyl(0.03, 0.2), T(('t', 0, 0, -1.2))), 'iron')
        # 钩键杆
        for side in (-1, 1):
            px = side * 1.32
            add('gear', tube([(0, -0.75, -1.15), (px * 0.6, -1.0, -1.15), (px, -1.25, -1.15), (px, -1.25, -0.05)], 0.018, 8), 'iron')
            add('gear', xform(cyl(0.05, 0.08), T(('t', px, -1.25, -0.6))), 'gold')
        # ---- 围观百官（武成殿前）----
        self.crowd = []
        r_ = np.random.default_rng(5)
        for i in range(11):
            ang = math.radians(-150 + i * 12)
            R = 3.4 + 0.25 * (i % 2)
            px, py = R * math.cos(ang) + 0.3, R * math.sin(ang)
            yaw = math.degrees(math.atan2(-py, 0.3 - px))
            parts, sh = figure('robe_r' if i % 3 == 0 else ('robe_g' if i % 3 == 1 else dict(col=(0.20, 0.22, 0.45), metal=0, rough=0.7)))
            base = T(('s', 1.7), ('rz', yaw), ('t', px, py, ZB0 - 0.36))
            for pd, m in parts: self.crowd.append(add('crowd', pd, m, xf=base))
        self.show_crowd(False)
        self.xray(False)

    def show_crowd(self, on):
        for a in self.crowd: a.SetVisibility(on)

    # ---- 状态 ----
    def xray(self, on, cab_op=0.13):
        for a in self.A['cab']: a.GetProperty().SetOpacity(cab_op if on else 1.0)
        for a, *_ in self.gears:
            a.GetProperty().SetEmissiveFactor(*((0.5, 0.35, 0.12) if on else (0, 0, 0)))

    def patina(self, k):
        for key in ('sky', 'frame', 'gear', 'bell', 'sunring'):
            for a in self.A.get(key, []):
                p = a.GetProperty()
                if p.GetOpacity() < 1: continue
                if not hasattr(a, '_c0'): a._c0 = p.GetColor(); a._m0 = p.GetMetallic(); a._r0 = p.GetRoughness()
                c0 = np.array(a._c0); pc = np.array(MAT['patina']['col'])
                if a._m0 > 0.5:
                    p.SetColor(*(c0 * (1 - k) + pc * k)); p.SetMetallic(a._m0 * (1 - k) + 0.35 * k); p.SetRoughness(a._r0 * (1 - k) + 0.8 * k)
        for a in self.A['sun'] + self.A['moon']:
            a.SetVisibility(True)

    def pose(self, sky=0.0, sun=30.0, moon=140.0, wheel=0.0, arm_l=20.0, arm_r=0.0, water=True, t=0.0):
        self._sky = sky
        sky_t = T(('rz', sky), ('rx', TILT))
        for key in ('sky', 'sunring', 'moonring'):
            for a in self.A[key]: a.SetUserTransform(sky_t)
        def ring_pt(R, rx, rz, ang):
            m = vtk.vtkTransform(); m.PostMultiply(); m.RotateX(rx); m.RotateZ(rz); m.RotateZ(sky); m.RotateX(TILT)
            return m.TransformPoint(R * math.cos(math.radians(ang)), R * math.sin(math.radians(ang)), 0)
        ps = ring_pt(self.RS, 24, 0, sun); pm = ring_pt(self.RM, 29, 40, moon)
        for a in self.A['sun']: a.SetUserTransform(T(('t', *ps)))
        for a in self.A['moon']: a.SetUserTransform(T(('t', *pm)))
        self.sun_p, self.moon_p = ps, pm
        self.wheel.SetUserTransform(T(('rx', wheel), ('t', self.WX, 0, self.WZ)))
        ratios = {'g1': 1, 'g2': -1, 'g3': -1, 'g4': 12 / 44, 'g5': -12 / 44 * 44 / 16}
        for a, base, ax, ctr, name in self.gears:
            ang = wheel * ratios[name]
            m = vtk.vtkTransform(); m.PostMultiply(); m.Concatenate(base); m.Translate(-ctr[0], -ctr[1], -ctr[2]); m.RotateWXYZ(ang, *ax); m.Translate(*ctr)
            a.SetUserTransform(m)
        for f, ang in zip(self.figs, (arm_l, arm_r)):
            sx, sy, sz = f['sh']
            for a in f['arms']:
                a.SetUserTransform(T(('ry', -ang), ('t', sx, sy if f['yaw'] == 0 else -sy, sz), ('rz', f['yaw']), ('t', f['px'], f['py'], ZTOP + 0.035)))
        for i, d in enumerate(self.drops):
            u = ((t * 1.6 + i / len(self.drops)) % 1.0)
            d.SetUserTransform(T(('t', 2.3, 0.4 + 0.02 * math.sin(i * 7), -0.3 - 0.42 * u)))
            d.SetVisibility(water)
        self.stream.SetVisibility(water)
