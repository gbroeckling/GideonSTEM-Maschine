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
# role colors — brighter "LED" palette so the printed/screen diagrams read at a glance
DA="#3a8be0"; DB="#2dba78"; DC="#a865d8"; DD="#e8973a"
FX3="#2bc5ce"; FX4="#d967b3"; FXSEL="#e8b13c"; NEU="#5a6175"; MAC="#c78531"
LR="#7fbf6a"   # Loop Recorder pad tint (greenish — drives global recorder)

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
page("G","G","base","FX1 SELECT","load FX1 + wet while held  (Group G page-press arms FX1 route+on)",
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
page("F2","F","scene","LOOP RECORDER","global; Size + Dry/Wet + transport (mirrored)",
    # bottom rows 1-4 + 5-8: Rec / Play / Undo / Delete (transport mirrored for two-hand reach)
    # row 9-12: Dry/Wet 0 / 33 / 66 / 100 %
    # row 13-16 (top): Size 4 / 8 / 16 / 32 beats
    ["Rec","Play","Undo","Delete","Rec","Play","Undo","Delete",
     "D/W\n0%","D/W\n33%","D/W\n66%","D/W\n100%",
     "Size\n4","Size\n8","Size\n16","Size\n32"], [LR]*16)
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
page("H3","H","pattern","PATTERN PICKER","sparse->busy  +  Solo engaged: pad press = play-from-step-1",
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

# ---------------- CONTROL MAP / DECK OVERVIEW (high-res, hardware-positioned, every functional
# button labeled with its CURRENT v0.6-alpha role) ----------------
def control_map():
    """High-resolution MK2 deck overview. Hardware layout matches the real Maschine MK2:
    top row = BROWSE/SAMPLING + two displays + transport-side buttons + DIAL; middle = display
    b1-b8 / k1-k8; lower-left = GROUP A-H, LAYER+UTILITY buttons, TRANSPORT buttons; lower-right
    = 4x4 pads. Every button that has a distinct mapped function carries its v0.6 label."""
    # Big canvas so the rendered image stays sharp when djtt scales it down for the listing hero.
    W, H = 3200, 2200
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)

    # ---- header ----
    ctext(d, W/2, 60, "GideonSTEM-Maschine  —  Maschine MK2 control map (ALPHA v0.6)",
          font(56, True), ACC)
    ctext(d, W/2, 116, "Group A-H = pick the page  ·  Scene / Pattern = pick the layer  ·  top pads 9-16 = Deck A · bottom pads 1-8 = Deck B",
          font(26), SUB)

    # ---- BROWSE / SAMPLING / arrows (top-left column) ----
    key(d, 80, 200, 320, 90, "BROWSE", "toggle browser view",
        fill="#2a2d36", tcol=ACC, r=14)
    key(d, 80, 310, 320, 90, "SAMPLING", "(unused — free button)",
        fill="#2a2d36", scol="#6b7280", r=14)
    key(d, 80, 420, 150, 70, "<",  "tree up",   fill="#2a2d36", r=12)
    key(d, 250, 420, 150, 70, ">", "tree down", fill="#2a2d36", r=12)
    ctext(d, 240, 510, "(master < / >  =  browser tree)", font(20), SUB)

    # ---- displays (centered) ----
    rr(d, 480, 200, 1700, 350, "#0c1a12", outline="#2c5", wd=4, r=14)
    d.line([(1330, 200), (1330, 550)], fill="#2c5", width=3)
    ctext(d, 905,  300, ["LEFT DISPLAY"],  font(38, True), "#7fe3a8")
    ctext(d, 1755, 300, ["RIGHT DISPLAY"], font(38, True), "#7fe3a8")
    ctext(d, 1330, 400, ["boots to  'Stems Full Mix'"], font(28, True), "#7fe3a8")
    ctext(d, 1330, 460, ["screen layout follows the Group button — see screen maps"],
          font(22), "#5fb98a")
    ctext(d, 1330, 505, ["volume / mute / filter / fine / FX 1+2 / 3+4 / all"],
          font(20), "#4f9a73")

    # ---- top-right column: VOL / SWING / TEMPO + DIAL + ENTER ----
    # VOL master (above)
    key(d, 2270, 200, 220, 80, "VOL", "master volume",
        fill="#2a2d36", tcol=ACC, r=12)
    # SWING — A/B target (v0.6 swing-skip)
    key(d, 2500, 200, 220, 80, "SWING",
        "swing-skip A/B target\nLED on = Deck A  (NEW v0.6)",
        fill="#2a2d36", tcol=ACC, r=12)
    # TEMPO — Load Deck A
    key(d, 2270, 290, 450, 70, "TEMPO",  "Load focused track → Deck A",
        fill="#2a2d36", tcol=ACC, r=12)
    # ENTER — Load Deck B
    key(d, 2270, 370, 450, 70, "ENTER",  "Load focused track → Deck B",
        fill="#2a2d36", tcol=ACC, r=12)

    # DIAL (big circle, multi-mode)
    cx, cy, cr = 2940, 320, 170
    d.ellipse([cx-cr, cy-cr, cx+cr, cy+cr], fill="#2a2d36", outline=ACC, width=6)
    d.ellipse([cx-30, cy-30, cx+30, cy+30], fill=ACC, outline="#fff", width=2)
    ctext(d, cx, cy-100, ["DIAL  (jog)"], font(36, True), ACC)
    ctext(d, cx, cy+95,
          ["turn:  browse  /  volume  /  SKIP",
           "press+hold:  SWING-SKIP engage  (v0.6)",
           "see Browse Knob section"],
          font(20, True), "#fff", lh=24)

    # ---- display row: b1-b8 buttons + k1-k8 knobs ----
    bx_start = 480; bw = 200; bg = 12
    ctext(d, bx_start + 8*bw/2 + 3.5*bg, 600,
          "DISPLAY SECTION  —  b1-b8 buttons and k1-k8 knobs (change with the Group, see screen maps)",
          font(26, True), SUB)
    for i in range(8):
        x = bx_start + i*(bw+bg)
        key(d, x, 630, bw, 80, f"b{i+1}", fill="#2a2d36", tcol=TXT, r=10)
    for i in range(8):
        x = bx_start + i*(bw+bg)
        # render as knob (circle)
        nx = x + bw/2
        d.ellipse([nx-50, 740, nx+50, 840], fill="#2a2d36", outline="#fff5", width=3)
        d.ellipse([nx-8, 770, nx+8, 786], fill="#fff8")
        ctext(d, nx, 870, f"k{i+1}", font(22, True), TXT)

    # ---- GROUP BUTTONS (A-H, hardware: 2 columns of 4) ----
    ctext(d, 380, 1010, "GROUP BUTTONS  —  pad page + screen", font(30, True), ACC)
    glabels = [
        ("A", "Stems Pads",   "per-stem mute + filter"),
        ("E", "Pitch / Key",  "semitone shift + RESET"),
        ("B", "Loops",        "8 fixed sizes 1/8..16 beats"),
        ("F", "Loop Station", "Capture A-D · recall to C"),
        ("C", "Beatjump",     "+/- 4..32 beats"),
        ("G", "FX1 Select",   "load FX1 + wet (page-press arms)"),
        ("D", "Remix C",      "4×4 cell trigger grid"),
        ("H", "Transport",    "Play / Cue / Sync / Flux"),
    ]
    # render in two columns (A,E top), (B,F), (C,G), (D,H)
    gcols_x = [50, 380]
    for i, (L, fn, hint) in enumerate(glabels):
        col = i % 2
        row = i // 2
        x = gcols_x[col]
        y = 1060 + row * 130
        rr(d, x, y, 320, 110, "#2a2d36", r=14)
        ctext(d, x+44, y+40, L, font(40, True), ACC)
        ctext(d, x+200, y+34, fn.split("\n"), font(22, True), TXT, lh=24)
        ctext(d, x+200, y+76, hint.split("\n"), font(18), SUB, lh=20)

    # ---- LAYER + UTILITY BUTTONS ----
    ctext(d, 1100, 1010, "LAYER + UTILITY", font(30, True), ACC)
    util = [
        ("SCENE",       "Scene layer (A2-H2)"),
        ("PATTERN",     "Pattern layer (A3-H3)\n(auto-arms FX3/FX4)"),
        ("SOLO",        "FX1 engage (route+on)"),
        ("MUTE",        "Mute ALL stems (toggle)"),
        ("VOLUME",      "Dial = focused deck vol"),
        ("NOTE REPEAT", "Cruise / Auto-DJ"),
    ]
    for i, (L, fn) in enumerate(util):
        col = i % 2
        row = i // 2
        x = 760 + col * 360
        y = 1060 + row * 130
        rr(d, x, y, 340, 110, "#222630", r=14)
        ctext(d, x+170, y+38, L, font(28, True), TXT)
        ctext(d, x+170, y+82, fn.split("\n"), font(18), SUB, lh=20)

    # ---- TRANSPORT (sits below the GROUP + LAYER+UTILITY blocks; full-width row) ----
    ctext(d, 700, 1610, "TRANSPORT", font(30, True), ACC)
    trans = [
        ("RESTART", "jump-to-start A+B"),
        ("STEP <",  "beatjump -4 focused"),
        ("STEP >",  "beatjump +4 focused"),
        ("GRID",    "focus A ↔ B"),
        ("PLAY",    "play focused deck"),
        ("REC",     "audio recorder toggle"),
        ("ERASE",   "SYNC ALL  (latched)\n1st: master+sync 4   2nd: off"),
        ("TAP",     "(unused)"),
        ("NAV",     "(unused)"),
    ]
    for i, (L, fn) in enumerate(trans):
        col = i % 5     # 5 across, 2 rows — keeps it shorter and clear of the pad block
        row = i // 5
        x = 50 + col * 360
        y = 1660 + row * 130
        # Highlight ERASE (new SYNC ALL) with accent border so the new feature pops
        outline = ACC if L == "ERASE" else EDGE
        wd = 4 if L == "ERASE" else 2
        rr(d, x, y, 340, 110, "#222630", r=14, outline=outline, wd=wd)
        ctext(d, x+170, y+34, L, font(26, True), TXT)
        ctext(d, x+170, y+76, fn.split("\n"), font(17), SUB, lh=20)

    # ---- PADS (16, big, on the right) ----
    px = 1900; py = 1060; ps = 230; pg = 22
    pad_total_w = 4*ps + 3*pg
    pad_total_h = pad_total_w
    rr(d, px-30, py-66, pad_total_w+60, pad_total_h+110, "#1b1e25", outline=EDGE, r=20, wd=3)
    ctext(d, px + pad_total_w/2, py - 36, "16 PADS  (4×4)  —  page contents change with Group + Layer",
          font(28, True), ACC)
    order = [[13,14,15,16],[9,10,11,12],[5,6,7,8],[1,2,3,4]]
    for r, rowp in enumerate(order):
        for c, p in enumerate(rowp):
            x = px + c*(ps+pg); y = py + r*(ps+pg)
            deck_color = DA if r < 2 else DB
            rr(d, x, y, ps, ps, deck_color, outline="#0008", wd=3, r=18)
            ctext(d, x+ps/2, y+ps/2, str(p), font(56, True), "#fff")
    ctext(d, px + pad_total_w/2, py + pad_total_h + 30,
          "top rows (9-16) = DECK A    ·    bottom rows (1-8) = DECK B",
          font(22, True), SUB)

    # ---- legend strip at the bottom ----
    ctext(d, W/2, H-90,
          "v0.6-alpha — SWING-SKIP (hold Dial, turn to seek Swing-selected deck via TID 103, replaces Beatjump-on-encoder)",
          font(22, True), ACC)
    ctext(d, W/2, H-55,
          "v0.5-alpha — Group G page-press arms FX1 (route A+B + unit on);  F2 Loop Recorder fully wired;  H3 + Solo = one-hit pattern fire;  Erase = Sync ALL",
          font(20), SUB)

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

# ---------------- PRINTABLE PDF (one diagram per letter page) ----------------
# Letter portrait at 200 DPI = 1700 x 2200 px. Each page: header strip + diagram
# centered + scaled to fit with whitespace margin. Multi-page PDF combines all.
PAGE_W, PAGE_H = 1700, 2200
MARGIN = 80
HEADER_H = 100

def page_for_print(diagram_img, title, page_label=""):
    # Letter LANDSCAPE so the diagram fills almost the whole page.
    PW, PH = PAGE_H, PAGE_W   # 2200 x 1700
    MARG = 40
    HDR = 80
    p = Image.new("RGB", (PW, PH), "#ffffff")
    d = ImageDraw.Draw(p)
    # header strip
    d.rectangle([0, 0, PW, HDR], fill="#16181d")
    d.text((MARG, 22), "GideonSTEM-Maschine  v0.6-alpha", font=font(22, True), fill=ACC)
    if page_label:
        tw = d.textlength(page_label, font=font(20, True))
        d.text((PW - MARG - tw, 22), page_label, font=font(20, True), fill=SUB)
    # title under header
    d.text((MARG, HDR + 16), title, font=font(30, True), fill="#16181d")
    # diagram nearly fills the page below the title
    body_top = HDR + 70
    body_bottom = PH - 42
    body_w = PW - 2 * MARG
    body_h = body_bottom - body_top
    iw, ih = diagram_img.size
    scale = min(body_w / iw, body_h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    resized = diagram_img.resize((nw, nh), Image.LANCZOS)
    x = (PW - nw) // 2
    y = body_top + (body_h - nh) // 2
    p.paste(resized, (x, y))
    # footer
    d.text((MARG, PH - 30), "github.com/gbroeckling/GideonSTEM-Maschine",
           font=font(13), fill="#666")
    return p

def build_pdf(name, items):
    """items: list of (PIL image, title, label). Saves as PDF."""
    pages = [page_for_print(img, title, lbl) for img, title, lbl in items]
    pages[0].save(f"{OUT}/{name}.pdf", save_all=True, append_images=pages[1:],
                  resolution=200.0)
    return pages

# (Removed the old 33-page-per-pad printable: dropped per Garry's feedback "not an image
# for every section". The 5-page logical version is built further down using the cheatsheets.)

# ---------------- DECK OVERVIEW = the (now-high-res, fully-labeled) control map ------------
# Earlier this used template_labeled.png, but at 1460×1222 it was fuzzy when djtt scaled the
# hero image, and it was missing labels for the v0.5/v0.6 features. The control_map() above
# is now 3200×2200, hardware-positioned, and labels every functional button — so use that.
import shutil
shutil.copy(f"{OUT}/control_map.png", f"{OUT}/deck_overview.png")
overview_img = Image.open(f"{OUT}/deck_overview.png")
print(f"  + deck_overview.png (= high-res control_map, {overview_img.size[0]}x{overview_img.size[1]})")

# Rebuild printable PDFs: 5 logical pages = overview + 3 layer cheatsheets + 1 screens cheat.
# Each cheatsheet ALREADY packs 8 pad pages in a 4x2 grid (set above via grid_sheet).
print()
print("=== Printable set (5 logical pages, letter LANDSCAPE) ===")
items_logical = [
    (overview_img, "MK2 Deck Overview  (hardware-positioned)", "1 / 5"),
    (cs_base,      "BASE layer  —  Group A-H pads",            "2 / 5"),
    (cs_scene,     "SCENE layer  —  Group A2-H2",              "3 / 5"),
    (cs_pattern,   "PATTERN layer  —  Group A3-H3  (drum Pattern Player)", "4 / 5"),
    (cs_screen,    "SCREEN pages  —  display knobs / buttons", "5 / 5"),
]
build_pdf("printable_full_set", items_logical)
# Also produce per-layer single-page PDFs for someone who only wants one layer's cheat
build_pdf("printable_overview", [(overview_img, "MK2 Deck Overview", "1 / 1")])
build_pdf("printable_base",     [(cs_base,      "BASE layer cheatsheet",    "1 / 1")])
build_pdf("printable_scene",    [(cs_scene,     "SCENE layer cheatsheet",   "1 / 1")])
build_pdf("printable_pattern",  [(cs_pattern,   "PATTERN layer cheatsheet", "1 / 1")])
build_pdf("printable_screens",  [(cs_screen,    "SCREEN pages cheatsheet",  "1 / 1")])

n=len(PAD)+len(SCREENS)+1
print(f"WROTE {OUT}/: deck_overview + {len(PAD)} pad pages + {len(SCREENS)} screens + 4 cheatsheets + layout_guide")
print(f"  + printable_full_set.pdf (5 letter-landscape pages, logically laid out)")
print(f"  + 5 single-page PDFs (overview / base / scene / pattern / screens)")
print(f"  = {n} core panels documenting 24 pad-pages and 8 screen-pages across 3 layers.")
