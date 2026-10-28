import os
import sys, math, numpy as np, cairocffi as cairo, cv2
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from puppet import *
from PIL import Image
import ui
W,H=1920,1128
CRACKS=4

def surf():
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); return s,cairo.Context(s)
def noise(seed,scales=((8,1.0),(24,0.5),(80,0.25),(240,0.12))):
    r=np.random.default_rng(seed); acc=np.zeros((H,W),np.float32)
    for n,a in scales:
        g=r.random((max(2,H*n//W),n)).astype(np.float32); acc+=cv2.resize(g,(W,H),interpolation=cv2.INTER_CUBIC)*a
    acc-=acc.min(); return acc/acc.max()
def paint_np(ctx,arr):   # arr HxWx3 float 0..1 → 铺满
    a=(np.clip(arr,0,1)*255).astype(np.uint8); bgra=np.dstack([a[...,2],a[...,1],a[...,0],np.full(a.shape[:2],255,np.uint8)]).copy()
    s=cairo.ImageSurface.create_for_data(bytearray(bgra.tobytes()),cairo.FORMAT_ARGB32,W,H); ctx.set_source_surface(s,0,0); ctx.paint(); return bgra
def wall(ctx,c1,c2,seed=1):
    n=noise(seed); a=np.array(c1)[None,None]*(1-n[...,None])+np.array(c2)[None,None]*n[...,None]
    paint_np(ctx,a)
def texture_over(s,seed=5,amt=0.10):
    """整画面斑驳 + 颗粒 + 发丝裂纹（像墙面老化，跨过人物）"""
    buf=np.ndarray((H,W,4),np.uint8,s.get_data()).copy(); n=noise(seed,((12,1),(40,.6),(160,.3)))
    g=np.random.default_rng(seed).normal(0,1,(H,W)).astype(np.float32)
    f=(1-amt*0.5+amt*n)+g*0.018
    out=buf.astype(np.float32); out[...,:3]*=f[...,None]
    img=np.clip(out,0,255).astype(np.uint8)[...,[2,1,0]].copy()
    r=np.random.default_rng(seed+1)
    for k in range(CRACKS):
        x,y=r.uniform(0,W),r.uniform(0,H); ang=r.uniform(0,6.3); pts=[]
        for i in range(r.integers(10,24)): ang+=r.uniform(-.45,.45); x+=math.cos(ang)*r.uniform(14,36); y+=math.sin(ang)*r.uniform(14,36); pts.append((int(x),int(y)))
        cv2.polylines(img,[np.array(pts)],False,(96,78,60),1,cv2.LINE_AA)
        cv2.polylines(img,[np.array(pts)+[1,2]],False,(200,188,166),1,cv2.LINE_AA)
    return img

def interlace(ctx,y0,h,col1,col2,bg,x0=0,x1=W,period=150):
    ctx.rectangle(x0,y0,x1-x0,h); ctx.set_source_rgb(*bg); ctx.fill()
    def path(ph):
        ctx.new_path(); N=int((x1-x0)/4)
        for i in range(N+1):
            x=x0+i*4; y=y0+h/2+math.sin((x-x0)/period*2*math.pi+ph)*h*0.3
            ctx.move_to(x,y) if i==0 else ctx.line_to(x,y)
    for ph,col in ((0,col1),(math.pi,col2)):
        path(ph); ctx.set_source_rgb(*LINE); ctx.set_line_width(h*0.24); ctx.stroke()
        path(ph); ctx.set_source_rgb(*col); ctx.set_line_width(h*0.15); ctx.stroke()
    # 交叠：每隔一个交点把第一条重画在上
    for k in range(int((x1-x0)/period*2)+2):
        xc=x0+period*(0.0+k*0.5)
        if k%2: continue
        ctx.save(); ctx.rectangle(xc-h*0.35,y0,h*0.7,h); ctx.clip()
        path(0); ctx.set_source_rgb(*LINE); ctx.set_line_width(h*0.24); ctx.stroke(); path(0); ctx.set_source_rgb(*col1); ctx.set_line_width(h*0.15); ctx.stroke(); ctx.restore()
    for yy in (y0,y0+h): ctx.rectangle(x0,yy-3,x1-x0,6); ctx.set_source_rgb(*LINE); ctx.fill()
def dots(ctx,y,col,x0=0,x1=W,step=26,r=5):
    x=x0+step/2
    while x<x1: ctx.new_path(); ctx.arc(x,y,r,0,7); ctx.set_source_rgb(*col); ctx.fill(); x+=step
def shield(ctx,cx,cy,r,c1,c2):
    ctx.new_path(); ctx.arc(cx,cy,r,0,7); ctx.set_source_rgb(*c1); ctx.fill_preserve(); ctx.set_source_rgb(*LINE); ctx.set_line_width(4); ctx.stroke()
    for k in range(8):
        a=k*math.pi/4; ctx.new_path(); ctx.move_to(cx,cy); ctx.arc(cx,cy,r*0.92,a,a+math.pi/8); ctx.close_path(); ctx.set_source_rgb(*c2); ctx.fill()
    ctx.new_path(); ctx.arc(cx,cy,r*0.92,0,7); ctx.set_source_rgb(*LINE); ctx.set_line_width(2); ctx.stroke()
    ctx.new_path(); ctx.arc(cx,cy,r*0.22,0,7); ctx.set_source_rgb(*C['iron']); ctx.fill_preserve(); ctx.set_source_rgb(*LINE); ctx.set_line_width(3); ctx.stroke()
def flame(ctx,cx,by,w,h,ph=0):
    for k,(col,sc) in enumerate(((rgb('b8432a'),1.0),(rgb('e08a32'),0.72),(rgb('f2cf6a'),0.42))):
        pts=[(cx-w*sc,by,'c')]
        for i in range(5):
            u=(i+0.5)/5; xx=cx-w*sc+u*2*w*sc; hh=h*sc*(0.55+0.45*math.sin(u*math.pi))*(0.85+0.15*math.sin(ph*7+i*2.1))
            pts+= [(xx+w*sc*0.08*math.sin(ph*5+i),by-hh,'c'),(xx+w*sc*0.2,by-hh*0.55)]
        pts+=[(cx+w*sc,by,'c')]
        shape(ctx,pts,col,3 if k==0 else 0)
def pillar(ctx,x,w,y0,y1):
    ctx.rectangle(x,y0,w,y1-y0); ctx.set_source_rgb(*rgb('8a5a32')); ctx.fill_preserve(); ctx.set_source_rgb(*LINE); ctx.set_line_width(4); ctx.stroke()
    ctx.save(); ctx.rectangle(x+10,y0,w-20,y1-y0); ctx.clip()
    for k in range(int((y1-y0)/90)+1):
        yy=y0+k*90; ctx.new_path(); ctx.arc(x+w/2,yy+45,w*0.32,0,7); ctx.set_source_rgb(*LINE); ctx.set_line_width(w*0.16); ctx.stroke()
        ctx.new_path(); ctx.arc(x+w/2,yy+45,w*0.32,0,7); ctx.set_source_rgb(*rgb('c08a4a')); ctx.set_line_width(w*0.09); ctx.stroke()
    ctx.restore()
    for xx in (x+10,x+w-10): ctx.move_to(xx,y0); ctx.line_to(xx,y1); ctx.set_source_rgb(*LINE); ctx.set_line_width(3); ctx.stroke()
def meat(ctx,x,y):
    shape(ctx,[(x-10,y-6),(x+40,y-40),(x+90,y-30),(x+96,y+10),(x+50,y+30),(x+4,y+16)],rgb('a24a34'),4)
    line(ctx,[(x+30,y-26),(x+70,y-14),(x+80,y+8)],rgb('d07a5a'),5)
    shape(ctx,[(x-50,y+10,'c'),(x+0,y-4,'c'),(x+4,y+14,'c'),(x-46,y+24,'c')],C['bone'],3,t=0)
    for dx,dy in ((-56,6),(-56,26)): ctx.new_path(); ctx.arc(x+dx,y+dy,11,0,7); ctx.set_source_rgb(*C['bone']); ctx.fill_preserve(); ctx.set_source_rgb(*LINE); ctx.set_line_width(3); ctx.stroke()
def ribbon(ctx,pts,lw=16,glow=True):
    if glow:
        for k,a in ((5,0.10),(3,0.16),(2,0.25)):
            ctx.new_path(); smooth(ctx,pts,False); ctx.set_source_rgba(1,0.85,0.45,a); ctx.set_line_width(lw*k); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    line(ctx,pts,LINE,lw+6); line(ctx,pts,rgb('e9c66e'),lw); line(ctx,pts,rgb('fbeeb8'),lw*0.3)
def floor(ctx,y,col,band=True):
    ctx.rectangle(0,y,W,H-y); ctx.set_source_rgb(*col); ctx.fill()
    ctx.rectangle(0,y-3,W,6); ctx.set_source_rgb(*LINE); ctx.fill()

def finish(s,name,zh,en,tags=(),tex=0.10,seed=5):
    img=texture_over(s,seed,tex); pic=Image.fromarray(img)
    fr=ui.frame(pic,zh,en,tags,0,H); fr.save(f'out/{name}.png'); return fr

# ---------- 剧照 1：大厅喂狼 ----------
def still_hall():
    s,c=surf(); wall(c,rgb('e8dcbf'),rgb('cdbb93'),1)
    interlace(c,0,96,rgb('b47a3a'),rgb('3d5a7a'),rgb('d9c9a2'))
    dots(c,112,C['red'],step=30,r=5)
    pillar(c,40,90,96,960); pillar(c,W-130,90,96,960)
    for cx,c1,c2 in ((420,C['red'],C['gold']),(560,C['blue'],C['bone']),(1360,C['gold'],C['red']),(1500,C['green'],C['bone'])): shield(c,cx,300,78,c1,c2)
    floor(c,960,rgb('b9a27a'))
    c.rectangle(0,990,W,22); c.set_source_rgb(*C['red2']); c.fill(); dots(c,1001,C['bone'],step=34,r=4)
    # 火盆
    shape(c,[(150,960,'c'),(190,880,'c'),(330,880,'c'),(370,960,'c')],C['iron2'],4,t=0)
    shape(c,[(130,880,'c'),(390,880,'c'),(370,850,'c'),(150,850,'c')],C['iron'],4,t=0); flame(c,260,852,110,230,0.3)
    # 暖光
    g=cairo.RadialGradient(260,760,30,260,760,900); g.add_color_stop_rgba(0,1,0.7,0.3,0.32); g.add_color_stop_rgba(1,1,0.7,0.3,0)
    c.set_source(g); c.paint()
    o=man(c,700,960,780,dict(nsh=1.32,nel=0.12,fsh=-0.15,fel=0.35,nhip=0.18,nkn=-0.12,fhip=-0.12,fkn=0.06,head=0.05))
    hx,hy=o['hand_n']; meat(c,hx+40,hy-8)
    wolf(c,1430,960,700,dict(head=-0.42,ears=0.1,fl1=0.25,fl2=-0.1,fr1=-0.05,hl1=-0.35,hl2=0.62,tail=-0.2))
    return finish(s,'still_1_hall',["小狼[b]芬里尔[/b]越长越大","只有[b]提尔[/b]敢亲手喂它"],["Young [b]Fenrir[/b] grew and grew.","Only [b]Tyr[/b] dared to feed him."],
                  [("提尔","Tyr",250,130),("芬里尔","Fenrir",840,190)])

# ---------- 剧照 2：林格维岛 绑狼 ----------
def bands(c,cols,y0,y1):
    n=len(cols); h=(y1-y0)/n
    for i,col in enumerate(cols): c.rectangle(0,y0+i*h,W,h+1); c.set_source_rgb(*col); c.fill()
def loop(c,cx,cy,rx,ry,tilt=0.0,lw=14):
    pts=[(cx+rx*math.cos(a)*math.cos(tilt)-ry*math.sin(a)*math.sin(tilt), cy+rx*math.cos(a)*math.sin(tilt)+ry*math.sin(a)*math.cos(tilt)) for a in np.linspace(0,2*math.pi,13)[:-1]]
    for k,al in ((4,0.12),(2.4,0.2)):
        c.new_path(); smooth(c,pts,True); c.set_source_rgba(1,0.85,0.45,al); c.set_line_width(lw*k); c.stroke()
    c.new_path(); smooth(c,pts,True); c.set_source_rgb(*LINE); c.set_line_width(lw+6); c.stroke()
    c.new_path(); smooth(c,pts,True); c.set_source_rgb(*rgb('e9c66e')); c.set_line_width(lw); c.stroke()
    c.new_path(); smooth(c,pts,True); c.set_source_rgb(*rgb('fbeeb8')); c.set_line_width(lw*0.3); c.stroke()
WP=dict(jaw=0.5,head=0.42,fl1=0.55,fl2=-0.35,fr1=0.35,fr2=-0.25,hl1=-0.7,hl2=1.0,hr1=-0.5,hr2=0.9,tail=-0.5,ears=-0.3)
TP=dict(nsh=1.40,nel=0.06,fsh=-0.25,fel=0.45,nhip=0.28,nkn=-0.18,fhip=-0.18,fkn=0.12,head=0.06)
def still_bind():
    s,c=surf()
    bands(c,[rgb('2c3b52'),rgb('3d5168'),rgb('5b6d7c'),rgb('8a8f8a'),rgb('b9a988'),rgb('d8c49a')],0,760)
    c.rectangle(0,760,W,120); c.set_source_rgb(*rgb('35506a')); c.fill()
    for row in range(3):
        for k in range(-1,W//60+2):
            x=k*60+(row%2)*30; y=785+row*36; c.new_path(); c.arc(x,y,22,math.pi,2*math.pi); c.set_source_rgb(*rgb('a9b8bf')); c.set_line_width(4); c.stroke()
    shape(c,[(0,1128,'c'),(0,900),(300,860),(700,880),(1200,850),(1700,875),(1920,860),(1920,1128,'c')],rgb('7b6a55'),4)
    for k in range(9):
        x=120+k*210; line(c,[(x,940),(x+60,900),(x+130,930)],rgb('5c4d3c'),4)
    ds,dc=surf(); tyr_x=720; o=man(dc,tyr_x,960,720,TP); hx,hy=o['hand_n']
    wl=wolf(dc,0,0,980,WP); wx,wy=hx+28-wl['mouth'][0], hy+4-wl['mouth'][1]
    print('wolf feet y',wy)
    wl=wolf(c,wx,wy,980,WP); v=wl['v']
    nx,ny=wl['neck']; loop(c,nx+10,ny+20,0.55*v,1.25*v,-0.5)
    bx,by=wl['belly']; loop(c,bx,by,0.45*v,1.0*v,0.1); hx2,hy2=wl['hind']; loop(c,hx2+20,hy2+40,0.4*v,0.9*v,0.25)
    th=man(c,330,960,650,dict(nsh=1.05,nel=0.3,fsh=0.9,fel=0.45,handgrip=True,fgrip=True,nhip=0.25,nkn=-0.1,fhip=-0.25,fkn=0.1,body=0.12),tunic='blue',tunic2='blue2',cloak='red',beard='red',helmet='wing')
    p1,p2=th['hand_f'],th['hand_n']
    ribbon(c,[(nx-20,ny+1.2*v),(nx-300,ny+260),(p2[0]+60,p2[1]+20),p2,p1,(p1[0]-120,p1[1]+90),(80,980)],12)
    o=man(c,tyr_x,960,720,TP)
    tags=[("提尔","Tyr",tyr_x/2-60,o['head'][1]/2-30),("托尔","Thor",330/2-70,th['head'][1]/2-10),("芬里尔","Fenrir",wl['head'][0]/2+40,max(30,wl['head'][1]/2-90)),("格莱普尼尔","Gleipnir",(nx+0.9*v)/2,ny/2+20)]
    return finish(s,'still_2_bind',["只有[b]提尔[/b]","把[r]右手[/r]放进了狼嘴"],["Only [b]Tyr[/b] laid","his [r]right hand[/r] in the jaws."],tags,seed=7), o, wl

# ---------- 剧照 3：夜 · 黑绘巨狼 ----------
def still_night():
    s,c=surf()
    bands(c,[rgb('121a28'),rgb('17233a'),rgb('1d2e46'),rgb('24405a'),rgb('2d5562'),rgb('3c6a66')],0,860)
    r=np.random.default_rng(4)
    for i in range(160):
        x,y=r.uniform(0,W),r.uniform(0,640); rr=r.uniform(1,3.2); c.new_path(); c.arc(x,y,rr,0,7); c.set_source_rgba(0.95,0.92,0.8,r.uniform(.4,.95)); c.fill()
    # 极光
    for k in range(3):
        c.new_path(); smooth(c,[(0,560+k*30),(400,480+k*20),(900,540+k*25),(1400,470+k*30),(1920,530+k*20)],False)
        c.set_source_rgba(0.55,0.85,0.6,0.10); c.set_line_width(70-k*18); c.stroke()
    # 巨狼（黑绘剪影 + 刻线），仰头
    wl=wolf(c,1150,1180,1500,dict(head=0.05,ears=0.1,tail=-0.5,fl1=0.0,fl2=0.0),black=True)
    # 群山
    shape(c,[(0,1128,'c'),(0,760),(180,640),(360,760),(560,600,'c'),(760,780),(980,650,'c'),(1180,800),(1400,640,'c'),(1640,780),(1920,660),(1920,1128,'c')],rgb('3b4a5a'),4,t=0.2)
    for x0,y0 in ((180,640),(560,600),(980,650),(1400,640)):
        shape(c,[(x0-70,y0+70,'c'),(x0,y0,'c'),(x0+70,y0+70,'c'),(x0+30,y0+60),(x0,y0+80),(x0-30,y0+60)],C['bone'],3,t=0.1)
    shape(c,[(0,1128,'c'),(0,900),(600,870),(1200,895),(1920,875),(1920,1128,'c')],rgb('cfd3d4'),4)
    # 众神小剪影（黑绘）
    blk=dict(tunic='black',tunic2='black',cloak='black',beard='black',skin='black',trousers='black',wrap=('black','black'),trim='ochre')
    for i,xx in enumerate((150,290,430,570,710)):
        man(c,xx,915,300,dict(nsh=0.15+1.0*(i==4),nel=0.1,fsh=-0.1,fel=0.2,head=-0.25,nhip=0.1,fhip=-0.1),helmet='wing' if i==1 else 'cone',hood=(i==3),**blk)
    ex,ey=wl['eye']
    g=cairo.RadialGradient(ex,ey,2,ex,ey,90); g.add_color_stop_rgba(0,1,0.75,0.3,0.9); g.add_color_stop_rgba(1,1,0.6,0.2,0); c.set_source(g); c.paint()
    return finish(s,'still_3_night',["众神真正害怕的","是一只[r]狼[/r]"],["What the gods","truly feared was a [r]wolf[/r]."],[("芬里尔","Fenrir",ex/2+110,ey/2-90)],tex=0.08,seed=9)

if __name__=='__main__':
    still_hall(); still_bind(); still_night()
