import streamlit as st
import pandas as pd
import numpy as np
import pyodbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dotenv import load_dotenv
from pathlib import Path
import base64
import os
import warnings
warnings.filterwarnings('ignore')

# ── ENV ───────────────────────────────────────────────────────────────────────
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# ── LOGO — use local file if downloaded, else Wikipedia URL ──────────────────
LOGO_PATH = Path(__file__).parent / "wc26_logo1.png"
if LOGO_PATH.exists():
    with open(LOGO_PATH, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()
    WC_LOGO_IMG = f"data:image/png;base64,{logo_b64}"
else:
    WC_LOGO_IMG = "https://upload.wikimedia.org/wikipedia/en/thumb/3/35/2026_FIFA_World_Cup.svg/400px-2026_FIFA_World_Cup.svg.png"

WC_LOGO_URL = "https://upload.wikimedia.org/wikipedia/en/thumb/3/35/2026_FIFA_World_Cup.svg/400px-2026_FIFA_World_Cup.svg.png"

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FIFA World Cup 2026 | Analytics",
    page_icon=WC_LOGO_IMG,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── DESIGN TOKENS — Electric Blue Glassmorphism (UNCHANGED) ──────────────────
BG        = "#06080f"
BG2       = "#080b14"
BLUE_DARK = "#003eb3"
BLUE_MID  = "#0070d4"
BLUE_LIT  = "#00b4ff"
BLUE_PALE = "#60d4ff"
GLASS     = "rgba(0,80,200,0.18)"
GLASS2    = "rgba(0,50,140,0.12)"
BORDER    = "rgba(0,160,255,0.2)"
BORDER2   = "rgba(0,160,255,0.1)"
WHITE     = "#ffffff"
WHITE60   = "rgba(255,255,255,0.6)"
WHITE30   = "rgba(255,255,255,0.3)"
WHITE10   = "rgba(255,255,255,0.07)"
GREEN     = "#00e676"
RED       = "#ff4560"
GOLD      = "#ffd600"


# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Hide Streamlit chrome ── */
#MainMenu {{ display: none !important; }}
footer {{ display: none !important; }}
header {{ display: none !important; }}
[data-testid="collapsedControl"] {{ display: none !important; }}
section[data-testid="stSidebar"] {{ display: none !important; }}
.block-container {{ padding-top: 0 !important; max-width: 100% !important; padding-left: 0 !important; padding-right: 0 !important; margin-top: 0 !important; }}

/* ── Kill Streamlit top spacing ── */
.stMainBlockContainer {{
    padding-top: 0 !important;
    margin-top: 0 !important;
}}
div[data-testid="stVerticalBlock"] > div:first-child {{
    margin-top: 0 !important;
    padding-top: 0 !important;
}}           

/* ── Remove gap between navbar and page content ── */
.stApp > div > div > div > div > div[data-testid="stVerticalBlock"] {{
    gap: 0 !important;
    padding-top: 0 !important;
}}
iframe {{ display: block; }}
div[data-testid="stVerticalBlockBorderWrapper"] {{
    padding-top: 0 !important;
    margin-top: 0 !important;
}}            

/* ── Base ── */
html, body, .stApp {{
    background-color: {BG} !important;
    color: {WHITE} !important;
    font-family: 'Inter', sans-serif !important;
}}


/* ── NAVBAR ── */
.navbar {{
    position: sticky;
    top: 0;
    z-index: 999;
    display: flex;
    align-items: center;
    padding: 0 20px;
    height: 60px;
    background: linear-gradient(90deg, rgba(0,50,160,0.92) 0%, rgba(0,20,60,0.88) 100%);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid {BORDER};
    gap: 0;
}}
.navbar-brand {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-right: 32px;
    flex-shrink: 0;
}}
.navbar-brand img {{
    width: 38px;
    height: 38px;
    object-fit: contain;
}}
.navbar-brand-text {{
    font-family: 'Bebas Neue', sans-serif;
    font-size: 16px;
    letter-spacing: 2.5px;
    color: {WHITE};
    line-height: 1.15;
}}
.navbar-brand-sub {{
    font-size: 8px;
    color: {WHITE30};
    letter-spacing: 2px;
    text-transform: uppercase;
}}
.navbar-right {{
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 18px;
    flex-shrink: 0;
}}
.live-badge {{
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 10px;
    color: {BLUE_LIT};
    letter-spacing: 1.5px;
    font-weight: 500;
}}
.live-dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: {BLUE_LIT};
    box-shadow: 0 0 8px {BLUE_LIT};
    animation: blink 2s infinite;
}}
@keyframes blink {{
    0%,100% {{ opacity:1; box-shadow: 0 0 8px {BLUE_LIT}; }}
    50% {{ opacity:0.35; box-shadow: 0 0 3px {BLUE_LIT}; }}
}}
.navbar-stat {{
    font-size: 11px;
    color: {WHITE30};
}}
.navbar-stat b {{ color: {WHITE}; font-weight: 600; }}
.navbar-built {{
    font-size: 10px;
    color: {WHITE30};
}}
.navbar-built span {{ color: {BLUE_LIT}; font-weight: 600; }}

/* ── Nav buttons row ── */
.nav-row {{
    background: linear-gradient(90deg, rgba(0,40,140,0.82) 0%, rgba(0,15,50,0.78) 100%);
    border-bottom: 1px solid {BORDER2};
    padding: 6px 20px;
    display: flex;
    gap: 4px;
}}

/* Reduce top spacing below nav */
.block-container {{
    padding-top: 0.8rem !important;
}}

/* Reduce title margin */
h1 {{
    margin-top: 0 !important;
    padding-top: 0 !important;
}}

/* ── Page content padding ── */
.page-wrap {{
    padding: 0 28px 40px 28px;
    margin-top: -32px;
    position: relative;
    z-index: 1;
}}

/* ── Metric cards ── */
[data-testid="metric-container"] {{
    background: linear-gradient(135deg, {GLASS}, {GLASS2}) !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    padding: 16px !important;
    backdrop-filter: blur(14px) !important;
}}

/* LABEL */
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] *,
[data-testid="stMetricLabel"] p {{
    color: {WHITE} !important;
    fill: {WHITE} !important;
    opacity: 1 !important;
}}

/* VALUE */
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {{
    color: {BLUE_LIT} !important;
}}

/* DELTA */
[data-testid="stMetricDelta"],
[data-testid="stMetricDelta"] * {{
    color: {WHITE} !important;
}}

/* ── Tabs (UNCHANGED) ── */
.stTabs [data-baseweb="tab-list"] {{
    background: {GLASS2} !important;
    border: 1px solid {BORDER2} !important;
    border-radius: 8px !important;
    padding: 4px !important;
    gap: 4px !important;
}}
.stTabs [data-baseweb="tab"] {{
    color: {WHITE30} !important;
    border-radius: 6px !important;
    font-size: 12px !important;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {GLASS}, {GLASS2}) !important;
    color: {BLUE_LIT} !important;
    border: 1px solid {BORDER} !important;
}}

