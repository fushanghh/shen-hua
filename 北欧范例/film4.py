import os
# 北欧01 · 提尔与魔狼芬里尔 —— 纯代码剪纸木偶动画，1920×1080，24fps，无旁白
import sys, math, os, numpy as np, cairocffi as cairo, cv2, subprocess
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from puppet import *
from PIL import Image, ImageDraw, ImageFont
import re

FPS=24; OW,OH=1440,1080; SW,SH=1920,800; PY=30; GY=760
PW,PH=1440,1020; OFF=260; K=0.75; SHC=1360
FZ=""+os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','字体','NotoSerifSC-Bold.otf')+""; FE="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FR="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
WOOD=rgb('3a2516'); WOOD2=rgb('2a1a10'); GOLDF=rgb('c9a050'); GOLD2F=rgb('8a6630')
def E(x): x=max(0,min(1,x)); return x*x*(3-2*x)
def seg(lt,a,b): return E((lt-a)/(b-a)) if b>a else float(lt>=a)
def lerp(a,b,u): return a+(b-a)*u

# ---------------- 通用小件 ----------------
def surf(w=SW,h=SH):
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h); return s,cairo.Context(s)
def nmap(seed,w,h,scales=((8,1.0),(24,0.5),(80,0.25),(240,0.12))):
    r=np.random.default_rng(seed); acc=np.zeros((h,w),np.float32)
    for n,a in scales:
        g=r.random((max(2,h*n//w),n)).astype(np.float32); acc+=cv2.resize(g,(w,h),interpolation=cv2.INTER_CUBIC)*a
    acc-=acc.min(); return acc/acc.max()
def paint_arr(c,a):
    a=(np.clip(a,0,1)*255).astype(np.uint8); h,w=a.shape[:2]
    bgra=np.dstack([a[...,2],a[...,1],a[...,0],np.full((h,w),255,np.uint8)])
    s=cairo.ImageSurface.create_for_data(bytearray(bgra.tobytes()),cairo.FORMAT_ARGB32,w,h); c.set_source_surface(s,0,0); c.paint()
def mottled(c,c1,c2,seed=1,y0=0,y1=SH):
    n=nmap(seed,SW,SH); a=np.array(c1)[None,None]*(1-n[...,None])+np.array(c2)[None,None]*n[...,None]
    c.save(); c.rectangle(0,y0,SW,y1-y0); c.clip(); paint_arr(c,a); c.restore()
def bands(c,cols,y0,y1):
    h=(y1-y0)/len(cols)
    for i,col in enumerate(cols): c.rectangle(0,y0+i*h,SW,h+1); c.set_source_rgb(*col); c.fill()
def circ(c,x,y,r,col,a=1.0):
    c.new_path(); c.arc(x,y,r,0,7); c.set_source_rgba(*col,a); c.fill()
def glow(c,x,y,r,col,a):
    g=cairo.RadialGradient(x,y,1,x,y,r); g.add_color_stop_rgba(0,*col,a); g.add_color_stop_rgba(1,*col,0); c.set_source(g); c.paint()
def flame(c,cx,by,w,h,t=0):
    for k,(col,sc) in enumerate(((rgb('b8432a'),1.0),(rgb('e08a32'),0.72),(rgb('f2cf6a'),0.42))):
        pts=[(cx-w*sc,by,'c')]
        for i in range(5):
            u=(i+0.5)/5; xx=cx-w*sc+u*2*w*sc; hh=h*sc*(0.55+0.45*math.sin(u*math.pi))*(0.8+0.2*math.sin(t*9+i*2.1+k))
            pts+=[(xx+w*sc*0.1*math.sin(t*7+i),by-hh,'c'),(xx+w*sc*0.2,by-hh*0.55)]
        pts+=[(cx+w*sc,by,'c')]; shape(c,pts,col,2.5 if k==0 else 0)
def meat(c,x,y,s=1.0):
    c.save(); c.translate(x,y); c.scale(s,s)
    shape(c,[(-10,-6),(40,-40),(90,-30),(96,10),(50,30),(4,16)],rgb('a24a34'),3.5); line(c,[(30,-26),(70,-14),(80,8)],rgb('d07a5a'),5)
    shape(c,[(-50,10,'c'),(0,-4,'c'),(4,14,'c'),(-46,24,'c')],C['bone'],3,t=0)
    for dx,dy in ((-56,6),(-56,26)): c.new_path(); c.arc(dx,dy,11,0,7); c.set_source_rgb(*C['bone']); c.fill_preserve(); c.set_source_rgb(*LINE); c.set_line_width(3); c.stroke()
    c.restore()
def ribbon(c,pts,lw=12,g=1.0):
    for k,a in ((5,0.10),(3,0.16),(2,0.25)):
        c.new_path(); smooth(c,pts,False); c.set_source_rgba(1,0.85,0.45,a*g); c.set_line_width(lw*k); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    line(c,pts,LINE,lw+5); line(c,pts,rgb('e9c66e'),lw); line(c,pts,rgb('fbeeb8'),lw*0.3)
def loop(c,cx,cy,rx,ry,tilt=0.0,lw=12,g=1.0):
    pts=[(cx+rx*math.cos(a)*math.cos(tilt)-ry*math.sin(a)*math.sin(tilt), cy+rx*math.cos(a)*math.sin(tilt)+ry*math.sin(a)*math.cos(tilt)) for a in np.linspace(0,2*math.pi,13)[:-1]]
    for k,al in ((4,0.12),(2.4,0.2)):
        c.new_path(); smooth(c,pts,True); c.set_source_rgba(1,0.85,0.45,al*g); c.set_line_width(lw*k); c.stroke()
    for col,w in ((LINE,lw+5),(rgb('e9c66e'),lw),(rgb('fbeeb8'),lw*0.3)):
        c.new_path(); smooth(c,pts,True); c.set_source_rgb(*col); c.set_line_width(w); c.stroke()
def chain(c,pts,r=16,col=None):
    """沿折线排铁链环（正面环 / 侧面杆交替）"""
    col=col or C['iron']; P=np.array(pts,float); seglen=np.hypot(*np.diff(P,axis=0).T); tot=seglen.sum(); d=0; k=0
    while d<tot:
        i=np.searchsorted(np.cumsum(seglen),d); i=min(i,len(seglen)-1); d0=np.cumsum(seglen)[i]-seglen[i]; u=(d-d0)/max(seglen[i],1e-6)
        x,y=P[i]+(P[i+1]-P[i])*u; ang=math.atan2(*(P[i+1]-P[i])[::-1])
        c.save(); c.translate(x,y); c.rotate(ang)
        if k%2==0:
            c.new_path(); c.save(); c.scale(1.0,0.62); c.arc(0,0,r,0,7); c.restore(); c.set_source_rgb(*LINE); c.set_line_width(r*0.55); c.stroke()
            c.new_path(); c.save(); c.scale(1.0,0.62); c.arc(0,0,r,0,7); c.restore(); c.set_source_rgb(*col); c.set_line_width(r*0.3); c.stroke()
        else:
            c.rectangle(-r,-r*0.22,2*r,r*0.44); c.set_source_rgb(*LINE); c.fill(); c.rectangle(-r+2,-r*0.1,2*r-4,r*0.2); c.set_source_rgb(*col); c.fill()
        c.restore(); d+=r*1.5; k+=1
def serpent(c,x,y,L,ph,thick=34,col=None,head=True,s=1.0):
    col=col or rgb('3f6e5c'); pts=[]
    for i in range(40):
        u=i/39; pts.append((x+u*L, y+math.sin(u*7+ph)*thick*1.6*(0.3+0.7*u)))
    c.new_path(); smooth(c,pts,False); c.set_source_rgb(*LINE); c.set_line_width(thick+6); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    c.new_path(); smooth(c,pts,False); c.set_source_rgb(*col); c.set_line_width(thick); c.stroke()
    c.new_path(); smooth(c,pts,False); c.set_source_rgb(*C['gold']); c.set_line_width(thick*0.18); c.set_dash([thick*0.5,thick*0.4]); c.stroke(); c.set_dash([])
    if head:
        hx,hy=pts[-1]; a=math.atan2(pts[-1][1]-pts[-3][1],pts[-1][0]-pts[-3][0])
        c.save(); c.translate(hx,hy); c.rotate(a)
        shape(c,[(-10,-thick*0.8),(thick*1.6,-thick*0.5),(thick*2.2,0,'c'),(thick*1.6,thick*0.5),(-10,thick*0.8)],col,3.5)
        shape(c,[(thick*0.7,-thick*0.36,'c'),(thick*1.1,-thick*0.42),(thick*1.0,-thick*0.18,'c')],rgb('e8a940'),2)
        line(c,[(thick*2.2,0),(thick*2.9,6),(thick*3.1,-6)],C['red'],3)
        c.restore()
def dust(c,x,y,age,n=7,s=1.0,col=None):
    if age<0 or age>1.2: return
    col=col or rgb('c9b48c'); r=np.random.default_rng(int(x*7+y))
    for i in range(n):
        a=r.uniform(math.pi,2*math.pi); v=r.uniform(40,120)*s
        px=x+math.cos(a)*v*age*1.4; py=y+math.sin(a)*v*age*0.6
        circ(c,px,py,(14+age*30)*s*r.uniform(0.6,1.2),col,max(0,0.55*(1-age/1.2)))
def sparks(c,x,y,age,n=14,col=None,seed=0,spd=1.0):
    if age<0 or age>0.8: return
    col=col or rgb('f6c860'); r=np.random.default_rng(seed)
    for i in range(n):
        a=r.uniform(-math.pi,0)+r.uniform(-0.3,0.3); v=r.uniform(150,420)*spd
        px=x+math.cos(a)*v*age; py=y+math.sin(a)*v*age+300*age*age
        c.move_to(px,py); c.line_to(px-math.cos(a)*14,py-math.sin(a)*14+8); c.set_source_rgba(*col,1-age/0.8); c.set_line_width(3); c.stroke()
def stars(c,t,n=200,seed=4,ymax=520):
    r=np.random.default_rng(seed)
    for i in range(n):
        x,y=r.uniform(0,SW),r.uniform(-OFF,ymax); rr=r.uniform(1,3); ph=r.uniform(0,6.3)
        circ(c,x,y,rr,(0.95,0.92,0.8),0.35+0.5*(0.5+0.5*math.sin(t*2.2+ph)))

RUNES={'f':[((0,0),(0,1)),((0,0.3),(0.5,0.02)),((0,0.56),(0.5,0.28))],
 'e':[((0,0),(0,1)),((0.6,0),(0.6,1)),((0,0),(0.3,0.3)),((0.3,0.3),(0.6,0))],
 'n':[((0,0),(0,1)),((-0.25,0.35),(0.25,0.62))],
 'r':[((0,0),(0,1)),((0,0),(0.45,0.22)),((0.45,0.22),(0,0.45)),((0,0.45),(0.45,1))],
 'i':[((0,0),(0,1))],
 'z':[((0,0),(0,1)),((0,0.6),(-0.35,1)),((0,0.6),(0.35,1))],
 't':[((0,0),(0,1)),((-0.35,0.3),(0,0)),((0,0),(0.35,0.3))]}
def rune(c,ch,x,y,h,col,w=None,a=1.0):
    w=w or h*0.09
    for (x0,y0),(x1,y1) in RUNES[ch]:
        c.move_to(x+x0*h,y+y0*h); c.line_to(x+x1*h,y+y1*h)
    c.set_source_rgba(*col,a); c.set_line_width(w); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()

# ---------------- 角色预设 ----------------
TYR=dict(helmet='spectacle',sword=True,cloak='blue',trousers='brown')
ODIN=dict(hood=True,patch=True,cloak='blue2',tunic='brown',tunic2='brown2',beard='grey',beard_len=1.35,helmet='none')
THOR=dict(tunic='blue',tunic2='blue2',cloak='red',beard='red',helmet='wing')
LOKI=dict(tunic='green',tunic2='brown2',cloak='ochre',beard='red',beard_len=0.35,helmet='none',hair='red')
FREYR=dict(tunic='ochre',tunic2='brown2',cloak='green',beard='gold',beard_len=0.6,helmet='none')
HEIM=dict(tunic='bone',tunic2='grey',cloak='blue',beard='bone',helmet='cone')
SKIR=dict(tunic='blue',tunic2='blue2',cloak='ochre',beard=None,helmet='none',hair='gold')
DWARF=dict(tunic='brown',tunic2='brown2',cloak='brown2',beard='grey',beard_len=1.5,helmet='none',hood=True)
ANGR=dict(dress=True,tunic='slate2',tunic2='black',cloak='brown2',beard=None,helmet='none',hair='grey',skin='grey',longsleeve=False)
HEL=dict(dress=True,tunic='black',tunic2='slate2',cloak=None,beard=None,helmet='none',hair='black',skin='bone',face='half',longsleeve=True)
VIDAR=dict(tunic='green',tunic2='brown2',cloak='brown',beard='brown',helmet='cone')
BLK=dict(tunic='black',tunic2='black',cloak='black',beard='black',skin='black',trousers='black',wrap=('black','black'),trim='ochre')
C['red_']=C['red']
def P(**k): d=dict(nsh=0.12,nel=0.2,fsh=-0.1,fel=0.2,nhip=0.04,nkn=-0.04,fhip=-0.06,fkn=0.02,head=0.0); d.update(k); return d
def walk(ph,amp=0.38,**k):
    s_=math.sin(ph); d=dict(nhip=amp*s_,fhip=-amp*s_,nkn=-0.5*max(0,-math.cos(ph)) ,fkn=-0.5*max(0,math.cos(ph)),nsh=-0.32*s_,fsh=0.32*s_,nel=0.25,fel=0.25,head=0.0)
    d.update(k); return d
def bob(ph,a=7): return -abs(math.sin(ph))*a
def trot(ph,**k):
    s_=math.sin(ph); d=dict(fl1=0.38*s_,fl2=-0.2-0.15*s_,fr1=-0.38*s_,fr2=-0.2+0.15*s_,hl1=-0.32-0.32*s_,hl2=0.62+0.2*s_,hr1=-0.32+0.32*s_,hr2=0.62-0.2*s_,tail=0.15*math.sin(ph*2))
    d.update(k); return d
LIE=dict(fl1=1.45,fl2=0.05,fr1=1.35,fr2=0.05,hl1=-1.2,hl2=2.3,hr1=-1.1,hr2=2.2,tail=-0.9)
def hammer(c,x,y,a=0.0,s=1.0):
    c.save(); c.translate(x,y); c.rotate(a); c.scale(s,s)
    shape(c,[(-6,-10,'c'),(6,-10,'c'),(6,70,'c'),(-6,70,'c')],C['brown'],3,t=0)
    shape(c,[(-34,-44,'c'),(34,-44,'c'),(30,-6,'c'),(-30,-6,'c')],C['iron'],3.5,t=0); line(c,[(-24,-26),(24,-26)],C['gold'],3)
    c.restore()
def spear(c,x,y,L=520):
    line(c,[(x,y+L*0.45),(x,y-L*0.55)],LINE,9); line(c,[(x,y+L*0.45),(x,y-L*0.55)],C['brown'],5)
    shape(c,[(x,y-L*0.55-70,'c'),(x+14,y-L*0.55-10),(x,y-L*0.55,'c'),(x-14,y-L*0.55-10)],C['iron'],3)
def sword_up(c,x,y,a=0,L=300):
    c.save(); c.translate(x,y); c.rotate(a)
    shape(c,[(-9,0,'c'),(9,0,'c'),(9,-L,'c'),(0,-L-30,'c'),(-9,-L,'c')],C['iron'],3.2,t=0); line(c,[(0,-10),(0,-L)],C['iron2'],2.4)
    shape(c,[(-34,-4,'c'),(34,-4,'c'),(34,8,'c'),(-34,8,'c')],C['gold'],3,t=0); shape(c,[(-6,8,'c'),(6,8,'c'),(6,56,'c'),(-6,56,'c')],C['brown'],3,t=0)
    c.restore()

# ---------------- 背景（缓存） ----------------
BG={}
def bg(name,fn):
    if name not in BG:
        s,c=surf(SW,SHC); c.translate(0,OFF); fn(c); s.flush()
        a=np.ndarray((SHC,SW,4),np.uint8,s.get_data()); a[:OFF]=a[OFF]; a[OFF+SH:]=a[OFF+SH-1]; s.mark_dirty(); BG[name]=s
    return BG[name]
def paintbg(c,name,fn): c.set_source_surface(bg(name,fn),0,-OFF); c.paint()
def bg_night(c):
    bands(c,[rgb('121a28'),rgb('17233a'),rgb('1d2e46'),rgb('24405a'),rgb('2d5562'),rgb('3c6a66')],0,640)
def mountains_front(c,col=rgb('3b4a5a'),snow=True,y=560):
    shape(c,[(0,SH+320,'c'),(0,y),(180,y-110),(360,y),(560,y-150,'c'),(760,y+20),(980,y-120,'c'),(1180,y+40),(1400,y-130,'c'),(1640,y+20),(1920,y-90),(1920,SH+320,'c')],col,3.5,t=0.2)
    if snow:
        for x0,y0 in ((180,y-110),(560,y-150),(980,y-120),(1400,y-130)):
            shape(c,[(x0-60,y0+60,'c'),(x0,y0,'c'),(x0+60,y0+60,'c'),(x0+26,y0+50),(x0,y0+68),(x0-26,y0+50)],C['bone'],3,t=0.1)
def bg_hall(c):
    from hall2 import planks, tapestry, gokstad, carved_pillar, bench, horn
    planks(c,0,640)
    c.rectangle(0,0,SW,92); c.set_source_rgb(*rgb('3a2516')); c.fill()
    for ph,col in ((0,rgb('b88446')),(math.pi,rgb('8f6232'))):
        pts=[(x,46+24*math.sin(x/130*math.pi+ph)) for x in range(-40,SW+60,30)]; line(c,pts,LINE,20); line(c,pts,col,12)
    c.rectangle(0,90,SW,5); c.set_source_rgb(*LINE); c.fill()
    tapestry(c,128,128)
    for cx in (470,640,1280,1450): gokstad(c,cx,370,58)
    bench(c,560,650); horn(c,380,556); shape(c,[(1080,560,'c'),(1090,532),(1160,532),(1170,560,'c')],rgb('7a5030'),3)
    carved_pillar(c,50,84,110,700); carved_pillar(c,SW-134,84,110,700)
    c.rectangle(0,650,SW,SH-650); c.set_source_rgb(*rgb('6e5236')); c.fill()
    r=np.random.default_rng(5)
    for i in range(200):
        x,y=r.uniform(0,SW),r.uniform(655,SH); a=r.uniform(-0.4,0.4); L=r.uniform(14,30)
        c.move_to(x,y); c.line_to(x+L*math.cos(a),y+L*math.sin(a)); c.set_source_rgba(0.84,0.7,0.42,0.5); c.set_line_width(2); c.stroke()
    c.rectangle(0,648,SW,5); c.set_source_rgb(*LINE); c.fill()
    for k in range(18):
        x=520+k*48; shape(c,[(x,690),(x+12,670),(x+40,669),(x+48,689),(x+30,702),(x+8,700)],rgb('8d8579'),3)
    c.rectangle(530,676,860,14); c.set_source_rgb(*rgb('2a1a10')); c.fill()
def hall_light(c,t,dark=0.0):
    for k,fx in enumerate((640,820,1000,1180,1320)): flame(c,fx,681,52,100+18*(k%2),t+0.6*k)
    for k in range(5):
        c.new_path(); smooth(c,[(900+k*40,640),(880+k*50+20*math.sin(t*0.6+k),450),(950+k*30,250),(960,0)],False); c.set_source_rgba(0.75,0.72,0.66,0.06); c.set_line_width(60); c.stroke()
    c.new_path(); c.move_to(900,0); c.line_to(1060,0); c.line_to(1250,650); c.line_to(980,650); c.close_path(); c.set_source_rgba(1,0.92,0.7,0.06); c.fill()
    glow(c,980,640,950,(1,0.68,0.3),0.30*(0.92+0.08*math.sin(t*11)))
    g=cairo.RadialGradient(SW/2,SH/2,420,SW/2,SH/2,1150); g.add_color_stop_rgba(0,0,0,0,dark*0.5); g.add_color_stop_rgba(1,0.05,0.02,0,0.5+dark*0.3); c.set_source(g); c.paint()
def bg_jotun(c):
    bands(c,[rgb('2a2440'),rgb('3a3456'),rgb('4f4a68'),rgb('6c6a80'),rgb('8f8c98'),rgb('b4aea8')],0,600)
    mountains_front(c,rgb('4a4f63'),True,560)
    c.rectangle(0,640,SW,SH-640); c.set_source_rgb(*rgb('d9dcdc')); c.fill(); c.rectangle(0,638,SW,5); c.set_source_rgb(*LINE); c.fill()
    for x in range(0,SW,140): shape(c,[(x,700),(x+30,690),(x+60,702)],None,2)
def bg_dark(c):
    bands(c,[rgb('120d0a'),rgb('1a130e'),rgb('231912'),rgb('2a1d14')],0,SH)
def bg_sea(c):
    bands(c,[rgb('2c3b52'),rgb('3d5168'),rgb('5b6d7c'),rgb('8a8f8a'),rgb('b9a988')],0,500)
    c.rectangle(0,500,SW,300); c.set_source_rgb(*rgb('2e4a63')); c.fill()
    shape(c,[(0,SH+320,'c'),(0,420),(140,360),(360,380),(520,470),(620,SH+320,'c')],rgb('6b5d4c'),4)
    for k in range(5): line(c,[(60+k*90,520+k*40),(120+k*90,500+k*40),(170+k*90,530+k*40)],rgb('4e4234'),3)
def bg_mist(c):
    bands(c,[rgb('8fa3b0'),rgb('a9bac2'),rgb('c3d0d4'),rgb('d8e0e0'),rgb('b9c7cc'),rgb('8a9ea8')],0,SH)
def bg_asgard(c):
    bands(c,[rgb('5b7fa0'),rgb('7a9bb6'),rgb('9fb8c6'),rgb('c7d3cf'),rgb('e2dcc4')],0,560)
    # 彩虹桥
    for k,col in enumerate((rgb('b54a2c'),rgb('d69a3a'),rgb('e2c25a'),rgb('5f8a5a'),rgb('3d5f8a'))):
        c.new_path(); c.arc(300,900,700-k*22,math.pi*1.12,math.pi*1.6); c.set_source_rgba(*col,0.75); c.set_line_width(22); c.stroke()
    # 阿斯加德木栅城门
    for x in range(1250,1920,46):
        shape(c,[(x,640,'c'),(x,330),(x+20,296,'c'),(x+40,330),(x+40,640,'c')],rgb('7e5230'),3.5,t=0)
    shape(c,[(1460,640,'c'),(1460,420),(1560,360,'c'),(1660,420),(1660,640,'c')],rgb('2a1a10'),4,t=0.3)
    c.rectangle(1250,400,670,20); c.set_source_rgb(*rgb('5c3d25')); c.fill()
    c.rectangle(0,640,SW,SH-640); c.set_source_rgb(*rgb('8a9a5a')); c.fill(); c.rectangle(0,638,SW,5); c.set_source_rgb(*LINE); c.fill()
    r=np.random.default_rng(3)
    for i in range(120):
        x,y=r.uniform(0,SW),r.uniform(650,SH); line(c,[(x,y),(x+4,y-14)],rgb('5f7040'),2.5)
def bg_field(c):
    bands(c,[rgb('8aa0b0'),rgb('a6b6bc'),rgb('c3c8c0'),rgb('ddd6c0')],0,600)
    mountains_front(c,rgb('6f7a80'),True,580)
    c.rectangle(0,640,SW,SH-640); c.set_source_rgb(*rgb('9a9c66')); c.fill(); c.rectangle(0,638,SW,5); c.set_source_rgb(*LINE); c.fill()
    r=np.random.default_rng(9)
    for i in range(140):
        x,y=r.uniform(0,SW),r.uniform(650,SH); line(c,[(x,y),(x+4,y-14)],rgb('6b6e40'),2.5)
def bg_cave_out(c):
    bands(c,[rgb('7d8fa0'),rgb('98a6ae'),rgb('b6bcb8'),rgb('d2cdbc')],0,640)
    shape(c,[(700,SH+320,'c'),(760,300),(980,120),(1300,90),(1700,180),(1920,160),(1920,SH+320,'c')],rgb('6b6258'),4)
    shape(c,[(1180,640,'c'),(1190,420),(1290,330,'c'),(1390,420),(1400,640,'c')],rgb('120d0a'),4,t=0.3)
    for k in range(8): line(c,[(900+k*120,200+k*30),(960+k*120,260+k*30)],rgb('514a42'),3)
    c.rectangle(0,640,SW,SH-640); c.set_source_rgb(*rgb('8a8070')); c.fill(); c.rectangle(0,638,SW,5); c.set_source_rgb(*LINE); c.fill()
def bg_forge(c):
    bands(c,[rgb('1a130e'),rgb('22180f'),rgb('2c1f14'),rgb('35261a')],0,640)
    r=np.random.default_rng(6)
    for i in range(30):
        x,y=r.uniform(0,SW),r.uniform(0,600); shape(c,[(x,y),(x+r.uniform(40,90),y+r.uniform(-10,10)),(x+r.uniform(30,70),y+r.uniform(30,60)),(x-10,y+40)],rgb('3c2c1e'),2)
    shape(c,[(760,640,'c'),(760,400),(960,250,'c'),(1160,400),(1160,640,'c')],rgb('5a4a3c'),5,t=0.4)
    for k in range(6):
        for j in range(4): shape(c,[(780+k*62,430+j*55),(830+k*62,430+j*55),(836+k*62,476+j*55),(776+k*62,476+j*55)],None,2)
    shape(c,[(860,640,'c'),(860,520),(960,470,'c'),(1060,520),(1060,640,'c')],rgb('2a120a'),4,t=0.4)
    c.rectangle(0,640,SW,SH-640); c.set_source_rgb(*rgb('3a2c20')); c.fill(); c.rectangle(0,638,SW,5); c.set_source_rgb(*LINE); c.fill()
    # 砧
    shape(c,[(1260,640,'c'),(1280,600,'c'),(1340,600,'c'),(1360,640,'c')],C['iron2'],4,t=0)
    shape(c,[(1200,560),(1400,560),(1440,575,'c'),(1360,600,'c'),(1260,600,'c'),(1210,580)],C['iron'],4)
def bg_lake(c):
    bands(c,[rgb('1d2433'),rgb('2a3245'),rgb('3d4558'),rgb('56596a'),rgb('7a7476'),rgb('9c8c80')],0,520)
    c.rectangle(0,520,SW,280); c.set_source_rgb(*rgb('141b26')); c.fill()
    for row in range(5):
        for k in range(-1,SW//80+2):
            x=k*80+(row%2)*40; y=545+row*44; c.new_path(); c.arc(x,y,24,math.pi*1.1,math.pi*1.9); c.set_source_rgb(*rgb('3c4a5c')); c.set_line_width(3); c.stroke()
    shape(c,[(120,SH+320,'c'),(180,700),(420,640),(900,610),(1400,630),(1760,690),(1840,SH+320,'c')],rgb('6c5e4c'),4)
    r=np.random.default_rng(4)
    for i in range(60):
        x=r.uniform(220,1720); y=r.uniform(650,780); line(c,[(x,y),(x+5,y-16)],rgb('8a5a6a'),3)
def bg_rock(c):
    bg_lake(c)
def bg_rag(c):
    bands(c,[rgb('1a0a08'),rgb('3a120c'),rgb('6a1e10'),rgb('9a3414'),rgb('c8601e'),rgb('e09a3a')],0,600)
    mountains_front(c,rgb('2a1410'),False,580)
    c.rectangle(0,640,SW,SH-640); c.set_source_rgb(*rgb('2a1a12')); c.fill(); c.rectangle(0,638,SW,5); c.set_source_rgb(*LINE); c.fill()
def bg_dawn(c):
    bands(c,[rgb('3a4a66'),rgb('5d6a86'),rgb('9a8aa0'),rgb('d8a690'),rgb('ecc79a'),rgb('f2dcb0')],0,600)
    mountains_front(c,rgb('5a5470'),True,600)
    c.rectangle(0,640,SW,SH-640); c.set_source_rgb(*rgb('d9d4c8')); c.fill(); c.rectangle(0,638,SW,5); c.set_source_rgb(*LINE); c.fill()

# ---------------- 文字 ----------------
TXT={}
KW={'b':(132,170,214),'r':(226,124,94),'g':(150,190,120),'n':(240,228,200)}
def segs(s):
    out=[];cur='n'
    for t in re.split(r'(\[/?[brg]\])',s):
        if not t: continue
        if t.startswith('[/'): cur='n';continue
        if t.startswith('['): cur=t[1];continue
        out.append((t,cur))
    return out
def text_img(key,lines,w,h):
    """lines: [(文字, 字体路径, 字号, y, dim)] → RGBA numpy"""
    if key in TXT: return TXT[key]
    im=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(im)
    for s,fp,sz,y,dim in lines:
        f=ImageFont.truetype(fp,sz); sg=segs(s); tw=sum(d.textlength(t,font=f) for t,_ in sg); x=w/2-tw/2
        for t,cc in sg:
            col=KW[cc] if not(dim and cc=='n') else (205,190,160)
            d.text((x,y),t,font=f,fill=col+(255,),stroke_width=0); x+=d.textlength(t,font=f)
    TXT[key]=np.array(im); return TXT[key]
def tag_img(zh,en):
    k=('tag',zh,en)
    if k in TXT: return TXT[k]
    fz=ImageFont.truetype(FZ,28); fe=ImageFont.truetype(FE,17)
    w=int(max(len(zh)*30,len(en)*10.5)+50); h=66
    im=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.polygon([(14,0),(w-14,0),(w-1,h/2),(w-14,h-1),(14,h-1),(0,h/2)],fill=(42,26,16,235),outline=(201,160,80,255))
    tw=d.textlength(zh,font=fz); d.text((w/2-tw/2,3),zh,font=fz,fill=(240,226,190,255))
    tw=d.textlength(en,font=fe); d.text((w/2-tw/2,40),en,font=fe,fill=(201,160,80,255))
    TXT[k]=np.array(im); return TXT[k]

# ---------------- 外框（原创：环链纹 + 木牌 + ᛏ） ----------------
def ringchain(c,y0,h,x0=0,x1=OW):
    c.rectangle(x0,y0,x1-x0,h); c.set_source_rgb(*WOOD2); c.fill()
    step=h*1.6; cy=y0+h/2; r=h*0.30; n=int((x1-x0)/step)+2
    for k in range(n):
        cx=x0+k*step
        for col,w in ((LINE,h*0.15),(GOLD2F,h*0.08)):
            c.new_path(); c.move_to(cx-step/2,cy); c.line_to(cx,cy-h*0.40); c.line_to(cx+step/2,cy); c.line_to(cx,cy+h*0.40); c.close_path(); c.set_source_rgb(*col); c.set_line_width(w); c.stroke()
    for k in range(n):
        cx=x0+k*step
        for col,w in ((LINE,h*0.16),(GOLDF,h*0.09)): c.new_path(); c.arc(cx,cy,r,0,7); c.set_source_rgb(*col); c.set_line_width(w); c.stroke()
    for yy in (y0,y0+h): c.rectangle(x0,yy-2,x1-x0,4); c.set_source_rgb(*GOLD2F); c.fill()
def tiwaz(c,cx,cy,R):
    c.new_path(); c.arc(cx,cy,R,0,7); c.set_source_rgb(*WOOD2); c.fill_preserve(); c.set_source_rgb(*GOLDF); c.set_line_width(5); c.stroke()
    c.new_path(); c.arc(cx,cy,R*0.80,0,7); c.set_source_rgb(*GOLD2F); c.set_line_width(2.5); c.stroke()
    for k in range(16):
        a=k*math.pi/8; circ(c,cx+R*0.9*math.cos(a),cy+R*0.9*math.sin(a),2.6,GOLDF)
    c.set_source_rgb(*GOLDF); c.set_line_width(R*0.16); c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(cx,cy-R*0.55); c.line_to(cx,cy+R*0.55); c.stroke(); c.move_to(cx-R*0.38,cy-R*0.18); c.line_to(cx,cy-R*0.55); c.line_to(cx+R*0.38,cy-R*0.18); c.stroke()
SX0,SX1,SY0,SY1=170,1270,862,1040
def make_base():
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,OW,OH); c=cairo.Context(s)
    c.set_source_rgb(*WOOD); c.paint(); ringchain(c,0,PY); ringchain(c,PY+PH,OH-PY-PH)
    return np.ndarray((OH,OW,4),np.uint8,s.get_data())[...,[2,1,0]].copy()
def make_ovl():
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,OW,OH); c=cairo.Context(s)
    ringchain(c,0,PY); ringchain(c,PY+PH,OH-PY-PH)
    c.rectangle(22,PY+14,OW-44,PH-28); c.set_source_rgb(*GOLD2F); c.set_line_width(3); c.stroke()
    c.rectangle(28,PY+20,OW-56,PH-40); c.set_source_rgba(*LINE,0.8); c.set_line_width(1.5); c.stroke()
    # 字幕木牌：压在画面底部，两侧露出动画
    c.rectangle(SX0,SY0,SX1-SX0,SY1-SY0); c.set_source_rgba(*WOOD,0.96); c.fill()
    r=np.random.default_rng(11)
    for i in range(10):
        yy=r.uniform(SY0+20,SY1-6); c.new_path(); c.move_to(SX0,yy)
        for x in range(SX0,SX1+40,40): c.line_to(min(x,SX1),yy+4*math.sin(x/150+i))
        c.set_source_rgba(0.12,0.07,0.04,r.uniform(0.25,0.5)); c.set_line_width(r.uniform(1,2)); c.stroke()
    c.save(); c.rectangle(SX0,SY0,SX1-SX0,18); c.clip(); ringchain(c,SY0,18,SX0,SX1); c.restore()
    c.rectangle(SX0,SY0,SX1-SX0,SY1-SY0); c.set_source_rgb(*GOLDF); c.set_line_width(3); c.stroke()
    c.rectangle(SX0+7,SY0+24,SX1-SX0-14,SY1-SY0-31); c.set_source_rgb(*GOLD2F); c.set_line_width(1.5); c.stroke()
    tiwaz(c,OW/2,OH-15,26); tiwaz(c,OW/2,15,22)
    a=np.ndarray((OH,OW,4),np.uint8,s.get_data()).copy(); al=a[...,3:4].astype(np.float32)/255
    rgbp=a[...,[2,1,0]].astype(np.float32); rgbs=np.where(al>0,rgbp/np.maximum(al,1e-6),0)
    return rgbs,al

import cairocffi as _c
BM=_c.Matrix(); BINV=_c.Matrix()
_man,_wolf=man,wolf
def _conv(o):
    for k_,v_ in list(o.items()):
        if isinstance(v_,tuple) and len(v_)==2: o[k_]=BINV.transform_point(*v_)
    return o
def man(c,*a,**k): return _conv(_man(c,*a,**k))
def wolf(c,*a,**k): return _conv(_wolf(c,*a,**k))
def sword_jaw(c,wl,k=1.0):
    (lx,ly),(ux,uy)=wl['lower'],wl['upper']
    a=math.atan2(ux-lx,-(uy-ly)); L=math.hypot(ux-lx,uy-ly)
    c.save(); c.translate(lx,ly); c.scale(k,k); sword_up(c,0,0,a,max(20,(L-30)/k)); c.restore()
def T(c,zh,en,x,y,side='L'):
    px,py=c.user_to_device(x,y); return (zh,en,px,py,side)
def D(zh,en,pt,side='L'):
    px,py=BM.transform_point(*pt); return (zh,en,px,py,side)
# ---------------- 镜头 ----------------
# 每个函数 f(c, lt, d) 在 1920×800 场景坐标下画，返回名签列表 [(zh,en,px,py)]
def s_night(c,lt,d,big=False):
    paintbg(c,'night',bg_night); stars(c,lt)
    for k in range(3):
        c.new_path(); smooth(c,[(0,430+k*26),(400,360+k*18+20*math.sin(lt*0.5+k)),(900,410+k*22),(1400,350+k*26+20*math.sin(lt*0.4)),(1920,400+k*18)],False)
        c.set_source_rgba(0.55,0.85,0.6,0.09); c.set_line_width(60-k*16); c.stroke()
    eye=seg(lt,1.0,2.0)
    wl=wolf(c,1330,1010,1300,dict(head=0.2+0.03*math.sin(lt*0.8),ears=0.1*seg(lt,1.0,1.6),tail=-0.5,jaw=0.08*seg(lt,2.5,3.5),eye=1),black=True)
    ex,ey=wl['eye']; glow(c,ex,ey,60+60*eye,(1,0.7,0.25),0.9*eye)
    mountains_front(c,rgb('3b4a5a'),True,560)
    shape(c,[(0,SH+320,'c'),(0,680),(600,660),(1200,680),(1920,665),(1920,SH+320,'c')],rgb('cfd3d4'),3.5)
    for i,xx in enumerate((140,260,380,500,620)):
        man(c,xx,700,240,P(nsh=0.15+0.9*(i==4)*seg(lt,1.4,2.2),nel=0.1,head=-0.25),helmet='wing' if i==1 else 'cone',hood=(i==3),**BLK)
    return [D("芬里尔","Fenrir",(ex-250,ey-110),'L')] if not big else []
def bg_redrune(c):
    bands(c,[rgb('2a120c'),rgb('3a1a10'),rgb('4a2214'),rgb('3a1a10'),rgb('2a120c')],0,SH)
    for r_ in (330,300): c.new_path(); c.arc(1200,400,r_,0,7); c.set_source_rgb(*rgb('8a5a2a')); c.set_line_width(4); c.stroke()
def s_stump(c,lt,d):
    paintbg(c,'redrune',bg_redrune)
    glow(c,1200,400,420,(1,0.6,0.25),0.3)
    a=lerp(1.0,2.55,seg(lt,0.3,1.8))
    man(c,820,1500,1300,P(nsh=a,nel=0.05,fsh=-0.1,fel=0.4,head=-0.1-0.15*seg(lt,0.3,1.8)),stump=True,**TYR)
    return []
def s_title(c,lt,d):
    s_night(c,lt+6,d,big=True)
    c.set_source_rgba(0,0,0,0.35); c.paint()
    a=seg(lt,0.2,1.0); c.save(); c.translate(SW/2,SH/2); sc=0.9+0.1*a; c.scale(sc,sc)
    w,h=1000,300
    c.new_path(); c.move_to(-w/2+40,-h/2); c.line_to(w/2-40,-h/2); c.line_to(w/2,0); c.line_to(w/2-40,h/2); c.line_to(-w/2+40,h/2); c.line_to(-w/2,0); c.close_path()
    c.set_source_rgba(*WOOD2,0.95*a); c.fill_preserve(); c.set_source_rgba(*GOLDF,a); c.set_line_width(6); c.stroke()
    c.new_path(); c.move_to(-w/2+56,-h/2+16); c.line_to(w/2-56,-h/2+16); c.line_to(w/2-18,0); c.line_to(w/2-56,h/2-16); c.line_to(-w/2+56,h/2-16); c.line_to(-w/2+18,0); c.close_path(); c.set_source_rgba(*GOLD2F,a); c.set_line_width(2.5); c.stroke()
    c.restore()
    return [('__title__',a)]
def s_loki(c,lt,d):
    paintbg(c,'jotun',bg_jotun)
    o1=man(c,800,GY,560,P(nsh=0.4+0.2*math.sin(lt*1.5),nel=0.9,fsh=-0.2,head=0.05*math.sin(lt)),**LOKI)
    o2=man(c,1180,GY,700,P(nsh=0.3,nel=0.4,fsh=-0.1,head=0.04*math.sin(lt*0.7+1)),flip=True,**ANGR)
    return [D("洛基","Loki",o1['head'],'L'),D("安格尔伯达","Angrboda",o2['head'],'R')]
def s_kids(c,lt,d):
    paintbg(c,'jotun',bg_jotun)
    man(c,330,GY,520,P(nsh=0.3,nel=0.5),**LOKI); man(c,1690,GY,640,P(nsh=0.3,nel=0.4),flip=True,**ANGR)
    tags=[]
    a1,a2,a3=seg(lt,0.2,0.8),seg(lt,1.4,2.0),seg(lt,2.6,3.2)
    if a1>0:
        c.save(); c.translate(700,GY); c.scale(a1,a1); w1=wolf(c,0,0,380,trot(lt*6) if lt<1 else dict(head=-0.2,tail=0.3*math.sin(lt*6))); c.restore(); tags.append(D("芬里尔","Fenrir",w1['eye'],'L'))
    if a2>0:
        c.save(); c.translate(1000,GY-80); c.scale(a2,a2); serpent(c,-160,0,320,lt*3,30); c.restore(); tags.append(T(c,"耶梦加得","Jörmungandr",1150,GY-90,'R'))
    if a3>0:
        c.save(); c.translate(1340,GY); c.scale(a3,a3); oh=man(c,0,0,520,P(nsh=0.2,nel=0.3,head=0.0),**HEL); c.restore(); tags.append(D("海拉","Hel",oh['head'],'R'))
    for t0,x,y in ((0.2,700,GY-100),(1.4,1000,GY-80),(2.6,1340,GY-260)): sparks(c,x,y,lt-t0,18,seed=int(x))
    return tags
def bg_stone(c):
    bands(c,[rgb('16121a'),rgb('1f1924'),rgb('2a2230'),rgb('1f1924')],0,SH)
def s_prophecy(c,lt,d):
    paintbg(c,'stone',bg_stone)
    pulse=0.5+0.5*math.sin(lt*3)
    glow(c,960,420,500,(0.9,0.3,0.2),0.25+0.15*pulse)
    st=[(780,780,'c'),(770,300),(820,140),(960,90),(1100,140),(1150,300),(1140,780,'c')]
    shape(c,st,rgb('8a8278'),5)
    c.new_path(); smooth(c,[(800,760),(796,300),(840,170),(960,124),(1080,170),(1124,300),(1120,760)],False); c.set_source_rgb(*rgb('a8402a')); c.set_line_width(26); c.stroke()
    c.new_path(); smooth(c,[(800,760),(796,300),(840,170),(960,124),(1080,170),(1124,300),(1120,760)],False); c.set_source_rgb(*LINE); c.set_line_width(2); c.set_dash([10,14]); c.stroke(); c.set_dash([])
    n=seg(lt,0.3,3.0)*12
    for k,ch in enumerate('fenriz'+'tyrfen'.replace('y','i')):
        row,col_=divmod(k,6); x=846+col_*44; y=300+row*150
        if k<n:
            glow(c,x+8,y+40,40,(1,0.5,0.25),0.25)
            rune(c,ch,x,y,80,rgb('f2b060'),6,min(1,n-k))
        else: rune(c,ch,x,y,80,rgb('5e574e'),6)
    return []
def s_odin_sea(c,lt,d):
    paintbg(c,'sea',bg_sea)
    for row in range(4):
        for k in range(-1,SW//60+2):
            x=k*60+(row%2)*30+((lt*30)%60); y=540+row*60; c.new_path(); c.arc(x,y,20,math.pi,2*math.pi); c.set_source_rgb(*rgb('a9b8bf')); c.set_line_width(3.5); c.stroke()
    th=seg(lt,0.6,1.3)
    o=man(c,300,370,420,P(nsh=lerp(-0.6,2.6,th),nel=lerp(0.6,0.1,th),fsh=-0.1,fel=0.3,fgrip=True,head=-0.05),**ODIN)
    hx,hy=o['hand_f']; spear(c,hx,hy,440)
    u=seg(lt,1.1,3.0)
    if u<1:
        sx=lerp(o['hand_n'][0],1450,u); sy=lerp(o['hand_n'][1],560,u)-math.sin(u*math.pi)*380
        c.save(); c.translate(sx,sy); c.rotate(u*6); serpent(c,-120,0,240,lt*8,26); c.restore()
    dust(c,1450,560,lt-3.0,10,2.0,rgb('dfe8ea'))
    if lt>3.0:
        a=1-seg(lt,3.0,4.0); 
        for k in range(8): circ(c,1450+math.cos(k)*80*(lt-3),540-abs(math.sin(k*1.3))*160*(lt-3)+200*(lt-3)**2,10,rgb('dfe8ea'),a)
    return [D("奥丁","Odin",o['head'],'R')] if lt>0.2 else []
def s_hel(c,lt,d):
    paintbg(c,'mist',bg_mist)
    y=lerp(560,900,seg(lt,0.5,4.0))
    oh=man(c,960,y,560,P(nsh=0.3,nel=0.3,fsh=-0.3,fel=0.3,head=0.1),**HEL)
    for k in range(5):
        x0=((lt*(30+k*12)+k*400)%2400)-400; yy=420+k*80
        c.new_path(); smooth(c,[(x0,yy),(x0+300,yy-30),(x0+700,yy+10),(x0+1100,yy-20)],False); c.set_source_rgba(0.95,0.97,0.98,0.35); c.set_line_width(70); c.stroke()
    return [D("海拉","Hel",oh['head'],'R')]
def s_bring(c,lt,d):
    paintbg(c,'asgard',bg_asgard)
    x=lerp(150,900,lt/d); ph=lt*6.5
    man(c,x,GY+bob(ph),560,walk(ph),**THOR)
    wolf(c,x+330,GY,360,trot(ph*1.2,head=-0.1))
    man(c,x-260,GY+bob(ph+1),540,walk(ph+1),**FREYR)
    return [T(c,"阿斯加德","Asgard",1460,330,'L')]
def s_hall_hide(c,lt,d):
    paintbg(c,'hall',bg_hall)
    for i,(xx,pre,sz) in enumerate(((1560,FREYR,400),(1680,HEIM,380),(300,THOR,410))):
        man(c,xx,800,sz,P(nsh=0.25,nel=2.3,fsh=0.1,fel=0.4,head=0.05*math.sin(lt*9+i)),**pre)
    hall_light(c,lt)
    wolf(c,1000,GY,520,dict(head=0.25+0.15*math.sin(lt*3),tail=0.3*math.sin(lt*4),ears=0.1))
    return [T(c,"芬里尔","Fenrir",1150,300,'R')] 
def tyr_feed(c,lt,walkin=True,feed=1.0,pat=0.0):
    return None
def s_hall_feed(c,lt,d):
    paintbg(c,'hall',bg_hall)
    for i,(xx,pre,sz) in enumerate(((1560,FREYR,400),(1680,HEIM,380),(300,THOR,410))):
        man(c,xx,800,sz,P(nsh=0.25,nel=2.3,fsh=0.1,fel=0.4,head=0.04*math.sin(lt*9+i)),**pre)
    hall_light(c,lt)
    w=seg(lt,0,2.0); x=lerp(200,640,w); ph=lt*6.5
    pose=walk(ph,amp=0.38*(1-w)) if w<1 else P()
    arm=seg(lt,2.0,3.0); pose.update(nsh=lerp(pose.get('nsh',0.1),1.30,arm),nel=lerp(0.25,0.14,arm),head=0.06*arm)
    o=man(c,x,GY+(bob(ph) if w<1 else 0),600,pose,**TYR)
    hx,hy=o['hand_n']; meat(c,hx+34,hy-4,0.8)
    wl=wolf(c,1360,GY,560,dict(head=lerp(0.2,-0.46,seg(lt,2.4,3.4)),ears=0.1,tail=0.3*math.sin(lt*5)*seg(lt,2.6,3.0)))
    return [D("提尔","Tyr",o['head'],'L')]
def s_hall_snap(c,lt,d):
    paintbg(c,'hall',bg_hall)
    hall_light(c,lt)
    j=0.6*math.sin(math.pi*seg(lt,0.4,1.0))
    eaten=lt>0.75
    pat=seg(lt,1.6,2.6); 
    o=man(c,640,GY,600,P(nsh=lerp(1.30,1.55,pat),nel=lerp(0.14,0.6,pat)+0.08*math.sin(lt*8)*pat,head=0.06),**TYR)
    hx,hy=o['hand_n']
    if not eaten: meat(c,hx+34,hy-4,0.8)
    wl=wolf(c,1360-80*seg(lt,0.3,0.6),GY,560,dict(head=lerp(-0.46,0.05,seg(lt,1.0,1.6)),jaw=j,ears=0.1,tail=0.4*math.sin(lt*7)))
    return []
def s_grow(c,lt,d):
    paintbg(c,'hall',bg_hall); hall_light(c,lt,0.3)
    step=min(2,int(lt/1.5)); L=[560,900,1400][step]; age=lt-step*1.5
    sc=1+0.08*math.exp(-age*6)*math.sin(age*30) if step>0 else 1
    o=man(c,420,GY,600,P(nsh=0.1,nel=0.2,head=-0.12*step),**TYR)
    c.save(); c.translate(1300,GY); c.scale(sc,sc); wolf(c,0,0,L,dict(head=0.3 if step==2 else 0.1,tail=-0.2)); c.restore()
    if step>0: dust(c,1300,GY,age,12,1.6)
    return []
def s_council(c,lt,d):
    paintbg(c,'hall',bg_hall)
    xs=[(420,THOR),(640,FREYR),(1280,HEIM),(1500,TYR)]
    for i,(xx,pre) in enumerate(xs):
        man(c,xx,GY+60,520,P(nsh=0.5+0.3*math.sin(lt*2+i),nel=0.8,head=0.12*math.sin(lt*1.6+i*1.7)),flip=(xx>960),**pre)
    od=man(c,960,GY+40,600,P(nsh=0.3,nel=0.4,fsh=0.6,fel=0.4,fgrip=True,head=0.0),**ODIN)
    shape(c,[(200,SH+320,'c'),(200,640),(1720,640),(1720,SH+320,'c')],rgb('5c3d25'),4,t=0)
    c.rectangle(200,640,1520,24); c.set_source_rgb(*rgb('7a5030')); c.fill()
    hall_light(c,lt,0.5)
    return [D("奥丁","Odin",od['head'],'R')]
def links_burst(c,cx,cy,age,n=22,seed=1,r=18):
    rr=np.random.default_rng(seed)
    for i in range(n):
        a=rr.uniform(0,2*math.pi); v=rr.uniform(300,800)
        x=cx+math.cos(a)*v*age; y=cy+math.sin(a)*v*age+700*age*age
        y=min(y,GY+10)
        c.save(); c.translate(x,y); c.rotate(age*rr.uniform(-12,12)); c.new_path(); c.save(); c.scale(1,0.6); c.arc(0,0,r,0,7); c.restore(); c.set_source_rgb(*LINE); c.set_line_width(r*0.55); c.stroke()
        c.new_path(); c.save(); c.scale(1,0.6); c.arc(0,0,r,0,7); c.restore(); c.set_source_rgb(*C['iron']); c.set_line_width(r*0.3); c.stroke(); c.restore()
def wolf_chained(c,lt,x,L,r,broken_at=None,arch=0.0,shake=0.0):
    jx=shake*math.sin(lt*45)*10
    c.save(); c.translate(x+jx,GY); c.rotate(-arch*0.06*math.sin(lt*14) if arch else 0)
    wl=wolf(c,0,0,L,dict(head=0.1-0.3*arch,jaw=0.25*arch,ears=-0.2,tail=-0.3))
    c.restore()
    v=wl['v']; nx,ny=wl['neck']; bx,by=wl['belly']; hx,hy=wl['hind']
    if broken_at is None or lt<broken_at:
        for cx,cy,rx,ry in ((nx+10,ny+20,0.6*v,1.3*v),(bx,by,0.55*v,1.1*v),(hx+10,hy+30,0.5*v,1.0*v)):
            pts=[(cx+rx*math.cos(a),cy+ry*math.sin(a)) for a in np.linspace(0,2*math.pi,24)]
            chain(c,pts,r)
        chain(c,[(nx-40,ny+1.2*v),(nx-300,GY-20),(200,GY-10)],r)
    else:
        age=lt-broken_at
        for cx,cy in ((nx,ny),(bx,by),(hx,hy)): links_burst(c,cx,cy,age,14,int(cx),r)
        if age<0.15: glow(c,bx,by,500,(1,0.95,0.8),0.8*(1-age/0.15))
        for cx in (nx,bx,hx): dust(c,cx,GY,age,8,1.4)
    return wl
def gods_left(c,lt,scare=0.0,n=3):
    for i,(xx,pre) in enumerate(((140,ODIN),(300,THOR),(460,FREYR))[:n]):
        man(c,xx-scare*60,GY,480,P(nsh=0.6+0.7*scare,nel=0.6+1.2*scare,fsh=0.2,head=-0.1*scare+0.05*math.sin(lt*7+i)*scare),**pre)
def s_chain1(c,lt,d):
    paintbg(c,'field',bg_field); gods_left(c,lt)
    wolf_chained(c,lt,1220,880,16)
    return [T(c,"莱丁","Lœðingr",720,560,'R')]
def s_break1(c,lt,d):
    paintbg(c,'field',bg_field); gods_left(c,lt,seg(lt,1.2,1.6))
    wolf_chained(c,lt,1220,880,16,broken_at=1.3,arch=seg(lt,0.2,1.2),shake=1.0 if lt<1.3 else 0)
    return []
def s_chain2(c,lt,d):
    paintbg(c,'field',bg_field); gods_left(c,lt)
    wolf_chained(c,lt,1240,960,24)
    return [T(c,"德罗米","Drómi",720,520,'R')]
def s_break2(c,lt,d):
    paintbg(c,'field',bg_field); gods_left(c,lt,seg(lt,1.4,1.8))
    wolf_chained(c,lt,1240,960,24,broken_at=1.5,arch=seg(lt,0.2,1.5),shake=1.0 if lt<1.5 else 0)
    return []
def s_proud(c,lt,d):
    paintbg(c,'field',bg_field)
    gods_left(c,lt,0.8)
    wolf(c,1260,GY,1080,dict(head=-0.05,tail=0.3*math.sin(lt*2)-0.1,ears=0.15))
    for i in range(16):
        rr=np.random.default_rng(i); x=rr.uniform(700,1800); c.save(); c.translate(x,GY+rr.uniform(0,30)); c.rotate(rr.uniform(0,3)); c.new_path(); c.save(); c.scale(1,0.6); c.arc(0,0,20,0,7); c.restore(); c.set_source_rgb(*C['iron2']); c.set_line_width(8); c.stroke(); c.restore()
    return []
def s_skirnir(c,lt,d):
    paintbg(c,'caveout',bg_cave_out)
    man(c,240,GY,560,P(nsh=1.4,nel=0.05,fsh=0.6,fel=0.4,fgrip=True),**ODIN)
    x=lerp(520,1230,seg(lt,0.3,d)); ph=lt*6.5
    os_=man(c,x,GY-20*seg(lt,2.5,d)+bob(ph),540,walk(ph),**SKIR)
    return [D("斯基尔尼尔","Skírnir",os_['head'],'L')] if lt>0.3 else []
def s_forge(c,lt,d,items=None):
    paintbg(c,'forge',bg_forge)
    fl=0.85+0.15*math.sin(lt*13)
    glow(c,960,580,700,(1,0.55,0.2),0.45*fl); flame(c,960,640,80,150,lt)
    for k,(xx,flip) in enumerate(((1180,False),(1500,True))):
        ph=(lt*2.4+k*0.5)%1
        arm=2.7 if ph<0.5 else lerp(2.7,1.0,E((ph-0.5)/0.25)) if ph<0.75 else 1.0
        o=man(c,xx,GY,360,P(nsh=arm,nel=0.2,fsh=0.6,fel=0.6,handgrip=True),flip=flip,**DWARF)
        hx,hy=o['hand_n']; hammer(c,hx,hy,(-1 if flip else 1)*(arm-1.2)*-0.8+(-1.4 if not flip else 1.4),0.7)
        if 0.75<ph<0.95: sparks(c,1300,560,(ph-0.75)*3,12,seed=k*31+int(lt))
    tags=[T(c,"矮人","Dwarves",1340,380,'L')] if items is None else []
    return tags
ITEMS=[("猫的脚步声","cat"),("女人的胡须","beard"),("山的根","root"),("熊的筋","bear"),("鱼的呼吸","fish"),("鸟的口水","bird")]
def icon(c,kind,x,y,r,a):
    c.save(); c.translate(x,y)
    c.new_path(); c.arc(0,0,r,0,7); c.set_source_rgba(*WOOD2,0.85*a); c.fill_preserve(); c.set_source_rgba(*GOLDF,a); c.set_line_width(5); c.stroke()
    col=(0.95,0.88,0.7); c.set_source_rgba(*col,a)
    if kind=='cat':
        circ(c,0,14,r*0.3,col,a)
        for dx,dy in ((-30,-20),(-12,-36),(12,-36),(30,-20)): circ(c,dx*r/80,dy*r/80,r*0.12,col,a)
    elif kind=='beard':
        for k in range(-3,4): c.move_to(k*10,-30); c.curve_to(k*14,0,k*6,20,k*12,40); c.set_source_rgba(*col,a); c.set_line_width(5); c.stroke()
    elif kind=='root':
        c.move_to(-40,0); c.line_to(0,-40); c.line_to(40,0); c.close_path(); c.set_source_rgba(*col,a); c.fill()
        for k in (-20,0,20): c.move_to(k,0); c.curve_to(k-10,20,k+10,30,k,46); c.set_line_width(4); c.stroke()
    elif kind=='bear':
        circ(c,0,4,r*0.38,col,a); circ(c,-26,-24,r*0.14,col,a); circ(c,26,-24,r*0.14,col,a)
    elif kind=='fish':
        c.move_to(-40,0); c.curve_to(-10,-26,20,-20,30,0); c.curve_to(20,20,-10,26,-40,0); c.close_path(); c.set_source_rgba(*col,a); c.fill()
        for k,(bx,by) in enumerate(((40,-24),(52,-44),(40,-60))): c.new_path(); c.arc(bx,by,5+k,0,7); c.set_line_width(3); c.stroke()
    elif kind=='bird':
        c.move_to(-44,0); c.curve_to(-20,-30,0,-10,0,0); c.curve_to(0,-10,20,-30,44,0); c.set_source_rgba(*col,a); c.set_line_width(6); c.stroke()
        c.move_to(0,14); c.curve_to(8,26,8,34,0,38); c.curve_to(-8,34,-8,26,0,14); c.fill()
    c.restore()
def s_items(c,lt,d,i0=0):
    tags=s_forge(c,lt,d,items=True); res=[]
    for k in range(2):
        idx=i0+k; t0=0.3+k*1.6; a=seg(lt,t0,t0+0.5); u=seg(lt,t0+0.6,t0+2.8)
        x=lerp(560+k*800,960,u); y=lerp(220,560,u)-math.sin(u*math.pi)*120; r=70*(1-0.7*u)
        if a>0 and u<1:
            glow(c,x,y,r*2.2,(1,0.85,0.5),0.4*a); icon(c,ITEMS[idx][1],x,y,r,a)
            res.append(('__item__',ITEMS[idx][0],x,y+r+14,a*(1-u)))
    return tags+res
def s_gone(c,lt,d):
    s_forge(c,lt,d,items=True); res=[]
    for k in range(6):
        x=360+k*240; y=260; a=1-seg(lt,0.8+k*0.25,1.6+k*0.25)
        if a>0: icon(c,ITEMS[k][1],x,y,56,a); sparks(c,x,y,lt-(0.8+k*0.25),10,seed=k)
    return res
def s_ribbon(c,lt,d):
    s_forge(c,lt,d,items=True)
    L=seg(lt,0.2,2.4); pts=[(600+i*40*L*1.8, 360+40*math.sin(i*0.6+lt*3)) for i in range(18)]
    glow(c,960,360,600,(1,0.85,0.45),0.35*L); ribbon(c,pts,14,1.0)
    return [T(c,"格莱普尼尔","Gleipnir",600,330,'L')]
def bg_lyngvi(c): bg_lake(c)
def s_lyngvi(c,lt,d):
    paintbg(c,'lake',bg_lake)
    ph=lt*6; x=lerp(300,620,seg(lt,0,d))
    for i,(xx,pre) in enumerate(((x-280,ODIN),(x-130,THOR),(x,TYR))):
        man(c,xx,GY+bob(ph+i),460,walk(ph+i,0.3),**pre)
    wolf(c,x+700,GY,1000,trot(ph*0.8,head=0.0))
    return [T(c,"林格维岛","Lyngvi",300,700,'R'),T(c,"阿姆斯瓦特尼尔湖","Ámsvartnir",1500,560,'R')]
def s_suspicious(c,lt,d):
    paintbg(c,'lake',bg_lake)
    sq=seg(lt,0.8,1.4)
    c.save(); c.translate(2150,1900); wl=wolf(c,0,0,2600,dict(head=0.3,ears=-0.3*sq,eye=1)); c.restore()
    ex,ey=wl['eye']; c.new_path(); c.rectangle(ex-60,ey-40,140,40*sq); c.set_source_rgb(*C['slate']); c.fill()
    ribbon(c,[(200,700),(500,640),(800,690),(1000,620)],14)
    return []
def s_demand(c,lt,d):
    paintbg(c,'lake',bg_lake)
    talk=0.15+0.4*abs(math.sin(lt*6))*(1 if 0.3<lt<3.2 else 0)
    c.save(); c.translate(2150,1900); wolf(c,0,0,2600,dict(head=0.3,jaw=talk,ears=-0.2)); c.restore()
    return []
def s_look(c,lt,d):
    paintbg(c,'lake',bg_lake)
    for i,(xx,pre) in enumerate(((300,ODIN),(560,THOR),(820,FREYR),(1080,HEIM),(1340,TYR))):
        turn=math.sin(lt*2.2+i*1.3)>0
        man(c,xx,GY,520,P(nsh=0.2,nel=0.5+0.4*(i%2),head=0.08*math.sin(lt*3+i)),flip=turn and i!=4,**pre)
    wolf(c,1720,GY,700,dict(head=0.1,ears=-0.2))
    return []
WP=dict(jaw=0.5,head=0.42,fl1=0.55,fl2=-0.35,fr1=0.35,fr2=-0.25,hl1=-0.7,hl2=1.0,hr1=-0.5,hr2=0.9,tail=-0.5,ears=-0.3)
_probe={}
def tyr_bind_pose(reach): return P(nsh=lerp(0.2,1.40,reach),nel=lerp(0.4,0.06,reach),fsh=-0.25,fel=0.45,nhip=0.28*reach,nkn=-0.18*reach,fhip=-0.18*reach,fkn=0.12*reach,head=0.06)
def s_bind(c,lt,d,mode='reach'):
    paintbg(c,'lake',bg_lake)
    if 'w' not in _probe:
        s2,c2=surf(); o=_man(c2,700,GY,620,tyr_bind_pose(1)); hx,hy=o['hand_n']; wl=_wolf(c2,0,0,900,WP)
        _probe['w']=(hx+24-wl['mouth'][0], hy+4-wl['mouth'][1])
    wx,wy=_probe['w']
    reach=seg(lt,0.3,2.2) if mode=='reach' else 1.0
    tight=seg(lt,0.2,3.5) if mode=='struggle' else 0.0
    shake=(math.sin(lt*38)*8*tight) if mode=='struggle' else 0
    jaw=0.5
    if mode=='bite': jaw=lerp(0.5,0.0,seg(lt,0.5,0.62))
    c.save(); c.translate(shake,0); wl=wolf(c,wx,wy,900,dict(WP,jaw=jaw,head=WP['head']+0.05*math.sin(lt*30)*tight)); c.restore()
    v=wl['v']; nx,ny=wl['neck']; bx,by=wl['belly']; hx2,hy2=wl['hind']; k=1-0.2*tight; g=1+0.8*tight*(0.5+0.5*math.sin(lt*10))
    loop(c,nx+10,ny+20,0.55*v*k,1.25*v*k,-0.5,g=g); loop(c,bx,by,0.45*v*k,1.0*v*k,0.1,g=g); loop(c,hx2+20,hy2+40,0.4*v*k,0.9*v*k,0.25,g=g)
    th=man(c,300,GY,580,P(nsh=1.05,nel=0.3,fsh=0.9,fel=0.45,handgrip=True,fgrip=True,nhip=0.25,nkn=-0.1,fhip=-0.25,fkn=0.1,body=0.12+0.06*tight),**THOR)
    p1,p2=th['hand_f'],th['hand_n']
    ribbon(c,[(nx-20,ny+1.2*v),(nx-260,ny+240),(p2[0]+60,p2[1]+20),p2,p1,(p1[0]-110,p1[1]+80),(60,GY+20)],11,g)
    x=lerp(560,700,reach) if mode=='reach' else 700
    o=man(c,x,GY,620,tyr_bind_pose(reach),**TYR)
    tags=[]
    if mode=='reach': tags=[D("提尔","Tyr",o['head'],'L')]
    return tags
def s_reach(c,lt,d): return s_bind(c,lt,d,'reach')
def s_struggle(c,lt,d): return s_bind(c,lt,d,'struggle')
def s_bite(c,lt,d):
    if lt<0.62: return s_bind(c,lt,d,'bite')
    c.set_source_rgb(0,0,0); c.paint()
    if lt<0.75: c.set_source_rgba(1,0.95,0.85,1-(lt-0.62)/0.13); c.paint()
    return [('__shake__',1-seg(lt,0.62,1.2))]
def s_laugh(c,lt,d):
    paintbg(c,'lake',bg_lake)
    for i,(xx,pre) in enumerate(((240,ODIN),(470,THOR),(1450,FREYR),(1680,HEIM))):
        b=abs(math.sin(lt*8+i))
        man(c,xx,GY+b*6,500,P(nsh=0.9,nel=1.6,fsh=0.6,fel=1.4,head=-0.25*b,body=-0.05*b),flip=(xx>960),**pre)
    man(c,960,GY,620,P(nsh=0.9,nel=1.4,fsh=0.8,fel=1.3,head=0.18),stump=True,eye_closed=True,**TYR)
    return []
def s_rock(c,lt,d):
    paintbg(c,'lake',bg_lake)
    dn=seg(lt,0.8,3.2)
    wolf(c,1250,GY+170,1150,dict(LIE,head=0.25,jaw=0.1,ears=-0.3))
    ribbon(c,[(980,560),(760,620),(560,640+dn*80),(420,660+dn*120)],12)
    shape(c,[(300,640+dn*140,'c'),(330,540+dn*140),(440,500+dn*140),(560,550+dn*140),(580,640+dn*140,'c')],rgb('7d7468'),4)
    c.rectangle(0,700,SW,420); c.set_source_rgb(*rgb('6c5e4c')); c.fill()
    man(c,180,GY+20,460,P(nsh=lerp(2.6,1.0,(lt*1.6)%1),nel=0.2,handgrip=True),**THOR)
    if (lt*1.6)%1>0.85: dust(c,430,700,((lt*1.6)%1-0.85)*3,8,1.2)
    return [T(c,"巨石 吉约尔","Gjöll",580,560+dn*140,'R')]
def s_sword(c,lt,d):
    paintbg(c,'lake',bg_lake)
    c.save(); c.translate(2150,1880); wl=wolf(c,0,0,2500,dict(head=0.3,jaw=0.75,ears=-0.3)); c.restore()
    a=seg(lt,0.3,1.3)
    if a<1:
        (lx,ly)=wl['lower']; c.save(); c.translate(-(1-a)**2*900,0); sword_jaw(c,wl,2.2); c.restore()
    else: sword_jaw(c,wl,2.2)
    if 1.3<lt<1.6: sparks(c,*wl['lower'],(lt-1.3)*2,14,seed=3)
    return []
def s_river(c,lt,d):
    paintbg(c,'lake',bg_lake)
    wl=wolf(c,1250,GY+170,1150,dict(LIE,head=0.25,jaw=0.7,ears=-0.3))
    mx,my=wl['mouth']; sword_jaw(c,wl)
    L=seg(lt,0.2,3.0)
    pts=[(mx-i*60*L*1.2, my+40+i*24*L+12*math.sin(i*0.8-lt*5)) for i in range(16)]
    line(c,pts,LINE,30); line(c,pts,rgb('6f9cb8'),22)
    for i in range(0,15,2): line(c,[pts[i],pts[i+1]],rgb('d6e6ee'),4)
    return [T(c,"期望之河 凡","Ván",pts[-1][0],pts[-1][1],'L')] if L>0.8 else []
def s_wait(c,lt,d):
    paintbg(c,'night',bg_night); stars(c,lt)
    c.rectangle(0,640,SW,480); c.set_source_rgb(*rgb('141b26')); c.fill()
    shape(c,[(120,SH+320,'c'),(180,700),(420,640),(900,610),(1400,630),(1760,690),(1840,SH+320,'c')],rgb('3c342c'),4)
    wl=wolf(c,1250,GY+170,1150,dict(LIE,head=0.25,jaw=0.7,ears=-0.3,eye=1))
    mx,my=wl['mouth']; sword_jaw(c,wl)
    ex,ey=wl['eye']; glow(c,ex,ey,50,(1,0.7,0.25),0.6+0.2*math.sin(lt*2))
    return []
def s_ragbreak(c,lt,d):
    paintbg(c,'rag',bg_rag)
    for i in range(60):
        rr=np.random.default_rng(i); x=(rr.uniform(0,SW)+lt*rr.uniform(20,60))%SW; y=(rr.uniform(0,SH)-lt*rr.uniform(10,40))%SH
        circ(c,x,y,rr.uniform(2,4),(1,0.6,0.3),0.6)
    j=lerp(0.3,1.15,seg(lt,1.0,2.6))
    shk=8*math.sin(lt*40)*(1-seg(lt,0.9,1.4))
    c.save(); c.translate(shk,0); wl=wolf(c,1350,GY+420,1500,dict(head=0.25,jaw=j,ears=0.2),black=True); c.restore()
    if lt<1.0: loop(c,wl['neck'][0],wl['neck'][1],120,220,-0.4)
    else:
        age=lt-1.0
        for k in range(8): ribbon(c,[(wl['neck'][0]+math.cos(k)*age*500,wl['neck'][1]+math.sin(k)*age*300),(wl['neck'][0]+math.cos(k)*age*700+30,wl['neck'][1]+math.sin(k)*age*400+40)],8,max(0,1-age))
    glow(c,*wl['eye'],80,(1,0.6,0.2),0.9)
    return [T(c,"诸神黄昏","Ragnarök",380,160,'R')]
def s_odin_vidar(c,lt,d):
    paintbg(c,'rag',bg_rag)
    wl=wolf(c,1450,GY+380,1400,dict(head=0.25,jaw=1.0 if lt<2.2 else lerp(1.0,1.4,seg(lt,2.4,3.4)),ears=0.2),black=True)
    mx,my=wl['mouth']
    u=seg(lt,0.2,1.6); ph=lt*7
    od=None
    if u<1: od=man(c,lerp(200,mx-60,u),GY-u*200+bob(ph),lerp(420,200,u),walk(ph,fgrip=True),**ODIN)
    if lt>2.0:
        v=seg(lt,2.0,2.8); ov=man(c,lerp(300,mx-200,v),GY,520,P(nsh=1.4,nel=-0.6,nhip=0.9*v,nkn=-0.3,head=-0.1),**VIDAR)
        return [D("维达","Víðarr",ov['head'],'L')]
    return [D("奥丁","Odin",od['head'],'L')] if od and u<0.8 else []
def s_garm(c,lt,d):
    paintbg(c,'rag',bg_rag)
    lunge=seg(lt,1.4,2.2)
    o=man(c,560+60*lunge,GY,620,P(nsh=lerp(2.4,1.5,lunge),nel=0.1,handgrip=True,fsh=0.6,fel=0.9,nhip=0.3*lunge,fhip=-0.3*lunge),stump=False,**TYR)
    hx,hy=o['hand_n']; sword_up(c,hx,hy,lerp(0.3,1.4,lunge),260)
    C['slate']=rgb('7a3a26'); C['slate2']=rgb('5a2a1a')
    wolf(c,1560-80*lunge,GY,820,dict(head=0.1,jaw=0.5,ears=-0.3,fl1=0.4*lunge,hl1=-0.6))
    C['slate']=rgb('6d7677'); C['slate2']=rgb('535b5d')
    return [T(c,"加尔姆","Garmr",1620,320,'R'),D("提尔","Tyr",o['head'],'L')]
def s_moral(c,lt,d):
    paintbg(c,'dawn',bg_dawn)
    glow(c,960,560,700,(1,0.85,0.55),0.45)
    a=seg(lt,0.8,2.2)
    man(c,960,GY,640,P(nsh=0.9,nel=1.2,fsh=-0.1,fel=0.3,head=-0.05),stump=True,**TYR)
    glow(c,1400,190,180,(1,0.85,0.4),0.7*a); rune(c,'t',1400,110,170,rgb('fbe3a0'),16,a)
    return []

# ---------------- 分镜表 ----------------
S=[
(4.5,s_night,("众神真正害怕的","是一只[r]狼[/r]"),("What the gods truly feared","was a [r]wolf[/r]."),(1.0,1.08,1150,350)),
(4.5,s_stump,("为了绑住它","战神付出了[r]一只手[/r]"),("To bind it,","the god of war gave [r]one hand[/r]."),(1.0,1.05,1100,400)),
(4.0,s_title,("",""),("",""),(1,1,960,400)),
(4.5,s_loki,("诡计之神[b]洛基[/b]","和女巨人[b]安格尔伯达[/b]"),("[b]Loki[/b], the trickster,","and the giantess [b]Angrboda[/b]"),(1.0,1.05,960,400)),
(5.0,s_kids,("生下三个孩子：小狼[b]芬里尔[/b]","巨蛇[b]耶梦加得[/b] 和半生半死的[b]海拉[/b]"),("had three children: the wolf [b]Fenrir[/b],","the serpent [b]Jörmungandr[/b], and half-dead [b]Hel[/b]."),(1.0,1.0,960,400)),
(4.5,s_prophecy,("预言说","他们会给众神带来[r]灾难[/r]"),("A prophecy said","they would bring [r]ruin[/r] to the gods."),(1.0,1.08,960,400)),
(4.5,s_odin_sea,("[b]奥丁[/b]把巨蛇","扔进了大海"),("[b]Odin[/b] threw the serpent","into the sea."),(1.0,1.04,800,400)),
(4.5,s_hel,("把[b]海拉[/b]送去","冰雾之国"),("He sent [b]Hel[/b]","down to the land of ice and mist."),(1.0,1.06,960,300)),
(4.5,s_bring,("只把小狼","带回了[g]阿斯加德[/g]"),("Only the wolf cub","was brought home to [g]Asgard[/g]."),(1.0,1.0,960,400)),
(4.5,s_hall_hide,("众神都怕它","躲得远远的"),("The gods feared him","and kept their distance."),(1.0,1.04,960,400)),
(5.0,s_hall_feed,("只有[b]提尔[/b]","敢走近喂它"),("Only [b]Tyr[/b]","dared to go near and feed him."),(1.0,1.05,960,400)),
(4.5,s_hall_snap,("小狼一口叼走肉","[b]提尔[/b]摸了摸它的头"),("The cub snapped up the meat;","[b]Tyr[/b] patted his head."),(1.05,1.12,1000,380)),
(4.5,s_grow,("可它一天比一天大","大得吓人"),("But he grew bigger every day,","frighteningly big."),(1.0,1.0,960,400)),
(4.5,s_council,("众神商量","必须把它[r]绑起来[/r]"),("The gods agreed:","he must be [r]bound[/r]."),(1.0,1.05,960,350)),
(4.5,s_chain1,("他们拿来铁链[b]莱丁[/b]","说：试试你的力气？"),("They brought the chain [b]Lœðingr[/b]:","\"Want to test your strength?\""),(1.0,1.04,1100,420)),
(4.0,s_break1,("狼一挣","铁链就[r]断了[/r]"),("One heave,","and the chain [r]snapped[/r]."),(1.0,1.0,1100,420)),
(4.5,s_chain2,("又打了一条","粗一倍的[b]德罗米[/b]"),("Then they forged [b]Drómi[/b],","twice as strong."),(1.0,1.04,1100,420)),
(4.0,s_break2,("狼弓背一蹬","又[r]断了[/r]"),("He arched his back and kicked,","and it [r]broke[/r] again."),(1.0,1.0,1100,420)),
(4.5,s_proud,("北欧人从此用“挣脱莱丁”","形容摆脱困境"),("Ever since, Norse folk say \"free from Lœðingr\"","to mean escaping a bind."),(1.0,1.05,1220,400)),
(4.0,s_proud,("狼越来越得意","众神越来越怕"),("The wolf grew prouder,","the gods more afraid."),(1.05,1.12,1220,330)),
(4.5,s_skirnir,("[b]奥丁[/b]派使者[b]斯基尔尼尔[/b]","去地下找矮人"),("[b]Odin[/b] sent [b]Skírnir[/b]","down to the dwarves."),(1.0,1.04,900,400)),
(4.5,s_forge,("矮人用六样东西","打造一条绳子"),("The dwarves forged a fetter","from six things:"),(1.0,1.05,1100,450)),
(4.0,lambda c,lt,d:s_items(c,lt,d,0),("[b]猫的脚步声[/b]","[b]女人的胡须[/b]"),("the sound of a cat's footfall,","a woman's beard,"),(1,1,960,400)),
(4.0,lambda c,lt,d:s_items(c,lt,d,2),("[b]山的根[/b]","[b]熊的筋[/b]"),("the roots of a mountain,","the sinews of a bear,"),(1,1,960,400)),
(4.0,lambda c,lt,d:s_items(c,lt,d,4),("[b]鱼的呼吸[/b]","[b]鸟的口水[/b]"),("the breath of a fish,","and the spittle of a bird."),(1,1,960,400)),
(4.5,s_gone,("所以这些东西","从此世上都[r]没有了[/r]"),("That is why these things","[r]no longer exist[/r]."),(1,1,960,400)),
(4.5,s_ribbon,("它像丝带一样又软又细","名叫[b]格莱普尼尔[/b]"),("Soft and smooth as a silk ribbon,","it was called [b]Gleipnir[/b]."),(1.0,1.06,960,360)),
(5.0,s_lyngvi,("众神带狼来到黑湖中的","[g]林格维岛[/g]"),("The gods led the wolf to","[g]Lyngvi[/g], an isle in a black lake."),(1.0,1.03,960,400)),
(4.5,s_suspicious,("狼看着丝带","这么细 [r]肯定有诈[/r]"),("The wolf eyed the ribbon:","so thin, [r]it must be a trick[/r]."),(1.0,1.06,1000,300)),
(4.5,s_demand,("要绑我","先把[r]一只手[/r]放进我嘴里"),("\"Bind me if you will,","but first put [r]a hand[/r] in my mouth.\""),(1.0,1.04,1000,300)),
(4.5,s_look,("众神你看我 我看你","没人动"),("The gods looked at one another.","No one moved."),(1.0,1.03,960,400)),
(5.0,s_reach,("只有[b]提尔[/b]","把[r]右手[/r]放进了狼嘴"),("Only [b]Tyr[/b] laid","his [r]right hand[/r] in the jaws."),(1.0,1.06,900,380)),
(4.5,s_struggle,("狼越挣","丝带勒得越紧"),("The harder he struggled,","the tighter it held."),(1.04,1.1,900,400)),
(4.0,s_bite,("狼一口[r]咬了下去[/r]",""),("The wolf [r]bit down[/r].",""),(1.08,1.15,900,330)),
(4.5,s_laugh,("众神都笑了","只有[b]提尔[/b]没有笑"),("All the gods laughed,","except [b]Tyr[/b]."),(1.0,1.05,960,350)),
(4.5,s_rock,("他们把绳尾穿过巨石","深深埋进地里"),("They threaded the cord through a boulder","and sank it deep into the earth."),(1.0,1.04,700,450)),
(4.0,s_sword,("一把剑撑在狼嘴里","它再也合不上嘴"),("A sword was wedged in his jaws,","so he could never close them."),(1.0,1.05,1000,350)),
(4.5,s_river,("口水流成一条河","叫作“期望之河”"),("His slaver ran into a river,","called Ván, \"Expectation\"."),(1.0,1.04,1000,450)),
(4.5,s_wait,("它就这样等着","等到[r]诸神黄昏[/r]"),("There he waits,","until [r]Ragnarök[/r]."),(1.0,1.08,1100,450)),
(5.0,s_ragbreak,("那一天 绳子[r]断了[/r]","巨狼张口 上颚顶天 下颚贴地"),("On that day the fetter [r]breaks[/r];","his jaws gape from earth to sky."),(1.0,1.06,1200,400)),
(5.0,s_odin_vidar,("它吞下了[b]奥丁[/b]","[b]维达[/b]一脚踩住下颚 撕开了它"),("He swallows [b]Odin[/b];","[b]Víðarr[/b] treads on his jaw and tears him apart."),(1.0,1.04,1200,420)),
(4.5,s_garm,("独臂的[b]提尔[/b]","迎战地狱犬[r]加尔姆[/r]"),("One-handed [b]Tyr[/b]","faces the hound [r]Garmr[/r]."),(1.0,1.06,960,400)),
(5.0,s_moral,("诺言要靠代价守住","[b]提尔[/b]用一只手 绑住了狼"),("A pledge is kept by its price:","[b]Tyr[/b] gave a hand to bind the wolf."),(1.0,1.06,960,380)),
(4.5,s_night,("众神真正害怕的","是一只[r]狼[/r]"),("What the gods truly feared","was a [r]wolf[/r]."),(1.0,1.08,1150,350)),
]
T0=np.cumsum([0]+[s[0] for s in S]); TOTAL=float(T0[-1])

def sub_img(i):
    zh,en=S[i][2],S[i][3]
    if zh[1]: lines=[(zh[0],FZ,38,0,False),(en[0],FE,25,47,True),(zh[1],FZ,38,80,False),(en[1],FE,25,127,True)]
    else: lines=[(zh[0],FZ,42,30,False),(en[0],FE,27,84,True)]
    return text_img(('sub',i),lines,SX1-SX0-20,160)

BASE=None; TEX=None; OVL=None
def render(t):
    global BASE,TEX,OVL
    if BASE is None:
        BASE=make_base(); n=nmap(5,PW,PH,((12,1),(40,.6),(160,.3))); g=np.random.default_rng(5).normal(0,1,(PH,PW)).astype(np.float32)
        OVL=make_ovl()
        TEX=((0.965+0.07*n)+g*0.015)[...,None]
    i=int(np.searchsorted(T0,t,side='right')-1); i=min(i,len(S)-1); lt=t-T0[i]; d,fn,zh,en,cam=S[i]
    s,c=surf(PW,PH); c.scale(K,K); c.translate(0,OFF)
    z=lerp(cam[0],cam[1],E(lt/d)); fx,fy=cam[2],cam[3]
    c.save(); c.translate(fx,fy); c.scale(z,z); c.translate(-fx,-fy)
    global BM,BINV
    BM=c.get_matrix(); BINV=c.get_matrix(); BINV.invert()
    # 名签坐标要从场景空间换到画面空间
    tags=fn(c,lt,d) or []
    M=c.get_matrix(); c.restore()
    shake=0
    for tg in tags:
        if tg[0]=='__shake__': shake=tg[1]
    s.flush(); pic=np.ndarray((PH,PW,4),np.uint8,s.get_data())[...,[2,1,0]].astype(np.float32)
    pic=np.clip(pic*TEX,0,255).astype(np.uint8)
    if shake>0:
        dx=int(14*shake*math.sin(lt*50)); pic=np.roll(pic,dx,axis=1)
    out=BASE.copy(); out[PY:PY+PH]=pic
    o_rgb,o_a=OVL; out[:]=(out*(1-o_a)+o_rgb*o_a).astype(np.uint8)
    def blit(img,x,y,alpha):
        h,w=img.shape[:2]; x=int(x); y=int(y)
        x0,y0=max(0,x),max(0,y); x1,y1=min(OW,x+w),min(OH,y+h)
        if x1<=x0 or y1<=y0 or alpha<=0: return
        sub=img[y0-y:y1-y,x0-x:x1-x].astype(np.float32); a=sub[...,3:4]/255*alpha
        out[y0:y1,x0:x1]=(out[y0:y1,x0:x1]*(1-a)+sub[...,:3]*a).astype(np.uint8)
    tag_a=seg(lt,0.3,0.8)*(1-seg(lt,d-0.35,d))
    for tg in tags:
        if tg[0]=='__title__':
            im=text_img('title',[("提尔与魔狼",FZ,104,20,False),("Tyr and the Wolf Fenrir",FE,36,150,True),("北欧神话 · Norse Myth",FZ,28,200,True)],1000,250)
            blit(im,(OW-1000)/2,PY+(OFF+400)*K-125,tg[1])
        elif tg[0]=='__runes__':
            n,pulse=tg[1],tg[2]
            im=text_img('runes',[("ᚠ ᛖ ᚾ ᚱ ᛁ ᛦ",FR,74,0,False)],700,100)
            w=im.shape[1]; part=im.copy(); cut=int(w*n/6); part[:,cut:,3]=0
            for k,y in enumerate((300,420,540)): blit(part,(OW-700)/2,PY+y-40,1.0 if k==0 else (1.0 if n>3+k else 0))
        elif tg[0]=='__item__':
            im=text_img(('it',tg[1]),[(tg[1],FZ,30,0,False)],300,44)
            px,py=M.transform_point(tg[2],tg[3]); blit(im,px-150,PY+py,tg[4])
        elif tg[0]=='__rune__':
            im=text_img('tiwaz',[("ᛏ",FR,190,0,False)],240,240); blit(im,OW/2-120,PY+40,tg[1])
        elif tg[0]=='__shake__': pass
        else:
            zh_,en_,px,py,side=tg; im=tag_img(zh_,en_); w,h=im.shape[1],im.shape[0]
            gap=46
            if side=='L' and px-gap-w<36: side='R'
            if side=='R' and px+gap+w>OW-36: side='L'
            bx=px-gap-w if side=='L' else px+gap; by=min(max(PY+30,PY+py-h/2),SY0-h-6)
            ex=bx+w if side=='L' else bx; ey=by+h/2
            if tag_a>0:
                ov=out.copy(); cv2.line(ov,(int(ex),int(ey)),(int(px+(-14 if side=='L' else 14)),int(PY+py)),(201,160,80),2,cv2.LINE_AA)
                cv2.circle(ov,(int(px+(-14 if side=='L' else 14)),int(PY+py)),4,(201,160,80),-1,cv2.LINE_AA)
                out[:]=(out*(1-tag_a)+ov*tag_a).astype(np.uint8)
            blit(im,bx,by,tag_a)
    # 字幕：前后 0.35s 淡入淡出
    a=seg(lt,0,0.35)*(1-seg(lt,d-0.3,d)) if i<len(S)-1 else seg(lt,0,0.35)
    if i==0: a=seg(lt,0.2,0.6)
    if S[i][2][0] or S[i][3][0]: blit(sub_img(i),SX0+10,SY0+22,a)
    return out

if __name__=='__main__':
    import argparse; ap=argparse.ArgumentParser(); ap.add_argument('--stills'); ap.add_argument('--part',type=int,default=0); ap.add_argument('--parts',type=int,default=1); ap.add_argument('--out',default='out')
    a=ap.parse_args(); os.makedirs(a.out,exist_ok=True)
    if a.stills:
        for tt in a.stills.split(','):
            Image.fromarray(render(float(tt))).save(f'{a.out}/s_{float(tt):06.2f}.jpg',quality=88)
    else:
        nf=int(round(TOTAL*FPS)); f0=nf*a.part//a.parts; f1=nf*(a.part+1)//a.parts
        p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{OW}x{OH}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p',f'{a.out}/part{a.part}.mp4'],stdin=subprocess.PIPE)
        for f in range(f0,f1):
            p.stdin.write(render(f/FPS).tobytes())
            if f%240==0: print(a.part,f,'/',f1,flush=True)
        p.stdin.close(); p.wait()
