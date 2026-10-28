import os
from PIL import Image, ImageDraw, ImageFont
import re, math
W,H=960,720
FZ=""+os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','字体','NotoSerifSC-Bold.otf')+""; FE="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
INK=(34,19,5); KW={'b':(49,82,135),'r':(157,64,39),'g':(70,110,60),'n':(34,19,5)}
NAVY=(24,30,42); STRIP=[(150,52,36),(196,160,72),(52,82,120),(84,110,72),(222,210,182)]
def strip(d,y,h):
    x=0;i=0
    while x<W:
        d.rectangle([x,y,x+13,y+h],fill=STRIP[i%4]); d.rectangle([x+14,y,x+16,y+h],fill=(236,226,200)); x+=17;i+=1
def valknut(d,cx,cy,r,col,w=2):
    for k in range(3):
        a0=k*2*math.pi/3; ox,oy=cx+r*.33*math.cos(a0-math.pi/2),cy+r*.33*math.sin(a0-math.pi/2)
        p=[(ox+r*.62*math.cos(a0+j*2*math.pi/3-math.pi/2),oy+r*.62*math.sin(a0+j*2*math.pi/3-math.pi/2)) for j in range(3)]
        d.line(p+[p[0]],fill=col,width=w)
def segs(s):
    out=[];cur='n'
    for t in re.split(r'(\[/?[brg]\])',s):
        if not t: continue
        if t.startswith('[/'): cur='n';continue
        if t.startswith('['): cur=t[1];continue
        out.append((t,cur))
    return out
def rich(d,cx,y,s,f,en=False):
    sg=segs(s); w=sum(d.textlength(t,font=f) for t,_ in sg); x=cx-w/2
    for t,c in sg:
        col=KW[c] if not(en and c=='n') else (96,78,58)
        d.text((x,y),t,font=f,fill=col); x+=d.textlength(t,font=f)
PY0,PY1=20,584
def frame(src,zh,en,tags=(),cy=0,chh=None):
    src=src.convert('RGB'); ch=chh or int(src.width/(W/(PY1-PY0)))
    pic=src.crop((0,cy,src.width,cy+ch)).resize((W,PY1-PY0),Image.LANCZOS)
    img=Image.new('RGB',(W,H)); img.paste(pic,(0,PY0)); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W,13],fill=NAVY); strip(d,13,5); d.rectangle([0,18,W,20],fill=NAVY)
    d.ellipse([W/2-15,0,W/2+15,28],fill=NAVY,outline=(196,160,72),width=2); valknut(d,W/2,14,22,(214,176,90),2)
    y0=PY1; d.rectangle([0,y0,W,H],fill=(186,150,96)); d.rectangle([0,y0,W,y0+3],fill=NAVY)
    bx0,bx1,by0,by1=70,W-70,y0+14,H-30
    d.rectangle([bx0,by0,bx1,by1],fill=(238,229,204),outline=(110,84,54),width=1)
    d.rectangle([bx0,by0,bx1,by0+5],fill=NAVY); 
    x=bx0;i=0
    while x<bx1-2:
        d.rectangle([x+1,by0+1,min(x+11,bx1-1),by0+4],fill=STRIP[i%4]); x+=13;i+=1
    d.rectangle([0,H-22,W,H],fill=NAVY); strip(d,H-19,5)
    fz=ImageFont.truetype(FZ,22); fe=ImageFont.truetype(FE,12)
    y=by0+12
    rich(d,W/2,y,zh[0],fz); rich(d,W/2,y+29,zh[1],fz)
    rich(d,W/2,y+60,en[0]+' '+en[1],fe,True)
    fz2=ImageFont.truetype(FZ,15); fe2=ImageFont.truetype(FE,10)
    for name,enn,x,yy in tags:
        h=len(name)*17+10; d.rectangle([x,yy,x+24,yy+h],fill=(246,240,226),outline=(30,24,20),width=1)
        for i,ch in enumerate(name): d.text((x+4,yy+5+i*17),ch,font=fz2,fill=INK)
        tw=d.textlength(enn,font=fe2); d.text((x+12-tw/2,yy+h+3),enn,font=fe2,fill=(240,230,200),stroke_width=2,stroke_fill=(30,24,20))
    return img