/* Plotly chart titles, subtitles, axis, legends */
.stPlotlyChart text {{
    fill: {WHITE} !important;
}}

.stPlotlyChart .gtitle,
.stPlotlyChart .xtitle,
.stPlotlyChart .ytitle {{
    fill: {WHITE} !important;
}}

.stPlotlyChart .legendtext {{
    fill: {WHITE} !important;
}}

/* Radio section alignment */
[data-testid="stRadio"] {{
    padding-left: 0 !important;
}}

/* Push only options slightly right */
[data-testid="stRadio"] div[role="radiogroup"] {{
    margin-left: 24px  !important;
    gap: 18px !important;
}}

/* Keep heading aligned */
[data-testid="stRadio"] [data-testid="stWidgetLabel"] {{
    color: {WHITE} !important;
    padding-left: 0 !important;
    margin-bottom: 6px !important;
}}
/* Shift only radio heading */
[data-testid="stRadio"] [data-testid="stWidgetLabel"] {{
    padding-left: 18px !important;
    margin-bottom: 6px !important;
    color: {WHITE} !important;
}}

/* Widget headings (dropdown, sliders, inputs etc.) */
[data-testid="stWidgetLabel"] {{
    color: {WHITE} !important;
    padding-left: 16px !important;   /* align with other content */
}}

[data-testid="stWidgetLabel"] p {{
    color: {WHITE} !important;
    margin-left: 0 !important;
}}

/* Align actual dropdown container */
div[data-baseweb="select"] {{
    margin-left: 20px !important;
    margin-right: 20px !important;
}}

/* Keep dropdown text white */
div[data-baseweb="select"] * {{
    color: {WHITE} !important;
}}

/* ── Selectbox (UNCHANGED) ── */
.stSelectbox > div > div {{
    background: {GLASS2} !important;
    border: 1px solid {BORDER} !important;
    color: {WHITE} !important;
    border-radius: 8px !important;
}}
.stRadio > div {{ gap: 8px !important; }}
.stRadio label {{ color: {WHITE60} !important; font-size: 13px !important; }}

/* ── Progress (UNCHANGED) ── */
.stProgress > div > div {{
    background: rgba(255,255,255,0.06) !important;
    border-radius: 4px !important;
}}
.stProgress > div > div > div {{
    background: linear-gradient(90deg, {BLUE_DARK}, {BLUE_LIT}) !important;
    border-radius: 4px !important;
}}

hr {{ border-color: {BORDER2} !important; margin: 16px 0 !important; }}

