"""
MOS – LWMove v2.0
Oaky North Mine | LW707 Recovery → LW708 Install (WOWO)
Sources: LWMove Demo spec PRD v1.0, OCN LW Move Plan BIBLE 708-601 v0.1,
         STD1400 Recovery Mesh & Bolt Up, Nepean AFC Drawing 1506-0000-000-00
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import streamlit.components.v1 as components

# ── PAGE CONFIG ──────────────────────────────────────────────────────
st.set_page_config(page_title="MOS – LWMove", layout="wide",
                   page_icon="⛏️", initial_sidebar_state="expanded")

st.markdown("""
<style>
  .main .block-container{padding-top:.7rem;padding-bottom:2rem}
  div[data-testid="metric-container"]{background:#161b22;border:1px solid #30363d;
    border-radius:10px;padding:12px 16px;box-shadow:0 2px 8px rgba(0,0,0,.35)}
  div[data-testid="metric-container"]>label{color:#8b949e!important;font-size:11px}
  div[data-testid="metric-container"]>div{color:#58a6ff!important}
  .stProgress>div>div>div>div{background:linear-gradient(90deg,#58a6ff,#1f6feb)}
  div[data-testid="stSidebarContent"]{background:#0d1117}
  .stTabs [data-baseweb="tab"]{background:#161b22;border-radius:6px 6px 0 0;
    border:1px solid #30363d;color:#8b949e;padding:5px 14px}
  .stTabs [aria-selected="true"]{background:#1f6feb!important;color:#fff!important;border-color:#1f6feb}
  .pill{display:inline-block;background:#1f6feb22;border:1px solid #1f6feb66;
    border-left:4px solid #58a6ff;border-radius:0 6px 6px 0;
    padding:5px 14px;color:#58a6ff;font-weight:700;font-size:13px;margin:8px 0 4px 0}
  .rchip{display:inline-block;background:#21262d;border:1px solid #30363d;
    border-radius:4px;padding:1px 7px;font-size:10px;color:#8b949e;margin:1px}
  .warn{background:#1a1200;border:1px solid #d97706;border-radius:6px;
    padding:8px 12px;font-size:12px;color:#fbbf24;margin:6px 0}
  .ok{background:#0a1f0a;border:1px solid #16a34a;border-radius:6px;
    padding:8px 12px;font-size:12px;color:#4ade80;margin:6px 0}
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ────────────────────────────────────────────────────────
MINE        = "Oaky North Mine (OCN)"
MOVE_FROM   = "LW707"
MOVE_TO     = "LW708"
MOVE_TYPE   = "WOWO – Walk On Walk Off"
NUM_SHIELDS = 203
NUM_PANS    = 203

PRE_INST_STATUSES  = ["Not Installed","Installed","Pre-Powered","Post-Powered"]
INSTALL_STATUSES   = ["Staged","Positioning","Installed","Commissioned","Blocked"]
RECOVERY_STATUSES  = ["In Place","Being Recovered","Recovered","Blocked"]
BOLT_ROW_STATUSES  = ["Not Started","In Progress","Complete","Signed Off"]

PRE_INST_COLORS = {"Not Installed":"#b91c1c","Installed":"#ca8a04",
                   "Pre-Powered":"#2563eb","Post-Powered":"#16a34a"}
INSTALL_COLORS  = {"Staged":"#b91c1c","Positioning":"#d97706","Installed":"#16a34a",
                   "Commissioned":"#0ea5e9","Blocked":"#7c3aed"}
RECOVERY_COLORS = {"In Place":"#16a34a","Being Recovered":"#d97706",
                   "Recovered":"#4b5563","Blocked":"#7c3aed"}

# PRD pre-install components (4-lane board)
PRE_INSTALL_COMPONENTS = [
    "MiniPans","Crusher","DCB","Concave","Drive Frame","CME",
    "PRS 1","PRS 2","PRS 3",
]

# BSL items
BSL_ITEMS = [
    "Crusher","Boot End","DCB Pan","CME",
    "Convex 1","Convex 2",
    "Concave 1","Concave 2","Concave 3",
    "Mini Pan 1","Mini Pan 2","Mini Pan 3","Mini Pan 4","Mini Pan 5",
]

# AFC pan types – Nepean drawing 1506-0000-000-00 OCN CCS MG→TG
def _pan_types():
    pt = {}
    for i in [1,2]:           pt[i] = "MG Drive"
    for i in range(3,8):     pt[i] = "MG Re-router"
    for i in range(8,11):    pt[i] = "MG Spec Re-router"
    for i in range(11,51):   pt[i] = "Standard"
    pt[51] = "Inspection"
    for i in range(52,102):  pt[i] = "Standard"
    pt[102] = pt[103] = "Midface"
    for i in range(104,153): pt[i] = "Standard"
    pt[153] = "Inspection"
    for i in range(154,193): pt[i] = "Standard"
    pt[193] = "Inspection"
    for i in range(194,197): pt[i] = "TG Spec Re-router"
    for i in range(197,202): pt[i] = "TG Re-router"
    for i in [202,203]:      pt[i] = "TG Drive"
    return pt

PAN_TYPES = _pan_types()
PAN_TYPE_BORDER = {
    "MG Drive":"#60a5fa","MG Re-router":"#93c5fd","MG Spec Re-router":"#bfdbfe",
    "Standard":"rgba(0,0,0,.3)","Inspection":"#fde68a","Midface":"#f9a8d4",
    "TG Spec Re-router":"#fed7aa","TG Re-router":"#fb923c","TG Drive":"#f97316",
}

# Bolt teams – gopher positions from LW Move Bible Section 9
BOLT_TEAMS = [
    {"id":1,"name":"HB Team 1","range":(1,30),   "gopher":30,  "outlet":"#14"},
    {"id":2,"name":"HB Team 2","range":(31,58),  "gopher":58,  "outlet":"#44"},
    {"id":3,"name":"HB Team 3","range":(59,87),  "gopher":87,  "outlet":"#74"},
    {"id":4,"name":"HB Team 4","range":(88,115), "gopher":115, "outlet":"#104"},
    {"id":5,"name":"HB Team 5","range":(116,144),"gopher":144, "outlet":"#134"},
    {"id":6,"name":"HB Team 6","range":(145,173),"gopher":173, "outlet":"#154"},
    {"id":7,"name":"HB Team 7","range":(174,203),"gopher":203, "outlet":"#184"},
]

BOLT_ROW_LABELS  = ["Rows 1+2","Rows 3+4","Rows 5+6","Rows 6a+7","Row 8","Row 9","Rib Bolts"]
BOLT_ROW_WEIGHTS = {"Rows 1+2":15,"Rows 3+4":15,"Rows 5+6":15,"Rows 6a+7":15,
                    "Row 8":15,"Row 9":15,"Rib Bolts":10}

# Per-zone bolt directions – Table 9-2 LW Move Bible
BOLT_DIRS = {
    "Rows 1+2":  ["MG→TG"]*7,
    "Rows 3+4":  ["TG→MG"]*7,
    "Rows 5+6":  ["MG→TG"]*7,
    "Rows 6a+7": ["TG→MG"]*7,
    "Row 8":     ["TG→MG","TG→MG","MG→TG","TG→MG","MG→TG","TG→MG","MG→TG"],
    "Row 9":     ["TG→MG","TG→MG","MG→TG","TG→MG","MG→TG","TG→MG","MG→TG"],
    "Rib Bolts": ["Per plan"]*7,
}

# 15-shear sequence – STD1400
BOLT_SHEARS = [
    {"sh":"15th Last","ch_m":13.5,"dir":"TG→MG","rows":"Mesh pull / pinning bolts","mega":False,
     "note":"Start mesh sequence. Advance EVEN shields 50%. Install capstan MG & TG."},
    {"sh":"14th Last","ch_m":12.5,"dir":"MG→TG","rows":"—","mega":False,"note":"Release winches, advance shields under mesh."},
    {"sh":"13th Last","ch_m":11.5,"dir":"TG→MG","rows":"—","mega":False,"note":""},
    {"sh":"12th Last","ch_m":10.5,"dir":"MG→TG","rows":"—","mega":False,"note":""},
    {"sh":"11th Last","ch_m":9.5, "dir":"TG→MG","rows":"—","mega":False,"note":""},
    {"sh":"10th Last","ch_m":8.5, "dir":"MG→TG","rows":"—","mega":False,"note":""},
    {"sh":"9th Last", "ch_m":7.5, "dir":"TG→MG","rows":"—","mega":False,"note":""},
    {"sh":"8th Last", "ch_m":6.5, "dir":"MG→TG","rows":"ROWS 1 & 2","mega":False,
     "note":"⚡ FIRST BOLTING RUN. 4×1800mm MS in front of every ODD shield. Positive isolate shearer cutter motors."},
    {"sh":"7th Last", "ch_m":5.5, "dir":"No bolts","rows":"—","mega":False,"note":"Advance shields only."},
    {"sh":"6th Last", "ch_m":4.5, "dir":"TG→MG","rows":"ROWS 3 & 4","mega":False,
     "note":"4×1800mm MS in front of every EVEN shield. Advance ODD shields."},
    {"sh":"5th Last", "ch_m":3.5, "dir":"No bolts","rows":"—","mega":False,"note":""},
    {"sh":"4th Last", "ch_m":2.5, "dir":"MG→TG","rows":"ROWS 5 & 6","mega":False,
     "note":"4×1800mm MS in front of every ODD shield (reversed butterfly plates upside down). Push AFC over."},
    {"sh":"3rd Last", "ch_m":1.5, "dir":"MG→TG","rows":"ROWS 6a & 7","mega":True,
     "note":"⚡ Load Megastrands Row 7. Extend every 4th relay bar 1 m. All shields set + positive/active."},
    {"sh":"2nd Last", "ch_m":0.5, "dir":"MG→TG","rows":"ROW 8 + Megabolt Row 7 GROUTED","mega":True,
     "note":"⚡ Grout Row 7 Megabolts – complete FRM0049. Extend every 4th relay bar to 1.5 m."},
    {"sh":"LAST",     "ch_m":0.0, "dir":"MG→TG","rows":"ROW 9 + Rib Bolts + Megabolt Row 8 GROUTED + Tell-Tales","mega":True,
     "note":"⚡ 0.5m final cut. Do NOT advance shields – final position. Grout Row 8 (FRM0049). "
            "Tell-tales every 10th shield. Complete FRM0477 Shutdown List. Power off section → commence teardown."},
]

# Schedule – LW Move Bible Table 3-1
SCHEDULE = pd.DataFrame({
    "Task": [
        "LW708 Pre-Install – Services & Monorail","LW708 AFC Chain Install",
        "LW708 Shearer Install","LW708 Install 1st Roof Support",
        "LW708 Install Last Roof Support","LW708 First Coal Cut",
        "LW707 Bolt-Up – Mesh Pull","LW707 Bolt Row 1",
        "LW707 Last Shear","LW707 Bolt-Up Complete",
        "LW707 Break Chain / Remove TG Drive / Shearer","LW707 Remove AFC Chain",
        "LW707 Remove AFC Hoses & Cables","LW707 Recover 1st Roof Support",
        "LW707 Recover Last Roof Support",
    ],
    "Category": [
        "Pre-Install","Pre-Install","Pre-Install","Install","Install","Commissioning",
        "Bolt-Up","Bolt-Up","Bolt-Up","Bolt-Up",
        "Recovery","Recovery","Recovery","Recovery","Recovery",
    ],
    "Start": [
        date(2024,8,1),date(2024,8,15),date(2024,8,20),date(2024,9,3),date(2024,10,15),date(2024,10,8),
        date(2024,9,14),date(2024,9,15),date(2024,9,30),date(2024,10,1),
        date(2024,9,30),date(2024,10,1),date(2024,10,11),date(2024,10,19),date(2024,11,1),
    ],
    "Finish": [
        date(2024,9,3),date(2024,8,20),date(2024,8,26),date(2024,9,15),date(2024,10,25),date(2024,10,8),
        date(2024,9,15),date(2024,10,6),date(2024,10,6),date(2024,10,6),
        date(2024,10,1),date(2024,10,11),date(2024,10,18),date(2024,10,25),date(2024,11,5),
    ],
    "Progress":[100,100,100,60,0,0,65,55,0,0,50,30,10,8,0],
})
CAT_COLORS = {"Pre-Install":"#06b6d4","Install":"#22c55e",
              "Bolt-Up":"#f59e0b","Recovery":"#ef4444","Commissioning":"#a855f7"}

PRE_INSTALL_SECTIONS = {
    "Roadway & Ground Control": [
        "MG roadway support complete to specification",
        "TG roadway support complete to specification",
        "Cut-through dimensions confirmed by survey",
        "Sumps dewatered and lined",
        "CribLocs installed at cut-through position",
        "E-Frame installed and tested (WI0340)",
        "PRS 1 installed & pressure-tested",
        "PRS 2 installed & pressure-tested",
        "PRS 3 installed & pressure-tested",
    ],
    "Mesh Pull & Face Prep (STD1400)": [
        "Face height increased to 2.5 m by 20 m chainage",
        "Mesh winch assembly fitted (shields 2,3,4 then every even + last 4)",
        "Bolt pods loaded on AFC every 3rd shield (WI0737)",
        "Gophers unloaded at positions 203, 173, 144, 115, 87, 58, 30",
        "Yellow rollers fitted every 2nd bolt pod",
        "Mesh sled positioned at TG – MG end = blue tow cover",
        "Capstan installed MG & TG (WI0257)",
        "Eye nuts / elephant's feet installed (STD1400 Fig 3-2)",
        "Starter rope hooks run every 4th shield",
    ],
    "Consumables Staged on Face": [
        "Bolt pod verified: 12×1.2m HT, 20×1.8m HT, 20×1.8m MS, 1×1.2m pinning",
        "2× bundles plates EVEN shields / 1× bundle ODD shields",
        "1× box 1000 mm resin every EVEN shield",
        "1× box 600 mm resin every 8th shield",
        "Shackle & rollers every even shield",
        "Winches on every even shield",
        "3/4/6 ft drill steels, dolly, turtle, bits, oil, anti-seize at gopher locations",
        "Megastrands loaded TG side – 20×8.2m every 10 shields (2 per shield)",
        "Grout bowls/kits staged (2 at MG + 1 midface), spare pumps/mixers at MG",
    ],
    "Services & Utilities": [
        "High-pressure water extended (face length)",
        "Mine-service air extended – T/G take-off C/T ring main",
        "MV power cabling extended and tested",
        "LV / control cabling extended",
        "Communications (leaky feeder / fibre) extended",
        "Goaf lighting installed",
    ],
    "Monorail & Lifting (STD0961)": [
        "Monorail installed – full face length (WI0358)",
        "Monorail beam joints inspected & torqued",
        "Monorail proof-loaded to SWL × 2",
        "Capstan / crane rigged and function-tested",
        "Rigging equipment inspected (SOP0072E)",
    ],
    "Conveyor & BSL": [
        "BSL position confirmed by survey – boot end pegged (WI0313)",
        "Belt extended / new belt fitted (WI0416)",
        "MG transfer point commissioned",
        "BSL mechanical & structural checks complete",
    ],
    "Documentation & Compliance": [
        "FRM0049 Long Tendon Grout Sheets printed (≥2 per megabolt row)",
        "FRM0477 Longwall Relocation Shutdown List in process room",
        "TAR0010 Bolt Up SCARP accessible to all ERZ Controllers",
        "TAR0907 Longwall Teardown TARP available",
        "MOP0892 Operational No Go Zones briefed to crew",
        "JSA / SLAM conducted prior to task commencement",
    ],
}
# ── SESSION STATE ────────────────────────────────────────────────────
def _init():
    if "lw_ready" in st.session_state:
        return
    st.session_state.pre_comp  = {c:"Not Installed"  for c in PRE_INSTALL_COMPONENTS}
    st.session_state.pre_ts    = {c:None             for c in PRE_INSTALL_COMPONENTS}
    st.session_state.pre_check = {s:{i:False for i in items}
                                   for s,items in PRE_INSTALL_SECTIONS.items()}
    st.session_state.inst_shields  = {i:"Staged"   for i in range(1,204)}
    st.session_state.inst_pans     = {i:"Staged"   for i in range(1,204)}
    st.session_state.inst_mg       = "Staged"
    st.session_state.inst_tg       = "Staged"
    st.session_state.inst_shearer  = "Staged"
    st.session_state.inst_bsl      = {k:"Staged"   for k in BSL_ITEMS}
    st.session_state.rec_shields   = {i:"In Place" for i in range(1,204)}
    st.session_state.rec_pans      = {i:"In Place" for i in range(1,204)}
    st.session_state.rec_mg        = "In Place"
    st.session_state.rec_tg        = "In Place"
    st.session_state.rec_shearer   = "In Place"
    st.session_state.rec_bsl       = {k:"In Place" for k in BSL_ITEMS}
    st.session_state.bolt          = {t["id"]:{r:"Not Started" for r in BOLT_ROW_LABELS}
                                       for t in BOLT_TEAMS}
    st.session_state.frm0049_r7    = False
    st.session_state.frm0049_r8    = False
    st.session_state.log           = []
    st.session_state.lw_ready      = True

_init()

# ── HELPERS ──────────────────────────────────────────────────────────
def cnt(d, targets):
    if isinstance(targets, str): targets = [targets]
    return sum(1 for v in d.values() if v in targets)

def inst_pct():
    done = (cnt(st.session_state.inst_shields,["Installed","Commissioned"]) +
            cnt(st.session_state.inst_pans,   ["Installed","Commissioned"]) +
            cnt(st.session_state.inst_bsl,    ["Installed","Commissioned"]) +
            (1 if st.session_state.inst_mg      in ["Installed","Commissioned"] else 0) +
            (1 if st.session_state.inst_tg      in ["Installed","Commissioned"] else 0) +
            (1 if st.session_state.inst_shearer in ["Installed","Commissioned"] else 0))
    return round(done / (NUM_SHIELDS+NUM_PANS+len(BSL_ITEMS)+3) * 100, 1)

def rec_pct():
    done = (cnt(st.session_state.rec_shields,"Recovered") +
            cnt(st.session_state.rec_pans,   "Recovered") +
            cnt(st.session_state.rec_bsl,    "Recovered") +
            (1 if st.session_state.rec_mg      == "Recovered" else 0) +
            (1 if st.session_state.rec_tg      == "Recovered" else 0) +
            (1 if st.session_state.rec_shearer == "Recovered" else 0))
    return round(done / (NUM_SHIELDS+NUM_PANS+len(BSL_ITEMS)+3) * 100, 1)

def bolt_pct():
    sw  = {"Not Started":0,"In Progress":.5,"Complete":1.,"Signed Off":1.}
    tot = sum(BOLT_ROW_WEIGHTS.values()) * len(BOLT_TEAMS)
    got = sum(BOLT_ROW_WEIGHTS.get(r,10)*sw.get(s,0)
              for td in st.session_state.bolt.values() for r,s in td.items())
    return round(got/tot*100,1) if tot else 0.

def pre_pct():
    av = [v for sec in st.session_state.pre_check.values() for v in sec.values()]
    return round(sum(av)/len(av)*100,1) if av else 0.

def pre_comp_pct():
    done = sum(1 for v in st.session_state.pre_comp.values() if v == "Post-Powered")
    return round(done/len(PRE_INSTALL_COMPONENTS)*100,1)

def log_event(msg):
    st.session_state.log.append({"Time":datetime.now().strftime("%d/%m %H:%M"),"Event":msg})
# ── PLAN VIEW HTML ───────────────────────────────────────────────────
def build_plan_html(mode):
    if mode == "install":
        shields_d,pans_d = st.session_state.inst_shields,st.session_state.inst_pans
        mg_v,tg_v,shr_v  = st.session_state.inst_mg,st.session_state.inst_tg,st.session_state.inst_shearer
        bsl_d = st.session_state.inst_bsl; clrs = INSTALL_COLORS
        ttl = f"{MOVE_TO} INSTALL — FACE PLAN VIEW  (Top Down · Looking Down)"
        n_sh = cnt(shields_d,["Installed","Commissioned"])
        n_p  = cnt(pans_d,   ["Installed","Commissioned"])
        n_b  = cnt(bsl_d,    ["Installed","Commissioned"]); lbl = "Installed/Commissioned"
    else:
        shields_d,pans_d = st.session_state.rec_shields,st.session_state.rec_pans
        mg_v,tg_v,shr_v  = st.session_state.rec_mg,st.session_state.rec_tg,st.session_state.rec_shearer
        bsl_d = st.session_state.rec_bsl; clrs = RECOVERY_COLORS
        ttl = f"{MOVE_FROM} RECOVERY — FACE PLAN VIEW  (Top Down · Looking Down)"
        n_sh = cnt(shields_d,"Recovered"); n_p = cnt(pans_d,"Recovered")
        n_b  = cnt(bsl_d,"Recovered"); lbl = "Recovered"

    s_html = "".join(
        f'<div class="s-blk" style="background:{clrs.get(shields_d[i],"#555")}" '
        f'title="Shield {i}: {shields_d[i]}">'
        f'{"" if i not in (1,25,50,75,100,125,150,175,203) else str(i)}</div>'
        for i in range(1,204)
    )
    p_html = "".join(
        f'<div class="p-blk" style="background:{clrs.get(pans_d[i],"#555")};'
        f'border-color:{PAN_TYPE_BORDER.get(PAN_TYPES.get(i,"Standard"),"rgba(0,0,0,.3)")}" '
        f'title="{PAN_TYPES.get(i,"Standard")} Pan {i}: {pans_d[i]}">'
        f'{"" if i not in (1,25,50,75,100,125,150,175,203) else str(i)}</div>'
        for i in range(1,204)
    )
    b_html = "".join(
        f'<div class="bsl-blk" style="background:{clrs.get(sv,"#555")}" title="{name}: {sv}">'
        f'<span>{name}</span></div>'
        for name,sv in bsl_d.items()
    )
    leg = "".join(f'<div class="leg"><div class="sw" style="background:{c}"></div>{s}</div>'
                  for s,c in clrs.items())
    pt_leg = "".join(
        f'<div class="leg"><div class="sw" style="background:#21262d;border:2px solid {c};border-radius:2px"></div>{pt}</div>'
        for pt,c in [("MG Drive","#60a5fa"),("Re-router","#93c5fd"),("Standard","#444"),
                     ("Inspection","#fde68a"),("Midface","#f9a8d4"),("TG Re-router","#fb923c"),("TG Drive","#f97316")]
    )
    sh_p = round(n_sh/NUM_SHIELDS*100); p_p = round(n_p/NUM_PANS*100)
    b_p  = round(n_b/len(bsl_d)*100) if bsl_d else 0
    mg_c = clrs.get(mg_v,"#555"); tg_c = clrs.get(tg_v,"#555"); shr_c = clrs.get(shr_v,"#555")
    mgok = mg_v in ["Installed","Commissioned","Recovered"]
    tgok = tg_v in ["Installed","Commissioned","Recovered"]
    shok = shr_v in ["Installed","Commissioned","Recovered"]

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
*{{box-sizing:border-box;margin:0;padding:0;font-family:'Segoe UI',system-ui,sans-serif}}
body{{background:#0d1117;color:#e6edf3;padding:12px 14px}}
.hdr{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid #21262d}}
.ttl{{font-size:13px;font-weight:700;color:#58a6ff;letter-spacing:.8px}}
.sub{{font-size:9px;color:#8b949e;margin-top:2px}}
.legs{{display:flex;gap:10px;flex-wrap:wrap;align-items:center}}
.leg{{display:flex;align-items:center;gap:5px;font-size:9px;color:#8b949e}}
.sw{{width:10px;height:10px;border-radius:2px;flex-shrink:0}}
.stats{{display:flex;gap:7px;margin-bottom:7px}}
.stat{{flex:1;background:#161b22;border:1px solid #21262d;border-radius:6px;padding:7px 9px;text-align:center}}
.sv{{font-size:16px;font-weight:700;color:#58a6ff}}
.sl{{font-size:8.5px;color:#8b949e;text-transform:uppercase;letter-spacing:.3px}}
.pb{{background:#21262d;border-radius:3px;height:4px;margin-top:4px;overflow:hidden}}
.pf{{height:100%;border-radius:3px;background:linear-gradient(90deg,#58a6ff,#1f6feb)}}
.face{{border:1px solid #21262d;border-radius:8px;background:#161b22;overflow-x:auto;margin-bottom:7px}}
.fi{{min-width:max-content;padding:12px 14px}}
.dbar{{display:flex;justify-content:space-between;font-size:8.5px;color:#8b949e;margin-bottom:6px}}
.rlbl{{font-size:8.5px;color:#6e7681;font-weight:600;text-transform:uppercase;letter-spacing:.4px;margin-bottom:2px}}
.row{{display:flex;align-items:center;gap:2px;margin-bottom:6px}}
.drv{{width:40px;height:30px;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:6.5px;font-weight:700;color:#fff;border:1.5px solid rgba(255,255,255,.2);flex-shrink:0;text-align:center;line-height:1.3}}
.shr{{height:30px;border-radius:4px;display:flex;align-items:center;justify-content:center;padding:0 7px;font-size:7px;font-weight:700;color:#fff;border:1.5px solid rgba(255,255,255,.2);flex-shrink:0;white-space:nowrap}}
.sr,.pr{{display:flex;gap:1px;flex:1}}
.s-blk{{width:9px;height:30px;border:1px solid rgba(0,0,0,.3);border-radius:1px;flex-shrink:0;display:flex;align-items:flex-end;justify-content:center;font-size:4.5px;color:rgba(255,255,255,.9);cursor:default;transition:transform .08s}}
.s-blk:hover{{transform:scaleY(1.18);border-color:rgba(255,255,255,.4);z-index:5}}
.p-blk{{width:9px;height:19px;border:1.5px solid rgba(0,0,0,.3);border-radius:1px;flex-shrink:0;display:flex;align-items:flex-end;justify-content:center;font-size:4.5px;color:rgba(255,255,255,.9);cursor:default;transition:transform .08s}}
.p-blk:hover{{transform:scaleY(1.2);border-color:rgba(255,255,255,.4);z-index:5}}
.sp{{width:43px;flex-shrink:0}}
.dvdr{{height:2px;background:linear-gradient(90deg,transparent,#30363d,transparent);margin:2px 0}}
.bsl-wrap{{border:1px solid #21262d;border-radius:8px;background:#161b22;padding:10px 12px}}
.bsl-ttl{{font-size:10px;font-weight:700;color:#58a6ff;text-transform:uppercase;letter-spacing:.5px;margin-bottom:7px}}
.bsl-row{{display:flex;gap:7px;flex-wrap:wrap}}
.bsl-blk{{min-width:72px;height:48px;border-radius:6px;display:flex;align-items:center;justify-content:center;border:1.5px solid rgba(255,255,255,.12);cursor:default;transition:transform .1s}}
.bsl-blk:hover{{transform:scale(1.05);border-color:rgba(255,255,255,.3)}}
.bsl-blk span{{font-size:8.5px;font-weight:600;color:#fff;text-align:center;pointer-events:none;text-shadow:0 1px 3px rgba(0,0,0,.7);padding:3px}}
.goaf{{height:5px;background:repeating-linear-gradient(45deg,#0d1117,#0d1117 4px,#1a1a2e 4px,#1a1a2e 8px);border-radius:2px;margin-bottom:3px;opacity:.7}}
.coal{{height:5px;background:repeating-linear-gradient(45deg,#0d1117,#0d1117 4px,#111 4px,#111 8px);border-radius:2px;margin-top:3px;opacity:.7}}
.fn{{font-size:7.5px;color:#6e7681;text-align:center;padding:1px 0}}
.ptleg{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:7px;padding:5px 10px;background:#161b22;border:1px solid #21262d;border-radius:6px}}
</style></head><body>
<div class="hdr">
  <div><div class="ttl">{ttl}</div>
  <div class="sub">{MINE} · MG Shield #1 ◄──────────────────────────────────────► TG Shield #203</div></div>
  <div class="legs">{leg}</div>
</div>
<div class="stats">
  <div class="stat"><div class="sv">{n_sh}/{NUM_SHIELDS}</div><div class="sl">Supports {lbl}</div><div class="pb"><div class="pf" style="width:{sh_p}%"></div></div></div>
  <div class="stat"><div class="sv">{n_p}/{NUM_PANS}</div><div class="sl">AFC Pans {lbl}</div><div class="pb"><div class="pf" style="width:{p_p}%"></div></div></div>
  <div class="stat"><div class="sv">{n_b}/{len(bsl_d)}</div><div class="sl">BSL {lbl}</div><div class="pb"><div class="pf" style="width:{b_p}%"></div></div></div>
  <div class="stat"><div class="sv" style="color:{'#22c55e' if mgok else '#ef4444'};font-size:10px">{mg_v}</div><div class="sl">MG Drive</div></div>
  <div class="stat"><div class="sv" style="color:{'#22c55e' if tgok else '#ef4444'};font-size:10px">{tg_v}</div><div class="sl">TG Drive</div></div>
  <div class="stat"><div class="sv" style="color:{'#22c55e' if shok else '#ef4444'};font-size:10px">{shr_v}</div><div class="sl">Shearer</div></div>
</div>
<div class="ptleg"><span style="font-size:9px;color:#58a6ff;font-weight:700;margin-right:6px">PAN TYPE (border):</span>{pt_leg}</div>
<div class="face"><div class="fi">
  <div class="dbar"><span>◄ MAINGATE (MG) · #1</span><span>⬤ {MINE} · LONGWALL FACE · TOP DOWN ⬤</span><span>#203 · TAILGATE (TG) ►</span></div>
  <div class="goaf"></div><div class="fn">▲ GOAF ▲</div>
  <div class="rlbl" style="margin-top:5px">2-Leg Hydraulic Roof Supports — {NUM_SHIELDS} units</div>
  <div class="row"><div class="drv" style="background:{mg_c}" title="MG Drive: {mg_v}">MG<br>DRIVE</div><div class="sr">{s_html}</div><div class="drv" style="background:{tg_c}" title="TG Drive: {tg_v}">TG<br>DRIVE</div></div>
  <div class="dvdr"></div>
  <div class="rlbl">Nepean AFC Panline — {NUM_PANS} pans + pan sides (Drg 1506-0000-000-00 OCN CCS MG→TG)</div>
  <div class="row"><div class="sp"></div><div class="pr">{p_html}</div><div class="shr" style="background:{shr_c}" title="SL750: {shr_v}">⚙ SL750<br>Shearer</div></div>
  <div class="fn">▼ COAL FACE ▼</div><div class="coal"></div>
</div></div>
<div class="bsl-wrap"><div class="bsl-ttl">⚙ Belt Storage Loop (BSL) — Maingate Inbye</div><div class="bsl-row">{b_html}</div></div>
</body></html>"""

# ── PRE-INSTALL 4-LANE BOARD HTML ────────────────────────────────────
def build_preinst_html():
    lanes = ["Not Installed","Installed","Pre-Powered","Post-Powered"]
    lc = {"Not Installed":"#7f1d1d","Installed":"#78350f","Pre-Powered":"#1e3a5f","Post-Powered":"#14532d"}
    hc = {"Not Installed":"#ef4444","Installed":"#f59e0b","Pre-Powered":"#3b82f6","Post-Powered":"#22c55e"}
    lane_items = {l:[] for l in lanes}
    for comp in PRE_INSTALL_COMPONENTS:
        sv = st.session_state.pre_comp[comp]
        ts = st.session_state.pre_ts.get(comp) or ""
        lane_items[sv].append((comp,ts))
    cols_html = ""
    for lane in lanes:
        items_h = "".join(
            (f'<div class="card"><div class="cn">{c}</div>' + (f'<div class="ct">{ts}</div>' if ts else '') + '</div>')
            for c,ts in lane_items[lane]
        ) or '<div class="empty">—</div>'
        cols_html += f'<div class="lane" style="background:{lc[lane]}22;border:1px solid {lc[lane]}88"><div class="lhdr" style="background:{hc[lane]}">{lane}</div><div class="lbody">{items_h}</div></div>'
    bar_h = "".join(
        f'<div class="bi" style="background:{PRE_INST_COLORS.get(st.session_state.pre_comp[c],"#555")}" title="{c}: {st.session_state.pre_comp[c]}">{c}</div>'
        for c in PRE_INSTALL_COMPONENTS
    )
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
*{{box-sizing:border-box;margin:0;padding:0;font-family:'Segoe UI',system-ui,sans-serif}}
body{{background:#0d1117;color:#e6edf3;padding:12px 14px}}
.ttl{{font-size:13px;font-weight:700;color:#58a6ff;letter-spacing:.8px;margin-bottom:10px}}
.lanes{{display:flex;gap:10px;margin-bottom:10px}}
.lane{{flex:1;border-radius:8px;overflow:hidden}}
.lhdr{{padding:7px 10px;font-size:11px;font-weight:700;color:#fff;text-align:center;letter-spacing:.5px}}
.lbody{{padding:8px;min-height:100px}}
.card{{background:#1a1f2b;border:1px solid #30363d;border-radius:6px;padding:6px 9px;margin-bottom:5px;font-size:11px;font-weight:600}}
.cn{{margin-bottom:2px}}.ct{{font-size:9px;color:#8b949e;font-weight:400}}
.empty{{color:#6e7681;font-size:10px;padding:4px}}
.bwrap{{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:9px 12px}}
.bttl{{font-size:10px;font-weight:700;color:#58a6ff;text-transform:uppercase;letter-spacing:.5px;margin-bottom:7px}}
.bar{{display:flex;gap:6px;flex-wrap:wrap}}
.bi{{padding:5px 10px;border-radius:4px;font-size:10px;font-weight:600;color:#fff;border:1px solid rgba(255,255,255,.15);white-space:nowrap}}
</style></head><body>
<div class="ttl">PRE-INSTALL — 4-LANE COMMISSIONING BOARD · {MINE} · {MOVE_TO}</div>
<div class="lanes">{cols_html}</div>
<div class="bwrap"><div class="bttl">Installed Equipment Bar</div><div class="bar">{bar_h}</div></div>
</body></html>"""

# ── BOLT-UP GRID HTML ─────────────────────────────────────────────────
def build_bolt_html():
    SC = {"Not Started":"#1e2a1e","In Progress":"#92400e","Complete":"#14532d","Signed Off":"#1e3a5f"}
    TC = {"Not Started":"#6b7280","In Progress":"#fcd34d","Complete":"#4ade80","Signed Off":"#93c5fd"}
    IC = {"Not Started":"–","In Progress":"⟳","Complete":"✓","Signed Off":"★"}
    hdr = "".join(f'<th style="color:#8b949e;font-size:10px;padding:6px 8px;border-bottom:1px solid #30363d;white-space:nowrap;background:#161b22">{r}</th>' for r in BOLT_ROW_LABELS)
    rows_h = ""
    for t in BOLT_TEAMS:
        tid = t["id"]; lo,hi = t["range"]
        cells = "".join(
            f'<td style="background:{SC.get(st.session_state.bolt[tid][r],"#161b22")};text-align:center;padding:7px 4px;border:1px solid #1a1f2b;font-size:12px;color:{TC.get(st.session_state.bolt[tid][r],"#fff")};font-weight:700" title="{r} Zone {tid}: {st.session_state.bolt[tid][r]} · Dir: {BOLT_DIRS.get(r,["?"])[tid-1]}">{IC.get(st.session_state.bolt[tid][r],"–")}</td>'
            for r in BOLT_ROW_LABELS
        )
        comp = sum(1 for r in BOLT_ROW_LABELS if st.session_state.bolt[tid][r] in ["Complete","Signed Off"])
        pct  = round(comp/len(BOLT_ROW_LABELS)*100)
        rows_h += f'<tr><td style="padding:7px 10px;background:#161b22;border:1px solid #1a1f2b;white-space:nowrap"><div style="font-size:11px;font-weight:700;color:#e6edf3">{t["name"]}</div><div style="font-size:9px;color:#8b949e">S#{lo}–{hi} · Gopher @{t["gopher"]} · Outlet {t["outlet"]}</div><div style="background:#21262d;border-radius:2px;height:3px;margin-top:4px;overflow:hidden"><div style="width:{pct}%;height:100%;background:linear-gradient(90deg,#22c55e,#16a34a)"></div></div><div style="font-size:8px;color:#22c55e;margin-top:2px">{pct}% complete</div></td>{cells}</tr>'
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>*{{box-sizing:border-box;margin:0;padding:0;font-family:'Segoe UI',sans-serif}}body{{background:#0d1117;color:#e6edf3;padding:12px}}.ttl{{font-size:13px;font-weight:700;color:#58a6ff;margin-bottom:8px;letter-spacing:.5px}}.wrap{{overflow-x:auto;border:1px solid #21262d;border-radius:8px}}table{{border-collapse:collapse;width:100%}}.leg{{display:flex;gap:14px;margin-top:8px;padding:6px 10px;background:#161b22;border:1px solid #21262d;border-radius:6px}}.li{{display:flex;align-items:center;gap:5px;font-size:10px;color:#8b949e}}.ls{{width:12px;height:12px;border-radius:2px}}</style></head><body>
<div class="ttl">BOLT-UP TRACKING — 7 TEAMS × {len(BOLT_ROW_LABELS)} ROW PHASES · {MINE} · STD1400</div>
<div class="wrap"><table><thead><tr><th style="background:#1a1f2b;padding:8px 10px;text-align:left;font-size:10px;color:#58a6ff;border-bottom:1px solid #30363d">Team / Range / Gopher / Outlet</th>{hdr}</tr></thead><tbody>{rows_h}</tbody></table></div>
<div class="leg"><div class="li"><div class="ls" style="background:#1e2a1e;border:1px solid #30363d"></div>Not Started</div><div class="li"><div class="ls" style="background:#92400e"></div>In Progress</div><div class="li"><div class="ls" style="background:#14532d"></div>Complete</div><div class="li"><div class="ls" style="background:#1e3a5f"></div>Signed Off</div></div>
</body></html>"""
# ── SIDEBAR ───────────────────────────────────────────────────────────
st.sidebar.markdown(f"""
<div style="background:linear-gradient(160deg,#1f2d3d,#0d1117);padding:14px;border-radius:10px;border:1px solid #21262d;margin-bottom:10px">
  <div style="color:#58a6ff;font-size:18px;font-weight:700;letter-spacing:1px">⛏️ MOS – LWMove</div>
  <div style="color:#e6edf3;font-size:11px;margin-top:4px;font-weight:600">{MINE}</div>
  <div style="color:#8b949e;font-size:10px;margin-top:2px">{MOVE_FROM} Recovery → {MOVE_TO} Install</div>
  <div style="color:#6e7681;font-size:9px;margin-top:1px">{MOVE_TYPE}</div>
</div>""", unsafe_allow_html=True)

page = st.sidebar.radio("Navigate", [
    "🏠  Dashboard","📋  Pre-Install","🛡️  Recovery",
    "📦  Install","🔩  Bolt-Up","📊  Metrics & Reports","📥  Data Input",
], label_visibility="collapsed")

st.sidebar.divider()
st.sidebar.markdown("**Live Progress**")
for label, val in [("Pre-Install Checklist",f"{pre_pct()}%"),
                    ("Pre-Install Components",f"{pre_comp_pct()}%"),
                    ("Bolt-Up",f"{bolt_pct()}%"),
                    ("Recovery",f"{rec_pct()}%"),
                    ("Install",f"{inst_pct()}%")]:
    st.sidebar.metric(label, val)
st.sidebar.divider()
st.sidebar.caption(f"Updated: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                   "MOS–LWMove v2.0 · OCN LW707→708\nBuilt from real site documents")

# ── DASHBOARD ─────────────────────────────────────────────────────────
if page == "🏠  Dashboard":
    st.title("MOS – LWMove  ·  Dashboard")
    st.caption(f"{MINE} · {MOVE_FROM} Recovery → {MOVE_TO} Install · {MOVE_TYPE} · {datetime.now().strftime('%d/%m/%Y %H:%M')} AEST")

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: st.metric("Pre-Install Checklist",f"{pre_pct()}%")
    with c2: st.metric("Bolt-Up Overall",f"{bolt_pct()}%")
    with c3: st.metric("Recovery Overall",f"{rec_pct()}%")
    with c4: st.metric("Install Overall",f"{inst_pct()}%")
    with c5: st.metric("Shields Installed",f"{cnt(st.session_state.inst_shields,['Installed','Commissioned'])}/{NUM_SHIELDS}")

    c6,c7,c8,c9 = st.columns(4)
    with c6: st.metric("Shields Recovered",f"{cnt(st.session_state.rec_shields,'Recovered')}/{NUM_SHIELDS}")
    with c7: st.metric("AFC Pans Installed",f"{cnt(st.session_state.inst_pans,['Installed','Commissioned'])}/{NUM_PANS}")
    with c8: st.metric("AFC Pans Recovered",f"{cnt(st.session_state.rec_pans,'Recovered')}/{NUM_PANS}")
    with c9: st.metric("Components Post-Powered",f"{sum(1 for v in st.session_state.pre_comp.values() if v=='Post-Powered')}/{len(PRE_INSTALL_COMPONENTS)}")

    st.divider()
    tab_g, tab_ph, tab_st = st.tabs(["📅 Master Schedule (Bible Dates)","📊 Phase Progress","🔵 Status Breakdown"])

    with tab_g:
        fig = px.timeline(SCHEDULE, x_start="Start", x_end="Finish", y="Task",
                          color="Category", color_discrete_map=CAT_COLORS,
                          hover_data={"Progress":True},
                          title=f"{MINE} — {MOVE_FROM}/{MOVE_TO} Move Master Schedule (OCN Bible Dates)")
        fig.update_layout(height=560,plot_bgcolor="#161b22",paper_bgcolor="#0d1117",
                          font=dict(color="#e6edf3"),
                          xaxis=dict(rangeslider=dict(visible=True),type="date",gridcolor="#21262d",tickfont=dict(size=10)),
                          yaxis=dict(gridcolor="#21262d",autorange="reversed",tickfont=dict(size=10)),
                          legend=dict(orientation="h",y=-0.2),title_font=dict(size=13,color="#58a6ff"))
        today = pd.Timestamp(date.today())          # this is the reliable date format for Plotly
fig.add_vline(x=today, line_dash="dot", line_color="#f59e0b")
fig.add_annotation(x=today, y=1.05, text="Today", showarrow=False,
                   font=dict(color="#f59e0b", size=10), yshift=10)
                      annotation_text="Today",annotation_font_color="#f59e0b",annotation_font_size=10)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Dates from OCN LW Move Plan BIBLE 708-601 v0.1, Table 3-1")

    with tab_ph:
        ov = pd.DataFrame({
            "Phase":["Pre-Install Checklist","Pre-Install Components","Bolt-Up","Recovery","Install"],
            "Complete %":[pre_pct(),pre_comp_pct(),bolt_pct(),rec_pct(),inst_pct()],
        })
        fig2 = px.bar(ov,x="Phase",y="Complete %",color="Complete %",text="Complete %",
                      color_continuous_scale=[[0,"#ef4444"],[.5,"#f59e0b"],[1,"#22c55e"]],
                      title=f"{MINE} — Phase Completion Overview")
        fig2.update_traces(texttemplate="%{text:.1f}%",textposition="outside")
        fig2.update_layout(height=360,plot_bgcolor="#161b22",paper_bgcolor="#0d1117",
                           font=dict(color="#e6edf3"),coloraxis_showscale=False,
                           yaxis=dict(range=[0,110],gridcolor="#21262d"),xaxis=dict(gridcolor="#21262d"))
        st.plotly_chart(fig2, use_container_width=True)

    with tab_st:
        def donut(d,clrs,ttl_s):
            cts={}
            for v in d.values(): cts[v]=cts.get(v,0)+1
            f=px.pie(names=list(cts.keys()),values=list(cts.values()),title=ttl_s,hole=.52,
                     color=list(cts.keys()),color_discrete_map=clrs)
            f.update_layout(height=270,plot_bgcolor="#161b22",paper_bgcolor="#161b22",
                            font=dict(color="#e6edf3",size=10),title_font=dict(size=11,color="#58a6ff"),
                            margin=dict(t=35,b=6,l=6,r=6),legend=dict(font=dict(size=9)))
            return f
        dc1,dc2,dc3,dc4=st.columns(4)
        with dc1: st.plotly_chart(donut(st.session_state.inst_shields,INSTALL_COLORS,"Supports – Install"),use_container_width=True)
        with dc2: st.plotly_chart(donut(st.session_state.rec_shields,RECOVERY_COLORS,"Supports – Recovery"),use_container_width=True)
        with dc3: st.plotly_chart(donut(st.session_state.inst_pans,INSTALL_COLORS,"AFC Pans – Install"),use_container_width=True)
        with dc4: st.plotly_chart(donut(st.session_state.inst_bsl,INSTALL_COLORS,"BSL – Install"),use_container_width=True)

    if st.session_state.log:
        st.divider()
        st.subheader("📝 Recent Activity Log")
        st.dataframe(pd.DataFrame(st.session_state.log[-15:][::-1]),use_container_width=True,hide_index=True)
# ── PRE-INSTALL ───────────────────────────────────────────────────────
elif page == "📋  Pre-Install":
    st.title(f"Pre-Install · {MOVE_TO} · {MINE}")
    st.caption("4-lane commissioning board (PRD spec) + comprehensive site prep checklist")
    tab_b, tab_c = st.tabs(["🗂 Component Board (4-Lane)","☑ Pre-Install Checklist"])

    with tab_b:
        components.html(build_preinst_html(), height=360, scrolling=False)
        st.divider()
        st.markdown('<div class="pill">Update Component Status</div>', unsafe_allow_html=True)
        for row_i in range(0,len(PRE_INSTALL_COMPONENTS),3):
            cols = st.columns(3)
            for col,comp in zip(cols, PRE_INSTALL_COMPONENTS[row_i:row_i+3]):
                with col:
                    cur = st.session_state.pre_comp[comp]
                    nv  = st.selectbox(f"**{comp}**", PRE_INST_STATUSES,
                                       index=PRE_INST_STATUSES.index(cur), key=f"pc_{comp}")
                    if nv != cur:
                        st.session_state.pre_comp[comp] = nv
                        st.session_state.pre_ts[comp]   = datetime.now().strftime("%d/%m %H:%M")
                        log_event(f"Pre-Install: {comp} → {nv}"); st.rerun()
                    c = PRE_INST_COLORS.get(cur,"#555")
                    ts = st.session_state.pre_ts.get(comp) or "—"
                    st.markdown(f'<span style="color:{c};font-size:11px">● {cur}</span> '
                                f'<span style="color:#6e7681;font-size:10px">{ts}</span>',
                                unsafe_allow_html=True)
        st.divider()
        st.markdown("**PRS 1–3 Layout (Maingate End)**")
        st.code(
            "MG ROAD:  [PRS 3]──[PRS 2]──[PRS 1]──┐ ← cut-through\n"
            "          ░░░░░░░░░░░░░ AFC PANLINE ░░░░░░░\n"
            "BSL ──────┤  MG DRIVE  ·  CRUSHER  ·  DCB  ·  BOOT END",
            language=None
        )

    with tab_c:
        st.progress(pre_pct()/100, text=f"Pre-Install Checklist: {pre_pct()}%")
        st.caption("All items must be completed before recovery commences per TAR0907 & STD1400.")
        for sec,items in PRE_INSTALL_SECTIONS.items():
            done  = sum(st.session_state.pre_check[sec].values())
            total = len(items)
            pct   = round(done/total*100) if total else 0
            with st.expander(f"{'✅' if done==total else '🔲'} {sec}  ·  {done}/{total}  ({pct}%)", expanded=(done<total)):
                st.progress(pct/100)
                cc = st.columns(2)
                for idx,item in enumerate(items):
                    with cc[idx%2]:
                        cur = st.session_state.pre_check[sec][item]
                        nv  = st.checkbox(item, value=cur, key=f"chk_{sec}_{item}")
                        if nv != cur:
                            st.session_state.pre_check[sec][item] = nv
                            log_event(f"Pre-Install: {'✅' if nv else '☐'} {item}"); st.rerun()
        st.divider()
        if st.button("🔒 Lock Pre-Install & Generate Handover Note", type="primary"):
            log_event(f"Pre-Install LOCKED — checklist {pre_pct()}% / components {pre_comp_pct()}%")
            st.success(f"Pre-Install locked at {pre_pct()}% checklist / {pre_comp_pct()}% components. "
                       "Recovery team may commence per support plans 2-57-2378 / 2379 / 2380.")

# ── RECOVERY ──────────────────────────────────────────────────────────
elif page == "🛡️  Recovery":
    st.title(f"{MOVE_FROM} Recovery · {MINE}")
    st.caption("Shred Recovery → AFC chain/hoses/cables → Roof supports (ref 2-57-2378/79/80)")
    rp = rec_pct()
    st.progress(rp/100, text=f"Overall Recovery: {rp}%")
    st.markdown('<span class="rchip">2-57-2378 MG Shield Extraction</span>'
                '<span class="rchip">2-57-2379 Run of Face (Sequential & Leapfrog)</span>'
                '<span class="rchip">2-57-2380 TG Shield Extraction</span>'
                '<span class="rchip">TAR0907 LW Teardown</span>'
                '<span class="rchip">WI0162 Panline Disassembly</span>'
                '<span class="rchip">WI0621 Shearer Recovery</span>',
                unsafe_allow_html=True)

    tab_v,tab_sq,tab_sh,tab_pa,tab_bsl,tab_dr = st.tabs([
        "🗺 Plan View","📋 Recovery Sequence","🛡 Shields","🔗 AFC Pans","⚙ BSL","⚡ Drives & Shearer"
    ])

    with tab_v:
        st.markdown("*Hover blocks for status · Use other tabs to update*")
        components.html(build_plan_html("recovery"), height=490, scrolling=False)

    with tab_sq:
        st.markdown('<div class="pill">Recovery Sequence Tracker</div>', unsafe_allow_html=True)
        seq_items = [
            ("1","Break AFC Chain","WI0110, WI0192"),
            ("2","Remove Shearer SL750","WI0621, WI0293 Remove TG Drum, WI0733 Remove Shearer Drum"),
            ("3","Remove TG Drive","WI0163, WI0037 Dismantle TG Motor & Gearbox, WI0308"),
            ("4","Remove AFC Chain","WI0730 AFC Chain Recovery, WI0297"),
            ("5","Remove AFC Hoses & Cables","WI0299 Reeling Hoses, WI0298 Pulling Bretby, WI0739"),
            ("6","MG Shield Extraction","Ref: 2-57-2378 (MG Shield Extraction)"),
            ("7","Run of Face – Sequential","Ref: 2-57-2379 (Sequential Salvage)"),
            ("8","Run of Face – Leapfrog","Ref: 2-57-2379 (Leapfrog Salvage)"),
            ("9","TG Shield Extraction","Ref: 2-57-2380 (TG Shield Extraction)"),
            ("10","AFC Panline Recovery","WI0162, WI0353 Transport Pans, WI0354 Wash Down Pans"),
            ("11","MG Drive Removal","WI0169 MG Drive Disassembly, WI0108 AFC No.1 Drive CST"),
            ("12","BSL Disassembly & Transport","WI0161 Bootend, WI0300 Convex, WI0303 Slope Sections, WI0301 Bootend Motor"),
        ]
        for num,task,refs in seq_items:
            key = f"recseq_{num}"
            if key not in st.session_state: st.session_state[key] = False
            c1,c2 = st.columns([6,1])
            with c1:
                st.markdown(f"**Step {num}: {task}**")
                st.caption(f"Ref: {refs}")
            with c2:
                done = st.checkbox("✓", value=st.session_state[key], key=f"cb_{key}")
                if done != st.session_state[key]:
                    st.session_state[key] = done
                    log_event(f"Recovery Seq {num}: {task} → {'Done' if done else 'Reset'}"); st.rerun()
        steps_done = sum(1 for n,_,_ in seq_items if st.session_state.get(f"recseq_{n}",False))
        st.progress(steps_done/len(seq_items), text=f"Recovery sequence: {steps_done}/{len(seq_items)} steps")

    with tab_sh:
        n_rec = cnt(st.session_state.rec_shields,"Recovered")
        st.progress(n_rec/NUM_SHIELDS, text=f"{n_rec}/{NUM_SHIELDS} shields recovered")
        c1,c2 = st.columns(2)
        with c1:
            lo,hi = st.slider("Shield range",1,203,(1,10),key="rsh_r")
            nst   = st.selectbox("Status",RECOVERY_STATUSES,key="rsh_nst")
            if st.button("Apply to shields",type="primary",key="rsh_app"):
                for i in range(lo,hi+1): st.session_state.rec_shields[i] = nst
                log_event(f"Recovery: Shields {lo}–{hi} → {nst}"); st.rerun()
        with c2:
            if st.button("Mark ALL Recovered",key="rsh_all"):
                for i in range(1,204): st.session_state.rec_shields[i] = "Recovered"
                log_event("Recovery: All 203 shields → Recovered"); st.rerun()
            if st.button("Reset All (In Place)",key="rsh_reset"):
                for i in range(1,204): st.session_state.rec_shields[i] = "In Place"; st.rerun()
        ind = st.number_input("Individual Shield #",1,203,1,key="rsh_ind")
        ist = st.selectbox("Status",RECOVERY_STATUSES,
                            index=RECOVERY_STATUSES.index(st.session_state.rec_shields[ind]),key="rsh_ist")
        if st.button("Update Shield",key="rsh_upd"):
            st.session_state.rec_shields[ind] = ist
            log_event(f"Recovery: Shield {ind} → {ist}"); st.rerun()
        st.divider()
        zr = [{"Zone":f"{t['name']} (#{t['range'][0]}–{t['range'][1]})",
               **{s:sum(1 for i in range(t['range'][0],t['range'][1]+1) if st.session_state.rec_shields[i]==s)
                  for s in RECOVERY_STATUSES}} for t in BOLT_TEAMS]
        st.dataframe(pd.DataFrame(zr),use_container_width=True,hide_index=True)

    with tab_pa:
        n_rp = cnt(st.session_state.rec_pans,"Recovered")
        st.progress(n_rp/NUM_PANS, text=f"{n_rp}/{NUM_PANS} AFC pans recovered")
        c1,c2 = st.columns(2)
        with c1:
            lo,hi = st.slider("Pan range",1,203,(1,10),key="rpa_r")
            nst   = st.selectbox("Status",RECOVERY_STATUSES,key="rpa_nst")
            if st.button("Apply to pans",type="primary",key="rpa_app"):
                for i in range(lo,hi+1): st.session_state.rec_pans[i] = nst
                log_event(f"Recovery: Pans {lo}–{hi} → {nst}"); st.rerun()
        with c2:
            if st.button("Mark ALL Pans Recovered",key="rpa_all"):
                for i in range(1,204): st.session_state.rec_pans[i] = "Recovered"
                log_event("Recovery: All pans → Recovered"); st.rerun()

    with tab_bsl:
        n_rb = cnt(st.session_state.rec_bsl,"Recovered")
        st.progress(n_rb/len(BSL_ITEMS), text=f"{n_rb}/{len(BSL_ITEMS)} BSL components recovered")
        for rs in range(0,len(BSL_ITEMS),3):
            cols = st.columns(3)
            for col,name in zip(cols,BSL_ITEMS[rs:rs+3]):
                with col:
                    cur = st.session_state.rec_bsl[name]
                    nv  = st.selectbox(f"**{name}**",RECOVERY_STATUSES,
                                       index=RECOVERY_STATUSES.index(cur),key=f"rb_{name}")
                    if nv != cur:
                        st.session_state.rec_bsl[name] = nv
                        log_event(f"Recovery: BSL {name} → {nv}"); st.rerun()

    with tab_dr:
        c1,c2,c3 = st.columns(3)
        for col,lbl,attr in [(c1,"MG Drive","rec_mg"),(c2,"TG Drive","rec_tg"),(c3,"Shearer SL750","rec_shearer")]:
            with col:
                cur = getattr(st.session_state,attr)
                nv  = st.selectbox(f"**{lbl}**",RECOVERY_STATUSES,
                                    index=RECOVERY_STATUSES.index(cur),key=f"rdr_{attr}")
                if nv != cur:
                    setattr(st.session_state,attr,nv)
                    log_event(f"Recovery: {lbl} → {nv}"); st.rerun()
                c = "#22c55e" if nv=="Recovered" else "#f59e0b" if nv=="Being Recovered" else "#ef4444"
                st.markdown(f'<span style="color:{c}">● {nv}</span>', unsafe_allow_html=True)

# ── INSTALL ───────────────────────────────────────────────────────────
elif page == "📦  Install":
    st.title(f"{MOVE_TO} Install · {MINE}")
    st.caption("MG Drive → BSL → AFC Panline → Roof Supports → TG Drive → Shearer → Commission")
    ip = inst_pct()
    st.progress(ip/100, text=f"Overall Install: {ip}%")
    st.markdown('<span class="rchip">WI0111 Shield Installation</span>'
                '<span class="rchip">WI0731 Fit MG Drive</span>'
                '<span class="rchip">WI0296 Fit TG Drive</span>'
                '<span class="rchip">WI0313 Install Bootend</span>'
                '<span class="rchip">WI0366 Installing AFC Chain</span>'
                '<span class="rchip">WI0309 Install Transformer & Pump Station</span>',
                unsafe_allow_html=True)

    tab_v,tab_sh,tab_pa,tab_bsl,tab_dr = st.tabs([
        "🗺 Plan View","🛡 Shields","🔗 AFC Pans","⚙ BSL","⚡ Drives & Shearer"
    ])

    with tab_v:
        components.html(build_plan_html("install"), height=490, scrolling=False)
        st.divider()
        seq_cols = st.columns(5)
        for col,(n,t,d) in zip(seq_cols,[("1️⃣","MG Drive","Position & pin (WI0731)"),
                                          ("2️⃣","BSL / Boot End","Assemble inbye MG (WI0313)"),
                                          ("3️⃣","AFC Panline","Lay pans MG→TG, add flights (WI0366)"),
                                          ("4️⃣","Roof Supports","Walk shields on MG→TG (WI0111)"),
                                          ("5️⃣","TG Drive + Shearer","Install TG drive (WI0296), drop shearer")]):
            with col: st.markdown(f"**{n} {t}**\n\n{d}")

    with tab_sh:
        n_i = cnt(st.session_state.inst_shields,["Installed","Commissioned"])
        st.progress(n_i/NUM_SHIELDS, text=f"{n_i}/{NUM_SHIELDS} shields installed")
        c1,c2 = st.columns(2)
        with c1:
            lo,hi = st.slider("Shield range",1,203,(1,10),key="ish_r")
            nst   = st.selectbox("Status",INSTALL_STATUSES,key="ish_nst")
            if st.button("Apply",type="primary",key="ish_app"):
                for i in range(lo,hi+1): st.session_state.inst_shields[i] = nst
                log_event(f"Install: Shields {lo}–{hi} → {nst}"); st.rerun()
        with c2:
            if st.button("Mark ALL Installed",key="ish_all"):
                for i in range(1,204): st.session_state.inst_shields[i] = "Installed"
                log_event("Install: All shields → Installed"); st.rerun()
            if st.button("Mark ALL Commissioned",key="ish_comm"):
                for i in range(1,204): st.session_state.inst_shields[i] = "Commissioned"
                log_event("Install: All shields → Commissioned"); st.rerun()
            if st.button("Reset All (Staged)",key="ish_reset"):
                for i in range(1,204): st.session_state.inst_shields[i] = "Staged"; st.rerun()
        ind = st.number_input("Individual Shield #",1,203,1,key="ish_ind")
        ist = st.selectbox("Status",INSTALL_STATUSES,
                            index=INSTALL_STATUSES.index(st.session_state.inst_shields[ind]),key="ish_ist")
        if st.button("Update Shield",key="ish_upd"):
            st.session_state.inst_shields[ind] = ist
            log_event(f"Install: Shield {ind} → {ist}"); st.rerun()
        st.divider()
        zr = [{"Zone":f"{t['name']} (#{t['range'][0]}–{t['range'][1]})",
               "% Done":f"{round(sum(1 for i in range(t['range'][0],t['range'][1]+1) if st.session_state.inst_shields[i] in ['Installed','Commissioned'])/(t['range'][1]-t['range'][0]+1)*100)}%",
               **{s:sum(1 for i in range(t['range'][0],t['range'][1]+1) if st.session_state.inst_shields[i]==s) for s in INSTALL_STATUSES}}
              for t in BOLT_TEAMS]
        st.dataframe(pd.DataFrame(zr),use_container_width=True,hide_index=True)

    with tab_pa:
        n_ip = cnt(st.session_state.inst_pans,["Installed","Commissioned"])
        st.progress(n_ip/NUM_PANS, text=f"{n_ip}/{NUM_PANS} pans installed")
        st.markdown("**Pan type breakdown (Nepean drawing 1506-0000-000-00)**")
        pt_ct = {}
        for i in range(1,204):
            pt = PAN_TYPES.get(i,"Standard"); sv = st.session_state.inst_pans[i]
            if pt not in pt_ct: pt_ct[pt] = {s:0 for s in INSTALL_STATUSES}
            pt_ct[pt][sv] = pt_ct[pt].get(sv,0)+1
        st.dataframe(pd.DataFrame(pt_ct).T.reset_index().rename(columns={"index":"Pan Type"}),
                     use_container_width=True,hide_index=True)
        c1,c2 = st.columns(2)
        with c1:
            lo,hi = st.slider("Pan range",1,203,(1,10),key="ipa_r")
            nst   = st.selectbox("Status",INSTALL_STATUSES,key="ipa_nst")
            if st.button("Apply to pans",type="primary",key="ipa_app"):
                for i in range(lo,hi+1): st.session_state.inst_pans[i] = nst
                log_event(f"Install: Pans {lo}–{hi} → {nst}"); st.rerun()
        with c2:
            if st.button("Mark ALL Pans Installed",key="ipa_all"):
                for i in range(1,204): st.session_state.inst_pans[i] = "Installed"
                log_event("Install: All pans → Installed"); st.rerun()

    with tab_bsl:
        n_ib = cnt(st.session_state.inst_bsl,["Installed","Commissioned"])
        st.progress(n_ib/len(BSL_ITEMS), text=f"{n_ib}/{len(BSL_ITEMS)} BSL components installed")
        for rs in range(0,len(BSL_ITEMS),3):
            cols = st.columns(3)
            for col,name in zip(cols,BSL_ITEMS[rs:rs+3]):
                with col:
                    cur = st.session_state.inst_bsl[name]
                    nv  = st.selectbox(f"**{name}**",INSTALL_STATUSES,
                                       index=INSTALL_STATUSES.index(cur),key=f"ib_{name}")
                    if nv != cur:
                        st.session_state.inst_bsl[name] = nv
                        log_event(f"Install: BSL {name} → {nv}"); st.rerun()

    with tab_dr:
        st.markdown("**Eickhoff SL750 Key Specs**")
        st.dataframe(pd.DataFrame({"Parameter":["Type","Web Depth","Machine Length","Machine Weight","Drum Diameter"],
                                    "Value":["DERDS / Double-ended ranging drum","1000 mm","~14.57 m","~75 t","1.8 m"]}),
                     use_container_width=True,hide_index=True)
        st.divider()
        c1,c2,c3 = st.columns(3)
        for col,lbl,attr in [(c1,"MG Drive","inst_mg"),(c2,"TG Drive","inst_tg"),(c3,"Shearer SL750","inst_shearer")]:
            with col:
                cur = getattr(st.session_state,attr)
                nv  = st.selectbox(f"**{lbl}**",INSTALL_STATUSES,
                                    index=INSTALL_STATUSES.index(cur),key=f"idr_{attr}")
                if nv != cur:
                    setattr(st.session_state,attr,nv)
                    log_event(f"Install: {lbl} → {nv}"); st.rerun()
                c = "#22c55e" if nv in ["Installed","Commissioned"] else "#f59e0b" if nv=="Positioning" else "#ef4444"
                st.markdown(f'<span style="color:{c}">● {nv}</span>', unsafe_allow_html=True)
# ── BOLT-UP ───────────────────────────────────────────────────────────
elif page == "🔩  Bolt-Up":
    st.title(f"Bolt-Up Tracking · {MOVE_FROM} · {MINE}")
    st.caption("7 hand bolter teams · 15-shear STD1400 sequence · Megastrands rows 7+8 · Per-zone directions (Bible Table 9-2)")
    bp = bolt_pct()
    st.progress(bp/100, text=f"Overall Bolt-Up: {bp}%")
    st.markdown('<span class="rchip">STD1400 Recovery Mesh & Bolt Up</span>'
                '<span class="rchip">TAR0010 Bolt Up SCARP</span>'
                '<span class="rchip">FRM0049 Long Tendon Grout Sheet</span>'
                '<span class="rchip">FRM0477 Relocation Shutdown List</span>'
                '<span class="rchip">MOP0892 No Go Zones</span>'
                '<span class="rchip">SOP0078 Isolation</span>',
                unsafe_allow_html=True)

    tab_grid, tab_shear, tab_upd, tab_cons = st.tabs([
        "📊 Team Grid","📐 Shear Sequence (STD1400)","✏️ Update Teams","📦 Consumables (Bible)"
    ])

    with tab_grid:
        components.html(build_bolt_html(), height=360, scrolling=False)
        st.divider()
        tnames = [t["name"] for t in BOLT_TEAMS]
        tpcts  = []
        for t in BOLT_TEAMS:
            sw  = {"Not Started":0,"In Progress":.5,"Complete":1.,"Signed Off":1.}
            wt  = sum(BOLT_ROW_WEIGHTS.values())
            got = sum(BOLT_ROW_WEIGHTS.get(r,10)*sw.get(s,0) for r,s in st.session_state.bolt[t["id"]].items())
            tpcts.append(round(got/wt*100,1))
        fig = px.bar(x=tnames,y=tpcts,labels={"x":"Team","y":"Completion %"},
                     title="Bolt-Up Completion % by Team",color=tpcts,
                     color_continuous_scale=[[0,"#ef4444"],[.5,"#f59e0b"],[1,"#22c55e"]],
                     text=[f"{p}%" for p in tpcts])
        fig.update_traces(textposition="outside")
        fig.update_layout(height=320,plot_bgcolor="#161b22",paper_bgcolor="#0d1117",
                          font=dict(color="#e6edf3"),coloraxis_showscale=False,
                          yaxis=dict(range=[0,110],gridcolor="#21262d"),xaxis=dict(gridcolor="#21262d"))
        st.plotly_chart(fig, use_container_width=True)

    with tab_shear:
        st.markdown('<div class="pill">15-Shear Sequence (STD1400) — Chainage & Bolt Rows</div>', unsafe_allow_html=True)
        shears_done_n = 0
        for sh in BOLT_SHEARS:
            key = f"sh_done_{sh['sh']}"
            if key not in st.session_state: st.session_state[key] = False
            is_bolt = sh["rows"] != "—"
            is_mega = sh["mega"]
            is_last = sh["sh"] == "LAST"
            icon = "🔴" if is_last else ("🟠" if is_mega else ("🟡" if is_bolt else "⚪"))
            c1,c2,c3,c4,c5 = st.columns([1.4,.8,1.3,2.5,1])
            with c1: st.markdown(f"**{icon} {sh['sh']}**")
            with c2: st.markdown(f"`{sh['ch_m']} m`")
            with c3: st.markdown(f"`{sh['dir']}`")
            with c4:
                st.markdown(f"**{sh['rows']}**" if is_bolt else "—")
                if sh["note"]: st.caption(sh["note"])
            with c5:
                done = st.checkbox("Done",value=st.session_state[key],key=f"shcb_{sh['sh']}")
                if done != st.session_state[key]:
                    st.session_state[key] = done
                    log_event(f"Bolt-Up Shear: {sh['sh']} → {'✅' if done else '☐'}"); st.rerun()
            if done: shears_done_n += 1
            if is_last:
                st.markdown('<div class="warn">⚠ LAST SHEAR — Do NOT advance shields (final position). '
                            'Complete FRM0477 Shutdown List. Power off section. Commence teardown.</div>',
                            unsafe_allow_html=True)
        st.progress(shears_done_n/len(BOLT_SHEARS),
                    text=f"Shear sequence: {shears_done_n}/{len(BOLT_SHEARS)} shears complete")
        st.divider()
        st.markdown("**Bolting Directions by Zone — LW Move Bible Table 9-2**")
        dir_rows = [{"Row Phase":r,**{t["name"]:BOLT_DIRS.get(r,["?"])[i] for i,t in enumerate(BOLT_TEAMS)}}
                    for r in BOLT_ROW_LABELS]
        st.dataframe(pd.DataFrame(dir_rows),use_container_width=True,hide_index=True)
        st.divider()
        st.subheader("Megabolt Sign-Off (FRM0049)")
        mc1,mc2 = st.columns(2)
        with mc1:
            r7 = st.checkbox("FRM0049 Row 7 Megabolts grouted & signed off (2nd last shear)",
                              value=st.session_state.frm0049_r7,key="frm_r7")
            if r7 != st.session_state.frm0049_r7:
                st.session_state.frm0049_r7 = r7
                log_event(f"FRM0049 Row 7 {'✅ signed off' if r7 else 'reset'}"); st.rerun()
        with mc2:
            r8 = st.checkbox("FRM0049 Row 8 Megabolts grouted & signed off (last shear)",
                              value=st.session_state.frm0049_r8,key="frm_r8")
            if r8 != st.session_state.frm0049_r8:
                st.session_state.frm0049_r8 = r8
                log_event(f"FRM0049 Row 8 {'✅ signed off' if r8 else 'reset'}"); st.rerun()
        if not st.session_state.frm0049_r7 or not st.session_state.frm0049_r8:
            st.markdown('<div class="warn">⚠ FRM0049 must be completed and returned to geotechnical engineer '
                        'at end of shift for each megabolt row before face is powered off.</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="ok">✅ Both FRM0049 Long Tendon Grout Sheets signed off.</div>',
                        unsafe_allow_html=True)

    with tab_upd:
        for t in BOLT_TEAMS:
            tid=t["id"]; lo,hi=t["range"]
            sw={"Not Started":0,"In Progress":.5,"Complete":1.,"Signed Off":1.}
            wt=sum(BOLT_ROW_WEIGHTS.values())
            got=sum(BOLT_ROW_WEIGHTS.get(r,10)*sw.get(s,0) for r,s in st.session_state.bolt[tid].items())
            pct=round(got/wt*100,1)
            with st.expander(f"**{t['name']}**  ·  #{lo}–{hi}  ·  Gopher @{t['gopher']}  ·  Outlet {t['outlet']}  ·  {pct}%"):
                cols=st.columns(len(BOLT_ROW_LABELS))
                for col,row in zip(cols,BOLT_ROW_LABELS):
                    with col:
                        cur=st.session_state.bolt[tid][row]
                        nv=st.selectbox(row,BOLT_ROW_STATUSES,index=BOLT_ROW_STATUSES.index(cur),key=f"bu_{tid}_{row}")
                        if nv!=cur:
                            st.session_state.bolt[tid][row]=nv
                            log_event(f"Bolt-Up: {t['name']} {row} → {nv}"); st.rerun()
                        st.caption(f"Dir: {BOLT_DIRS.get(row,['?'])[tid-1]}")
                st.progress(pct/100, text=f"{pct}% complete")

    with tab_cons:
        st.markdown('<div class="pill">Bolt Pod Contents — LW Move Bible Section 9.2</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            "Item":["1.2 m High Tensile bolts","1.8 m High Tensile bolts","1.8 m Mild Steel bolts",
                    "1.2 m Pinning bolts","1000 mm resin box","600 mm resin box","Plates bundles"],
            "Qty per Pod":["12","20","20","1","—","—","—"],
            "Loading Rule":["Per bolt pod","Per bolt pod","Per bolt pod","Per bolt pod",
                            "1 box per EVEN shield","1 box per 8th shield","2×EVEN / 1×ODD shield"],
        }),use_container_width=True,hide_index=True)
        st.markdown('<div class="pill">Megastrand Loading — LW Move Bible Section 9.3 (TG side)</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            "Item":["8.2 m Megastrands","1000/36 Medium Set Chem boxes","600 mm chem boxes","Bags FB400","Plates"],
            "Qty per 10 shields":["20 (2 per shield)","2 boxes (10 per box)","1 box","24 bags","20 (individually)"],
        }),use_container_width=True,hide_index=True)
        st.info("Grout bowl/kit at midface. All grout bowls maintained at MG "
                "(2 in use during grouting, spare pumps/mixers at MG).")
        st.markdown('<div class="pill">Bolt Pod Loading on AFC (WI0737)</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            "Item":["Yellow rollers","Bolt pods","Bundles of plates","1000 mm chem boxes","Gophers"],
            "Frequency":["Every 2nd bolt pod (every 2nd shield has a roller)","Every 3rd shield",
                         "6× bundles","3× boxes (≈12.5 per shield – 25 per box)","At positions 203,173,144,115,87,58,30"],
        }),use_container_width=True,hide_index=True)

# ── METRICS & REPORTS ─────────────────────────────────────────────────
elif page == "📊  Metrics & Reports":
    st.title("Metrics & Reports")
    tab1,tab2,tab3,tab4 = st.tabs(["📈 Overview","🛡 Shield Detail","🔩 Bolt-Up Detail","📋 Shift Handover"])

    with tab1:
        ov=pd.DataFrame({"Phase":["Pre-Install Checklist","Pre-Install Components","Bolt-Up","Recovery","Install"],
                         "Complete %":[pre_pct(),pre_comp_pct(),bolt_pct(),rec_pct(),inst_pct()]})
        fig=px.bar(ov,x="Phase",y="Complete %",color="Complete %",text="Complete %",
                   color_continuous_scale=[[0,"#ef4444"],[.5,"#f59e0b"],[1,"#22c55e"]],
                   title=f"{MINE} — Phase Completion Overview")
        fig.update_traces(texttemplate="%{text:.1f}%",textposition="outside")
        fig.update_layout(height=360,plot_bgcolor="#161b22",paper_bgcolor="#0d1117",
                          font=dict(color="#e6edf3"),coloraxis_showscale=False,
                          yaxis=dict(range=[0,110],gridcolor="#21262d"),xaxis=dict(gridcolor="#21262d"))
        st.plotly_chart(fig,use_container_width=True)
        st.download_button("⬇ Download Overview CSV",ov.to_csv(index=False),"overview.csv","text/csv")

    with tab2:
        view=st.radio("View",["Install","Recovery"],horizontal=True)
        d=st.session_state.inst_shields if view=="Install" else st.session_state.rec_shields
        clrs_m=INSTALL_COLORS if view=="Install" else RECOVERY_COLORS
        sh_df=pd.DataFrame([{"Shield #":i,"Status":d[i],"Pan Type":PAN_TYPES.get(i,"Standard"),
                              "Team Zone":next(t["name"] for t in BOLT_TEAMS if t["range"][0]<=i<=t["range"][1])}
                             for i in range(1,204)])
        fl=st.multiselect("Filter status",options=list(clrs_m.keys()),default=list(clrs_m.keys()))
        st.dataframe(sh_df[sh_df["Status"].isin(fl)],use_container_width=True,hide_index=True,height=460)
        st.download_button(f"⬇ Download Shield {view} CSV",sh_df.to_csv(index=False),f"shields_{view.lower()}.csv","text/csv")

    with tab3:
        bu_rows=[]
        for t in BOLT_TEAMS:
            tid=t["id"]
            sw={"Not Started":0,"In Progress":.5,"Complete":1.,"Signed Off":1.}
            wt=sum(BOLT_ROW_WEIGHTS.values()); got=0
            row={"Team":t["name"],"Range":f"#{t['range'][0]}–{t['range'][1]}","Outlet":t["outlet"]}
            for r in BOLT_ROW_LABELS:
                row[r]=st.session_state.bolt[tid][r]
                got+=BOLT_ROW_WEIGHTS.get(r,10)*sw.get(st.session_state.bolt[tid][r],0)
            row["% Complete"]=f"{round(got/wt*100,1)}%"
            bu_rows.append(row)
        bu_df=pd.DataFrame(bu_rows)
        st.dataframe(bu_df,use_container_width=True,hide_index=True)
        st.download_button("⬇ Download Bolt-Up CSV",bu_df.to_csv(index=False),"bolt_up.csv","text/csv")

    with tab4:
        st.markdown('<div class="pill">Shift Handover Report Generator</div>', unsafe_allow_html=True)
        shift_t = st.selectbox("Shift",["Day Shift (06:00–18:00)","Night Shift (18:00–06:00)"])
        erzc    = st.text_input("ERZ Controller Name")
        notes   = st.text_area("Additional Notes / Incidents", height=70)
        if st.button("📄 Generate Shift Handover", type="primary"):
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            handover = (
                f"MOS – LWMove | SHIFT HANDOVER REPORT\n"
                f"{MINE} · {MOVE_FROM} Recovery → {MOVE_TO} Install · {MOVE_TYPE}\n"
                f"Generated: {now} | Shift: {shift_t} | ERZC: {erzc or 'Not recorded'}\n\n"
                f"{'═'*60}\nLIVE PROGRESS SNAPSHOT\n{'═'*60}\n"
                f"Pre-Install Checklist:  {pre_pct()}%\n"
                f"Pre-Install Components: {pre_comp_pct()}%\n"
                f"Bolt-Up:                {bolt_pct()}%\n"
                f"Recovery:               {rec_pct()}%\n"
                f"Install:                {inst_pct()}%\n\n"
                f"Shields Installed:  {cnt(st.session_state.inst_shields,['Installed','Commissioned'])}/{NUM_SHIELDS}\n"
                f"Shields Recovered:  {cnt(st.session_state.rec_shields,'Recovered')}/{NUM_SHIELDS}\n"
                f"AFC Pans Installed: {cnt(st.session_state.inst_pans,['Installed','Commissioned'])}/{NUM_PANS}\n"
                f"AFC Pans Recovered: {cnt(st.session_state.rec_pans,'Recovered')}/{NUM_PANS}\n"
                f"BSL Installed:      {cnt(st.session_state.inst_bsl,['Installed','Commissioned'])}/{len(BSL_ITEMS)}\n\n"
                f"MG Drive:  {st.session_state.inst_mg}  |  TG Drive: {st.session_state.inst_tg}  |  Shearer: {st.session_state.inst_shearer}\n"
                f"FRM0049 Row 7 Grouting: {'✅ SIGNED OFF' if st.session_state.frm0049_r7 else '⚠ OUTSTANDING'}\n"
                f"FRM0049 Row 8 Grouting: {'✅ SIGNED OFF' if st.session_state.frm0049_r8 else '⚠ OUTSTANDING'}\n\n"
                f"{'═'*60}\nBOLT-UP TEAM STATUS\n{'═'*60}\n"
            ) + "\n".join(
                f"  {t['name']} (#{t['range'][0]}–{t['range'][1]}): " +
                " | ".join(f"{r[:6]}: {st.session_state.bolt[t['id']][r]}" for r in BOLT_ROW_LABELS)
                for t in BOLT_TEAMS
            ) + (
                f"\n\n{'═'*60}\nADDITIONAL NOTES\n{'═'*60}\n{notes or 'Nil'}\n\n"
                f"{'═'*60}\nACTIVITY LOG (last 10 events)\n{'═'*60}\n"
            ) + "\n".join(
                f"  [{e['Time']}] {e['Event']}"
                for e in st.session_state.log[-10:][::-1]
            ) + "\n\nEND OF HANDOVER REPORT"
            st.text_area("Handover Report",handover,height=480)
            st.download_button("⬇ Download Handover TXT",handover,
                               f"handover_{datetime.now().strftime('%Y%m%d_%H%M')}.txt","text/plain")

# ── DATA INPUT ────────────────────────────────────────────────────────
elif page == "📥  Data Input":
    st.title("Data Input")
    tab_up,tab_man,tab_log = st.tabs(["📂 Upload Spreadsheet","✏️ Manual Edit","📝 Shift Log"])

    with tab_up:
        st.dataframe(pd.DataFrame({
            "File Type":["Bolt-Up Handout","Shield Status","AFC Pan Log","Daily Progress"],
            "Key Columns":["Team, Shields, Hose Outlet, Progress_%, Last_Row_Completed",
                           "Shield #, Status, Team Zone, Timestamp",
                           "Pan #, Pan Type, Status, Notes",
                           "Date, Phase, Items Complete, Total, %"],
        }),use_container_width=True,hide_index=True)
        file = st.file_uploader("Upload (.xlsx / .csv)",type=["xlsx","csv","xls"])
        if file:
            try:
                df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
                st.success(f"✅ Loaded: **{file.name}** — {len(df)} rows × {len(df.columns)} columns")
                st.dataframe(df,use_container_width=True)
                log_event(f"File uploaded: {file.name} ({len(df)} rows)")
            except Exception as e:
                st.error(f"Could not parse file: {e}")

    with tab_man:
        target = st.selectbox("Edit dataset",["Bolt-Up Teams","BSL Install","BSL Recovery",
                                               "Shield Install (range)","Shield Recovery (range)"])
        if target == "Bolt-Up Teams":
            bu=pd.DataFrame([{"Team":t["name"],**{r:st.session_state.bolt[t["id"]][r] for r in BOLT_ROW_LABELS}} for t in BOLT_TEAMS])
            ed=st.data_editor(bu,num_rows="fixed",use_container_width=True,
                              column_config={r:st.column_config.SelectboxColumn(r,options=BOLT_ROW_STATUSES) for r in BOLT_ROW_LABELS},
                              key="bolt_ed")
            if st.button("💾 Save",type="primary"):
                for i,t in enumerate(BOLT_TEAMS):
                    for r in BOLT_ROW_LABELS: st.session_state.bolt[t["id"]][r]=ed.iloc[i][r]
                log_event("Manual edit: Bolt-Up saved"); st.success("Saved."); st.rerun()
        elif target == "BSL Install":
            bdf=pd.DataFrame([{"Component":k,"Status":v} for k,v in st.session_state.inst_bsl.items()])
            ed=st.data_editor(bdf,num_rows="fixed",use_container_width=True,
                              column_config={"Status":st.column_config.SelectboxColumn("Status",options=INSTALL_STATUSES)},key="bsl_i_ed")
            if st.button("💾 Save",type="primary",key="bsl_i_save"):
                for _,r in ed.iterrows(): st.session_state.inst_bsl[r["Component"]]=r["Status"]
                log_event("Manual edit: BSL Install saved"); st.success("Saved."); st.rerun()
        elif target == "BSL Recovery":
            bdf=pd.DataFrame([{"Component":k,"Status":v} for k,v in st.session_state.rec_bsl.items()])
            ed=st.data_editor(bdf,num_rows="fixed",use_container_width=True,
                              column_config={"Status":st.column_config.SelectboxColumn("Status",options=RECOVERY_STATUSES)},key="bsl_r_ed")
            if st.button("💾 Save",type="primary",key="bsl_r_save"):
                for _,r in ed.iterrows(): st.session_state.rec_bsl[r["Component"]]=r["Status"]
                log_event("Manual edit: BSL Recovery saved"); st.success("Saved."); st.rerun()
        elif target == "Shield Install (range)":
            c1,c2=st.columns(2)
            with c1: lo,hi=st.slider("Shield range",1,203,(1,30))
            with c2: nst=st.selectbox("New status",INSTALL_STATUSES)
            st.markdown(f"Sets **{hi-lo+1}** shields ({lo}–{hi}) → **{nst}**")
            if st.button("Apply",type="primary"):
                for i in range(lo,hi+1): st.session_state.inst_shields[i]=nst
                log_event(f"Manual: Shields {lo}–{hi} install → {nst}"); st.success("Applied."); st.rerun()
        elif target == "Shield Recovery (range)":
            c1,c2=st.columns(2)
            with c1: lo,hi=st.slider("Shield range",1,203,(1,30))
            with c2: nst=st.selectbox("New status",RECOVERY_STATUSES)
            if st.button("Apply",type="primary"):
                for i in range(lo,hi+1): st.session_state.rec_shields[i]=nst
                log_event(f"Manual: Shields {lo}–{hi} recovery → {nst}"); st.success("Applied."); st.rerun()

    with tab_log:
        with st.form("log_form"):
            entry=st.text_area("Manual log entry",height=70,
                               placeholder="e.g. Day shift: Shields 1–45 installed. No issues.")
            if st.form_submit_button("Add Entry",type="primary") and entry.strip():
                log_event(f"[Manual] {entry.strip()}"); st.rerun()
        st.divider()
        if st.session_state.log:
            ldf=pd.DataFrame(st.session_state.log[::-1])
            st.dataframe(ldf,use_container_width=True,hide_index=True,height=420)
            st.download_button("⬇ Download Log CSV",ldf.to_csv(index=False),"activity_log.csv","text/csv")
        else:
            st.info("No log entries yet — all app updates are auto-recorded here.")
