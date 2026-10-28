import os
# 北欧01 完整版配乐：numpy 合成芯片音乐 + 音效，按分镜时间表对点
import sys, numpy as np, soundfile as sf, subprocess, scipy.signal as ss
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import film4 as F
SR=44100; TOT=F.TOTAL+0.5; N=int(SR*TOT); T0=[float(x) for x in F.T0]
rng=np.random.default_rng(7)
mus=np.zeros(N); sfx=np.zeros(N)
def mtof(m): return 440*2**((m-69)/12)
def env(n,a=0.005,d=0.08,s=0.6,r=0.06):
    e=np.ones(n)*s; ia,idd,ir=int(a*SR),int(d*SR),int(r*SR); ia=max(1,min(ia,n)); e[:ia]=np.linspace(0,1,ia)
    j=min(ia+idd,n); e[ia:j]=np.linspace(1,s,j-ia)
    if 0<ir<n: e[-ir:]*=np.linspace(1,0,ir)
    return e
def pulse(f,n,duty=0.25,vib=0.0):
    t=np.arange(n)/SR; ph=np.cumsum(f*(1+vib*np.sin(2*np.pi*5.5*t)*np.clip(t/0.25,0,1))/SR); return np.where(ph%1<duty,1.0,-1.0)
def tri(f,n):
    ph=np.arange(n)*f/SR; w=4*np.abs(ph%1-0.5)-1; return np.round(w*7.5)/7.5
