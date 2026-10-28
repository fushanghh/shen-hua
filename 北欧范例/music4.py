import os
# ===== 埃及金字塔风配乐：Hijaz 调式 · 奈伊笛滑音 · 乌德琴 · 达布卡手鼓 · 弦乐铺底 =====
HJ=[0,1,4,5,7,8,10]   # D Hijaz：D Eb F# G A Bb C
D=62
def hz(k,base=D):
    o,i=divmod(int(k),7); return mtof(base+12*o+HJ[i])
def oud(t,f,dur,vol,bright=0.5):
    n=int(min(dur+0.6,2.5)*SR); p=max(2,int(SR/f)); buf=rng.uniform(-1,1,p)*(1.0)
    buf=lp(buf,bright); out=np.zeros(n); i=0; prev=buf.copy()
    while i<n:
        m=min(p,n-i); out[i:i+m]=prev[:m]; prev=0.996*0.5*(prev+np.roll(prev,1)); i+=m
    e=np.ones(n); r=int(0.08*SR); k=int(dur*SR)
    if k<n: e[k:]=np.exp(-np.arange(n-k)/SR*14)
    put(out*e,t,vol,mus)
def ney(t0,notes,bpm,vol,base=D,glide=0.07,breath=0.12):
    """notes: [(级数 or None, 拍)] → 连续音高带滑音、颤音、气声"""
    B=60/bpm; tot=sum(b for _,b in notes)*B; n=int(tot*SR)+1
    f=np.zeros(n); a=np.zeros(n); t=0; last=None
    for k_,b in notes:
        i0,i1=int(t*SR),int((t+b*B)*SR); i1=min(i1,n)
        if k_ is None: t+=b*B; continue
        ft=hz(k_,base); seg_=np.full(i1-i0,ft)
        if last is not None:
            g=min(int(glide*SR),i1-i0); seg_[:g]=np.geomspace(last,ft,g)
        f[i0:i1]=seg_; L=i1-i0; x=np.arange(L)/SR
        env_=np.minimum(1,x/0.06)*np.minimum(1,(L/SR-x)/0.05+0.15); a[i0:i1]=np.clip(env_,0,1)
        vib=np.clip((x-0.25)/0.4,0,1)*0.012*np.sin(2*np.pi*5.2*x); f[i0:i1]*=1+vib
        last=ft; t+=b*B
    f[f==0]=mtof(base); ph=2*np.pi*np.cumsum(f)/SR
    tone=np.sin(ph)+0.32*np.sin(2*ph)+0.14*np.sin(3*ph)+0.05*np.sin(4*ph)
    br=ss.lfilter(*ss.butter(2,[800/(SR/2),5000/(SR/2)],'band'),rng.standard_normal(n))
    a=np.convolve(a,np.ones(400)/400,'same')
    put((tone*0.8+br*breath*3)*a,t0,vol,mus)
def pad(t0,t1,degs,vol,base=D-12):
    n=int((t1-t0)*SR); x=np.arange(n)/SR; out=np.zeros(n)
    for k_ in degs:
        for dt in (-0.004,0,0.005):
            f=hz(k_,base)*(1+dt); out+=((x*f)%1*2-1)
    out=ss.lfilter(*ss.butter(2,1400/(SR/2)),out)/(3*len(degs))
    e=np.minimum(1,x/1.2)*np.minimum(1,(t1-t0-x)/1.0); put(out*np.clip(e,0,1),t0,vol,mus)
def doum(t,vol=0.5):
    n=int(0.4*SR); x=np.arange(n)/SR; f=95*np.exp(-x*5)+62; put(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*7)+lp(rng.standard_normal(n),0.1)*np.exp(-x*30)*0.3,t,vol,mus)
def tek(t,vol=0.25,ka=False):
    n=int(0.07*SR); x=np.arange(n)/SR; y=ss.lfilter(*ss.butter(2,2500/(SR/2),'high'),rng.standard_normal(n))*np.exp(-x*(70 if not ka else 90))
    y+=np.sin(2*np.pi*(780 if not ka else 640)*x)*np.exp(-x*60)*0.6; put(y,t,vol*(0.6 if ka else 1),mus)
