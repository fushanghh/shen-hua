# 托特赌月 配乐与音效：古埃及 D Hijaz · 尼笛 · 乌德 · 达布卡 —— 全部 numpy 合成
import sys, os, numpy as np, soundfile as sf, subprocess, scipy.signal as ss
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film as F
SR=44100; TOT=F.TOTAL+0.8; N=int(SR*TOT); T0=[float(x) for x in F.T0]
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
