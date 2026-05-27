"""Write the mapping function over each control on the clean MK2 template image
(images/Screenshot 2026-05-26 221606.png). Coordinates come from green-region
detection (original 730x576); we render at 2x for readability."""
from PIL import Image, ImageDraw, ImageFont

SRC="images/Screenshot 2026-05-26 221606.png"; S=2
im=Image.open(SRC).convert("RGB").resize((730*S,576*S))
ov=Image.new("RGBA",im.size,(0,0,0,0)); d=ImageDraw.Draw(ov)
def F(sz,b=True): return ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf" if b else "C:/Windows/Fonts/arial.ttf",sz)
TXT=(255,255,255,255); ACC=(255,176,0,255)
def box(cx,cy,w,h,lines,fnt,fill,tcol=TXT,r=8):
    x0,y0=cx-w/2,cy-h/2
    d.rounded_rectangle([x0,y0,x0+w,y0+h],radius=r,fill=fill,outline=(0,0,0,180),width=2)
    if isinstance(lines,str): lines=lines.split("\n")
    lh=fnt.size+2; ty=cy-lh*len(lines)/2
    for ln in lines:
        tw=d.textlength(ln,font=fnt); d.text((cx-tw/2,ty),ln,font=fnt,fill=tcol); ty+=lh
def sc(x,y): return x*S,y*S

DA=(46,111,176,225); DB=(31,138,91,225); DC=(138,79,192,230); VU=(176,58,58,230)
GRP=(40,44,54,235); ACCBOX=(70,55,10,235)

# ---- GROUP buttons A-H (function = pad page) ----
groups=[("A","Stems\nPads",62,397),("B","Loops",121,397),("C","Beat\njump",179,397),("D","Remix\nC",238,397),
        ("E","Pitch\nKey",62,443),("F","Loop\nRoll",179-58,443),("G","VU\nMeter",179,443),("H","Trans\nport",238,443)]
for L,fn,x,y in groups:
    cx,cy=sc(x,y); box(cx,cy,96,74,f"{L}\n{fn}",F(15),GRP,ACC)

# ---- DISPLAY KNOBS (k1-8) and BUTTONS (b1-8) ----
kxs=[192,261,329,400,469,538,607,675]
stem4=["Drums","Bass","Other","Vocals"]
for i,x in enumerate(kxs):
    cx,cy=sc(x,175)
    lbl=("A " if i<4 else "B ")+stem4[i%4]
    box(cx,cy,62,40,["VOL",lbl],F(11),(40,44,54,235),ACC)
for i,x in enumerate(kxs):
    cx,cy=sc(x,24)
    lbl=("A " if i<4 else "B ")+stem4[i%4]
    box(cx,cy,62,34,["MUTE",lbl],F(10),(40,44,54,225),TXT)
d.text(sc(150,150)[0],F(12)) if False else None
box(*sc(433,98),300,30,"DISPLAY: stems mix  ·  boots to 05 STEMS FULL MIX",F(14),(12,40,24,210),(150,235,180,255))

# ---- DIAL ----
cx,cy=sc(150,272); box(cx,cy,90,70,"DIAL\nturn=browse\npush=LOAD",F(12),ACCBOX,ACC)
# ---- master TEMPO / ENTER / master arrows (best-effort positions) ----
box(*sc(62,257),48,22,"VOL",F(10),(40,44,54,220),TXT)
box(*sc(62,289),48,22,"SWING",F(9),(40,44,54,220),(150,156,168,255))
box(*sc(62,322),48,22,"TEMPO=Ld A",F(9),ACCBOX,ACC)
box(*sc(238,263),52,34,"ENTER\nLoad B",F(11),ACCBOX,ACC)

# ---- TRANSPORT (regular 4-col grid, two rows) ----
trans_top=[("RESTART","start A+B",62),("STEP <","jump -4",121),("STEP >","jump +4",179),("GRID","focus A↔B",238)]
trans_bot=[("PLAY","focus",62),("REC","record",121),("ERASE","—",179),("SHIFT","—",238)]
for L,fn,x in trans_top:
    cx,cy=sc(x,518); box(cx,cy,98,40,[L,fn],F(11),(34,38,48,235),ACC)
for L,fn,x in trans_bot:
    cx,cy=sc(x,555); box(cx,cy,98,34,[L,fn],F(11),(34,38,48,235),TXT if fn!="—" else (120,126,138,255))

# ---- BROWSE (top-left) ----
box(*sc(63,77),50,32,"BROWSE\nview",F(10),ACCBOX,ACC)

# ---- PADS 4x4 : deck split + numbers + pointer to pad maps ----
padcols=[410,494,578,662]; padrows=[(281,[13,14,15,16]),(365,[9,10,11,12]),(450,[5,6,7,8]),(534,[1,2,3,4])]
for ri,(ry,nums) in enumerate(padrows):
    tint=(46,111,176,90) if ri<2 else (31,138,91,90)
    for ci,n in enumerate(nums):
        cx,cy=sc(padcols[ci],ry)
        d.rounded_rectangle([cx-74,cy-74,cx+74,cy+74],radius=12,fill=tint,outline=(0,0,0,120),width=2)
        tw=d.textlength(str(n),font=F(26)); d.text((cx-tw/2,cy-16),str(n),font=F(26),fill=(255,255,255,255))
box(*sc(536,281),150,30,"DECK A pads (9-16)",F(13),(46,111,176,235))
box(*sc(536,534),150,30,"DECK B pads (1-8)",F(13),(31,138,91,235))
box(*sc(536,365),250,26,"16 pads change per Group — see A-H maps",F(12),(20,20,24,210),ACC)

out=Image.alpha_composite(im.convert("RGBA"),ov).convert("RGB")
# title banner
band=Image.new("RGB",(out.width,70),(22,24,29)); out2=Image.new("RGB",(out.width,out.height+70),(22,24,29))
out2.paste(band,(0,0)); out2.paste(out,(0,70))
dd=ImageDraw.Draw(out2)
t="GideonSTEM-Maschine  —  Maschine MK2 control map (ALPHA)"
tw=dd.textlength(t,font=F(30)); dd.text(((out2.width-tw)/2,18),t,font=F(30),fill=(255,176,0))
out2.save("template_labeled.png"); print("wrote template_labeled.png",out2.size)
