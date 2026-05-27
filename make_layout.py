"""Generate labeled layout diagrams for GideonSTEM-Maschine:
   - master.png       : whole MK2, every control labeled with its mapping function
   - padA..padH.png   : the 8 Group pad pages, each pad labeled
   - cheatsheet.png    : master + all 8 pad pages stacked (the listing image)
All data taken from build_gideonStemsMaster.py."""
from PIL import Image, ImageDraw, ImageFont

F = "C:/Windows/Fonts/arial.ttf"; FB = "C:/Windows/Fonts/arialbd.ttf"
def font(sz, bold=False): return ImageFont.truetype(FB if bold else F, sz)

BG="#16181d"; PANEL="#23262e"; EDGE="#3a3f4b"; TXT="#e8e8ea"; SUB="#9aa0ac"
ACC="#ffb000"; DA="#2e6fb0"; DB="#1f8a5b"; DC="#8a4fc0"; VU="#b03a3a"; KEY="#c08a2e"

def rr(d,x,y,w,h,fill,outline=EDGE,wd=2,r=10):
    d.rounded_rectangle([x,y,x+w,y+h],radius=r,fill=fill,outline=outline,width=wd)

def ctext(d,cx,cy,lines,fnt,fill=TXT,lh=None):
    if isinstance(lines,str): lines=lines.split("\n")
    lh=lh or (fnt.size+3)
    total=lh*len(lines); y=cy-total/2
    for ln in lines:
        w=d.textlength(ln,font=fnt); d.text((cx-w/2,y),ln,font=fnt,fill=fill); y+=lh

def key(d,x,y,w,h,title,sub="",fill=PANEL,tcol=TXT,scol=SUB,r=9):
    rr(d,x,y,w,h,fill,r=r)
    if sub:
        ctext(d,x+w/2,y+h*0.36,title.split("\n"),font(15,True),tcol)
        ctext(d,x+w/2,y+h*0.72,sub.split("\n"),font(12),scol)
    else:
        ctext(d,x+w/2,y+h/2,title.split("\n"),font(15,True),tcol)

