import sys, time
from g3d import *
from model import Device, ZB0, ZTOP
import comp as C

S = Stage()
S.ren.UseImageBasedLightingOn(); S.ren.SetEnvironmentTexture(C.env_tex(), True)
key = S.light((3, -6, 6), (1, 0.86, 0.68), 1.25)
rim = S.light((-5, 5, 4), (0.55, 0.72, 1.0), 0.8)
fill = S.light((-4, -5, 1), (1, 0.8, 0.6), 0.35)
D = Device(S)

def shadow_poly():
    e = 2.4
    pts = [S.project(p) for p in [(-e, -2.3, ZB0 - 0.36), (3.3, -2.3, ZB0 - 0.36), (3.3, 2.3, ZB0 - 0.36), (-e, 2.3, ZB0 - 0.36)]]
    return [(x, y + 18) for x, y in pts]

def frame(cam, pose, mood='warm', xray=False, patina=0.0):
    D.xray(xray); D.patina(patina); D.pose(**pose)
    S.cam(*cam)
    rgba = S.grab()
    gc = S.project((0, 0, 0))
    bg = C.background((gc[0], gc[1]), mood)
    C.contact_shadow(bg, shadow_poly(), 170, 30)
    return C.compose(bg, rgba)

out = []
# 1 片头
im = frame(((5.6, -7.0, 4.6), (-1.9, 0.9, -0.55), (0, 0, 1), 32), dict(sky=20, sun=35, moon=150, wheel=20, arm_l=25, arm_r=5, t=0.3))
C.chrome(im); C.title(im, '水运浑天', '一千三百年前的「自动」宇宙模型', '一行 × 梁令瓒 · 唐开元十三年（725）', y=330, cx=480)
C.subtitle(im, '它用〖水〗推动齿轮|让整片星空〖一天转一圈〗')
im = C.vignette(im); im.convert('RGB').save('still_1.jpg', quality=92); out.append('still_1.jpg')

# 2 X光：水力传动
im = frame(((5.6, -6.8, 2.1), (0.9, 0, -0.55), (0, 0, 1), 36), dict(sky=60, sun=35, moon=150, wheel=40, arm_l=25, arm_r=5, t=0.55), xray=True)
C.chrome(im)
C.callout(im, S.project((2.3, 0.4, -0.6)), '注水激轮', '水落进斗里，推动水轮', 150, -170, idx=1)
C.callout(im, S.project((1.6, 0, D.WZ)), '轮轴传动', '水轮的转动送进柜子里', 60, 120, idx=2)
C.callout(im, S.project((0, 0, -1.15)), '齿轮减速', '大小齿轮把速度降下来', -260, 170, idx=3)
C.callout(im, S.project((-0.55, -0.6, 0.45)), '浑象自转', '一日一夜，天转一周', -230, 110, idx=4)
C.subtitle(im, '柜子里〖轮轴〗交错、〖钩键〗相扣|水一直流，天就一直转')
im = C.vignette(im); im.convert('RGB').save('still_2.jpg', quality=92); out.append('still_2.jpg')

# 3 日环月环
im = frame(((3.1, -4.8, 3.7), (0.3, 0, 0.05), (0, 0, 1), 34), dict(sky=110, sun=-20, moon=60, wheel=0, t=0.1), mood='night')
C.chrome(im)
C.callout(im, S.project(D.sun_p), '日', '每天东移 1 度', 170, -110, col=C.GOLD)
C.callout(im, S.project(D.moon_p), '月', '每天东移 13又7/19 度', -220, 60, col=C.CYAN)
C.bignum(im, '365', 1620, 470, 170, label='转 · 太阳绕天一周')
C.bignum(im, '29+', 1620, 760, 130, col=C.CYAN, label='转 · 日月相会一次')
C.subtitle(im, '天外还套着两道环：〖日〗和「月」|各走各的速度，比天慢半拍')
im = C.vignette(im); im.convert('RGB').save('still_3.jpg', quality=92); out.append('still_3.jpg')

# 4 木人击鼓撞钟
im = frame(((0.0, -4.6, 1.05), (0, -1.1, 0.3), (0, 0, 1), 40), dict(sky=150, sun=40, moon=170, wheel=0, arm_l=-8, arm_r=10, t=0.2))
C.chrome(im)
pd = S.project(D.drum_pos); pb = S.project(D.bell_pos)
C.ring_burst(im, pd, 40, 0.9); C.onomat(im, '咚！', (pd[0] - 40, pd[1] - 170), 96)
C.ring_burst(im, pb, 46, 0.9, col=C.CYAN); C.onomat(im, '当——', (pb[0] + 40, pb[1] - 180), 90, col=C.CYAN, rot=6)
C.bignum(im, '100', 260, 330, 120, label='刻 · 每刻击鼓一次')
C.bignum(im, '12', 1660, 330, 120, col=C.CYAN, label='辰 · 每辰撞钟一次')
C.subtitle(im, '地平上站着两个〖木人〗|到点就自己敲鼓、撞钟')
im = C.vignette(im); im.convert('RGB').save('still_4.jpg', quality=92); out.append('still_4.jpg')

# 5 结尾：铜涩
key.SetColor(0.75, 0.85, 1.0); key.SetIntensity(0.9)
im = frame(((-4.9, -5.6, 3.8), (0.5, 0.2, -0.45), (0, 0, 1), 32), dict(sky=0, sun=35, moon=150, wheel=0, arm_l=25, arm_r=5, water=False), mood='cold', patina=0.85)
C.chrome(im)
C.quote_card(im, ['“无几而铜铁渐涩，', '　不能自转。”'], '——《旧唐书·天文志》', x=1180, y=300)
C.subtitle(im, '没过多久，铜铁就〖生锈卡住〗|它被收进集贤院，再也没转过')
im = C.vignette(im, 0.7); im.convert('RGB').save('still_5.jpg', quality=92); out.append('still_5.jpg')
print(out)
