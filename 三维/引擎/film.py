import sys, os, math, json, time
import numpy as np
from PIL import Image, ImageDraw
from g3d import *
from model import Device, ZB0, ZTOP
import comp as C

FPS = 24
def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t

# ---------------- 镜头表 ----------------
V = dict(
    WIDE=dict(f=(0.3, 0, -0.4), d=10.8, el=22, az=-52, fov=32),
    GLOBE=dict(f=(0, 0, 0.25), d=5.4, el=26, az=-62, fov=32),
    FIG=dict(f=(0, -1.1, 0.3), d=3.6, el=11, az=-90, fov=40),
    WHEEL=dict(f=(2.3, 0.15, -0.85), d=3.8, el=12, az=-28, fov=34),
    XRAY=dict(f=(0.9, 0, -0.6), d=9.3, el=13, az=-50, fov=36),
    RINGS=dict(f=(0.3, 0, 0.05), d=6.4, el=34, az=-57, fov=34),
    TOP=dict(f=(0, 0, 0), d=6.0, el=62, az=-80, fov=34),
)
def cam(view, **k):
    c = dict(V[view]); c.update(k); return c

TAG = '唐 · 开元十三年（725）'
SH = [
 dict(k='hook1', sub='公元725年，长安的宫殿前|摆出了一台〖会自己动〗的机器', a=cam('WIDE', az=-75, d=13), b=cam('WIDE', az=-55, d=11), mood='warm'),
 dict(k='hook2', sub='没人推它|铜球上的〖整片星空〗却在缓缓转动', a=cam('GLOBE', az=-80, el=18), b=cam('GLOBE', az=-55, el=24, d=4.8), skyspd=14),
 dict(k='hook3', sub='到了时辰|两个小〖木人〗还会自己敲鼓、撞钟', a=cam('FIG', d=4.2), b=cam('FIG', d=3.5, el=8), strikes=[('L', 1.4), ('R', 2.6), ('L', 3.6)]),
 dict(k='title', sub='', a=cam('WIDE', az=-40, f=(-1.9, 0.9, -0.55), d=12, el=25), b=cam('WIDE', az=-48, f=(-1.9, 0.9, -0.55), d=11.4, el=25), dur=5.2),
 dict(k='eclipse', sub='事情起因是：唐朝的旧历法|【日食老是算不准】', a=cam('RINGS', az=-30, d=5), b=cam('RINGS', az=-38, d=4.6), mood='night', tag='开元九年（721）', src='《旧唐书·天文志》：太史频奏日蚀不效'),
 dict(k='yixing', sub='唐玄宗请来僧人〖一行〗|让他重修一部新历法', a=cam('GLOBE', az=-120, el=20), b=cam('GLOBE', az=-100, el=22), tag='开元九年（721）'),
 dict(k='liang', sub='要修历，先得把天看准|小官〖梁令瓒〗先削出一台木头样机', a=cam('GLOBE', az=-20, el=30, d=5.8), b=cam('GLOBE', az=-35, el=26, d=5.2), tag='开元年间'),
 dict(k='youyi', sub='两人先铸成〖黄道游仪〗测星|又接着造了这台浑天铜仪', a=cam('TOP', az=-60), b=cam('TOP', az=-80, el=55), tag='开元十一年（723）'),
 dict(k='layers', sub='它分三层：上面是〖天〗|中间是〖地〗，下面藏着〖动力〗', a=cam('WIDE', az=-35, d=11.5), b=cam('WIDE', az=-50, d=10.8)),
 dict(k='globe', sub='铜铸的圆球就是天|刻满了〖星宿〗、〖赤道〗和周天度数', a=cam('GLOBE', az=-70, d=4.4, el=20), b=cam('GLOBE', az=-45, d=4.0, el=24), skyspd=10),
 dict(k='horizon', sub='木柜就是地平面|球〖一半在上，一半在下〗', a=cam('WIDE', az=-90, el=6, d=9, f=(0, 0, -0.3)), b=cam('WIDE', az=-90, el=12, d=8.2, f=(0, 0, -0.3)), xray=True, cab_op=0.35),
 dict(k='water', sub='动力来自〖水〗：水从高处落进斗里|推着水轮一格一格地转', a=cam('WHEEL', az=-15, d=4.2), b=cam('WHEEL', az=-35, d=3.6), water_sfx=True),
 dict(k='gears', sub='水轮带动柜里的〖轮轴〗|再由齿轮一级一级地〖减速〗', a=cam('XRAY', az=-40, d=8.0, f=(1.0, 0, -1.0)), b=cam('XRAY', az=-58, d=7.2, f=(0.8, 0, -1.0)), xray=True, wheelspd=60),
 dict(k='day', sub='最后让天球〖一昼夜正好转一圈〗|和天上的星星同步', a=cam('GLOBE', az=-60, d=5.6), b=cam('GLOBE', az=-40, d=5.2), skyspd=55),
 dict(k='rings', sub='天外还套着〖两道环〗|一道挂太阳，一道挂「月亮」', a=cam('RINGS', az=-75), b=cam('RINGS', az=-50, d=6.0), mood='night'),
 dict(k='sun', sub='天每转一圈，太阳往东挪〖1度〗|转满〖365圈〗，太阳走完一周', a=cam('RINGS', az=-40, d=5.6), b=cam('RINGS', az=-30, d=5.6), mood='night', skyspd=0, sunspd=40),
 dict(k='moon', sub='月亮每天挪「13又7/19度」|转「29圈多」，日月相会一次', a=cam('RINGS', az=-30, d=5.6), b=cam('RINGS', az=-20, d=5.8), mood='night', skyspd=0, moonspd=70),
 dict(k='drum', sub='地平上的两个木人，一个管〖鼓〗|每〖一刻〗敲一下，一昼夜一百刻', a=cam('FIG', az=-120, d=2.6, f=(-1.0, -1.2, 0.35)), b=cam('FIG', az=-105, d=2.4, f=(-1.0, -1.2, 0.35)), strikes=[('L', 1.5), ('L', 3.3)]),
 dict(k='bell', sub='一个管〖钟〗|每〖一个时辰〗撞一下，一昼夜十二时辰', a=cam('FIG', az=-60, d=2.6, f=(1.0, -1.2, 0.4)), b=cam('FIG', az=-75, d=2.4, f=(1.0, -1.2, 0.4)), strikes=[('R', 1.8)]),
 dict(k='hook', sub='柜子里〖钩键交错、关锁相持〗|时间一到，自动触发', a=cam('XRAY', az=-75, d=7.0, el=8, f=(0, -0.6, -0.8)), b=cam('XRAY', az=-95, d=6.4, el=10, f=(0, -0.6, -0.8)), xray=True, strikes=[('L', 3.0), ('R', 3.4)], wheelspd=40),
 dict(k='crowd', sub='它摆在武成殿前给百官看|都说它〖精妙〗', a=cam('WIDE', az=-90, d=17, el=20, f=(0.3, -1, -0.8)), b=cam('WIDE', az=-80, d=15, el=24, f=(0.3, -1, -0.8)), crowd=True, src='《旧唐书》：置于武成殿前以示百僚'),
 dict(k='rust', sub='可没过多久，铜铁就〖生涩卡住〗|它再也转不动了', a=cam('WIDE', az=-60, d=10.5), b=cam('WIDE', az=-35, d=11.5), mood='cold', rust=True),
 dict(k='quote', sub='它被收进集贤院|从此〖不再使用〗', a=cam('WIDE', az=-30, d=11.5, f=(-0.6, 0.6, -0.45)), b=cam('WIDE', az=-24, d=11.8, f=(-0.6, 0.6, -0.45)), mood='cold', patina=0.85, still=True),
 dict(k='legacy', sub='但它第一次用齿轮〖自动报时〗|比欧洲最早的机械钟早了〖五百多年〗', a=cam('XRAY', az=-50, d=8.6), b=cam('XRAY', az=-62, d=8.0), xray=True, src='据李约瑟《中国科学技术史》', strikes=[('L', 3.2)]),
 dict(k='susong', sub='三百多年后，北宋苏颂造出〖水运仪象台〗|走的正是这条路', a=cam('WIDE', az=-120, d=11, el=18), b=cam('WIDE', az=-95, d=11, el=20), tag='北宋 · 元祐三年（1088）'),
 dict(k='end', sub='一千三百年前，它让天在屋檐下转起来|你觉得，它算不算〖中国最早的钟〗？', a=cam('WIDE', az=-50, d=10, el=24), b=cam('WIDE', az=-50, d=14.5, el=30, f=(0.3, 0, 1.2)), dur=6.5),
]
for s in SH:
    if 'dur' not in s:
        n = len(s['sub'].replace('|', '').replace('〖', '').replace('〗', '').replace('「', '').replace('」', '').replace('【', '').replace('】', ''))
        s['dur'] = round(max(4.0, 1.3 + n * 0.16), 2)