/* ── Custom classes (ALL UNCHANGED) ── */
.sec-label {{
    font-size: 9px;
    color: rgba(0,180,255,0.55);
    letter-spacing: 2.5px;
    text-transform: uppercase;
    margin-bottom: 8px;
    font-family: 'Inter', sans-serif;
}}
.page-title {{
    font-family: 'Bebas Neue', sans-serif;
    font-size: 36px;
    letter-spacing: 3px;
    color: {WHITE};
    line-height: 1;
    margin-bottom: 4px;
    padding-left: 28px;
}}
.page-sub {{
    font-size: 11px;
    color: {WHITE30};
    letter-spacing: 1px;
    margin-bottom: 16px;
     padding-left: 28px;
}}
.match-card {{
    background: linear-gradient(135deg, rgba(0,70,200,0.2), rgba(0,30,90,0.12));
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
}}
.match-card-plain {{
    background: rgba(255,255,255,0.035);
    border: 1px solid {BORDER2};
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
}}
.match-score {{
    font-family: 'Bebas Neue', sans-serif;
    font-size: 28px;
    color: {WHITE};
    text-align: center;
    line-height: 1;
}}
.match-team {{
    font-size: 13px;
    font-weight: 600;
    color: {WHITE};
    letter-spacing: 0.5px;
}}
.match-meta {{
    font-size: 10px;
    color: {WHITE30};
    letter-spacing: 1px;
    text-transform: uppercase;
}}
.badge {{ display:inline-block; font-size:8px; padding:2px 7px; border-radius:8px; font-weight:600; letter-spacing:0.5px; margin-top:3px; }}
.badge-win {{ background:rgba(0,140,255,0.18); color:{BLUE_LIT}; border:1px solid rgba(0,140,255,0.3); }}
.badge-draw {{ background:rgba(255,255,255,0.07); color:{WHITE}; border:1px solid rgba(255,255,255,0.2); }}
.badge-away {{ background:rgba(0,60,180,0.2); color:{BLUE_PALE}; border:1px solid rgba(0,100,220,0.3); }}
.badge-upset {{ background:rgba(255,214,0,0.15); color:{GOLD}; border:1px solid rgba(255,214,0,0.3); }}
.form-w {{ display:inline-flex;width:22px;height:22px;border-radius:50%;background:{GREEN};color:#000;align-items:center;justify-content:center;font-size:10px;font-weight:700;margin:2px; }}
.form-d {{ display:inline-flex;width:22px;height:22px;border-radius:50%;background:rgba(255,255,255,0.2);color:{WHITE};align-items:center;justify-content:center;font-size:10px;font-weight:700;margin:2px; }}
.form-l {{ display:inline-flex;width:22px;height:22px;border-radius:50%;background:{RED};color:{WHITE};align-items:center;justify-content:center;font-size:10px;font-weight:700;margin:2px; }}
.stat-card {{
    background: linear-gradient(135deg, rgba(0,70,200,0.22), rgba(0,30,90,0.14));
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 12px 14px;
    text-align: center;
}}
.stat-val {{ font-size: 22px; font-weight: 700; color: {WHITE}; }}
.stat-accent {{ color: {BLUE_LIT}; }}
.stat-lbl {{ font-size: 9px; color: {WHITE30}; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 3px; }}
.accent-line {{ height: 2px; border-radius: 2px; background: linear-gradient(90deg, {BLUE_DARK}, {BLUE_MID}, {BLUE_LIT}); margin-top: 12px; }}
.podium-gold {{
    background: linear-gradient(135deg, rgba(0,80,200,0.3), rgba(0,40,120,0.2));
    border: 1px solid {BLUE_LIT};
    border-radius: 12px; padding: 20px; text-align: center;
}}
.podium-silver {{
    background: rgba(255,255,255,0.04);
    border: 1px solid {BORDER};
    border-radius: 12px; padding: 20px; text-align: center; margin-top: 24px;
}}
.podium-name {{ font-family:'Bebas Neue',sans-serif; font-size:20px; letter-spacing:2px; color:{WHITE}; margin-top:8px; }}
.podium-prob {{ font-size:22px; font-weight:700; color:{BLUE_LIT}; margin-top:6px; }}
.podium-sub {{ font-size:10px; color:{WHITE30}; }}

/* ── Standings custom rows ── */
.s-row {{
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 9px 12px;
    border-radius: 7px;
    margin-bottom: 4px;
    border-left: 3px solid transparent;
}}
.s-row-1 {{
    background: linear-gradient(90deg, rgba(0,130,255,0.22), rgba(0,80,200,0.10));
    border-left-color: {BLUE_LIT};
}}
.s-row-2 {{
    background: linear-gradient(90deg, rgba(0,100,200,0.16), rgba(0,60,160,0.08));
    border-left-color: {BLUE_MID};
}}
.s-row-3 {{
    background: linear-gradient(90deg, rgba(0,62,179,0.12), rgba(0,40,120,0.06));
    border-left-color: {BLUE_DARK};
}}
.s-row-4 {{
    background: rgba(255,255,255,0.03);
    border-left-color: rgba(255,255,255,0.12);
}}
.s-pos {{ width:16px; font-size:11px; font-weight:700; flex-shrink:0; }}
.s-team {{ flex:1; font-size:12px; font-weight:600; color:{WHITE}; }}
.s-stat {{ width:26px; text-align:center; font-size:11px; color:{WHITE60}; flex-shrink:0; }}
.s-pts {{ width:28px; text-align:center; font-size:13px; font-weight:700; flex-shrink:0; }}
.s-adv {{ width:14px; text-align:center; font-size:10px; flex-shrink:0; }}
.s-header {{
    display:flex; align-items:center; gap:6px;
    padding:3px 12px 6px 12px;
}}
.s-header-lbl {{ font-size:8px; color:{WHITE30}; letter-spacing:1.5px; text-transform:uppercase; }}
</style>
""", unsafe_allow_html=True)

# ── WC26 logo background watermark ──────────────────────────────────────────
st.markdown(f"""
<div style="
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 420px;
    height: 420px;
    background-image: url('{WC_LOGO_IMG}');
    background-repeat: no-repeat;
    background-size: contain;
    background-position: center;
    opacity: 0.08;
    pointer-events: none;
    z-index: 0;
"></div>
""", unsafe_allow_html=True)

# ── PLOTLY THEME (UNCHANGED) ──────────────────────────────────────────────────
PLOT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color=WHITE, size=12),
    title_font=dict(family="Bebas Neue", size=18, color=WHITE),
    xaxis=dict(gridcolor="rgba(0,160,255,0.08)", zerolinecolor="rgba(0,160,255,0.1)", color=WHITE30, showgrid=True),
    yaxis=dict(gridcolor="rgba(0,160,255,0.08)", zerolinecolor="rgba(0,160,255,0.1)", color=WHITE30, showgrid=True),
    margin=dict(l=20, r=20, t=46, b=20),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=WHITE60)),
)
BLUE_SCALE = [[0, "#1a3a8f"], [0.5, BLUE_MID], [1.0, BLUE_LIT]]

# ── CONNECTION (UNCHANGED) ────────────────────────────────────────────────────
def get_connection():
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')},1433;"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_USERNAME')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;",
        autocommit=True
    )

# ── DATA (UNCHANGED) ──────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_matches():
    conn = get_connection()
    return pd.read_sql("""
        SELECT m.match_id, m.match_date, m.stage, m.group_name,
               t1.team_name as home_team, t1.fifa_code as home_code,
               m.home_score, m.away_score,
               t2.team_name as away_team, t2.fifa_code as away_code
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.team_id
        JOIN teams t2 ON m.away_team_id = t2.team_id
        WHERE m.home_score IS NOT NULL ORDER BY m.match_date DESC
    """, conn)

@st.cache_data(ttl=300)
def load_teams():
    return pd.read_sql("SELECT * FROM teams", get_connection())

@st.cache_data(ttl=300)
def load_predictions():
    return pd.read_sql("SELECT * FROM predictions ORDER BY win_probability DESC", get_connection())

FIFA_RANKINGS = {
    'France':2,'Spain':3,'England':4,'Brazil':5,'Portugal':6,
    'Netherlands':7,'Argentina':8,'Belgium':9,'Germany':10,'Morocco':13,
    'United States':14,'Mexico':15,'Switzerland':16,'Croatia':17,'Uruguay':18,
    'Colombia':19,'Japan':20,'Ecuador':21,'Senegal':22,'Sweden':23,
    'South Korea':24,'Turkey':25,'Australia':26,'Canada':27,'Saudi Arabia':28,
    'Egypt':31,'Austria':32,'South Africa':64,'Ghana':54,'Tunisia':30,
    'Ivory Coast':48,'Norway':34,'Scotland':38,'Czechia':40,'Iran':20,
    'Qatar':35,'Bosnia-Herzegovina':55,'Paraguay':58,'Algeria':42,
    'New Zealand':100,'Jordan':87,'Iraq':63,'Uzbekistan':50,'Congo DR':56,
    'Cape Verde Islands':80,'Haiti':83,'Curaçao':85,'Panama':70
}

def calc_standings(df):
    rows = {}
    for _, m in df.iterrows():
        home, away = m['home_team'], m['away_team']
        hg, ag = int(m['home_score']), int(m['away_score'])
        group = m['group_name'].replace('GROUP_', '')
        for team, gf, ga in [(home, hg, ag), (away, ag, hg)]:
            if team not in rows:
                rows[team] = dict(Team=team, Group=group, P=0, W=0, D=0, L=0, GF=0, GA=0, GD=0, Pts=0)
            r = rows[team]
            r['P']+=1; r['GF']+=gf; r['GA']+=ga; r['GD']+=gf-ga
            if gf>ga:    r['W']+=1; r['Pts']+=3
            elif gf==ga: r['D']+=1; r['Pts']+=1
            else:        r['L']+=1
    return pd.DataFrame(rows.values()).sort_values(
        ['Group','Pts','GD','GF'], ascending=[True,False,False,False])

def match_result_label(row):
    if row['home_score'] > row['away_score']: return 'home'
    elif row['away_score'] > row['home_score']: return 'away'
    return 'draw'

# ── STANDINGS HELPERS ─────────────────────────────────────────────────────────
def render_standings_header():
    st.markdown(f"""<div class="s-header">
        <div style="width:16px"></div>
        <div class="s-header-lbl" style="flex:1">Team</div>
        <div class="s-header-lbl" style="width:26px;text-align:center">P</div>
        <div class="s-header-lbl" style="width:26px;text-align:center">W</div>
        <div class="s-header-lbl" style="width:26px;text-align:center">D</div>
        <div class="s-header-lbl" style="width:26px;text-align:center">L</div>
        <div class="s-header-lbl" style="width:26px;text-align:center">GF</div>
        <div class="s-header-lbl" style="width:26px;text-align:center">GA</div>
        <div class="s-header-lbl" style="width:26px;text-align:center">GD</div>
        <div class="s-header-lbl" style="width:28px;text-align:center;color:{BLUE_LIT}">PTS</div>
        <div style="width:14px"></div>
    </div>""", unsafe_allow_html=True)

def render_standings_table(gdf, highlight_team=None):
    for idx, (_, row) in enumerate(gdf.iterrows()):
        pos = idx + 1
        if pos == 1:
            row_cls = "s-row s-row-1"
            pos_col = BLUE_LIT
            pts_col = BLUE_LIT
            adv = "✓"; adv_col = GREEN
        elif pos == 2:
            row_cls = "s-row s-row-2"
            pos_col = BLUE_MID
            pts_col = BLUE_MID
            adv = "✓"; adv_col = GREEN
        elif pos == 3:
            row_cls = "s-row s-row-3"
            pos_col = BLUE_DARK
            pts_col = WHITE
            adv = "?"; adv_col = GOLD
        else:
            row_cls = "s-row s-row-4"
            pos_col = WHITE30
            pts_col = WHITE
            adv = ""; adv_col = WHITE30

        hl_outline = f"outline:1px solid {BLUE_LIT};" if highlight_team and row['Team']==highlight_team else ""
        gd_str = f"+{int(row['GD'])}" if row['GD']>=0 else str(int(row['GD']))

        st.markdown(f"""<div class="{row_cls}" style="{hl_outline}">
            <div class="s-pos" style="color:{pos_col}">{pos}</div>
            <div class="s-team">{row['Team']}</div>
            <div class="s-stat">{int(row['P'])}</div>
            <div class="s-stat">{int(row['W'])}</div>
            <div class="s-stat">{int(row['D'])}</div>
            <div class="s-stat">{int(row['L'])}</div>
            <div class="s-stat">{int(row['GF'])}</div>
            <div class="s-stat">{int(row['GA'])}</div>
            <div class="s-stat">{gd_str}</div>
            <div class="s-pts" style="color:{pts_col}">{int(row['Pts'])}</div>
            <div class="s-adv" style="color:{adv_col}">{adv}</div>
        </div>""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
matches_df   = load_matches()
teams_df     = load_teams()
pred_df      = load_predictions()
standings_df = calc_standings(matches_df)

matches_df['match_date']  = pd.to_datetime(matches_df['match_date'])
matches_df['group_short'] = matches_df['group_name'].str.replace('GROUP_','')
matches_df['total_goals'] = matches_df['home_score'] + matches_df['away_score']
matches_df['result_type'] = matches_df.apply(match_result_label, axis=1)

total_goals = int(matches_df['total_goals'].sum())
avg_goals   = round(total_goals / len(matches_df), 2)
home_wins   = int((matches_df['result_type']=='home').sum())
away_wins   = int((matches_df['result_type']=='away').sum())
draws       = int((matches_df['result_type']=='draw').sum())
n_matches   = len(matches_df)

# ── NAVBAR ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="navbar">
  <div class="navbar-brand">
    <img src="{WC_LOGO_IMG}" alt="WC26 Logo"/>
    <div>
      <div class="navbar-brand-text">FIFA WC 2026</div>
      <div class="navbar-brand-sub">Live Analytics</div>
    </div>
  </div>
  <div class="navbar-right">
    <div class="live-badge"><div class="live-dot"></div>LIVE</div>
    <div class="navbar-stat"><b>{n_matches}</b> matches</div>
    <div class="navbar-stat"><b>{total_goals}</b> goals</div>
    <div class="navbar-stat"><b>{avg_goals}</b> avg/match</div>
    <div class="navbar-stat">{pd.Timestamp.now().strftime('%d %b · %H:%M')}</div>
    <div class="navbar-built">by <span>Sahil Bhure</span> · Warwick</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── NAVIGATION BUTTONS ────────────────────────────────────────────────────────
PAGES = [
    "🏠  Overview",
    "📊  Group Standings",
    "⚽  Match Results",
    "🔍  Team Deep Dive",
    "📈  Tournament Trends",
    "🏆  Predictions",
]

if "page" not in st.session_state:
    st.session_state.page = PAGES[0]

# Render nav as Streamlit buttons inside a styled container
st.markdown('<div class="nav-row">', unsafe_allow_html=True)
nav_cols = st.columns(len(PAGES))
for i, p in enumerate(PAGES):
    with nav_cols[i]:
        is_active = st.session_state.page == p
        btn_style = f"""
            background: {'linear-gradient(135deg,'+GLASS+','+GLASS2+')' if is_active else 'transparent'} !important;
            border: {'1px solid '+BORDER if is_active else 'none'} !important;
            color: {BLUE_LIT if is_active else WHITE30} !important;
            border-radius: 6px !important;
            font-size: 11px !important;
            font-weight: {'600' if is_active else '400'} !important;
            padding: 5px 8px !important;
            width: 100% !important;
            cursor: pointer !important;
            letter-spacing: 0.3px !important;
        """
        if st.button(p, key=f"nav_{i}", use_container_width=True):
            st.session_state.page = p
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Style the nav buttons
st.markdown(f"""
<style>
div[data-testid="stHorizontalBlock"] {{
    gap: 4px !important;
    padding: 0 !important;
    margin: 0 !important;
    background: linear-gradient(90deg, rgba(0,40,140,0.82), rgba(0,15,50,0.78)) !important;
    border-bottom: 1px solid {BORDER2} !important;
    padding: 6px 20px !important;
}}
div[data-testid="stHorizontalBlock"] > div {{
    flex: 1 !important;
}}
div[data-testid="stHorizontalBlock"] button {{
    background: transparent !important;
    border: none !important;
    color: {WHITE30} !important;
    font-size: 11px !important;
    padding: 5px 6px !important;
    border-radius: 6px !important;
    width: 100% !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: 0.3px !important;
    transition: all 0.15s !important;
}}
div[data-testid="stHorizontalBlock"] button:hover {{
    background: {GLASS} !important;
    color: {WHITE} !important;
    border: 1px solid {BORDER2} !important;
}}
div[data-testid="stHorizontalBlock"] button p {{
    color: inherit !important;
    font-size: 11px !important;
}}
</style>
""", unsafe_allow_html=True)

page = st.session_state.page
st.markdown('<div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW (UNCHANGED from original)
# ══════════════════════════════════════════════════════════════════════════════
if "Overview" in page:
    st.markdown('<div class="page-title">FIFA WORLD CUP 2026</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">Live Tournament Analytics · Powered by Azure SQL + Python ML</div>', unsafe_allow_html=True)
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
    st.markdown("")

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Matches Played", n_matches, f"{72-n_matches} remaining")
    c2.metric("Total Goals", total_goals)
    c3.metric("Avg Goals/Match", avg_goals)
    c4.metric("Home Win Rate", f"{round(home_wins/n_matches*100)}%")
    c5.metric("Draw Rate", f"{round(draws/n_matches*100)}%")

    st.markdown("")
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="sec-label">Goals by Group</div>', unsafe_allow_html=True)
        gbg = matches_df.groupby('group_short')['total_goals'].sum().reset_index()
        gbg.columns = ['Group','Goals']
        fig = go.Figure(go.Bar(
            x=gbg['Group'], y=gbg['Goals'],
            marker=dict(color=gbg['Goals'], colorscale=BLUE_SCALE, showscale=False),
            text=gbg['Goals'], textposition='outside',
            textfont=dict(color=WHITE, size=11)
        ))
        fig.update_layout(**PLOT, height=300, title="Goals Scored per Group", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="sec-label">Results Distribution</div>', unsafe_allow_html=True)
        fig2 = go.Figure(go.Pie(
            labels=['Home Win','Away Win','Draw'],
            values=[home_wins, away_wins, draws],
            hole=0.6,
            marker_colors=[BLUE_LIT, BLUE_MID, "rgba(255,255,255,0.15)"],
            textfont=dict(color=WHITE, size=12),
        ))
        fig2.add_annotation(text=f"<b>{n_matches}</b><br><span style='font-size:10px'>matches</span>",
                            x=0.5, y=0.5, showarrow=False,
                            font=dict(color=WHITE, size=14))
        fig2.update_layout(**PLOT, height=300, title="Match Result Distribution")
        fig2.update_layout(legend=dict(orientation='h', y=-0.08))
        st.plotly_chart(fig2, use_container_width=True)

    col_l2, col_r2 = st.columns(2)
    with col_l2:
        st.markdown('<div class="sec-label">Top Scoring Teams</div>', unsafe_allow_html=True)
        hg = matches_df[['home_team','home_score']].rename(columns={'home_team':'team','home_score':'g'})
        ag = matches_df[['away_team','away_score']].rename(columns={'away_team':'team','away_score':'g'})
        top = pd.concat([hg,ag]).groupby('team')['g'].sum().reset_index().sort_values('g').tail(10)
        fig3 = go.Figure(go.Bar(
            x=top['g'], y=top['team'], orientation='h',
            marker=dict(color=top['g'], colorscale=BLUE_SCALE, showscale=False),
            text=top['g'], textposition='outside', textfont=dict(color=WHITE)
        ))
        fig3.update_layout(**PLOT, height=340, title="Top 10 Teams — Goals Scored", showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with col_r2:
        st.markdown('<div class="sec-label">Notable Results</div>', unsafe_allow_html=True)
        hs = matches_df[matches_df['total_goals']>=4].sort_values('total_goals', ascending=False).head(5)
        for _, r in hs.iterrows():
            st.markdown(f"""<div class="match-card">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div class="match-meta">{r['match_date'].strftime('%d %b')} · Group {r['group_short']}</div>
                    <div><span class="badge badge-win">🔥 {int(r['total_goals'])} GOALS</span></div>
                </div>
                <div style="display:flex;align-items:center;margin-top:10px">
                    <div style="flex:1;font-size:14px;font-weight:600;{hw}">{r['home_team']}</div>
                    <div class="match-score" style="width:80px;flex-shrink:0;text-align:center">{int(r['home_score'])} – {int(r['away_score'])}</div>
                    <div style="flex:1;font-size:14px;font-weight:600;text-align:right;{aw}">{r['away_team']}</div>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-label" style="margin-top:12px">Upset Tracker — Away Wins</div>', unsafe_allow_html=True)
    away_w = matches_df[matches_df['result_type']=='away'].copy()
    if len(away_w):
        cols_aw = st.columns(min(len(away_w), 3))
        for i, (_, r) in enumerate(away_w.iterrows()):
            rk_h = FIFA_RANKINGS.get(r['home_team'],90)
            rk_a = FIFA_RANKINGS.get(r['away_team'],90)
            upset = rk_a > rk_h
            with cols_aw[i % 3]:
                st.markdown(f"""<div class="match-card-plain">
                    <div class="match-meta">{r['match_date'].strftime('%d %b')} · Group {r['group_short']}</div>
                    <div style="display:flex;align-items:center;margin-top:10px">
                        <div style="flex:1;font-size:14px;font-weight:600;{hw}">{r['home_team']}</div>
                        <div class="match-score" style="width:80px;flex-shrink:0;text-align:center">{int(r['home_score'])} – {int(r['away_score'])}</div>
                        <div style="flex:1;font-size:14px;font-weight:600;text-align:right;{aw}">{r['away_team']}</div>
                    </div>
                    <div style="margin-top:4px">
                        {'<span class="badge badge-upset">⚡ UPSET · Rank #'+str(rk_a)+' beat #'+str(rk_h)+'</span>' if upset else '<span class="badge badge-away">AWAY WIN</span>'}
                    </div>
                </div>""", unsafe_allow_html=True)
    else:
        st.info("No away wins yet")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — GROUP STANDINGS (NEW custom HTML rows)
# ══════════════════════════════════════════════════════════════════════════════
elif "Standings" in page:
    st.markdown('<div class="page-title">Group Standings</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">Live · Calculated from {n_matches} matches · ✓ = Qualified · ? = Third place contender</div>', unsafe_allow_html=True)
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
    st.markdown("")

    groups = sorted(standings_df['Group'].unique())
    sel = st.selectbox("Select Group", ["All Groups"] + list(groups))

    if sel == "All Groups":
        rows_g = [groups[i:i+3] for i in range(0, len(groups), 3)]
        for row_g in rows_g:
            cols = st.columns(3)
            for ci, grp in enumerate(row_g):
                with cols[ci]:
                    st.markdown(f'<div class="sec-label">Group {grp}</div>', unsafe_allow_html=True)
                    gdf = standings_df[standings_df['Group']==grp].reset_index(drop=True)
                    render_standings_header()
                    render_standings_table(gdf)
                    st.markdown("")
    else:
        cl, cr = st.columns([1,1])
        with cl:
            st.markdown(f'<div class="sec-label">Group {sel}</div>', unsafe_allow_html=True)
            gdf = standings_df[standings_df['Group']==sel].reset_index(drop=True)
            render_standings_header()
            render_standings_table(gdf)
        with cr:
            colors = [BLUE_LIT if i<2 else BLUE_DARK if i==2 else "rgba(255,255,255,0.15)" for i in range(len(gdf))]
            fig = go.Figure(go.Bar(
                x=gdf['Team'], y=gdf['Pts'],
                marker_color=colors,
                text=gdf['Pts'], textposition='outside',
                textfont=dict(color=WHITE)
            ))
            fig.update_layout(**PLOT, height=320, title=f"Group {sel} — Points", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown(f'<div class="sec-label">Group {sel} Results</div>', unsafe_allow_html=True)
        grp_m = matches_df[matches_df['group_short']==sel].sort_values('match_date', ascending=False)
        for _, r in grp_m.iterrows():
            rt = r['result_type']
            badge = '<span class="badge badge-win">HOME WIN</span>' if rt=='home' else \
                    '<span class="badge badge-away">AWAY WIN</span>' if rt=='away' else \
                    '<span class="badge badge-draw">DRAW</span>'
            hw = f"color:{BLUE_LIT};font-weight:700" if rt=='home' else ""
            aw = f"color:{BLUE_LIT};font-weight:700" if rt=='away' else ""
            st.markdown(f"""<div class="match-card-plain">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div class="match-meta">{r['match_date'].strftime('%d %b %Y')}</div>
                    {badge}
                </div>
                <div style="display:flex;align-items:center;justify-content:space-between;margin-top:8px">
                    <div class="match-team" style="{hw}">{r['home_team']}</div>
                    <div class="match-score">{int(r['home_score'])} – {int(r['away_score'])}</div>
                    <div class="match-team" style="text-align:right;{aw}">{r['away_team']}</div>
                </div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — MATCH RESULTS (UNCHANGED)
# ══════════════════════════════════════════════════════════════════════════════
elif "Match Results" in page:
    st.markdown('<div class="page-title">Match Results</div>', unsafe_allow_html=True)
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
    st.markdown("")

    c1, c2, c3 = st.columns(3)
    with c1:
        grp_f = st.selectbox("Group", ["All"] + sorted(matches_df['group_short'].unique()))
    with c2:
        res_f = st.selectbox("Result", ["All","Home Win","Away Win","Draw"])
    with c3:
        sort_f = st.radio("Sort", ["Latest first","Earliest first"], horizontal=True)

    filt = matches_df.copy()
    if grp_f != "All": filt = filt[filt['group_short']==grp_f]
    if res_f == "Home Win": filt = filt[filt['result_type']=='home']
    elif res_f == "Away Win": filt = filt[filt['result_type']=='away']
    elif res_f == "Draw": filt = filt[filt['result_type']=='draw']
    filt = filt.sort_values('match_date', ascending=(sort_f=="Earliest first"))

    st.markdown(f'<div class="sec-label">{len(filt)} matches</div>', unsafe_allow_html=True)
    st.markdown("")

    cols2 = st.columns(2)
    for i, (_, r) in enumerate(filt.iterrows()):
        rt = r['result_type']
        badge = '<span class="badge badge-win">HOME WIN</span>' if rt=='home' else \
                '<span class="badge badge-away">AWAY WIN</span>' if rt=='away' else \
                '<span class="badge badge-draw">DRAW</span>'
        hw = f"color:{BLUE_LIT};font-weight:700" if rt=='home' else f"color:{WHITE}"
        aw = f"color:{BLUE_LIT};font-weight:700" if rt=='away' else f"color:{WHITE}"
        with cols2[i%2]:
            st.markdown(f"""<div class="match-card-plain">
                <div style="display:flex;justify-content:space-between">
                    <div class="match-meta">Group {r['group_short']} · {r['match_date'].strftime('%d %b')}</div>
                    {badge}
                </div>
                <div style="display:flex;align-items:center;justify-content:space-between;margin-top:10px">
                    <div style="font-size:14px;font-weight:600;{hw}">{r['home_team']}</div>
                    <div class="match-score">{int(r['home_score'])} – {int(r['away_score'])}</div>
                    <div style="font-size:14px;font-weight:600;text-align:right;{aw}">{r['away_team']}</div>
                </div>
                <div class="match-meta" style="margin-top:6px">⚽ {int(r['total_goals'])} goals</div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — TEAM DEEP DIVE (standings now use custom HTML)
# ══════════════════════════════════════════════════════════════════════════════
elif "Team" in page:
    st.markdown('<div class="page-title">Team Deep Dive</div>', unsafe_allow_html=True)
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
    st.markdown("")

    all_teams = sorted(set(matches_df['home_team'].tolist() + matches_df['away_team'].tolist()))
    sel_team  = st.selectbox("Select a team", all_teams)

    tm = matches_df[(matches_df['home_team']==sel_team)|(matches_df['away_team']==sel_team)].sort_values('match_date')

    if len(tm) == 0:
        st.info("No matches played yet.")
    else:
        gf_t = sum(int(r['home_score']) if r['home_team']==sel_team else int(r['away_score']) for _,r in tm.iterrows())
        ga_t = sum(int(r['away_score']) if r['home_team']==sel_team else int(r['home_score']) for _,r in tm.iterrows())
        pts  = sum((3 if (r['home_team']==sel_team and r['home_score']>r['away_score']) or
                         (r['away_team']==sel_team and r['away_score']>r['home_score'])
                    else 1 if r['home_score']==r['away_score'] else 0)
                   for _,r in tm.iterrows())
        wins   = sum(1 for _,r in tm.iterrows() if
                     (r['home_team']==sel_team and r['home_score']>r['away_score']) or
                     (r['away_team']==sel_team and r['away_score']>r['home_score']))
        draws_t = sum(1 for _,r in tm.iterrows() if r['home_score']==r['away_score'])
        losses  = len(tm) - wins - draws_t
        rank    = FIFA_RANKINGS.get(sel_team, 90)
        grp     = tm.iloc[0]['group_short']
        gd      = gf_t - ga_t

        c1,c2,c3,c4,c5,c6 = st.columns(6)
        c1.metric("Group", grp)
        c2.metric("FIFA Rank", f"#{rank}")
        c3.metric("Points", pts)
        c4.metric("Goals For", gf_t)
        c5.metric("Goals Against", ga_t)
        c6.metric("GD", f"+{gd}" if gd>=0 else str(gd))

        st.markdown("")
        cl, cr = st.columns(2)

        with cl:
            st.markdown('<div class="sec-label">Form Guide</div>', unsafe_allow_html=True)
            form_html = ""
            for _,r in tm.iterrows():
                is_home = r['home_team']==sel_team
                gf = int(r['home_score']) if is_home else int(r['away_score'])
                ga = int(r['away_score']) if is_home else int(r['home_score'])
                if gf>ga: form_html += '<span class="form-w">W</span>'
                elif gf==ga: form_html += '<span class="form-d">D</span>'
                else: form_html += '<span class="form-l">L</span>'
            st.markdown(form_html, unsafe_allow_html=True)
            st.markdown("")

            st.markdown('<div class="sec-label">Match Log</div>', unsafe_allow_html=True)
            for _,r in tm.sort_values('match_date', ascending=False).iterrows():
                is_home = r['home_team']==sel_team
                gf = int(r['home_score']) if is_home else int(r['away_score'])
                ga = int(r['away_score']) if is_home else int(r['home_score'])
                opp = r['away_team'] if is_home else r['home_team']
                ha  = "HOME" if is_home else "AWAY"
                if gf>ga: rc,rt = GREEN,"W"
                elif gf==ga: rc,rt = WHITE30,"D"
                else: rc,rt = RED,"L"
                st.markdown(f"""<div class="match-card-plain">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                            <div class="match-meta">{ha} · {r['match_date'].strftime('%d %b')}</div>
                            <div class="match-team" style="margin-top:4px">vs {opp}</div>
                        </div>
                        <div style="text-align:right">
                            <div class="match-score" style="font-size:22px">{gf} – {ga}</div>
                            <div style="color:{rc};font-size:11px;font-weight:700">{rt}</div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

        with cr:
            st.markdown('<div class="sec-label">Goals Performance</div>', unsafe_allow_html=True)
            lbls = [f"vs {r['away_team'] if r['home_team']==sel_team else r['home_team']}" for _,r in tm.iterrows()]
            gf_v = [int(r['home_score']) if r['home_team']==sel_team else int(r['away_score']) for _,r in tm.iterrows()]
            ga_v = [int(r['away_score']) if r['home_team']==sel_team else int(r['home_score']) for _,r in tm.iterrows()]
            fig_t = go.Figure()
            fig_t.add_bar(name='Scored', x=lbls, y=gf_v, marker_color=BLUE_LIT)
            fig_t.add_bar(name='Conceded', x=lbls, y=ga_v, marker_color=RED)
            fig_t.update_layout(**PLOT, height=260, title='Goals Per Match', barmode='group')
            fig_t.update_layout(legend=dict(orientation='h', y=-0.2))
            st.plotly_chart(fig_t, use_container_width=True)

            st.markdown('<div class="sec-label">Group Position</div>', unsafe_allow_html=True)
            grp_s = standings_df[standings_df['Group']==grp].reset_index(drop=True)
            render_standings_header()
            render_standings_table(grp_s, highlight_team=sel_team)

            team_pred = pred_df[pred_df['team_name']==sel_team]
            if len(team_pred):
                tp = team_pred.iloc[0]
                st.markdown('<div class="sec-label" style="margin-top:12px">AI Predictions</div>', unsafe_allow_html=True)
                pc1, pc2 = st.columns(2)
                pc1.metric("Advance from Group", f"{tp['advancement_prob_pct']}%")
                pc2.metric("Win Tournament", f"{tp['win_probability']}%")
                st.progress(int(float(tp['advancement_prob_pct'])))

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — TOURNAMENT TRENDS (UNCHANGED)
# ══════════════════════════════════════════════════════════════════════════════
elif "Trends" in page:
    st.markdown('<div class="page-title">Tournament Trends</div>', unsafe_allow_html=True)
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
    st.markdown("")

    tab1, tab2, tab3, tab4 = st.tabs(["📅 Daily Goals","🌍 Confederations","⚡ Upsets","📊 Group Analysis"])

    with tab1:
        matches_df['date_only'] = matches_df['match_date'].dt.date
        daily = matches_df.groupby('date_only').agg(
            goals=('total_goals','sum'), matches=('match_id','count'), avg=('total_goals','mean')
        ).reset_index()
        fig_d = make_subplots(specs=[[{"secondary_y":True}]])
        fig_d.add_trace(go.Bar(x=daily['date_only'].astype(str), y=daily['goals'],
                               name='Total Goals', marker_color=BLUE_MID), secondary_y=False)
        fig_d.add_trace(go.Scatter(x=daily['date_only'].astype(str), y=daily['avg'].round(2),
                                   name='Avg/Match', mode='lines+markers',
                                   line=dict(color=BLUE_LIT, width=2),
                                   marker=dict(size=7, color=BLUE_LIT)), secondary_y=True)
        fig_d.add_hline(y=avg_goals, line_dash="dash", line_color="rgba(255,255,255,0.2)",
                        annotation_text=f"Avg {avg_goals}", secondary_y=True)
        fig_d.update_layout(**PLOT, height=380, title="Goals Per Match Day")
        fig_d.update_yaxes(color=WHITE30, secondary_y=False)
        fig_d.update_yaxes(color=BLUE_LIT, secondary_y=True)
        st.plotly_chart(fig_d, use_container_width=True)
        ca, cb, cc = st.columns(3)
        bd = daily.loc[daily['goals'].idxmax()]
        ca.metric("Most Goals in a Day", f"{int(bd['goals'])}", str(bd['date_only']))
        cb.metric("Most Matches in a Day", int(daily['matches'].max()))
        cc.metric("Match Days Played", len(daily))

    with tab2:
        conf_map = teams_df[['team_name','confederation']].copy()
        hc = matches_df[['home_team','home_score']].rename(columns={'home_team':'team','home_score':'g'})
        ac = matches_df[['away_team','away_score']].rename(columns={'away_team':'team','away_score':'g'})
        cg = pd.concat([hc,ac]).merge(conf_map, left_on='team', right_on='team_name')
        cg2 = cg.groupby('confederation')['g'].agg(['sum','mean']).reset_index()
        cg2.columns = ['Confederation','Total','Avg']
        cg2 = cg2.sort_values('Total', ascending=False)
        cl2, cr2 = st.columns(2)
        with cl2:
            fig_c = go.Figure(go.Bar(
                x=cg2['Confederation'], y=cg2['Total'],
                marker=dict(color=cg2['Total'], colorscale=BLUE_SCALE, showscale=False),
                text=cg2['Total'], textposition='outside', textfont=dict(color=WHITE)
            ))
            fig_c.update_layout(**PLOT, height=340, title="Goals by Confederation", showlegend=False)
            st.plotly_chart(fig_c, use_container_width=True)
        with cr2:
            fig_c2 = go.Figure(go.Bar(
                x=cg2['Confederation'], y=cg2['Avg'].round(2),
                marker=dict(color=cg2['Avg'], colorscale=BLUE_SCALE, showscale=False),
                text=cg2['Avg'].round(2), textposition='outside', textfont=dict(color=WHITE)
            ))
            fig_c2.update_layout(**PLOT, height=340, title="Avg Goals/Match by Confederation", showlegend=False)
            st.plotly_chart(fig_c2, use_container_width=True)

    with tab3:
        st.markdown('<div class="sec-label">Upset Tracker — Lower-ranked team wins or holds a draw</div>', unsafe_allow_html=True)
        upsets = []
        for _,r in matches_df.iterrows():
            rh = FIFA_RANKINGS.get(r['home_team'],90)
            ra = FIFA_RANKINGS.get(r['away_team'],90)
            hg,ag = int(r['home_score']),int(r['away_score'])
            if ag>hg and ra>rh:
                upsets.append({'Match':f"{r['home_team']} vs {r['away_team']}",
                               'Score':f"{hg}-{ag}",'Winner':r['away_team'],
                               'Rank Diff':ra-rh,'Date':r['match_date'].strftime('%d %b')})
            elif hg>ag and rh>ra:
                upsets.append({'Match':f"{r['home_team']} vs {r['away_team']}",
                               'Score':f"{hg}-{ag}",'Winner':r['home_team'],
                               'Rank Diff':rh-ra,'Date':r['match_date'].strftime('%d %b')})
            elif hg==ag and abs(rh-ra)>=20:
                upsets.append({'Match':f"{r['home_team']} vs {r['away_team']}",
                               'Score':f"{hg}-{ag}",'Winner':'Draw',
                               'Rank Diff':abs(rh-ra),'Date':r['match_date'].strftime('%d %b')})
        if upsets:
            udf = pd.DataFrame(upsets).sort_values('Rank Diff', ascending=False)
            for _,u in udf.iterrows():
                col = GOLD if u['Rank Diff']>=30 else BLUE_LIT
                st.markdown(f"""<div class="match-card-plain">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                            <div class="match-meta">{u['Date']}</div>
                            <div class="match-team" style="margin-top:4px">{u['Match']}</div>
                            <div class="match-meta" style="margin-top:2px">Winner: {u['Winner']}</div>
                        </div>
                        <div style="text-align:right">
                            <div class="match-score" style="font-size:22px;color:{col}">{u['Score']}</div>
                            <div style="color:{col};font-size:10px;font-weight:700">⚡ {u['Rank Diff']} rank diff</div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No significant upsets yet")

    with tab4:
        st.markdown('<div class="sec-label">Group Competitiveness — Points Spread & Avg Goals</div>', unsafe_allow_html=True)
        cd = []
        for grp in sorted(standings_df['Group'].unique()):
            gdf2 = standings_df[standings_df['Group']==grp]
            gm   = matches_df[matches_df['group_short']==grp]
            if len(gdf2)>=2:
                cd.append({'Group':grp,
                           'Pts Spread':int(gdf2['Pts'].max()-gdf2['Pts'].min()),
                           'Avg Goals':round(gm['total_goals'].mean(),2) if len(gm) else 0})
        cdf = pd.DataFrame(cd)
        cl3, cr3 = st.columns(2)
        with cl3:
            fig_s = go.Figure(go.Bar(
                x=cdf['Group'], y=cdf['Avg Goals'],
                marker=dict(color=cdf['Avg Goals'], colorscale=BLUE_SCALE, showscale=False),
                text=cdf['Avg Goals'], textposition='outside', textfont=dict(color=WHITE)
            ))
            fig_s.update_layout(**PLOT, height=320, title="Avg Goals per Match by Group", showlegend=False)
            st.plotly_chart(fig_s, use_container_width=True)
        with cr3:
            fig_s2 = go.Figure(go.Bar(
                x=cdf['Group'], y=cdf['Pts Spread'],
                marker=dict(color=cdf['Pts Spread'],
                            colorscale=[[0,BLUE_LIT],[1,RED]], showscale=False),
                text=cdf['Pts Spread'], textposition='outside', textfont=dict(color=WHITE)
            ))
            fig_s2.update_layout(**PLOT, height=320, title="Points Spread (Higher = Less Competitive)", showlegend=False)
            st.plotly_chart(fig_s2, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — PREDICTIONS (UNCHANGED)
# ══════════════════════════════════════════════════════════════════════════════
elif "Predictions" in page:
    st.markdown('<div class="page-title">AI Predictions</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">Random Forest model · Results saved directly from notebook · Last updated {pred_df["updated_at"].max() if "updated_at" in pred_df.columns else "recently"}</div>', unsafe_allow_html=True)
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
    st.markdown("")

    tab1, tab2 = st.tabs(["🏆 Tournament Winner","📊 Group Advancement"])

    with tab1:
        top10 = pred_df.head(10)
        if len(top10) >= 3:
            r1,r2,r3 = top10.iloc[0], top10.iloc[1], top10.iloc[2]
            p2, p1, p3 = st.columns(3)
            with p1:
                st.markdown(f"""<div class="podium-gold">
                    <div style="font-size:36px">🥇</div>
                    <div class="podium-name">{r1['team_name']}</div>
                    <div class="podium-sub">Group {r1['group_name']} · Rank #{int(r1['fifa_ranking'])}</div>
                    <div class="podium-prob">{r1['win_probability']}%</div>
                    <div class="podium-sub">win probability</div>
                    <div class="podium-sub" style="margin-top:4px">Adv: {r1['advancement_prob_pct']}%</div>
                </div>""", unsafe_allow_html=True)
            with p2:
                st.markdown(f"""<div class="podium-silver">
                    <div style="font-size:28px">🥈</div>
                    <div class="podium-name">{r2['team_name']}</div>
                    <div class="podium-sub">Group {r2['group_name']} · Rank #{int(r2['fifa_ranking'])}</div>
                    <div style="font-size:18px;font-weight:700;color:{WHITE};margin-top:6px">{r2['win_probability']}%</div>
                    <div class="podium-sub">Adv: {r2['advancement_prob_pct']}%</div>
                </div>""", unsafe_allow_html=True)
            with p3:
                st.markdown(f"""<div class="podium-silver">
                    <div style="font-size:28px">🥉</div>
                    <div class="podium-name">{r3['team_name']}</div>
                    <div class="podium-sub">Group {r3['group_name']} · Rank #{int(r3['fifa_ranking'])}</div>
                    <div style="font-size:18px;font-weight:700;color:{WHITE};margin-top:6px">{r3['win_probability']}%</div>
                    <div class="podium-sub">Adv: {r3['advancement_prob_pct']}%</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("")
        fig_w = go.Figure(go.Bar(
            x=top10['team_name'], y=top10['win_probability'],
            marker=dict(color=top10['win_probability'], colorscale=BLUE_SCALE, showscale=False),
            text=top10['win_probability'].astype(str)+'%',
            textposition='outside', textfont=dict(color=WHITE)
        ))
        fig_w.update_layout(**PLOT, height=360, title="Tournament Win Probability — Top 10", showlegend=False)
        st.plotly_chart(fig_w, use_container_width=True)
        st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:11px;color:{WHITE30};margin-top:8px">Win probability = 50% current form (advancement prob) + 30% FIFA ranking + 20% momentum. Predictions computed by <code>02_knockout_predictor.ipynb</code> and saved to Azure SQL.</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="sec-label">Advancement Probability — All Teams</div>', unsafe_allow_html=True)
        grp_sel = st.selectbox("Filter by group", ["All Groups"] + sorted(pred_df['group_name'].dropna().unique()))
        disp = pred_df if grp_sel=="All Groups" else pred_df[pred_df['group_name']==grp_sel]
        disp = disp.sort_values('advancement_prob_pct', ascending=False)
        for _,row in disp.iterrows():
            prob = float(row['advancement_prob_pct'])
            emoji = "🟢" if prob>=60 else "🟡" if prob>=35 else "🔴"
            gd_str = f"+{int(row['goal_difference'])}" if row['goal_difference']>=0 else str(int(row['goal_difference']))
            col_prob = BLUE_LIT if prob>=60 else GOLD if prob>=35 else RED
            c1,c2,c3,c4,c5 = st.columns([3,1,1,1,2])
            with c1:
                st.markdown(f'{emoji} **{row["team_name"]}** &nbsp; <span style="font-size:10px;color:{WHITE30}">Group {row["group_name"]} · Rank #{int(row["fifa_ranking"])}</span>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div style="font-size:12px;color:{WHITE60}">**{int(row["points"])}** pts</div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div style="font-size:12px;color:{WHITE60}">GD **{gd_str}**</div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div style="font-size:12px;color:{WHITE60}">**{int(row["played"])}** played</div>', unsafe_allow_html=True)
            with c5:
                st.markdown(f'<div style="text-align:right;color:{col_prob};font-weight:700;font-size:17px">{prob}%</div>', unsafe_allow_html=True)
            st.progress(int(prob))
            st.markdown("")

st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;padding:20px;font-size:10px;color:{WHITE30};
            border-top:1px solid {BORDER2};margin-top:20px;letter-spacing:1px">
    Built by <span style="color:{BLUE_LIT};font-weight:600">Sahil Bhure</span> &nbsp;·&nbsp;
    MSc Business Analytics · Warwick Business School &nbsp;·&nbsp;
    Azure SQL · Python · Streamlit &nbsp;·&nbsp;
    Data: football-data.org
</div>
""", unsafe_allow_html=True)