# ---------------- MASTER LAYOUT ----------------
def master():
    W,H=1320,975
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    ctext(d,W/2,30,"GideonSTEM-Maschine — Maschine MK2 controller map (ALPHA)",font(26,True),ACC)
    ctext(d,W/2,60,"top pads (9-16) = Deck A   ·   bottom pads (1-8) = Deck B   ·   Group A-H switches the pad page AND the screen layout",font(14),SUB)

    # ---- top-left function buttons ----
    key(d,40,95,150,46,"BROWSE","toggle browser",fill="#2a2d36",tcol=ACC)
    key(d,40,150,150,40,"SAMPLING","(unused)",scol="#6b7280")
    key(d,40,198,70,36,"◄","",fill="#2a2d36")
    key(d,120,198,70,36,"►","",fill="#2a2d36")

    # ---- displays ----
    rr(d,215,95,500,150,"#0c1a12",outline="#2c5", wd=2,r=8)
    ctext(d,465,140,["LEFT  +  RIGHT  DISPLAY"],font(15,True),"#7fe3a8")
    ctext(d,465,172,["boots to  ‘05 - STEMS FULL MIX’"],font(13),"#5fb98a")
    ctext(d,465,200,["Drums | Bass | Other | Vocals  mix levels"],font(12),"#4f9a73")

    # ---- master knobs / dial ----
    key(d,745,95,80,46,"VOL","master")
    key(d,835,95,80,46,"SWING","—",scol="#6b7280")
    key(d,925,95,80,46,"TEMPO","Load Deck A",tcol=ACC)
    # big dial
    d.ellipse([1050,95,1170,215],fill="#2a2d36",outline=ACC,width=3)
    ctext(d,1110,140,["DIAL"],font(17,True),ACC)
    ctext(d,1110,165,["turn = browse","push = LOAD focus"],font(11),SUB)
    key(d,745,155,150,40,"◄ / ►  (master)","browser scroll up/down",tcol=TXT)
    key(d,905,155,90,40,"ENTER","Load Deck B",tcol=ACC)

    # ---- display buttons + knobs ----
    ctext(d,520,272,"DISPLAY SECTION   (Group A-E = stems)",font(13,True),SUB)
    for i in range(8):
        key(d,215+i*125,290,110,40,f"b{i+1}",fill="#2a2d36",tcol=TXT)
    for i in range(8):
        key(d,215+i*125,338,110,46,f"k{i+1}",fill="#2a2d36",tcol=TXT)
    ctext(d,108,360,"STEMS:\nk1 Drums\nk2 Bass\nk3 Other\nk4 Vocals\n(k5-8 = 2nd deck)",font(12),SUB)

    # ---- groups ----
    ctext(d,300,420,"GROUP BUTTONS  (pad page + screen)",font(14,True),ACC)
    glabels=[("A","Stems Pads"),("B","Loops"),("C","Beatjump"),("D","Remix C"),
             ("E","Pitch/Key"),("F","Loop Roll"),("G","VU Meter"),("H","Transport")]
    gx=[60,210,360,510];
    for i,(L,fn) in enumerate(glabels):
        col=i%4; row=i//4
        key(d,gx[col],445+row*70,140,58,L,fn,fill="#2a2d36",tcol=ACC)

    # ---- transport ----
    ctext(d,250,600,"TRANSPORT",font(14,True),ACC)
    trans=[("RESTART","jump to start A+B"),("STEP ◄","beatjump -4"),("STEP ►","beatjump +4"),
           ("GRID","focus A↔B (LED=B)"),("PLAY","play focus (LED grn)"),("REC","recorder (LED red)"),
           ("ERASE","—"),("SHIFT","—")]
    for i,(L,fn) in enumerate(trans):
        col=i%4; row=i//4
        key(d,60+col*150,625+row*64,140,54,L,fn,fill="#222630",
            tcol=TXT if fn!="—" else "#6b7280", scol=SUB if fn!="—" else "#6b7280")

    # ---- pad grid (right) ----
    px,py,ps,pg=830,430,110,12
    rr(d,px-14,py-40,4*ps+3*pg+28,4*ps+3*pg+56,"#1b1e25",outline=EDGE,r=14)
    ctext(d,px+(4*ps+3*pg)/2,py-22,"16 PADS  (4×4)",font(15,True),ACC)
    order=[[13,14,15,16],[9,10,11,12],[5,6,7,8],[1,2,3,4]]
    for r,rowp in enumerate(order):
        deck = DA if r<2 else DB
        for c,p in enumerate(rowp):
            x=px+c*(ps+pg); y=py+r*(ps+pg)
            rr(d,x,y,ps,ps,deck,outline="#0008",wd=2,r=12)
            ctext(d,x+ps/2,y+ps/2,str(p),font(20,True),"#fff")
    ctext(d,px+(4*ps+3*pg)/2,py+4*ps+3*pg+22,"top rows = DECK A   ·   bottom rows = DECK B",font(12),SUB)
    im.save("master.png"); return im