T0 = np.cumsum([0] + [s['dur'] for s in SH])
TOTAL = T0[-1]

def orbit(c):
    f = np.array(c['f']); az, el = math.radians(c['az']), math.radians(c['el'])
    p = f + c['d'] * np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
    return tuple(p), tuple(f), c['fov']

def cam_at(s, p):
    e = ease(p); a, b = s['a'], s['b']
    c = {k: (tuple(lerp(np.array(a[k]), np.array(b[k]), e)) if k == 'f' else lerp(a[k], b[k], e)) for k in a}
    return orbit(c)

def strike_angle(strikes, side, lt):
    rest = 25 if side == 'L' else 8
    hit = -10 if side == 'L' else -6
    ang = rest
    for sd, t in strikes:
        if sd != side: continue
        d = lt - t
        if -0.35 < d < 0: ang = lerp(rest, rest + 25, ease((d + 0.35) / 0.35))       # 抬起
        elif 0 <= d < 0.08: ang = lerp(rest + 25, hit, d / 0.08)
        elif 0.08 <= d < 0.6: ang = lerp(hit, rest, ease((d - 0.08) / 0.52))
    return ang

# ---------------- 渲染器 ----------------
class R:
    def __init__(self):
        self.S = S = Stage()
        S.ren.UseImageBasedLightingOn(); S.ren.SetEnvironmentTexture(C.env_tex(), True)
        self.key = S.light((3, -6, 6), (1, 0.86, 0.68), 1.25)
        S.light((-5, 5, 4), (0.55, 0.72, 1.0), 0.8)
        S.light((-4, -5, 1), (1, 0.8, 0.6), 0.35)
        self.D = Device(S)
        self.bgcache = {}

    def shadow(self):
        S = self.S
        pts = [S.project(p) for p in [(-2.4, -2.2, ZB0 - 0.36), (3.2, -2.2, ZB0 - 0.36), (3.2, 2.2, ZB0 - 0.36), (-2.4, 2.2, ZB0 - 0.36)]]
        return [(x, y + 16) for x, y in pts]

    def frame(self, t):
        i = int(np.searchsorted(T0, t, side='right') - 1); i = min(i, len(SH) - 1)
        s = SH[i]; lt = t - T0[i]; p = lt / s['dur']
        S, D = self.S, self.D
        mood = s.get('mood', 'warm')
        # 状态
        rust = s.get('rust'); still = s.get('still')
        patina = s.get('patina', 0.0)
        if rust: patina = float(0.85 * ease((p - 0.15) / 0.6))
        if s['k'] in ('legacy', 'susong', 'end'): patina = 0.0
        if mood == 'cold':
            self.key.SetColor(0.75, 0.85, 1.0); self.key.SetIntensity(0.95)
        else:
            self.key.SetColor(1, 0.86, 0.68); self.key.SetIntensity(1.25)
        skyspd = s.get('skyspd', 6)
        flow = 1.0
        if rust: flow = max(0, 1 - ease(p / 0.7))
        if still: flow = 0
        skyang = 20 + t * skyspd * (flow if (rust or still) else 1)
        if rust: skyang = 20 + T0[i] * 6 + 6 * (lt - 0.35 * lt * lt / s['dur'])
        if still: skyang = 20 + T0[i - 1] * 6 + 6 * SH[i - 1]['dur'] * 0.65
        sun = 35 + s.get('sunspd', 0) * lt + (T0[i] * 1.0)
        moon = 150 + s.get('moonspd', 0) * lt + T0[i] * 3
        wspd = s.get('wheelspd', 36)
        wheel = t * wspd if not (rust or still) else (T0[i] * wspd + wspd * (lt - 0.5 * lt * lt / (s['dur'] * 0.7)) if rust and lt < s['dur'] * 0.7 else T0[i] * wspd + wspd * s['dur'] * 0.35)
        st = s.get('strikes', [])
        D.xray(bool(s.get('xray')), s.get('cab_op', 0.13))
        D.patina(patina)
        D.show_crowd(bool(s.get('crowd')))
        D.pose(sky=skyang, sun=sun, moon=moon, wheel=wheel, arm_l=strike_angle(st, 'L', lt), arm_r=strike_angle(st, 'R', lt), water=bool(flow > 0.3), t=t)
        pos, foc, fov = cam_at(s, p)
        S.cam(pos, foc, (0, 0, 1), fov)
        rgba = S.grab()
        key = (i,)
        if key not in self.bgcache:
            self.bgcache = {}
            gc = S.project((0, 0, 0))
            self.bgcache[key] = C.background((gc[0], gc[1]), mood, t=T0[i], seed=3 + i)
        bg = self.bgcache[key].copy()
        if s['k'] not in ('hook2', 'globe', 'day', 'eclipse', 'yixing', 'liang', 'sun', 'moon', 'drum', 'bell', 'hook3'):
            C.contact_shadow(bg, self.shadow(), 160, 30)
        im = C.compose(bg, rgba)
        self.overlay(im, s, lt, p, t)
        # 淡入淡出
        fa = 1.0
        if lt < 0.25: fa = lt / 0.25
        if i == len(SH) - 1 and s['dur'] - lt < 1.0: fa = (s['dur'] - lt) / 1.0
        im = C.vignette(im, 0.7 if mood == 'cold' else 0.55)
        if fa < 1:
            a = np.asarray(im).astype(np.float32) * fa; im = Image.fromarray(a.astype(np.uint8))
        return im.convert('RGB')

    def overlay(self, im, s, lt, p, t):
        S, D = self.S, self.D
        k = s['k']
        def ap(t0, dur=0.4): return ease((lt - t0) / dur)
        C.chrome(im, tag=s.get('tag', TAG) if k != 'end' else '唐 · 一行 × 梁令瓒')
        if s.get('src'):
            d = ImageDraw.Draw(im, 'RGBA'); d.text((W - 64, 122), s['src'], font=C.font(C.SANS, 24), fill=(215, 195, 160, int(220 * ap(0.3))), anchor='rm')
        if k == 'title':
            a = ap(0.2, 0.7)
            C.title(im, '水运浑天', '世界最早的「机械报时」天文钟', '一行 × 梁令瓒 · 唐开元十三年（725）', a=a, y=330, cx=480)
        elif k in ('hook3', 'drum', 'bell', 'hook', 'legacy'):
            pass
        if k == 'eclipse':
            ps = S.project(D.sun_p); pm = S.project(D.moon_p)
            C.callout(im, ps, '预报的日食', '到时候却没发生', 200, 140, a=ap(0.6), col=C.RED)
            if lt > 1.6:
                dd = ImageDraw.Draw(im, 'RGBA'); x, y = 1500, 470; a = int(255 * ap(1.6, 0.25))
                dd.line([(x - 70, y - 70), (x + 70, y + 70)], fill=C.RED + (a,), width=16); dd.line([(x + 70, y - 70), (x - 70, y + 70)], fill=C.RED + (a,), width=16)
        if k == 'yixing':
            namecard(im, '一行', '683—727 · 僧人 · 天文学家', '主持编修《大衍历》', ap(0.4, 0.5))
        if k == 'liang':
            namecard(im, '梁令瓒', '率府兵曹 · 能画也能造', '先做出“游仪木样”', ap(0.4, 0.5))
        if k == 'youyi':
            C.callout(im, S.project(rp(D, 24, 1.006, 200)), '黄道', '太阳一年走的路线', -260, -80, a=ap(0.8))
            C.callout(im, S.project(rp(D, 0, 1.006, 250)), '赤道', '天球的“腰线”', 220, 90, a=ap(1.4))
        if k == 'layers':
            C.callout(im, S.project((0, -0.4, 0.85)), '天', '铜铸浑象', -260, -60, a=ap(0.5), idx=1)
            C.callout(im, S.project((-1.2, -1.6, ZTOP)), '地', '木柜地平', -200, 90, a=ap(1.5), idx=2)
            C.callout(im, S.project((2.3, -0.45, -1.2)), '动力', '水轮', 150, 80, a=ap(2.5), idx=3)
        if k == 'globe':
            C.callout(im, S.project(rp(D, 0, 1.0, 245)), '赤道', None, 200, 60, a=ap(0.8))
            C.callout(im, S.project((-0.45, -0.75, 0.55)), '星宿', '二十八宿与中外星官', -240, -80, a=ap(1.4))
        if k == 'horizon':
            dd = ImageDraw.Draw(im, 'RGBA'); a = ap(0.8)
            y0 = S.project((0, -1.0, ZTOP))[1]
            dd.line([(260, y0), (W - 260, y0)], fill=C.GOLD2 + (int(230 * a),), width=3)
            dd.text((W - 270, y0 - 16), '地平线', font=C.font(C.SANSK, 34), fill=C.GOLD2 + (int(255 * a),), anchor='rs')
            dd.text((300, y0 - 22), '地上：看得见的半个天', font=C.font(C.SANS, 30), fill=C.WHITE + (int(255 * ap(1.4)),), anchor='ls')
            dd.text((300, y0 + 48), '地下：转到地平下的星星', font=C.font(C.SANS, 30), fill=C.CYAN + (int(255 * ap(2.0)),), anchor='ls')
        if k == 'water':
            C.callout(im, S.project((2.3, 0.4, -0.45)), '注水', '水流落进水斗', -260, -90, a=ap(0.6), idx=1)
            C.callout(im, S.project((2.3, -0.4, -1.2)), '激轮', '水斗一满就压下去', -240, 110, a=ap(1.8), idx=2)
        if k == 'gears':
            C.callout(im, S.project((1.0, 0, D.WZ + 0.3)), '主动轮', '跟着水轮一起转', 150, -150, a=ap(0.6), idx=1)
            C.callout(im, S.project((0.7, 0, -1.1)), '小齿轮', '12 齿', -100, -200, a=ap(1.5), idx=2)
            C.callout(im, S.project((-0.4, -0.3, -1.12)), '大齿轮', '44 齿 · 越转越慢', -260, 120, a=ap(2.4), idx=3)
        if k == 'day':
            clock(im, (1600, 520), (lt / s['dur']) * 1.0, ap(0.3))
        if k == 'rings':
            C.callout(im, S.project(D.sun_p), '日环', '挂着太阳', 180, -100, a=ap(0.8))
            C.callout(im, S.project(D.moon_p), '月环', '挂着月亮', -220, -100, a=ap(1.8), col=C.CYAN)
        if k == 'sun':
            C.callout(im, S.project(D.sun_p), '太阳', '每天东移 1 度', 170, -100, a=ap(0.4))
            n = int(lerp(1, 365, ease((lt - 0.8) / (s['dur'] - 1.6))))
            C.bignum(im, str(n), 1620, 480, 170, a=ap(0.6), label='转 · 太阳绕天一周')
        if k == 'moon':
            C.callout(im, S.project(D.moon_p), '月亮', '每天东移 13又7/19 度', -220, -110, a=ap(0.4), col=C.CYAN)
            n = lerp(0, 29.5, ease((lt - 0.8) / (s['dur'] - 1.6)))
            C.bignum(im, f'{n:.1f}' if n < 29.4 else '29+', 1620, 480, 170, col=C.CYAN, a=ap(0.6), label='转 · 日月相会一次')
        if k in ('hook3', 'drum', 'bell', 'hook', 'legacy'):
            for sd, t0 in s.get('strikes', []):
                d = lt - t0
                if 0 <= d < 0.9:
                    pos = D.drum_pos if sd == 'L' else D.bell_pos
                    pp = S.project(pos); a = 1 - d / 0.9
                    C.ring_burst(im, pp, 30 + 120 * d, a, col=C.GOLD2 if sd == 'L' else C.CYAN)
                    if k not in ('hook', 'legacy'):
                        C.onomat(im, '咚！' if sd == 'L' else '当——', (pp[0] + (-60 if sd == 'L' else 60), pp[1] - 170 - 30 * d), 96, a=min(1, a * 1.6), col=C.GOLD2 if sd == 'L' else C.CYAN, rot=-8 if sd == 'L' else 6)
            if k == 'drum':
                C.bignum(im, '100', 330, 400, 130, a=ap(0.8), label='刻 / 一昼夜')
            if k == 'bell':
                C.bignum(im, '12', 330, 400, 130, col=C.CYAN, a=ap(0.8), label='时辰 / 一昼夜')
        if k == 'quote':
            C.quote_card(im, ['“无几而铜铁渐涩，', '　不能自转。”'], '——《旧唐书·天文志》', a=ap(0.3, 0.6), x=1180, y=300)
            dd = ImageDraw.Draw(im, 'RGBA')
            dd.text((1180, 520), '白话：没多久铜铁生锈发涩，自己转不动了。', font=C.font(C.SANS, 28), fill=(225, 230, 235, int(240 * ap(1.2))), anchor='ls')
        if k == 'susong':
            namecard(im, '苏颂', '1020—1101 · 北宋', '水运仪象台：集观测、演示、报时于一体', ap(0.4, 0.5))
        if k == 'end':
            a = ap(3.6, 0.8)
            if a > 0:
                C.title(im, '水运浑天', '一行 × 梁令瓒 · 725', None, a=a, y=190, cx=W / 2)
        C.subtitle(im, s['sub'], a=ap(0.15, 0.35))

