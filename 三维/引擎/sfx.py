import numpy as np, wave, film
SR=44100; N=int(film.TOTAL*SR)+SR; out=np.zeros(N)
rng=np.random.default_rng(1)
def add(sig,t,g=1.0):
    i=int(t*SR); j=min(N,i+len(sig)); out[i:j]+=sig[:j-i]*g
def drum():
    t=np.arange(int(0.9*SR))/SR
    f=60+60*np.exp(-t*25)
    body=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*6)
    hit=rng.normal(size=len(t))*np.exp(-t*60)*0.4
    return np.tanh((body+hit)*1.5)*0.9
def bell():
    t=np.arange(int(3.5*SR))/SR; s=np.zeros_like(t)
    for f,a,d in [(420,1,1.0),(420*2.76,.5,1.6),(420*5.4,.25,2.5),(420*1.5,.35,1.2),(840*1.01,.3,1.3)]:
        s+=a*np.sin(2*np.pi*f*t)*np.exp(-t*d)
    s*= (1-np.exp(-t*400))
    return s/np.abs(s).max()*0.6
def lp(x,a): 
    y=np.zeros_like(x); acc=0
    for i in range(len(x)): acc+=a*(x[i]-acc); y[i]=acc
    return y
def water(dur):
    n=int(dur*SR); x=rng.normal(size=n)
    # cheap bandpass via differences of moving averages
    k1,k2=8,60
    c=np.cumsum(np.r_[0,x]); a=(c[k1:]-c[:-k1])/k1; b=(c[k2:]-c[:-k2])/k2
    m=min(len(a),len(b)); y=a[:m]-b[:m]
    y*=0.6+0.4*np.sin(np.arange(m)/SR*2*np.pi*0.7)
    # droplets
    for _ in range(int(dur*9)):
        i=rng.integers(0,m-2000); tt=np.arange(1500)/SR; f=900+rng.random()*900
        y[i:i+1500]+=np.sin(2*np.pi*f*tt*(1+tt*8))*np.exp(-tt*60)*1.5
    return y/ (np.abs(y).max()+1e-9)*0.25
def tick():
    t=np.arange(int(0.05*SR))/SR
    return np.sin(2*np.pi*2400*t)*np.exp(-t*150)*0.25+rng.normal(size=len(t))*np.exp(-t*300)*0.1
def whoosh(d=1.2):
    n=int(d*SR); x=rng.normal(size=n); t=np.arange(n)/SR
    c=np.cumsum(np.r_[0,x]); k=40; y=(c[k:]-c[:-k])/k; y=y[:n-k]
    env=np.sin(np.pi*np.arange(len(y))/len(y))**2
    return y*env/np.abs(y).max()*0.35
D,B=drum(),bell()
for i,s in enumerate(film.SH):
    t0=film.T0[i]; dur=s['dur']; k=s['k']
    for sd,tt in s.get('strikes',[]): add(D if sd=='L' else B, t0+tt, 0.9 if sd=='L' else 0.7)
    flow = k not in ('quote',)
    g={'water':1.0,'gears':0.35,'hook':0.3,'legacy':0.3}.get(k,0.12)
    if k=='rust':
        w=water(dur)*np.clip(1-np.arange(int(dur*SR))/(dur*SR*0.7),0,1)[:len(water(0.01))*0+int(dur*SR)-60] if False else None
        ww=water(dur); env=np.clip(1-np.arange(len(ww))/(len(ww)*0.7),0,1); add(ww*env,t0,0.4)
    elif flow and k not in ('eclipse','yixing','liang','sun','moon','end','susong'):
        add(water(dur),t0,g)
    if k in ('gears','hook','legacy','water'):
        for tt in np.arange(0.2,dur,0.42): add(tick(),t0+tt,0.7 if k!='water' else 0.3)
    if k=='title': add(whoosh(1.4),t0+0.0,1); add(B,t0+0.6,0.5)
    if k=='end': add(B,t0+3.6,0.45)
    if k=='rust':
        for tt in np.linspace(0.2,dur*0.7,8): add(tick(),t0+tt*(1+0.1*tt),0.6)
# fades
out=out[:int(film.TOTAL*SR)]
out/=max(1,np.abs(out).max()/0.85)
pcm=(out*32767).astype(np.int16)
with wave.open('sfx.wav','wb') as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(pcm.tobytes())
print('ok',len(out)/SR)
