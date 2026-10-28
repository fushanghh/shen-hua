import os
# 纯代码北欧画像石木偶：cairo 矢量部件 + 关节
import cairocffi as cairo, math, numpy as np

LINE=(0.15,0.10,0.07)
LWPX=4.0
def rgb(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
C=dict(skin=rgb('d9a777'),skin2=rgb('c48d5e'),red=rgb('9a3b26'),red2=rgb('7a2b1c'),blue=rgb('2f4e72'),blue2=rgb('243d5b'),
       gold=rgb('c99a45'),gold2=rgb('e3bd6a'),bone=rgb('ece0c4'),brown=rgb('6b4528'),brown2=rgb('4e3220'),iron=rgb('8b8f92'),iron2=rgb('6c7174'),
       ochre=rgb('b47a3a'),green=rgb('4f6a4a'),slate=rgb('6d7677'),slate2=rgb('535b5d'),grey=rgb('c9c2b4'),black=rgb('1d1712'),white=rgb('f3ead6'))

def smooth(ctx,pts,closed=True,t=0.5):
    """Catmull-Rom 曲线；点写成 (x,y,'c') 表示尖角"""
    n=len(pts); P=[(p[0],p[1]) for p in pts]; sharp=[len(p)>2 for p in pts]
    ctx.move_to(*P[0])
    rng=range(n) if closed else range(n-1)
    for i in rng:
        p0=P[i-1] if (closed or i>0) else P[i]; p1=P[i]; p2=P[(i+1)%n]; p3=P[(i+2)%n] if (closed or i+2<n) else p2
        k1=0 if sharp[i] else t/3; k2=0 if sharp[(i+1)%n] else t/3
        c1=(p1[0]+(p2[0]-p0[0])*k1, p1[1]+(p2[1]-p0[1])*k1); c2=(p2[0]-(p3[0]-p1[0])*k2, p2[1]-(p3[1]-p1[1])*k2)
        ctx.curve_to(*c1,*c2,*p2)
    if closed: ctx.close_path()

def shape(ctx,pts,fill,lw=3.2,line=LINE,closed=True,t=0.5):
    ctx.new_path(); smooth(ctx,pts,closed,t)
    if fill is not None: ctx.set_source_rgb(*fill); ctx.fill_preserve()
    if lw: ctx.set_source_rgb(*line); ctx.set_line_width(lw); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
    else: ctx.new_path()
def clip_shape(ctx,pts,t=0.5): ctx.new_path(); smooth(ctx,pts,True,t); ctx.clip()
def line(ctx,pts,col=LINE,lw=2.4,closed=False,t=0.5):
    ctx.new_path(); smooth(ctx,pts,closed,t); ctx.set_source_rgb(*col); ctx.set_line_width(lw); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
def spiral(ctx,cx,cy,r,turns=2.2,col=None,lw=2.5,a0=0,dirn=1):
    col=col or C['gold']; ctx.new_path(); N=60
    for i in range(N+1):
        u=i/N; a=a0+dirn*u*turns*2*math.pi; rr=r*(1-u*0.92)
        x,y=cx+rr*math.cos(a),cy+rr*math.sin(a)
        ctx.move_to(x,y) if i==0 else ctx.line_to(x,y)
    ctx.set_source_rgb(*col); ctx.set_line_width(lw); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
def eye(ctx,x,y,w,col_iris=None,closed=False,tail=True):
    """正面杏仁眼（侧脸程式）"""
    if closed: line(ctx,[(x-w,y),(x,y+w*0.25),(x+w,y)],lw=2.6); return
    shape(ctx,[(x-w,y,'c'),(x-w*0.2,y-w*0.42),(x+w*0.75,y-w*0.18),(x+w,y,'c'),(x+w*0.1,y+w*0.32)],C['white'],2.2)
    ctx.new_path(); ctx.arc(x+w*0.18,y-w*0.04,w*0.27,0,7); ctx.set_source_rgb(*(col_iris or LINE)); ctx.fill()
    line(ctx,[(x-w*1.05,y-w*0.05),(x-w*0.2,y-w*0.5),(x+w*0.8,y-w*0.22),(x+w*1.4,y+w*0.05)] if tail else [(x-w,y),(x,y-w*.45),(x+w,y)],lw=2.8)

def tablet(ctx,x,y,w,h,lw):
    """板织带：金底 + 红蓝人字/菱纹"""
    ctx.save(); ctx.rectangle(x,y,w,h); ctx.set_source_rgb(*C['gold']); ctx.fill_preserve(); ctx.clip_preserve(); ctx.new_path()
    st=h*0.9; k=0; xx=x
    while xx<x+w+st:
        col=C['red2'] if k%2==0 else C['blue2']
        ctx.move_to(xx,y+h*0.5); ctx.line_to(xx+st*0.5,y+h*0.12); ctx.line_to(xx+st,y+h*0.5); ctx.line_to(xx+st*0.5,y+h*0.88); ctx.close_path()
        ctx.set_source_rgb(*col); ctx.fill()
        ctx.new_path(); ctx.arc(xx+st*0.5,y+h*0.5,h*0.1,0,7); ctx.set_source_rgb(*C['bone']); ctx.fill(); xx+=st; k+=1
    ctx.restore(); ctx.rectangle(x,y,w,h); ctx.set_source_rgb(*LINE); ctx.set_line_width(lw); ctx.stroke()

FURL=rgb('a9a597')
class J:
    """关节变换：with J(ctx,x,y,angle) 以 (x,y) 为轴，angle=0 朝下，正值朝前(+x)"""
    def __init__(s,ctx,x,y,a=0,sx=1): s.c=ctx; s.x=x; s.y=y; s.a=a; s.sx=sx
    def __enter__(s): s.c.save(); s.c.translate(s.x,s.y); s.c.rotate(-s.a); s.c.scale(s.sx,1); return s.c
    def __exit__(s,*e): s.c.restore()

def taper(L,w0,w1,r0=None,r1=None):
    """沿 +y 的锥形肢体（两端圆）"""
    r0=r0 or w0; r1=r1 or w1
    return [(-w0,0),(-w0*0.7,-r0*0.7),(0,-r0),(w0*0.7,-r0*0.7),(w0,0),(w1*1.02,L*0.5),(w1,L),(w1*0.7,L+r1*0.7),(0,L+r1),(-w1*0.7,L+r1*0.7),(-w1,L),(-w1*1.02,L*0.5)]

# ---------------- 人物 ----------------
DEF=dict(tunic='red',tunic2='red2',cloak='blue',trim='gold',beard='gold',helmet='cone',skin='skin',trousers='brown',
         wrap=('bone','blue'),eye_closed=False,patch=False,hood=False,beard_len=1.0,hammer=False,spear=False,raven=False,crown=False,longsleeve=True,sword=False,trimcol='gold',flip=False,dress=False,hair=None,stump=False,face=None)
def man(ctx,x,y,s,pose=None,**kw):
    """s = 身高（像素）。朝右（+x）。返回关键点（手、头）世界坐标"""
    o=dict(DEF); o.update(kw); p=dict(nsh=0.15,nel=0.25,fsh=-0.12,fel=0.2,nhip=0.05,nkn=-0.05,fhip=-0.08,fkn=0.0,head=0.0,body=0.0,handgrip=False,fgrip=False)
    p.update(pose or {}); u=s/8.0; out={}
    ctx.save(); ctx.translate(x,y)
    if o['flip']: ctx.scale(-1,1)
    ctx.scale(u/100,u/100)   # 局部单位：1 头 = 100
    lw=LWPX*100/u
    ctx.translate(0,-400); ctx.rotate(-p['body']); hip=(0,0)
    sk=C[o['skin']]
    def arm(sx,sy,a1,a2,near,grip):
        with J(ctx,sx,sy,a1) as c:
            shape(c,taper(150,27,20),C[o['tunic']] if near else C[o['tunic2']],lw)
            line(c,[(-21,128),(21,128)],C[o['trim']],7); 
            with J(c,0,150,a2-a1) as c2:
                if o['longsleeve']:
                    shape(c2,taper(124,21,16),C[o['tunic']] if near else C[o['tunic2']],lw)
                    tablet(c2,-17,100,34,22,lw*0.7)
                else:
                    shape(c2,taper(128,19,14),sk if near else C['skin2'],lw)
                    shape(c2,[(-16,100,'c'),(16,100,'c'),(15,118,'c'),(-15,118,'c')],C['blue'],lw*0.8,t=0)
                with J(c2,0,128,0) as c3:
                    if near and o['stump']:
                        shape(c3,[(-18,-10),(18,-10),(16,22),(0,30),(-16,22)],C['bone'],lw)
                        line(c3,[(-16,4),(16,-2)],C['skin2'],2); line(c3,[(-16,14),(16,8)],C['skin2'],2)
                        m=c3.get_matrix(); out['hand_n']=m.transform_point(0,20)
                    elif grip:
                        shape(c3,[(-20,0),(20,0),(30,30),(18,60),(-12,62),(-24,30)],sk if near else C['skin2'],lw)
                        line(c3,[(18,22),(-6,30)],lw=1.8); line(c3,[(18,38),(-8,44)],lw=1.8)
                    else:
                        shape(c3,[(-18,0),(18,0),(26,28),(42,40),(46,48,'c'),(28,46),(22,54),(18,92),(10,98,'c'),(-2,94),(-14,82),(-20,40)],sk if near else C['skin2'],lw)
                        for fx in (4,-6): line(c3,[(fx+8,60),(fx,90)],lw=1.6)
                    # 手的世界坐标
                    m=c3.get_matrix(); xx,yy=m.transform_point(0,60 if grip else 70)
                    out['hand_n' if near else 'hand_f']=(xx,yy)
    def leg(hx,hy,a1,a2,near):
        with J(ctx,hx,hy,a1) as c:
            shape(c,taper(200,36,25),C[o['trousers']] if near else C['brown2'],lw)
            with J(c,0,200,a2-a1) as c2:
                shape(c2,taper(175,24,14),C[o['wrap'][0]] if near else C['grey'],lw)
                c2.save(); clip_shape(c2,taper(175,24,14))
                for k in range(-2,9): line(c2,[(-40,k*24),(40,k*24+30)],C[o['wrap'][1]] if near else C['blue2'],9)
                c2.restore(); c2.new_path(); smooth(c2,taper(175,24,14)); c2.set_source_rgb(*LINE); c2.set_line_width(lw); c2.stroke()
                with J(c2,0,175,-(a2)) as c3:   # 脚保持水平
                    shape(c3,[(-26,-14),(30,-12),(70,6),(96,22,'c'),(60,30),(-28,30,'c'),(-34,8)],C['brown'] if near else C['brown2'],lw)
    # 远侧：腿、手臂、披风
    leg(-14,10,p['fhip'],p['fhip']+p['fkn'],False)
    arm(-78,-250,p['fsh'],p['fsh']+p['fel'],False,p['fgrip'])
    if o['cloak']:
        shape(ctx,[(-60,-262),(-100,-240),(-130,-120),(-150,60),(-175,240,'c'),(-120,262),(-40,250),(-60,100),(-50,-120)],C[o['cloak']],lw)
        line(ctx,[(-175,240),(-120,262),(-40,250)],C[o['trim']],6)
    if o['sword']:
        with J(ctx,-20,0,-0.95) as cs:
            shape(cs,[(-15,0,'c'),(15,0,'c'),(12,300,'c'),(0,322,'c'),(-12,300,'c')],C['brown2'],lw,t=0)
            shape(cs,[(-13,280,'c'),(13,280,'c'),(0,324,'c')],C['gold'],lw*0.7,t=0)
            for yy in (60,150): line(cs,[(-15,yy),(15,yy)],C['gold'],5)
    if o['spear']:
        pass
    # 近侧腿
    leg(16,10,p['nhip'],p['nhip']+p['nkn'],True)
    if o['dress']:
        sk_=[(-56,0),(56,0),(118,384,'c'),(-118,384,'c')]
        shape(ctx,sk_,C[o['tunic']],lw); tablet(ctx,-116,360,232,26,lw*0.8)
        for k in range(-3,4): line(ctx,[(k*10,10),(k*30,360)],C[o['tunic2']],2)
    # 躯干 + 束腰外衣
    body=[(-82,-252),(-30,-282),(32,-282),(86,-252),(80,-170),(50,-60),(48,0,'c'),(84,190,'c'),(-84,190,'c'),(-50,0,'c'),(-54,-60),(-74,-170)]
    shape(ctx,body,C[o['tunic']],lw)
    ctx.save(); clip_shape(ctx,body)
    for k in range(-8,9):
        line(ctx,[(k*34-200,-300),(k*34+200,200)],C[o['tunic2']],2.2); line(ctx,[(k*34+200,-300),(k*34-200,200)],C[o['tunic2']],2.2)
    ctx.restore()
    tablet(ctx,-86,162,172,30,lw*0.8)
    # 领口织带 + 胸前竖织带
    line(ctx,[(-34,-282),(-14,-246),(0,-238),(14,-246),(34,-282)],LINE,15); line(ctx,[(-34,-282),(-14,-246),(0,-238),(14,-246),(34,-282)],C['gold'],9)
    line(ctx,[(0,-238),(0,-140)],LINE,13); line(ctx,[(0,-238),(0,-140)],C['gold'],7)
    for yy in range(-232,-146,14): line(ctx,[(-3,yy),(0,yy+7),(3,yy)],C['red2'],2)
    shape(ctx,[(-64,-8,'c'),(64,-8,'c'),(64,14,'c'),(-64,14,'c')],C['brown'],lw*0.8,t=0)
    shape(ctx,[(-10,-12,'c'),(14,-12,'c'),(14,18,'c'),(-10,18,'c')],C['gold'],lw*0.6,t=0)
    if o['sword']:
        with J(ctx,-20,0,-0.95) as cs:
            shape(cs,[(-30,-8,'c'),(30,-8,'c'),(30,4,'c'),(-30,4,'c')],C['iron'],lw*0.7,t=0)
            shape(cs,[(-7,-8,'c'),(7,-8,'c'),(7,-60,'c'),(-7,-60,'c')],C['brown'],lw*0.7,t=0)
            shape(cs,[(-18,-60,'c'),(18,-60,'c'),(14,-78),(0,-84),(-14,-78)],C['gold'],lw*0.7)
    if o['cloak']:
        ctx.new_path(); ctx.arc(52,-262,13,0,7); ctx.set_source_rgb(*C['gold']); ctx.fill_preserve(); ctx.set_source_rgb(*LINE); ctx.set_line_width(lw*0.7); ctx.stroke()
    # 头
    with J(ctx,6,-282,p['head']) as c:
        c.scale(1.12,1.12)
        if o['hood']:
            shape(c,[(-62,-60),(-40,-150),(10,-176),(58,-150),(70,-80),(52,-30),(-70,40)],C[o['cloak']] or C['blue'],lw)
        # 发辫在后
        if not o['hood']:
            shape(c,[(-50,-112),(-30,-92),(-30,-20),(-40,70),(-52,74),(-60,-20)],C['gold'],lw)
            for k in range(6): line(c,[(-54,-60+k*20),(-38,-48+k*20)],C['ochre'],2)
        if o['hair']:
            shape(c,[(-30,-160),(30,-176),(40,-150),(-20,-120),(-60,-40),(-80,80),(-110,110,'c'),(-96,40),(-70,-60),(-60,-120)],C[o['hair']],lw)
            for k in range(5): line(c,[(-40-k*8,-120+k*10),(-70-k*6,40+k*12)],C['ochre'] if o['hair']!='black' else C['slate2'],2)
        face=[(-48,-108),(-30,-158),(26,-168),(52,-146),(56,-124,'c'),(80,-90,'c'),(64,-84),(66,-76),(60,-70),(52,-30),(0,-6),(-40,-30)]
        shape(c,face,C[o['skin']],lw)
        shape(c,[(-14,-104),(2,-110),(6,-88),(-8,-76),(-18,-86)],C[o['skin']],lw*0.8)
        line(c,[(-6,-98),(-2,-88)],lw=1.8)
        line(c,[(38,-92),(30,-78),(18,-70)],C['skin2'],2.6)
        eye(c,36,-112,13,closed=o['eye_closed'])
        line(c,[(20,-130),(46,-132),(60,-124)],lw=3)
        if o['patch']:
            shape(c,[(24,-124),(50,-124),(52,-104),(28,-100)],C['black'],lw); line(c,[(-40,-140),(30,-120)],C['black'],3)
        # 胡子
        bl=o['beard_len']; bc=C[o['beard']] if o['beard'] else None
        beard=[(4,-100),(30,-86),(60,-76),(52,-64),(58,-52),(54,-20),(46,40*bl),(38,110*bl),(28,140*bl,'c'),(18,108*bl),(-4,30*bl),(-20,-40),(-16,-80)]
        if bc is not None: shape(c,beard,bc,lw)
        for k in range(int(9*bl) if bc is not None else 0):
            yy=-40+k*18
            if yy<130*bl: line(c,[(14+k*1.2,yy),(30,yy+8),(46-k*1.2,yy)],C['ochre'],2)
        if bc is not None: shape(c,[(48,-80),(66,-76),(64,-70),(50,-72)],bc,1.8)   # 上唇胡
        else: line(c,[(52,-70),(62,-68)],LINE,2.4)
        if o['face']=='half':   # 海拉：半边脸腐黑
            c.save(); c.new_path(); smooth(c,face); c.clip(); c.rectangle(-80,-200,70,220); c.set_source_rgb(*C['slate2']); c.fill(); c.restore()
        # 头饰
        if o['helmet']=='cone' and not o['hood']:
            shape(c,[(-56,-120,'c'),(-30,-182),(4,-226,'c'),(40,-186),(66,-122,'c')],C['iron'],lw)
            line(c,[(4,-224),(6,-130)],C['iron2'],2.4)
            shape(c,[(-58,-134,'c'),(68,-134,'c'),(68,-116,'c'),(-58,-116,'c')],C['gold'],lw*0.8,t=0)
            shape(c,[(56,-120,'c'),(68,-120,'c'),(70,-86,'c'),(60,-86,'c')],C['iron'],lw*0.8,t=0)
        elif o['helmet']=='spectacle' and not o['hood']:
            shape(c,[(-64,-122),(-54,-60),(-40,-30),(-16,-34),(-14,-100)],C['iron2'],lw)
            for yy in range(-112,-40,12):
                for xx in range(-56,-20,12): c.new_path(); c.arc(xx+(yy//12%2)*6,yy,3.6,0,7); c.set_source_rgb(*C['iron']); c.set_line_width(1.6); c.stroke()
            shape(c,[(-58,-120,'c'),(-46,-176),(4,-202),(50,-178),(64,-122,'c')],C['iron'],lw)
            line(c,[(4,-200),(6,-124)],C['iron2'],5); line(c,[(-40,-170),(50,-170)],C['iron2'],3)
            shape(c,[(-60,-134,'c'),(66,-134,'c'),(66,-118,'c'),(-60,-118,'c')],C['iron2'],lw*0.8,t=0)
            c.new_path(); c.move_to(14,-122); c.curve_to(10,-96,52,-92,58,-120); c.set_source_rgb(*LINE); c.set_line_width(13); c.stroke()
            c.new_path(); c.move_to(14,-122); c.curve_to(10,-96,52,-92,58,-120); c.set_source_rgb(*C['iron']); c.set_line_width(8); c.stroke()
            line(c,[(58,-122),(66,-88)],LINE,12); line(c,[(58,-122),(66,-88)],C['iron'],7)
        elif o['helmet']=='wing' and not o['hood']:
            shape(c,[(-56,-120,'c'),(-40,-176),(8,-196),(52,-176),(66,-122,'c')],C['iron'],lw)
            shape(c,[(-50,-150,'c'),(-110,-210),(-90,-170),(-120,-180),(-80,-130,'c')],C['bone'],lw)
            shape(c,[(-58,-134,'c'),(68,-134,'c'),(68,-116,'c'),(-58,-116,'c')],C['gold'],lw*0.8,t=0)
        m=c.get_matrix(); out['head']=m.transform_point(10,-160)
    # 近侧手臂
    arm(80,-250,p['nsh'],p['nsh']+p['nel'],True,p['handgrip'])
    ctx.restore(); return out

# ---------------- 狼（乌尔内斯式） ----------------
def wolf(ctx,x,y,L,pose=None,black=False,face_left=True):
    """L=体长像素(鼻尖到臀)；脚底在 y。black=黑绘剪影＋陶土刻线"""
    p=dict(jaw=0.0,head=0.0,fl1=0.12,fl2=-0.06,fr1=-0.18,fr2=0.04,hl1=-0.32,hl2=0.62,hr1=-0.12,hr2=0.5,tail=0.0,eye=1.0,ears=0.0,bob=0.0)
    p.update(pose or {})
    v=L/8.4; ctx.save(); ctx.translate(x,y+p['bob']); ctx.scale(v/100 if face_left else -v/100, v/100)
    lw=LWPX*100/v
    B=C['black'] if black else C['slate']; F=rgb('15110d') if black else C['slate2']; I=rgb('d08a46') if black else C['gold']
    def fleg(hx,hy,a1,a2,col,near):
        with J(ctx,hx,hy,a1) as c:
            shape(c,taper(165,40,17),col,lw)
            if near: line(c,[(14,20),(9,150)],I,3.5)
            with J(c,0,165,a2-a1) as c2:
                shape(c2,taper(150,15,11),col,lw)
                with J(c2,0,150,-a2) as c3:
                    shape(c3,[(-14,-10),(14,-12),(14,10,'c'),(-44,12,'c'),(-48,0),(-30,-8)],col,lw)
    def hleg(hx,hy,a1,a2,col,near):
        with J(ctx,hx,hy,a1) as c:
            shape(c,[(-62,-20),(0,-60),(64,-20),(44,80),(18,170),(-16,174),(-48,70)],col,lw)
            if near: spiral(c,0,10,44,2.0,I,3.6,a0=2.4,dirn=-1)
            with J(c,0,170,a2-a1) as c2:
                shape(c2,taper(165,15,10),col,lw)
                with J(c2,0,165,-a2) as c3:
                    shape(c3,[(-14,-10),(14,-12),(14,10,'c'),(-44,12,'c'),(-48,0),(-30,-8)],col,lw)
    fleg(-150,-330,p['fr1'],p['fr1']+p['fr2'],F,False)
    hleg(230,-360,p['hr1'],p['hr1']+p['hr2'],F,False)
    with J(ctx,300,-420,p['tail']+1.9) as c:   # 尾巴
        tl=[(-26,0),(-10,90),(20,170),(70,240),(80,300,'c'),(50,270),(40,320,'c'),(20,270),(-20,190),(-40,100)]
        shape(c,tl,B,lw); line(c,[(-14,30),(4,140),(50,250)],I,3.4)
    body=[(-238,-560),(-150,-470),(-40,-440),(80,-430),(250,-450),(320,-410),(318,-330),(250,-300),(140,-300),(40,-320),(-80,-262),(-200,-250),(-290,-300),(-318,-400),(-322,-500)]
    shape(ctx,body,B,lw)
    if not black:
        ctx.save(); ctx.new_path(); smooth(ctx,body); ctx.clip()
        shape(ctx,[(-330,-330),(-200,-300),(-60,-300),(100,-340),(320,-350),(330,-200),(-330,-200)],FURL,0)
        r=np.random.default_rng(3)
        for i in range(70):
            fx=r.uniform(-300,300); fy=r.uniform(-450,-330)+0.0*fx
            line(ctx,[(fx,fy),(fx+18,fy+8),(fx+30,fy+22)],C['slate2'],3)
        ctx.restore(); ctx.new_path(); smooth(ctx,body); ctx.set_source_rgb(*LINE); ctx.set_line_width(lw); ctx.stroke()
    line(ctx,[(-230,-268),(-120,-276),(0,-330),(130,-320),(250,-315),(296,-355),(270,-420),(120,-410),(-40,-420)],I,4)
    spiral(ctx,-170,-370,60,2.1,I,4.2,a0=0.4)
    fleg(-180,-320,p['fl1'],p['fl1']+p['fl2'],B,True)
    hleg(210,-350,p['hl1'],p['hl1']+p['hl2'],B,True)
    # 鬃毛
    for k in range(5):
        mx,my=-250+k*30,-520+k*42
        line(ctx,[(mx,my),(mx+60,my-34),(mx+120,my-14),(mx+140,my+26)],I,4.2); spiral(ctx,mx+142,my+26,17,1.5,I,3.6,a0=-1.3)
    m0=ctx.get_matrix(); out={'neck':m0.transform_point(-250,-470),'belly':m0.transform_point(0,-360),'hind':m0.transform_point(230,-360),'v':v}
    with J(ctx,-300,-520,p['head']) as c:
        # 远耳
        shape(c,[(10,-50),(44,-140,'c'),(60,-36)],F,lw)
        if p['jaw']>0.04:   # 口腔：上颚到下颌之间的暗红楔形
            ja=p['jaw']; tx_,ty_=-110,-50
            lx=-60+tx_*math.cos(-ja)-ty_*math.sin(-ja); ly=40+tx_*math.sin(-ja)+ty_*math.cos(-ja)
            shape(c,[(-20,36),(-228,16),(lx,ly),(-60,52)],rgb('5a1c18'),lw*0.8)
            line(c,[(-50,44),(lx*0.6-20,ly*0.6+20)],rgb('a8443a'),10)
        with J(c,-60,40,p['jaw']) as cj:   # 下颌（正角度=向下张开）
            shape(cj,[(30,-14),(-60,-6),(-150,-12),(-178,-10,'c'),(-168,6),(-90,22),(10,20)],B,lw)
            for k in range(6):
                tx=-160+k*22; shape(cj,[(tx,-10,'c'),(tx+9,-10,'c'),(tx+4,-28-5*(k%2),'c')],C['white'],1.4,t=0)
            mj=cj.get_matrix(); out['lower']=mj.transform_point(-120,-12)
        if p['jaw']>0.04:
            for k in range(6):
                tx=-218+k*24; shape(c,[(tx,22,'c'),(tx+9,22,'c'),(tx+4,42+5*(k%2),'c')],C['white'],1.4,t=0)
        head=[(60,10),(40,-50),(-20,-78),(-100,-62),(-160,-30),(-236,4,'c'),(-232,20),(-170,24),(-90,30),(-20,50),(40,46)]
        shape(c,head,B,lw)
        if not black:
            c.save(); c.new_path(); smooth(c,head); c.clip()
            shape(c,[(-240,10),(-150,-6),(-60,0),(20,20),(60,60),(-240,60)],FURL,0)
            c.restore(); c.new_path(); smooth(c,head); c.set_source_rgb(*LINE); c.set_line_width(lw); c.stroke()
        shape(c,[(-238,-2),(-226,-12),(-214,2),(-226,12)],C['black'],1.4)
        with J(c,-10,-60,p['ears']) as ce:
            shape(ce,[(-34,4),(-14,-104,'c'),(30,-8)],B,lw); line(ce,[(-16,-8),(-12,-74)],I,3.4)
        line(c,[(-226,18),(-140,24),(-80,30),(-40,50)],I,3.4); spiral(c,-38,40,14,1.4,I,3,a0=3.6)
        if p['eye']>0:
            ex,ey=-104,-36
            shape(c,[(ex-24,ey+4,'c'),(ex,ey-10),(ex+26,ey-2,'c'),(ex+44,ey+2,'c'),(ex+20,ey+10)],rgb('e8a940'),2)
            c.new_path(); c.arc(ex+3,ey,5.5,0,7); c.set_source_rgb(*LINE); c.fill()
            line(c,[(ex-32,ey-6),(ex+6,ey-20),(ex+54,ey-4)],I,3.2)
        m=c.get_matrix(); out.update({'upper':m.transform_point(-130,16),'mouth':m.transform_point(-150,10),'eye':m.transform_point(-100,-36),'head':m.transform_point(-40,-80)})
    ctx.restore(); return out