def rp(D, tilt, R, ang):
    m = vtk.vtkTransform(); m.PostMultiply(); m.RotateX(tilt); m.RotateZ(D._sky if hasattr(D, '_sky') else 0); m.RotateX(-56)
    return m.TransformPoint(R * math.cos(math.radians(ang)), R * math.sin(math.radians(ang)), 0)

def namecard(im, name, l1, l2, a, x=110, y=360):
    if a <= 0: return
    d = ImageDraw.Draw(im, 'RGBA')
    off = int((1 - a) * -40)
    d.rounded_rectangle([x + off - 20, y - 110, x + off + 560, y + 120], 18, fill=(12, 10, 8, int(170 * a)), outline=C.GOLD + (int(200 * a),), width=2)
    d.text((x + off + 10, y - 20), name, font=C.font(C.SERIF, 96), fill=C.GOLD2 + (int(255 * a),), anchor='ls')
    d.text((x + off + 14, y + 36), l1, font=C.font(C.SANSK, 30), fill=C.WHITE + (int(255 * a),), anchor='ls')
    d.text((x + off + 14, y + 86), l2, font=C.font(C.SANS, 28), fill=(220, 205, 175, int(240 * a)), anchor='ls')

def clock(im, c, frac, a):
    d = ImageDraw.Draw(im, 'RGBA'); x, y = c; R = 170
    d.ellipse([x - R, y - R, x + R, y + R], fill=(10, 10, 14, int(150 * a)), outline=C.GOLD + (int(230 * a),), width=4)
    names = '子丑寅卯辰巳午未申酉戌亥'
    f = C.font(C.SERIFB, 30)
    for i, n in enumerate(names):
        ang = math.radians(-90 + i * 30)
        d.text((x + (R - 32) * math.cos(ang), y + (R - 32) * math.sin(ang)), n, font=f, fill=C.WHITE + (int(240 * a),), anchor='mm')
    ang = math.radians(-90 + 360 * frac)
    d.line([(x, y), (x + (R - 70) * math.cos(ang), y + (R - 70) * math.sin(ang))], fill=C.GOLD2 + (int(255 * a),), width=6)
    d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=C.GOLD2 + (int(255 * a),))
    d.text((x, y + R + 44), '一昼夜 = 天转一周', font=C.font(C.SANSK, 32), fill=C.GOLD2 + (int(255 * a),), anchor='mm')

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'info':
        print(TOTAL, len(SH)); print(json.dumps([(s['k'], s['dur']) for s in SH], ensure_ascii=False))
    elif mode == 'still':
        r = R()
        for ts in sys.argv[2:]:
            r.frame(float(ts)).save(f'chk_{float(ts):.2f}.jpg', quality=88)
    elif mode == 'render':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        os.makedirs('frames', exist_ok=True)
        r = R(); t0 = time.time()
        for f in range(a, b):
            fn = f'frames/{f:05d}.jpg'
            if os.path.exists(fn): continue
            r.frame(f / FPS).save(fn, quality=90)
            if f % 100 == 0: print(f, time.time() - t0, flush=True)
