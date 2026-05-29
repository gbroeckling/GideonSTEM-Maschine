"""Generate labeled layout diagrams for GideonSTEM-Maschine.

Covers the CURRENT build (3 modifier layers x 8 groups = 24 pad pages, plus 8
fixed screen pages). The Group A-H button picks the GROUP (native channel switch);
the Scene button (Mod#2=1) and Pattern button (Mod#2=2) pick the LAYER.

Outputs (into ./diagrams_out/):
  control_map.png            whole MK2, every control labeled
  pad_<G>.png                8 base-layer pad maps      (A..H)
  pad_<G>2.png               8 Scene-layer pad maps     (A2..H2)
  pad_<G>3.png               8 Pattern-layer pad maps    (A3..H3)
  screen_<G>.png             8 display knob/button maps  (A..H)
  cheatsheet_base.png        base layer, 8 pads stacked
  cheatsheet_scene.png       Scene layer, 8 pads stacked
  cheatsheet_pattern.png     Pattern layer, 8 pads stacked
  cheatsheet_screens.png     8 screen maps stacked
  layout_guide.png           everything in one tall image (the listing image)

All pad/label/screen data is transcribed from build_gideonStemsMaster.py.
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = "diagrams_out"
os.makedirs(OUT, exist_ok=True)

F = "C:/Windows/Fonts/arial.ttf"; FB = "C:/Windows/Fonts/arialbd.ttf"
def font(sz, bold=False): return ImageFont.truetype(FB if bold else F, sz)

BG="#16181d"; PANEL="#23262e"; EDGE="#3a3f4b"; TXT="#e8e8ea"; SUB="#9aa0ac"; ACC="#ffb000"
# role colors
DA="#2e6fb0"; DB="#1f8a5b"; DC="#8a4fc0"; DD="#c87a2e"
FX3="#1f9aa0"; FX4="#b0498f"; FXSEL="#c8902e"; NEU="#454c5b"; MAC="#a06a20"

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
        ctext(d,x+w/2,y+h*0.34,title.split("\n"),font(15,True),tcol)
        ctext(d,x+w/2,y+h*0.72,sub.split("\n"),font(12),scol)
    else:
        ctext(d,x+w/2,y+h/2,title.split("\n"),font(15,True),tcol)

# ---------------------------------------------------------------------------
# PAD PAGE DATA — 24 pages. Each: (group, layer, title, subtitle, [16 labels], colors)
# labels indexed pad1..pad16; pads 1-8 = bottom (Deck B / FX3), 9-16 = top (Deck A / FX4).
# colors: a mode string OR an explicit 16-entry list.
# ---------------------------------------------------------------------------
def AB(a,b): return [b]*8+[a]*8           # bottom=b color, top=a color
def lr(a,b): return [a,a,a,a,a,a,a,a,b,b,b,b,b,b,b,b]

PAD = {}
def page(pid, group, layer, title, sub, labels, colors):
    assert len(labels)==16, pid
    PAD[pid]=(group,layer,title,sub,labels,colors)

STEMS=["Drums","Bass","Other","Vocals"]

# ===== LAYER 1 — BASE (Scene OFF, Pattern OFF) =====
page("A","A","base","STEMS PADS","mute & filter per stem",
    [f"B Mute\n{s}" for s in STEMS]+[f"B Filt\n{s}" for s in STEMS]+
    [f"A Mute\n{s}" for s in STEMS]+[f"A Filt\n{s}" for s in STEMS], lr(DB,DA))
page("B","B","base","LOOPS","instant fixed-size loop",
    [f"B Loop\n{s}" for s in ["1/8","1/4","1/2","1","2","4","8","16"]]+
    [f"A Loop\n{s}" for s in ["1/8","1/4","1/2","1","2","4","8","16"]], lr(DB,DA))
page("C","C","base","BEATJUMP","jump by beats",
    [f"B {s}" for s in ["-4","+4","-8","+8","-16","+16","-32","+32"]]+
    [f"A {s}" for s in ["-4","+4","-8","+8","-16","+16","-32","+32"]], lr(DB,DA))
page("D","D","base","REMIX DECK C","4x4 cell trigger grid (Deck C)",
    [f"S1\nC{c}" for c in (1,2,3,4)]+[f"S2\nC{c}" for c in (1,2,3,4)]+
    [f"S3\nC{c}" for c in (1,2,3,4)]+[f"S4\nC{c}" for c in (1,2,3,4)], "C")
page("E","E","base","PITCH / KEY","key shift, 0 = reset",
    [f"B {s}" for s in ["-4","-3","-2","-1","0\nRESET","+1","+2","+3"]]+
    [f"A {s}" for s in ["-4","-3","-2","-1","0\nRESET","+1","+2","+3"]], lr(DB,DA))
page("F","F","base","LOOP STATION","capture (silent) + recall to Deck C",
    ["Capture\nA","Capture\nB","Capture\nC","Capture\nD"]+
    [f"Recall\nS1 C{c}" for c in (1,2,3,4)][0:4]+
    [f"Recall\nS2 C{c}" for c in (1,2,3,4)]+[f"Recall\nS3 C{c}" for c in (1,2,3,4)], "single")
page("G","G","base","FX1 SELECT","load FX1 effect + wet while held",
    ["Beat-\nmasher","Gater","Delay","Tape\nDelay","Iceverb","Phaser","Phaser\nFlux","Bouncer",
     "Oscill-\nator","Zzzurp","Strr-\netch","Filter\nLFO","Bass-o-\nMatic","Delay\nT3","Phaser\nPulse","Delay\ndub"],"fxsel")
page("H","H","base","TRANSPORT","play / cue / sync / flux",
    ["B Play","B Cue","B Sync","B Flux","B Play","B Cue","B Sync","B Flux",
     "A Play","A Cue","A Sync","A Flux","A Play","A Cue","A Sync","A Flux"], lr(DB,DA))

# ===== LAYER 2 — SCENE (Scene light ON, Mod#2=1) =====
page("A2","A","scene","STEM FX SEND","route deck->FX + per-stem send",
    ["B ->FX1","B ->FX2","B ->FX3","B ->FX4"]+[f"B Send\n{s}" for s in STEMS]+
    ["A ->FX1","A ->FX2","A ->FX3","A ->FX4"]+[f"A Send\n{s}" for s in STEMS], lr(DB,DA))
page("B2","B","scene","LOOP ROLL","momentary roll size",
    [f"B Roll\n{s}" for s in ["1/16","1/8","1/4","1/2","1","2","4","8"]]+
    [f"A Roll\n{s}" for s in ["1/16","1/8","1/4","1/2","1","2","4","8"]], lr(DB,DA))
page("C2","C","scene","PHRASE JUMP","big jumps by beats",
    [f"B {s}" for s in ["-16","+16","-32","+32","-64","+64","-128","+128"]]+
    [f"A {s}" for s in ["-16","+16","-32","+32","-64","+64","-128","+128"]], lr(DB,DA))
page("D2","D","scene","REMIX DECK C 5-8","4x4 cells 5-8 (Deck C)",
    [f"S1\nC{c}" for c in (5,6,7,8)]+[f"S2\nC{c}" for c in (5,6,7,8)]+
    [f"S3\nC{c}" for c in (5,6,7,8)]+[f"S4\nC{c}" for c in (5,6,7,8)], "C")
page("E2","E","scene","TONE PLAY","play one stem chromatically",
    [f"B +{s}" for s in (1,2,3,4)]+["B 0\nRESET"]+[f"B +{s}" for s in (5,6,7)]+
    [f"A +{s}" for s in (1,2,3,4)]+["A 0\nRESET"]+[f"A +{s}" for s in (5,6,7)], lr(DB,DA))
page("F2","F","scene","LOOP RECORDER","global; 4 controls x4 rows  (experimental)",
    (["Rec /\nPlay","Size -","Size +","Undo"])*4, "single")
page("G2","G","scene","FX1 SELECT (hard)","same effects, harder/wetter bank",
    ["Beat-\nmasher","Gater","Delay","Tape\nDelay","Iceverb","Phaser","Phaser\nFlux","Bouncer",
     "Oscill-\nator","Zzzurp","Strr-\netch","Filter\nLFO","Bass-o-\nMatic","Delay\nT3","Phaser\nPulse","Delay\nmax"],"fxsel")
page("H2","H","scene","TRANSPORT C/D","play / cue / sync / flux",
    ["D Play","D Cue","D Sync","D Flux","D Play","D Cue","D Sync","D Flux",
     "C Play","C Cue","C Sync","C Flux","C Play","C Cue","C Sync","C Flux"], lr(DD,DC))

# ===== LAYER 3 — PATTERN (Pattern light ON, Mod#2=2) — Pattern Player on FX3/FX4 =====
page("A3","A","pattern","FX3 CONTROL ROOM","drum voice 1 (FX3)",
    ["On","Play /\nMute","Next\nSmp","Prev\nSmp","Pat 1","Pat 3","Pat 5","Pat 7",
     "Vol\n25%","Vol\n50%","Vol\n75%","Vol\n100%","Pitch\n-12","Pitch\n0","Pitch\n+7","Pitch\n+12"],"fx3")
page("B3","B","pattern","FX4 CONTROL ROOM","drum voice 2 (FX4)",
    ["On","Play /\nMute","Next\nSmp","Prev\nSmp","Pat 1","Pat 3","Pat 5","Pat 7",
     "Vol\n25%","Vol\n50%","Vol\n75%","Vol\n100%","Pitch\n-12","Pitch\n0","Pitch\n+7","Pitch\n+12"],"fx4")
page("C3","C","pattern","DRUM MIXER","route + level the two voices",
    ["A->FX3","B->FX3","C->FX3","D->FX3","A->FX4","B->FX4","C->FX4","D->FX4",
     "FX3\nPlay","FX4\nPlay","FX3\nOn","FX4\nOn","FX3\nVol-","FX3\nVol+","FX4\nVol-","FX4\nVol+"],
    [FX3,FX3,FX3,FX3,FX4,FX4,FX4,FX4,FX3,FX4,FX3,FX4,FX3,FX3,FX4,FX4])
page("D3","D","pattern","TONE PLAY DRUMS","play drums chromatically",
    [f"FX3\n+{i}" for i in range(8)]+[f"FX4\n+{i}" for i in range(8)], lr(FX3,FX4))
page("E3","E","pattern","SOUND DESIGN","flip samples / decay sweep",
    ["FX3\nNext","FX3\nPrev","FX3\nReset","FX3\nPlay","FX3\nDec 0","FX3\nDec\n33","FX3\nDec\n66","FX3\nDec\n100",
     "FX4\nNext","FX4\nPrev","FX4\nReset","FX4\nPlay","FX4\nDec 0","FX4\nDec\n33","FX4\nDec\n66","FX4\nDec\n100"], lr(FX3,FX4))
page("F3","F","pattern","GATE & VOLUME","mute-gate stutter + volume",
    ["FX3\nGate","FX3\nGate","FX3\nPlay","FX3\nReset","FX3\nVol 0","FX3\nVol\n33","FX3\nVol\n66","FX3\nVol\n100",
     "FX4\nGate","FX4\nGate","FX4\nPlay","FX4\nReset","FX4\nVol 0","FX4\nVol\n33","FX4\nVol\n66","FX4\nVol\n100"], lr(FX3,FX4))
page("G3","G","pattern","MACROS","one-tap combos across both voices",
    ["DROP","BUILD","FILL","CLEAR","FX3\nPat 1","FX3\nPat 3","FX3\nPat 5","FX3\nPat 7",
     "FX4\nPat 1","FX4\nPat 3","FX4\nPat 5","FX4\nPat 7","FX3\nPlay","FX4\nPlay","FX3\nVol+","FX4\nVol+"],
    [MAC,MAC,MAC,MAC,FX3,FX3,FX3,FX3,FX4,FX4,FX4,FX4,FX3,FX4,FX3,FX4])
page("H3","H","pattern","PATTERN PICKER","pick groove (sparse->busy)",
    [f"FX3\nPat {i}" for i in range(1,9)]+[f"FX4\nPat {i}" for i in range(1,9)], lr(FX3,FX4))

LAYER_NAME={"base":"BASE  (Scene off)","scene":"SCENE  (Scene light on)","pattern":"PATTERN  (Pattern light on)"}
LAYER_TINT={"base":"#2a2d36","scene":"#2d2838","pattern":"#23302e"}

def colors_for(colors):
    if isinstance(colors,list): return colors
    return {"AB":lr(DB,DA),"CD":lr(DD,DC),"C":[DC]*16,"single":[NEU]*16,
            "fxsel":[FXSEL]*16,"fx3":[FX3]*16,"fx4":[FX4]*16}[colors]

# ---------------- PAD PAGE RENDER ----------------
def padpage(pid):
    group,layer,title,sub,labels,colors=PAD[pid]
    cols=colors_for(colors)
    W,Hh=620,640; im=Image.new("RGB",(W,Hh),BG); d=ImageDraw.Draw(im)
    rr(d,10,10,W-20,Hh-20,LAYER_TINT[layer],outline=EDGE,r=16,wd=2)
    # layer badge
    rr(d,24,24,150,30,PANEL,r=8); ctext(d,99,39,LAYER_NAME[layer].split("  ")[0],font(14,True),ACC)
    ctext(d,W/2,58,f"GROUP {group} — {title}",font(22,True),ACC)
    ctext(d,W/2,88,sub,font(13),SUB)
    ps=112; pg=14; gx=(W-(4*ps+3*pg))/2; gy=120
    order=[[13,14,15,16],[9,10,11,12],[5,6,7,8],[1,2,3,4]]
    for r,rowp in enumerate(order):
        for c,p in enumerate(rowp):
            x=gx+c*(ps+pg); y=gy+r*(ps+pg)
            rr(d,x,y,ps,ps,cols[p-1],outline="#0009",wd=2,r=12)
            lab=labels[p-1]
            ctext(d,x+ps/2,y+ps/2-2,lab.split("\n"),font(15,True),"#fff",lh=17)
    foot=LAYER_NAME[layer]
    ctext(d,W/2,Hh-28,foot,font(12),SUB)
    im.save(f"{OUT}/pad_{pid}.png"); return im

# ---------------- SCREEN (display) PAGES ----------------
# (group, title, [8 knob labels k1..k8], [8 button labels b1..b8])
SCREENS={
 "A":("STEMS FULL MIX  (boot screen)",
      [f"A Vol\n{s}" for s in STEMS]+[f"B Vol\n{s}" for s in STEMS],
      [f"A Mute\n{s}" for s in STEMS]+[f"B Mute\n{s}" for s in STEMS]),
 "B":("STEMS ENCODERS",
      [f"A Vol\n{s}" for s in STEMS]+[f"B Vol\n{s}" for s in STEMS],
      ["push =\nmute"]*8),
 "C":("STEMS MIX CTRL",
      [f"A Filt\n{s}" for s in STEMS]+[f"B Filt\n{s}" for s in STEMS],
      [f"A Mute\n{s}" for s in STEMS]+[f"B Mute\n{s}" for s in STEMS]),
 "D":("STEMS FINE VOL",
      [f"A Fine\n{s}" for s in STEMS]+[f"B Fine\n{s}" for s in STEMS],
      [f"A Mute\n{s}" for s in STEMS]+[f"B Mute\n{s}" for s in STEMS]),
 "E":("STEMS FILTER",
      [f"A Filt\n{s}" for s in STEMS]+[f"B Filt\n{s}" for s in STEMS],
      [f"A FiltOn\n{s}" for s in STEMS]+[f"B FiltOn\n{s}" for s in STEMS]),
 "F":("FX 1 + 2",
      ["FX1\nD/Wet","FX1\nKnob1","FX1\nKnob2","FX1\nKnob3","FX2\nD/Wet","FX2\nKnob1","FX2\nKnob2","FX2\nKnob3"],
      ["FX1 On","FX1\nBtn1","FX1\nBtn2","FX1\nBtn3","FX2 On","FX2\nBtn1","FX2\nBtn2","FX2\nBtn3"]),
 "G":("FX 3 + 4",
      ["FX3\nD/Wet","FX3\nKnob1","FX3\nKnob2","FX3\nKnob3","FX4\nD/Wet","FX4\nKnob1","FX4\nKnob2","FX4\nKnob3"],
      ["FX3 On","FX3\nBtn1","FX3\nBtn2","FX3\nBtn3","FX4 On","FX4\nBtn1","FX4\nBtn2","FX4\nBtn3"]),
 "H":("FX ALL",
      ["FX1\nD/Wet","FX2\nD/Wet","FX3\nD/Wet","FX4\nD/Wet","FX1\nKnob1","FX2\nKnob1","FX3\nKnob1","FX4\nKnob1"],
      ["FX1 On","FX2 On","FX3 On","FX4 On","FX1\nBtn1","FX2\nBtn1","FX3\nBtn1","FX4\nBtn1"]),
}
SCREEN_COL={"A":DA,"B":DA,"C":DA,"D":DA,"E":DA,"F":FX3,"G":FX3,"H":FX3}

def screenpage(group):
    title,knobs,btns=SCREENS[group]
    W,Hh=1180,360; im=Image.new("RGB",(W,Hh),BG); d=ImageDraw.Draw(im)
    rr(d,10,10,W-20,Hh-20,PANEL,outline=EDGE,r=16,wd=2)
    ctext(d,W/2,46,f"GROUP {group} SCREEN — {title}",font(22,True),ACC)
    ctext(d,W/2,74,"display buttons (b1-b8)  +  display knobs (k1-k8)",font(12),SUB)
    col=SCREEN_COL[group]
    bw=132; bg=8; gx=(W-(8*bw+7*bg))/2
    for i in range(8):
        x=gx+i*(bw+bg)
        rr(d,x,100,bw,70,"#2a2d36",r=9)
        ctext(d,x+bw/2,118,f"b{i+1}",font(11,True),SUB)
        ctext(d,x+bw/2,148,btns[i].split("\n"),font(13,True),TXT,lh=15)
    for i in range(8):
        x=gx+i*(bw+bg)
        rr(d,x,184,bw,128,col,outline="#0009",r=10)
        d.ellipse([x+bw/2-30,196,x+bw/2+30,256],outline="#fff8",width=3)
        ctext(d,x+bw/2,226,f"k{i+1}",font(12,True),"#fff")
        ctext(d,x+bw/2,288,knobs[i].split("\n"),font(13,True),"#fff",lh=15)
    im.save(f"{OUT}/screen_{group}.png"); return im

# ---------------- CONTROL MAP (master) ----------------
def control_map():
    W,H=1340,1020
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    ctext(d,W/2,30,"GideonSTEM-Maschine — Maschine MK2 control map (ALPHA v0.4)",font(26,True),ACC)
    ctext(d,W/2,60,"Group A-H = pick the page  ·  Scene / Pattern = pick the layer  ·  top pads 9-16 = Deck A · bottom 1-8 = Deck B",font(14),SUB)

    key(d,40,95,150,46,"BROWSE","toggle browser",fill="#2a2d36",tcol=ACC)
    key(d,40,150,150,40,"SAMPLING","(unused)",scol="#6b7280")
    key(d,40,198,70,36,"<","",fill="#2a2d36"); key(d,120,198,70,36,">","",fill="#2a2d36")

    rr(d,215,95,500,150,"#0c1a12",outline="#2c5",wd=2,r=8)
    ctext(d,465,135,["LEFT  +  RIGHT  DISPLAY"],font(15,True),"#7fe3a8")
    ctext(d,465,166,["boots to 'Stems Full Mix'"],font(13),"#5fb98a")
    ctext(d,465,196,["screen layout follows the Group button (see screen maps)"],font(11),"#4f9a73")

    key(d,745,95,80,46,"VOL","master")
    key(d,835,95,80,46,"SWING","-",scol="#6b7280")
    key(d,925,95,80,46,"TEMPO","Load Deck A",tcol=ACC)
    d.ellipse([1050,95,1170,215],fill="#2a2d36",outline=ACC,width=3)
    ctext(d,1110,140,["DIAL"],font(17,True),ACC)
    ctext(d,1110,165,["turn = browse","push = LOAD focus"],font(11),SUB)
    key(d,745,155,150,40,"< / >  (master)","browser tree select",tcol=TXT)
    key(d,905,155,90,40,"ENTER","Load Deck B",tcol=ACC)

    ctext(d,520,272,"DISPLAY SECTION  (b1-b8 buttons / k1-k8 knobs — change with the Group)",font(13,True),SUB)
    for i in range(8): key(d,215+i*125,290,110,40,f"b{i+1}",fill="#2a2d36",tcol=TXT)
    for i in range(8): key(d,215+i*125,338,110,46,f"k{i+1}",fill="#2a2d36",tcol=TXT)

    ctext(d,300,420,"GROUP BUTTONS  (pad page + screen)",font(14,True),ACC)
    glabels=[("A","Stems Pads"),("B","Loops"),("C","Beatjump"),("D","Remix C"),
             ("E","Pitch/Key"),("F","Loop Station"),("G","FX1 Select"),("H","Transport")]
    gx=[60,210,360,510]
    for i,(L,fn) in enumerate(glabels):
        col=i%4; row=i//4
        key(d,gx[col],445+row*70,140,58,L,fn,fill="#2a2d36",tcol=ACC)

    # layer buttons
    ctext(d,250,600,"LAYER + UTILITY BUTTONS",font(14,True),ACC)
    util=[("SCENE","layer 2 (hold)"),("PATTERN","layer 3 (hold)"),("SOLO","FX1 engage"),
          ("MUTE","mute all stems"),("VOLUME","Dial = deck vol"),("NOTE REPEAT","Cruise/Auto-DJ")]
    for i,(L,fn) in enumerate(util):
        col=i%3; row=i//3
        key(d,60+col*200,625+row*64,185,54,L,fn,fill="#222630",tcol=TXT)

    ctext(d,250,775,"TRANSPORT",font(14,True),ACC)
    trans=[("RESTART","jump start A+B"),("STEP <","beatjump -4"),("STEP >","beatjump +4"),
           ("GRID","focus A<->B"),("PLAY","play focus"),("REC","recorder")]
    for i,(L,fn) in enumerate(trans):
        col=i%3; row=i//3
        key(d,60+col*200,800+row*64,185,54,L,fn,fill="#222630",tcol=TXT)

    px,py,ps,pg=840,440,112,12
    rr(d,px-14,py-40,4*ps+3*pg+28,4*ps+3*pg+56,"#1b1e25",outline=EDGE,r=14)
    ctext(d,px+(4*ps+3*pg)/2,py-22,"16 PADS  (4x4)",font(15,True),ACC)
    order=[[13,14,15,16],[9,10,11,12],[5,6,7,8],[1,2,3,4]]
    for r,rowp in enumerate(order):
        deck=DA if r<2 else DB
        for c,p in enumerate(rowp):
            x=px+c*(ps+pg); y=py+r*(ps+pg)
            rr(d,x,y,ps,ps,deck,outline="#0008",wd=2,r=12)
            ctext(d,x+ps/2,y+ps/2,str(p),font(20,True),"#fff")
    ctext(d,px+(4*ps+3*pg)/2,py+4*ps+3*pg+22,"top rows = DECK A  ·  bottom rows = DECK B",font(12),SUB)
    im.save(f"{OUT}/control_map.png"); return im

# ---------------- COMPOSITES ----------------
def grid_sheet(images, cols, name, header):
    pw,ph=images[0].size; gap=20; padtop=70
    rows=(len(images)+cols-1)//cols
    W=cols*pw+(cols+1)*gap
    H=padtop+rows*ph+(rows+1)*gap
    sheet=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(sheet)
    ctext(d,W/2,38,header,font(28,True),ACC)
    for i,p in enumerate(images):
        r=i//cols; c=i%cols
        sheet.paste(p,(gap+c*(pw+gap), padtop+gap+r*(ph+gap)))
    sheet.save(f"{OUT}/{name}.png"); return sheet

# ---------------- BUILD ALL ----------------
cm=control_map()
base_ids   =["A","B","C","D","E","F","G","H"]
scene_ids  =[i+"2" for i in "ABCDEFGH"]
pattern_ids=[i+"3" for i in "ABCDEFGH"]

base_imgs   =[padpage(i) for i in base_ids]
scene_imgs  =[padpage(i) for i in scene_ids]
pattern_imgs=[padpage(i) for i in pattern_ids]
screen_imgs =[screenpage(g) for g in "ABCDEFGH"]

cs_base   =grid_sheet(base_imgs,4,"cheatsheet_base","BASE LAYER  —  Group A-H pads (Scene & Pattern lights off)")
cs_scene  =grid_sheet(scene_imgs,4,"cheatsheet_scene","SCENE LAYER  —  hold/latch SCENE  (Mod#2 = 1)")
cs_pattern=grid_sheet(pattern_imgs,4,"cheatsheet_pattern","PATTERN LAYER  —  hold/latch PATTERN  (Pattern Player on FX3/FX4)")
cs_screen =grid_sheet(screen_imgs,2,"cheatsheet_screens","SCREEN PAGES  —  display knobs/buttons per Group")

# full layout guide: control map on top, then the 4 cheatsheets stacked
def stack(images, name):
    gap=30; W=max(i.size[0] for i in images)+2*gap
    H=sum(i.size[1] for i in images)+gap*(len(images)+1)
    out=Image.new("RGB",(W,H),BG); y=gap
    for i in images:
        out.paste(i,((W-i.size[0])//2,y)); y+=i.size[1]+gap
    out.save(f"{OUT}/{name}.png"); return out

stack([cm,cs_base,cs_scene,cs_pattern,cs_screen],"layout_guide")

n=len(PAD)+len(SCREENS)+1
print(f"WROTE {OUT}/: control_map + {len(PAD)} pad pages + {len(SCREENS)} screens + 4 cheatsheets + layout_guide")
print(f"  = {n} core panels documenting 24 pad-pages and 8 screen-pages across 3 layers.")