def noise(n,period=1): v=rng.choice([-1.0,1.0],size=n//period+2); return np.repeat(v,period)[:n]
def put(sig,t,vol,buf):
    i=int(t*SR)
    if i>=N: return
    sig=sig[:N-i]; buf[i:i+len(sig)]+=sig*vol
def note(t,dur,m,vol,ch='p',duty=0.25,vib=0.0,s=0.6,r=0.06,a=0.005):
    n=int(dur*SR); f=mtof(m); w=pulse(f,n,duty,vib) if ch=='p' else tri(f,n); put(w*env(n,a=a,s=s,r=r),t,vol,mus)
def kick(t,vol=0.6):
    n=int(0.25*SR); tt=np.arange(n)/SR; f=150*np.exp(-tt*25)+45; ph=2*np.pi*np.cumsum(f)/SR
    put((np.sign(np.sin(ph))*0.5+np.sin(ph)*0.5)*np.exp(-tt*9),t,vol,mus)
def snare(t,vol=0.3): n=int(0.18*SR); tt=np.arange(n)/SR; put(noise(n,2)*np.exp(-tt*22),t,vol,mus)
def hat(t,vol=0.08): n=int(0.05*SR); tt=np.arange(n)/SR; put(noise(n,1)*np.exp(-tt*80),t,vol,mus)
def boom(t,vol=1.0,buf=None):
    n=int(1.8*SR); tt=np.arange(n)/SR; f=90*np.exp(-tt*6)+32; w=np.sin(2*np.pi*np.cumsum(f)/SR)
    put((w*0.9+noise(n,24)*0.25)*np.exp(-tt*2.4),t,vol,mus if buf is None else buf)
def lp(x,a): return ss.lfilter([a],[1,a-1],x)

DOR=[0,2,3,5,7,9,10]  # D 多利亚
PHR=[0,1,4,5,7,8,10]  # 弗里几亚属（暗、异域）
D=62
def deg(scale,k,base=D):
    o,i=divmod(k,7); return base+12*o+scale[i]
def melody(t0,t1,scale,bpm,vol,seed,base=D,duty=0.25,step=0.5,rest=0.25,vib=0.008,octave=0):
    r=np.random.default_rng(seed); B=60/bpm; t=t0; k=4
    while t<t1-0.2:
        dur=B*step*r.choice([1,1,2,1,3])
        if r.random()>rest: note(t,dur*0.95,deg(scale,k,base)+12*octave,vol,'p',duty,vib,s=0.7,r=0.08)
        k=int(np.clip(k+r.choice([-2,-1,-1,1,1,2,0]),0,9)); t+=dur
def bass(t0,t1,scale,bpm,vol,pat=(0,0,4,0,3,0,4,2),base=D-24,step=0.5):
    B=60/bpm; t=t0; i=0
    while t<t1-0.1: note(t,B*step*0.9,deg(scale,pat[i%len(pat)],base),vol,'t',s=0.85); t+=B*step; i+=1
def drums(t0,t1,bpm,vol,style='folk'):
    B=60/bpm; t=t0; i=0
    while t<t1-0.05:
        if style=='folk':
            if i%4==0: kick(t,0.45*vol)
            if i%4==2: snare(t,0.22*vol)
            hat(t+B/2,0.06*vol)
        elif style=='war':
            kick(t,0.55*vol); 
            if i%2==1: snare(t,0.3*vol)
            hat(t+B/2,0.08*vol); 
            if i%4==3: kick(t+B/2,0.4*vol)
        elif style=='heart':
            if i%2==0: kick(t,0.5*vol); kick(t+0.18,0.3*vol)
        t+=B; i+=1
def drone(t0,t1,m,vol):
    n=int((t1-t0)*SR); put(tri(mtof(m),n)*env(n,a=0.4,s=1,r=0.6),t0,vol,mus); put(tri(mtof(m+7),n)*env(n,a=0.6,s=1,r=0.6),t0,vol*0.5,mus)
def horn(t,dur,m,vol): note(t,dur,m,vol,'p',0.5,0.006,s=0.85,r=0.3,a=0.08)
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

# ---------------- 音效 ----------------
tt=np.arange(N)/SR
w=lp(rng.standard_normal(N),0.02); wenv=np.zeros(N)
for a,b in ((0,S(3)),(S(38),S(39)),(S(43),TOT)): wenv[int(a*SR):int(b*SR)]=1
wenv=np.convolve(wenv,np.ones(int(0.5*SR))/(0.5*SR),'same'); sfx+=w*(0.6+0.4*np.sin(tt*1.3))*wenv*0.45
def growl(t,dur,vol):
    n=int(dur*SR); x=np.arange(n)/SR; saw=((x*58)%1)*2-1
    am=0.6+0.4*np.sign(np.sin(2*np.pi*23*x+3*np.sin(2*np.pi*3*x))); g=(saw*0.6+lp(rng.standard_normal(n),0.08)*1.5)*am
    put(lp(g,0.15)*np.minimum(1,x/0.3)*np.minimum(1,(dur-x)/0.4),t,vol,sfx)
def yip(t,vol=0.2):
    for k in range(2):
        n=int(0.14*SR); x=np.arange(n)/SR; f=900+700*np.sin(np.pi*x/0.14); put(np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*np.exp(-x*12)*0.7,t+k*0.2,vol,sfx)
def whoosh(t,vol=0.18):
    n=int(0.35*SR); x=np.arange(n)/SR; y=lp(rng.standard_normal(n),0.15); put(y*np.sin(np.pi*x/0.35)*3,t-0.2,vol,sfx)
def clank(t,vol=0.25,f0=1800):
    n=int(0.5*SR); x=np.arange(n)/SR; s_=(np.sin(2*np.pi*f0*x)+0.6*np.sin(2*np.pi*f0*2.31*x)+0.4*np.sin(2*np.pi*f0*3.7*x))*np.exp(-x*9)
    put(s_+noise(n,1)*np.exp(-x*60)*0.6,t,vol,sfx)
def crash(t,vol=0.6):
    for k in range(10): clank(t+rng.uniform(0,0.5),vol*rng.uniform(0.3,0.7),rng.uniform(900,2600))
    n=int(0.8*SR); x=np.arange(n)/SR; put(noise(n,1)*np.exp(-x*6),t,vol*0.5,sfx); boom(t,0.6,sfx)
def splash(t,vol=0.5):
    n=int(1.2*SR); x=np.arange(n)/SR; put(lp(rng.standard_normal(n),0.3)*np.exp(-x*3)*np.minimum(1,x/0.02),t,vol,sfx)
def water(t,dur,vol=0.2):
    n=int(dur*SR); x=np.arange(n)/SR; b=lp(rng.standard_normal(n),0.05)*(0.6+0.4*np.sin(2*np.pi*3.3*x))
    for k in range(int(dur*6)):
        m=int(rng.uniform(0,n-2000)); f=rng.uniform(500,1200); y=np.sin(2*np.pi*np.cumsum(np.linspace(f,f*1.6,1800))/SR)*np.exp(-np.arange(1800)/400); b[m:m+1800]+=y*0.3
    put(b*np.minimum(1,x/0.4)*np.minimum(1,(dur-x)/0.4),t,vol,sfx)
def sparkle(t,vol=0.06):
    for k in range(6): note(t+k*0.06,0.12,86+k*2,vol,'p',0.125,s=0.3,r=0.05)
def thud(t,vol=0.5):
    n=int(0.4*SR); x=np.arange(n)/SR; put(np.sin(2*np.pi*70*x)*np.exp(-x*14)+lp(noise(n,1),0.2)*np.exp(-x*20),t,vol,sfx)
for i in range(1,len(T0)-1): whoosh(T0[i])
growl(0.4,3.2,0.5); growl(S(43)+0.4,3.0,0.45)
for t in (S(4)+0.3,S(4)+2.7): sparkle(t)
yip(S(4)+0.3); yip(S(9)+1.0,0.15); yip(S(11)+0.6,0.2)
splash(S(6)+3.0,0.6)
for k in range(2): thud(S(12)+1.5*(k+1),0.7)
for i in (14,16): clank(S(i)+0.5,0.2); clank(S(i)+1.6,0.15)
growl(S(15)+0.2,1.1,0.35); crash(S(15)+1.3); growl(S(17)+0.2,1.3,0.4); crash(S(17)+1.5,0.7)
for i in range(21,27):    # 打铁对点：(lt*2.4+k*0.5)%1 == 0.75
    for k in (0,1):
        for n_ in range(20):
            lt=(n_+0.75-k*0.5)/2.4
            if 0<lt<F.S[i][0]: clank(S(i)+lt,0.10,2200+k*300)
for i in (22,23,24):
    for k in range(2): sparkle(S(i)+0.3+k*1.6,0.04)
sparkle(S(26)+0.3,0.06)
growl(S(28)+1.0,2.0,0.3); growl(S(29)+0.4,2.8,0.35); growl(S(32)+0.2,3.6,0.45)
put(noise(int(0.4*SR),1)*np.exp(-np.arange(int(0.4*SR))/SR*30)*0.9+np.sin(2*np.pi*55*np.arange(int(0.4*SR))/SR)*np.exp(-np.arange(int(0.4*SR))/SR*8),bite,0.8,sfx)
for k in range(6): thud(S(35)+0.6+k/1.6,0.4)
clank(S(36)+1.2,0.25,1400); water(S(37)+0.2,4.2,0.25)
crash(S(39)+1.0,0.8); growl(S(39)+1.0,3.5,0.6); growl(S(40)+0.5,3.5,0.5); clank(S(41)+1.6,0.3,1600); growl(S(41)+1.4,2.0,0.4)

mix=np.tanh((mus*0.75+sfx*0.5)*1.0); st=np.stack([mix,mix],1); st[:,1]=np.roll(st[:,1],int(0.008*SR))
sf.write('out/mix_raw.wav',st,SR)
subprocess.run(['ffmpeg','-v','error','-y','-i','out/mix_raw.wav','-af','loudnorm=I=-15:TP=-1.5:LRA=9','-ar','44100','out/mix.wav'],check=True)
print('ok',TOT)