# ---------------- PAD PAGES ----------------
# labels indexed [pad1..pad16]; "\n" splits lines
PAGES = {
 "A":("STEMS PADS","mute & filter per stem",[
    "B Mute\nDrums","B Mute\nBass","B Mute\nOther","B Mute\nVocals",
    "B Filt\nDrums","B Filt\nBass","B Filt\nOther","B Filt\nVocals",
    "A Mute\nDrums","A Mute\nBass","A Mute\nOther","A Mute\nVocals",
    "A Filt\nDrums","A Filt\nBass","A Filt\nOther","A Filt\nVocals"]),
 "B":("LOOPS","instant fixed-size loop",[
    "B Loop\n1/8","B Loop\n1/4","B Loop\n1/2","B Loop\n1",
    "B Loop\n2","B Loop\n4","B Loop\n8","B Loop\n16",
    "A Loop\n1/8","A Loop\n1/4","A Loop\n1/2","A Loop\n1",
    "A Loop\n2","A Loop\n4","A Loop\n8","A Loop\n16"]),
 "C":("BEATJUMP","jump by beats",[
    "B -4","B +4","B -8","B +8","B -16","B +16","B -32","B +32",
    "A -4","A +4","A -8","A +8","A -16","A +16","A -32","A +32"]),
 "D":("REMIX DECK C","4×4 cell trigger grid",[
    "S1\nC1","S1\nC2","S1\nC3","S1\nC4","S2\nC1","S2\nC2","S2\nC3","S2\nC4",
    "S3\nC1","S3\nC2","S3\nC3","S3\nC4","S4\nC1","S4\nC2","S4\nC3","S4\nC4"]),
 "E":("PITCH / KEY","key shift, 0 = reset",[
    "B -4","B -3","B -2","B -1","B 0\nRESET","B +1","B +2","B +3",
    "A -4","A -3","A -2","A -1","A 0\nRESET","A +1","A +2","A +3"]),
 "F":("LOOP ROLL","momentary roll size",[
    "B Roll\n1/16","B Roll\n1/8","B Roll\n1/4","B Roll\n1/2",
    "B Roll\n1","B Roll\n2","B Roll\n4","B Roll\n8",
    "A Roll\n1/16","A Roll\n1/8","A Roll\n1/4","A Roll\n1/2",
    "A Roll\n1","A Roll\n2","A Roll\n4","A Roll\n8"]),
 "G":("VU METER","main output level (out)",[
    "L","L","R","R","L","L","R","R","L","L","R","R","L","L","R","R"]),
 "H":("TRANSPORT","play / cue / sync / flux",[
    "B Play","B Cue","B Sync","B Flux","B Play","B Cue","B Sync","B Flux",
    "A Play","A Cue","A Sync","A Flux","A Play","A Cue","A Sync","A Flux"]),
}
DECKCOL={"A":(DA,DB),"B":(DA,DB),"C":(DA,DB),"E":(DA,DB),"F":(DA,DB),"H":(DA,DB),
         "D":(DC,DC),"G":(VU,VU)}

def padpage(letter):
    title,sub,labels=PAGES[letter]
    W,Hh=600,600; im=Image.new("RGB",(W,Hh),BG); d=ImageDraw.Draw(im)
    rr(d,10,10,W-20,Hh-20,"#1b1e25",outline=EDGE,r=16,wd=2)
    ctext(d,W/2,46,f"GROUP {letter} — {title}",font(22,True),ACC)
    ctext(d,W/2,76,sub,font(14),SUB)
    topcol,botcol=DECKCOL[letter]
    ps=112; pg=14; gx=(W-(4*ps+3*pg))/2; gy=110
    order=[[13,14,15,16],[9,10,11,12],[5,6,7,8],[1,2,3,4]]
    for r,rowp in enumerate(order):
        col=topcol if r<2 else botcol
        for c,p in enumerate(rowp):
            x=gx+c*(ps+pg); y=gy+r*(ps+pg)
            rr(d,x,y,ps,ps,col,outline="#0009",wd=2,r=12)
            ctext(d,x+ps/2,y+ps/2-3,labels[p-1].split("\n"),font(16,True),"#fff",lh=18)
    foot=("top rows = DECK A · bottom = DECK B") if letter not in ("D","G") else \
         ("one 4×4 grid on DECK C" if letter=="D" else "left half = L · right half = R · lights with level")
    ctext(d,W/2,Hh-30,foot,font(13),SUB)
    im.save(f"pad{letter}.png"); return im

m=master()
pads=[padpage(L) for L in "ABCDEFGH"]

# ---------------- CHEAT SHEET ----------------
cols=2; gap=24; pw,ph=pads[0].size
grid_w=cols*pw+(cols-1)*gap
W=max(m.size[0],grid_w)+2*gap
rows=4
H=m.size[1]+gap+rows*ph+(rows-1)*gap+gap
sheet=Image.new("RGB",(W,H),BG)
sheet.paste(m,((W-m.size[0])//2,gap))
y0=m.size[1]+2*gap; x0=(W-grid_w)//2
for i,p in enumerate(pads):
    r=i//cols; c=i%cols
    sheet.paste(p,(x0+c*(pw+gap), y0+r*(ph+gap)))
sheet.save("cheatsheet.png")
print("WROTE master.png, padA-H.png, cheatsheet.png", sheet.size)