def riq(t,vol=0.06):
    n=int(0.12*SR); x=np.arange(n)/SR; put(ss.lfilter(*ss.butter(2,6000/(SR/2),'high'),rng.standard_normal(n))*np.exp(-x*30),t,vol,mus)
def frame(t,vol=0.5):
    n=int(1.0*SR); x=np.arange(n)/SR; f=70*np.exp(-x*3)+48; put(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*3.5),t,vol,mus)
RHY={'maqsum':['D','T','.','T','D','.','T','.'],'baladi':['D','D','.','T','D','.','T','.'],
     'malfuf':['D','.','.','T','.','.','T','.'],'heart':['D','.','.','.','d','.','.','.'],'saidi':['D','T','.','D','D','.','T','.']}
def perc(t0,t1,bpm,style,vol=1.0,fills=True):
    E8=60/bpm/2; pat=RHY[style]; t=t0; i=0
    while t<t1-0.02:
        c_=pat[i%8]
        if c_=='D': doum(t,0.55*vol)
        elif c_=='d': doum(t,0.3*vol)
        elif c_=='T': tek(t,0.26*vol)
        else:
            if fills and style!='heart': tek(t,0.12*vol,ka=True)
        if style!='heart' and i%2==1: riq(t,0.05*vol)
        t+=E8; i+=1
def oud_ost(t0,t1,bpm,vol,pat=(0,4,3,4,1,4,0,4),base=D-12):
    E8=60/bpm/2; t=t0; i=0
    while t<t1-0.05: oud(t,hz(pat[i%len(pat)],base),E8*0.9,vol,0.55); t+=E8; i+=1
def oud_mel(t0,notes,bpm,vol,base=D):
    B=60/bpm; t=t0
    for k_,b in notes:
        if k_ is not None:
            oud(t,hz(k_,base),b*B,vol,0.6)
            if b>=1.5:   # 长音用乌德琴的震音
                for j in range(1,int(b*B/0.11)): oud(t+j*0.11,hz(k_,base),0.1,vol*0.45,0.6)
        t+=b*B
    return t
PA=[(4,1),(5,0.5),(4,0.5),(3,0.5),(2,0.5),(1,1),(2,0.5),(1,0.5),(0,2),(None,1)]
PB=[(0,0.5),(1,0.5),(2,1),(3,0.5),(4,1.5),(5,0.5),(4,0.5),(3,1),(2,1),(1,0.5),(0,0.5)]
PC=[(7,1.5),(6,0.5),(5,1),(4,1),(5,0.5),(4,0.5),(3,0.5),(2,0.5),(1,1),(0,1)]
PD=[(4,2),(5,1),(4,1),(2,2),(1,1),(0,1)]
PE=[(0,1),(2,1),(4,2),(5,0.5),(4,0.5),(3,0.5),(2,0.5),(1,1),(0,1)]
def seq(t0,t1,bpm,phrases,fn,vol,base=D):
    B=60/bpm; t=t0; k=0
    while True:
        ph=phrases[k%len(phrases)]; L=sum(b for _,b in ph)*B
        if t+L>t1+0.3: break
        fn(t,ph,bpm,vol,base); t+=L; k+=1
S=lambda i:T0[i]
up=lambda ph:[(None if k_ is None else k_,b) for k_,b in ph]
# ① 钩子：持续低音 + 框鼓 + 低音奈伊笛
drone(0,S(3),D-24,0.30); pad(0,S(2),[0,4],0.20)
frame(0.05,0.9); frame(S(1),0.8); frame(S(1)+2.5,0.5)
ney(0.6,PD,72,0.16,base=D-12); 
# ② 标题：大鼓 + 和声
frame(S(2)+0.2,1.0); boom(S(2)+0.2,0.6); pad(S(2),S(3)+1,[0,2,4],0.22)
ney(S(2)+0.6,[(7,2),(6,0.5),(5,0.5),(4,2)],72,0.13)
# ③ 洛基三子 / 预言 / 奥丁：乌德琴固定音型 + 马克苏姆鼓 + 奈伊笛主题
B1=96
oud_ost(S(3),S(9),B1,0.22); perc(S(3),S(5),B1,'maqsum',0.7); perc(S(5),S(6),B1,'heart',0.9); perc(S(6),S(9),B1,'maqsum',0.9)
seq(S(3),S(9),B1,[PA,PB,PA,PC],lambda t,ph,b,v,ba:ney(t,ph,b,v,ba),0.15)
pad(S(5),S(6),[0,1,4],0.2)
# ④ 大厅：轻快巴拉迪，乌德琴领奏
B2=100
oud_ost(S(9),S(13),B2,0.16,(0,4,2,4,0,4,1,4)); perc(S(9),S(13),B2,'baladi',0.9)
seq(S(9),S(13),B2,[PB,PE,PA],lambda t,ph,b,v,ba:oud_mel(t,ph,b,v,ba),0.30)
# ⑤ 铁链：萨伊迪重拍 + 弦乐 + 高八度奈伊
B3=112
perc(S(13),S(20),B3,'saidi',1.2); oud_ost(S(13),S(20),B3,0.2,(0,0,4,0,1,0,4,3)); pad(S(13),S(20),[0,4],0.22)
seq(S(13),S(20),B3,[PC,PA,PB],lambda t,ph,b,v,ba:ney(t,ph,b,v,ba),0.14)
# ⑥ 矮人工坊：神秘，持续音 + 乌德琴震音旋律
drone(S(20),S(27),D-24,0.22); pad(S(20),S(27),[0,1,4],0.16)
seq(S(20),S(26),90,[PE,PD],lambda t,ph,b,v,ba:oud_mel(t,ph,b,v,ba+12),0.20)
for i in range(int((S(27)-S(26))/0.125)):
    oud(S(26)+i*0.125,hz([7,8,9,10,9,8][i%6]),0.12,0.12,0.8)
# ⑦ 林格维岛：紧张，心跳鼓渐强
B4=104
for k,i in enumerate(range(27,33)):
    oud_ost(S(i),S(i+1),B4,0.16+0.02*k,(0,1,0,1,0,4,1,0))
    perc(S(i),S(i+1),B4,'heart' if i<31 else 'malfuf',0.7+0.12*k,fills=False)
pad(S(27),S(33),[0,1],0.2); ney(S(28)+0.2,PD,72,0.12)
for i in range(16): tek(S(33)-0.9+i*0.05,0.08+0.02*i)
# ⑧ 咬下：重击后静默
bite=S(33)+0.62; frame(bite,1.3); boom(bite,1.1); pad(bite+0.4,S(34)+0.5,[0,1],0.18)
# ⑨ 余波：独奏奈伊笛哀歌
drone(S(34),S(39),D-24,0.22); pad(S(34),S(39),[0,4],0.16)
ney(S(34)+0.3,PD+[(None,1)]+PA,66,0.17); ney(S(36)+2.0,PE+PD,66,0.15)
# ⑩ 诸神黄昏：全编制
B5=120
perc(S(39),S(42),B5,'saidi',1.4); oud_ost(S(39),S(42),B5,0.24,(0,0,1,0,4,3,1,0)); pad(S(39),S(42),[0,2,4],0.28)
seq(S(39),S(42),B5,[PC,PC,PA],lambda t,ph,b,v,ba:ney(t,ph,b,v,ba+12),0.12)
for i in (39,40,41): frame(S(i)+0.1,1.0)
# ⑪ 寓意：乌德琴 + 奈伊笛收束到主音
pad(S(42),S(43)+0.5,[0,2,4],0.2); oud_mel(S(42)+0.3,PA,80,0.26); ney(S(42)+0.3,PA,80,0.10,base=D+12)
# ⑫ 回到开场
drone(S(43),TOT,D-24,0.30); frame(S(43)+0.05,0.9); ney(S(43)+0.6,PD,72,0.15,base=D-12)
