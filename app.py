"""
Analysis Journey — Global Maritime Solutions
A storytelling-driven Streamlit page that walks an executive reader through
the full investigative process behind the Q1 2025 Operational Review:
why each question was asked, how it was tested, what was found, and what
it means for the business.

Run standalone with:   streamlit run Analysis_Journey.py
Or drop into a multipage app's `pages/` folder.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import plotly.io as pio
# Fix: orjson circular import bug on some Windows Python 3.12 environments
pio.json.config.default_engine = "json"
 
 
# ──────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Analysis Journey · Global Maritime Solutions",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────────────────────
# DESIGN TOKENS — "Ship's Log" palette
# A maritime-instrument aesthetic: chart-paper backgrounds, navy ink,
# brass accents (the metal of a sextant or engine-room dial), and a
# signal-red used the way it's used on nautical charts and flags.
# ──────────────────────────────────────────────────────────────────────────
BG          = "#F0F3F5"   # chart-paper / fog-over-harbour
INK         = "#0B2545"   # deep navy ink
NAVY_DEEP   = "#081C30"   # hero band
NAVY_MED    = "#11314F"   # secondary surfaces
BRASS       = "#A6792B"   # signature accent
BRASS_LIGHT = "#C9A24B"
SIGNAL_RED  = "#B3372C"   # alert / not-supported
SEAFOAM     = "#2F6F76"   # secondary series / partial
SLATE       = "#44546B"   # body text
CARD_BG     = "#FFFFFF"
BORDER      = "#DCE3E6"
SUPPORTED_GREEN = "#3A6B52"
SUPPORTED_BG    = "#E7F0EA"
NOTSUP_BG       = "#F6E8E6"
PARTIAL_BG      = "#F5EFE0"

AGE_ORDER  = ["New (<5yr)", "Modern (5-15yr)", "Mature (16-30yr)", "Old (>30yr)"]
SUEZ_ORDER = ["Pre-Suez", "During-Suez", "Post-Suez", "Normal"]
CAT_COLORS = {"Cargo": NAVY_MED, "Container": SEAFOAM, "Passenger": SIGNAL_RED, "Tanker": BRASS}

# ──────────────────────────────────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
.stApp { background-color: #F0F3F5; }
.block-container { padding-top: 1.5rem; padding-bottom: 4rem; max-width: 1180px; }

h1, h2, h3 { font-family: 'Spectral', serif; color: #0B2545; }
p, li, span, div { color: #0B2545; }

/* ---------- HERO ---------- */
.hero-band {
    background: linear-gradient(135deg, #081C30 0%, #0B2545 60%, #11314F 100%);
    border-radius: 6px;
    padding: 2.6rem 3rem 2.2rem 3rem;
    margin-bottom: 1.6rem;
    position: relative;
    overflow: hidden;
}
.hero-band::after {
    content: "";
    position: absolute;
    right: -60px; top: -60px;
    width: 260px; height: 260px;
    border: 1px solid rgba(201,162,75,0.18);
    border-radius: 50%;
}
.hero-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    color: #C9A24B;
    letter-spacing: 0.18em;
    font-size: 0.78rem;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}
.hero-title {
    font-family: 'Spectral', serif;
    color: #F6F4EE;
    font-weight: 700;
    font-size: 2.5rem;
    line-height: 1.15;
    margin: 0 0 0.5rem 0;
}
.hero-sub {
    color: #C7D2DC;
    font-size: 1.02rem;
    max-width: 720px;
    line-height: 1.55;
    margin-bottom: 0;
}
.hero-rule { border-top: 1px solid rgba(201,162,75,0.35); margin: 1.4rem 0 1.2rem 0; }
.hero-kpi-label { font-family:'IBM Plex Mono', monospace; color:#8FA3B8; font-size:0.72rem; letter-spacing:0.08em; text-transform:uppercase;}
.hero-kpi-value { font-family:'Spectral', serif; color:#F6F4EE; font-size:1.5rem; font-weight:600; }

/* ---------- SECTION LABEL / EYEBROW ---------- */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #A6792B;
    font-weight: 600;
    margin: 0.9rem 0 0.3rem 0;
}
.section-label:first-child { margin-top: 0; }

/* ---------- BODY TEXT IN CARDS ---------- */
.hyp-question {
    font-family: 'Spectral', serif;
    font-style: italic;
    font-size: 1.18rem;
    font-weight: 500;
    color: #0B2545;
    margin: 0 0 0.2rem 0;
    line-height: 1.4;
}
.hyp-body { font-size: 0.95rem; color: #44546B; line-height: 1.55; margin: 0 0 0.2rem 0; }
.approach-list { margin: 0 0 0.2rem 0; padding-left: 1.1rem; }
.approach-list li { font-size: 0.92rem; color: #44546B; line-height: 1.5; margin-bottom: 0.25rem; }

/* ---------- LOG TAB ---------- */
.hyp-tab {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #FFFFFF;
    background: #0B2545;
    padding: 0.22rem 0.7rem;
    border-radius: 3px;
    margin-bottom: 0.9rem;
}
.hyp-tab .chap { color: #C9A24B; }

/* ---------- INSIGHT BOX ---------- */
.insight-box {
    background: #FAF8F2;
    border-left: 3px solid #A6792B;
    border-radius: 0 4px 4px 0;
    padding: 0.85rem 1.1rem;
    margin: 1.1rem 0 0.8rem 0;
}
.insight-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #A6792B;
    font-weight: 700;
    margin-bottom: 0.25rem;
}
.insight-box p { font-size: 0.93rem; color: #2A3548; line-height: 1.55; margin: 0; }

/* ---------- CONCLUSION ROW ---------- */
.conclusion-row { display: flex; align-items: flex-start; gap: 1rem; margin-top: 0.4rem; }
.stamp {
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 700;
    font-size: 0.74rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.35rem 0.8rem;
    border-radius: 4px;
    border: 2px solid;
    transform: rotate(-2.5deg);
    white-space: nowrap;
    flex-shrink: 0;
}
.stamp-supported    { color: #3A6B52; border-color: #3A6B52; background: #E7F0EA; }
.stamp-not-supported{ color: #B3372C; border-color: #B3372C; background: #F6E8E6; }
.stamp-partial      { color: #A6792B; border-color: #A6792B; background: #F5EFE0; }
.conclusion-text { font-size: 0.93rem; color: #44546B; line-height: 1.55; padding-top: 0.15rem; }

/* ---------- CHAPTER DIVIDER ---------- */
.chapter-divider { margin: 2.6rem 0 1.2rem 0; }
.chapter-num {
    font-family: 'IBM Plex Mono', monospace;
    color: #A6792B;
    font-size: 0.85rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
.chapter-title {
    font-family: 'Spectral', serif;
    font-weight: 700;
    font-size: 1.7rem;
    color: #0B2545;
    margin: 0.15rem 0 0.35rem 0;
}
.chapter-sub { font-size: 0.96rem; color: #44546B; max-width: 760px; line-height: 1.5; }
.chapter-rule { border: none; border-top: 2px solid #0B2545; margin-top: 0.9rem; }

/* ---------- FRAMEWORK PILLAR CARDS ---------- */
.pillar-card {
    background: #FFFFFF;
    border: 1px solid #DCE3E6;
    border-top: 3px solid #A6792B;
    border-radius: 4px;
    padding: 1.1rem 1.2rem 1.2rem 1.2rem;
    height: 100%;
}
.pillar-num { font-family:'IBM Plex Mono', monospace; color:#A6792B; font-size:0.8rem; letter-spacing:0.1em;}
.pillar-title { font-family:'Spectral', serif; font-weight:600; font-size:1.12rem; margin:0.25rem 0 0.4rem 0; }
.pillar-text { font-size: 0.88rem; color:#44546B; line-height:1.5; }

/* ---------- VOYAGE TIMELINE ---------- */
.voyage-wrap { display:flex; align-items:center; margin: 1.4rem 0 0.4rem 0; }
.voyage-stop { flex:1; text-align:center; position:relative; }
.voyage-line { position:absolute; top:9px; left:0; right:0; height:2px; background:#DCE3E6; z-index:0; }
.voyage-dot { width:16px; height:16px; border-radius:50%; margin:0 auto; position:relative; z-index:1; border:3px solid #F0F3F5; }
.voyage-label { font-family:'IBM Plex Mono', monospace; font-size:0.68rem; letter-spacing:0.05em; text-transform:uppercase; color:#44546B; margin-top:0.45rem; }
.voyage-sub { font-size: 0.74rem; color:#8493A6; margin-top: 0.1rem;}

/* ---------- METRIC STRIP ---------- */
div[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #DCE3E6;
    border-radius: 4px;
    padding: 0.7rem 0.9rem 0.5rem 0.9rem;
}
div[data-testid="stMetricLabel"] { font-family:'IBM Plex Mono', monospace; font-size:0.72rem; letter-spacing:0.05em; text-transform:uppercase; }
div[data-testid="stMetricValue"] { font-family:'Spectral', serif; color:#0B2545; }

/* ---------- SUMMARY TABLE ---------- */
.summary-table { width:100%; border-collapse: collapse; font-size: 0.88rem; }
.summary-table th {
    font-family:'IBM Plex Mono', monospace; font-size:0.68rem; letter-spacing:0.07em; text-transform:uppercase;
    color:#8493A6; text-align:left; padding:0.5rem 0.6rem; border-bottom:2px solid #0B2545;
}
.summary-table td { padding:0.55rem 0.6rem; border-bottom:1px solid #DCE3E6; color:#2A3548; vertical-align: top;}
.summary-table tr:last-child td { border-bottom: none; }

/* ---------- RECOMMENDATION CARDS ---------- */
.rec-card {
    background:#FFFFFF; border:1px solid #DCE3E6; border-left:3px solid #0B2545;
    border-radius:0 4px 4px 0; padding:0.9rem 1.1rem; margin-bottom:0.7rem;
}
.rec-num { font-family:'IBM Plex Mono', monospace; color:#A6792B; font-size:0.78rem; font-weight:700; }
.rec-title { font-family:'Spectral', serif; font-weight:600; font-size:1.0rem; margin: 0.15rem 0 0.25rem 0;}
.rec-text { font-size:0.88rem; color:#44546B; line-height:1.5; }

footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ──────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading voyage records…")
def load_data(uploaded=None) -> pd.DataFrame:
    if uploaded is not None:
        d = pd.read_csv(uploaded)
    else:
        d = pd.read_csv("final_dataset.csv")
    d["date_id"] = pd.to_datetime(d["date_id"])
    d["age_bucket"] = pd.Categorical(d["age_bucket"], categories=AGE_ORDER, ordered=True)
    d["suez_period"] = pd.Categorical(d["suez_period"], categories=SUEZ_ORDER, ordered=True)
    return d

import os
df = None
load_error = None
if os.path.exists("final_dataset.csv"):
    df = load_data()
else:
    st.warning(
        "Couldn't find `final_dataset.csv` next to this script. "
        "Upload it below to render the journey (the file produced at the end of the EDA notebook)."
    )
    up = st.file_uploader("Upload final_dataset.csv", type="csv")
    if up is not None:
        df = load_data(up)
    else:
        st.stop()

# ──────────────────────────────────────────────────────────────────────────
# CHART THEME HELPER
# ──────────────────────────────────────────────────────────────────────────
def style_fig(fig, height=360, showlegend=False):
    fig.update_layout(
        font=dict(family="IBM Plex Sans, sans-serif", size=12.5, color=INK),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=36, b=10),
        height=height,
        showlegend=showlegend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=11)),
        hoverlabel=dict(bgcolor="white", font_family="IBM Plex Mono", font_size=11, bordercolor=BORDER),
    )
    fig.update_xaxes(showgrid=False, linecolor=BORDER, ticks="outside", tickcolor=BORDER)
    fig.update_yaxes(showgrid=True, gridcolor=BORDER, zeroline=False)
    return fig

# ──────────────────────────────────────────────────────────────────────────
# REUSABLE UI BLOCKS
# ──────────────────────────────────────────────────────────────────────────
def chapter_header(number_label, title, subtitle):
    st.markdown(f"""
    <div class="chapter-divider">
        <div class="chapter-num">Chapter {number_label}</div>
        <div class="chapter-title">{title}</div>
        <div class="chapter-sub">{subtitle}</div>
        <hr class="chapter-rule"/>
    </div>
    """, unsafe_allow_html=True)

def stamp_html(status):
    cls = {"Supported": "stamp-supported", "Not Supported": "stamp-not-supported", "Partially Supported": "stamp-partial"}[status]
    return f'<span class="stamp {cls}">{status}</span>'

def hypothesis_card(number, chapter_tag, question, hypothesis_stmt, why_matters,
                     approach_bullets, render_chart, finding_text, status, conclusion_text,
                     metric_caption=None):
    with st.container(border=True):
        st.markdown(
            f'<div class="hyp-tab">Log Entry {number:02d} <span class="chap">· {chapter_tag}</span></div>',
            unsafe_allow_html=True,
        )
        left, right = st.columns([1, 1.18], gap="large")
        with left:
            st.markdown('<div class="section-label">Business Question</div>', unsafe_allow_html=True)
            st.markdown(f'<p class="hyp-question">{question}</p>', unsafe_allow_html=True)

            st.markdown('<div class="section-label">Hypothesis</div>', unsafe_allow_html=True)
            st.markdown(f'<p class="hyp-body">{hypothesis_stmt}</p>', unsafe_allow_html=True)

            st.markdown('<div class="section-label">Why It Matters</div>', unsafe_allow_html=True)
            st.markdown(f'<p class="hyp-body">{why_matters}</p>', unsafe_allow_html=True)

            st.markdown('<div class="section-label">Analysis Approach</div>', unsafe_allow_html=True)
            bullets_html = "".join(f"<li>{b}</li>" for b in approach_bullets)
            st.markdown(f'<ul class="approach-list">{bullets_html}</ul>', unsafe_allow_html=True)

        with right:
            st.markdown('<div class="section-label">Visualization</div>', unsafe_allow_html=True)
            render_chart()
            if metric_caption:
                st.caption(metric_caption)

        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-label">Key Finding</div>
            <p>{finding_text}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="conclusion-row">
            {stamp_html(status)}
            <div class="conclusion-text">{conclusion_text}</div>
        </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────
# HERO
# ──────────────────────────────────────────────────────────────────────────
n_records   = len(df)
n_terminals = df["terminal_id"].nunique()
n_vessels   = df["vessel_id"].nunique()
date_min, date_max = df["date_id"].min(), df["date_id"].max()
overall_median_duration = df["move_duration"].median()

st.markdown(f"""
<div class="hero-band">
    <div class="hero-eyebrow">Analysis Journey &nbsp;·&nbsp; Global Maritime Solutions &nbsp;·&nbsp; Q1 2025 Operational Review</div>
    <div class="hero-title">Why is cargo handling time inconsistent<br/>across our terminal network?</div>
    <p class="hero-sub">
        In March 2021, the Ever Given grounding shut down the Suez Canal for six days and exposed
        structural inconsistencies in how long it takes to move cargo through our terminals.
        This page walks through the investigation exactly as it happened — every hypothesis we tested,
        why we tested it, what the data said, and what it means for the network going forward.
    </p>
    <div class="hero-rule"></div>
    <div style="display:flex; gap:2.6rem; flex-wrap:wrap;">
        <div><div class="hero-kpi-label">Movement records</div><div class="hero-kpi-value">{n_records:,}</div></div>
        <div><div class="hero-kpi-label">Terminals</div><div class="hero-kpi-value">{n_terminals}</div></div>
        <div><div class="hero-kpi-label">Vessels tracked</div><div class="hero-kpi-value">{n_vessels:,}</div></div>
        <div><div class="hero-kpi-label">Period covered</div><div class="hero-kpi-value">{date_min.year}–{date_max.year}</div></div>
        <div><div class="hero-kpi-label">12-month target</div><div class="hero-kpi-value">−15% move duration</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# BUSINESS PROBLEM / OBJECTIVE / DATASET OVERVIEW
# ──────────────────────────────────────────────────────────────────────────
intro_l, intro_r = st.columns([1.15, 1], gap="large")
with intro_l:
    st.markdown('<div class="section-label">The Business Problem</div>', unsafe_allow_html=True)
    st.markdown("""
    <p class="hyp-body">
    Global Maritime Solutions runs a network of terminals whose single most important
    operational KPI is <b>move duration</b> — the minutes it takes to complete a cargo
    movement. After the Suez Canal disruption, leadership noticed that move duration had
    become noticeably less predictable, but it wasn't clear whether the Suez event was the
    real cause, or whether it simply coincided with pre-existing weaknesses in vessel
    scheduling, terminal capacity, or shift operations.
    </p>
    <p class="hyp-body">
    Rather than assume an answer, this analysis treats every plausible explanation as a
    hypothesis to be tested against three years of movement-level data, and reports
    honestly on what survived contact with the evidence and what didn't.
    </p>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Project Objective</div>', unsafe_allow_html=True)
    st.markdown("""
    <p class="hyp-body">
    Identify the true drivers of move-duration variability across three lenses —
    <b>disruption impact</b>, <b>infrastructure bottlenecks</b>, and <b>operational
    efficiency</b> — and use the answer to support a 15% reduction in average move
    duration within 12 months.
    </p>
    """, unsafe_allow_html=True)

with intro_r:
    st.markdown('<div class="section-label">Dataset Overview</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <p class="hyp-body">
    Four source tables were joined into a single movement-level analytical base:
    <code>fact_cargo_movements</code> (the {n_records:,} movements themselves),
    <code>dim_time</code>, <code>dim_vessel</code> and <code>dim_terminal</code>.
    After de-duplication, impossible-value removal, and median-imputation of missing
    values, five features were engineered to make the disruption and its alternatives
    testable: <code>vessel_age</code> / <code>age_bucket</code>, <code>handling_speed</code>,
    <code>peak_season</code>, and <code>suez_period</code> (Pre / During / Post / Normal).
    </p>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric("Median move duration", f"{overall_median_duration:.0f} min")
    c2.metric("Disruption-window records", f"{(df['suez_period']=='During-Suez').sum()}", help="2021-03-23 → 2021-03-31")

# ──────────────────────────────────────────────────────────────────────────
# VOYAGE TIMELINE (signature element)
# ──────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">The Disruption Timeline This Investigation Is Built Around</div>', unsafe_allow_html=True)
voyage_stops = [
    ("Pre-Suez", "Jan 1 – Mar 22, 2021", BRASS),
    ("During-Suez", "Mar 23 – 31 · Ever Given blocked", SIGNAL_RED),
    ("Post-Suez", "Apr 1 – Jun 30, 2021", SEAFOAM),
    ("Normal Operations", "Remainder of 2021–2024 (baseline)", NAVY_MED),
]
stop_parts = []
for label, sub, color in voyage_stops:
    stop_parts.append(
        '<div class="voyage-stop">'
        '<div class="voyage-line"></div>'
        f'<div class="voyage-dot" style="background:{color};"></div>'
        f'<div class="voyage-label">{label}</div>'
        f'<div class="voyage-sub">{sub}</div>'
        "</div>"
    )
stops_html = "".join(stop_parts)
st.markdown(f'<div class="voyage-wrap">{stops_html}</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# ANALYTICAL FRAMEWORK
# ──────────────────────────────────────────────────────────────────────────
st.markdown('<div style="height:1.6rem;"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Analytical Framework — Three Lenses, Eight Hypotheses</div>', unsafe_allow_html=True)
st.markdown("""
<p class="hyp-body" style="margin-bottom:1rem;">
We deliberately tested the operational explanations first — the ones a terminal manager would
reach for instinctively — before turning to the disruption itself. That ordering is the spine of
the page below: <b>Chapter 1</b> rules conventional suspects in or out, <b>Chapter 2</b> looks at
whether the network itself is the problem, and <b>Chapter 3</b> goes back to where this all
started — the Suez Canal.
</p>
""", unsafe_allow_html=True)

p1, p2, p3 = st.columns(3, gap="medium")
with p1:
    st.markdown("""
    <div class="pillar-card">
        <div class="pillar-num">01 · Efficiency Anomaly Analysis</div>
        <div class="pillar-title">Is it how we operate?</div>
        <div class="pillar-text">Tests vessel age, vessel category, cargo volume, and shift
        timing as everyday drivers of slow handling — the factors operators already control.</div>
    </div>""", unsafe_allow_html=True)
with p2:
    st.markdown("""
    <div class="pillar-card">
        <div class="pillar-num">02 · Infrastructure Bottleneck Analysis</div>
        <div class="pillar-title">Is it where we operate?</div>
        <div class="pillar-text">Tests whether specific terminals in the network are
        structurally slower than others, independent of vessel or cargo mix.</div>
    </div>""", unsafe_allow_html=True)
with p3:
    st.markdown("""
    <div class="pillar-card">
        <div class="pillar-num">03 · Suez Canal Disruption Analysis</div>
        <div class="pillar-title">Is it the shock we already suspected?</div>
        <div class="pillar-text">Tests whether the Ever Given grounding actually
        shows up in the data — regionally, temporally, and in cargo volume.</div>
    </div>""", unsafe_allow_html=True)
# ══════════════════════════════════════════════════════════════════════════
# CHAPTER 1 — EFFICIENCY ANOMALY ANALYSIS
# ══════════════════════════════════════════════════════════════════════════
chapter_header(
    "1", "Ruling Out the Usual Suspects",
    "Before blaming a six-day canal blockage, we tested the explanations a terminal "
    "manager would reach for first: tired old vessels, slow cargo types, heavy loads, "
    "and night-shift fatigue. None of them turned out to be the story."
)

# ---- H-01 Vessel Age -------------------------------------------------------
age_stats = df.groupby("age_bucket", observed=True).agg(
    median_duration=("move_duration", "median"),
    avg_speed=("handling_speed", "mean"),
    median_speed=("handling_speed", "median"),
    n=("movement_id", "count"),
).reindex(AGE_ORDER)
spread1 = age_stats["median_duration"].max() - age_stats["median_duration"].min()
spread1_pct = spread1 / overall_median_duration * 100
new_avg_speed = age_stats.loc["New (<5yr)", "avg_speed"]
new_med_speed = age_stats.loc["New (<5yr)", "median_speed"]

def chart_age():
    fig = go.Figure()
    for cat in AGE_ORDER:
        sub = df.loc[df["age_bucket"] == cat, "move_duration"]
        fig.add_trace(go.Box(
            y=sub, name=cat, marker_color=NAVY_MED, line_color=INK,
            fillcolor="rgba(17,49,79,0.18)", boxmean=True,
        ))
    fig.update_layout(yaxis_title="Move duration (min)")
    st.plotly_chart(style_fig(fig, height=360), use_container_width=True, config={"displayModeBar": False})

hypothesis_card(
    number=1, chapter_tag="Efficiency Anomaly",
    question="Do older vessels cause slower cargo handling?",
    hypothesis_stmt="Older vessels require longer cargo handling times than newer ones, "
                     "due to wear, outdated equipment, or maintenance issues.",
    why_matters="If true, this would justify prioritising fleet renewal or pre-emptive "
                "maintenance scheduling for older vessels as a lever on move duration.",
    approach_bullets=[
        "Engineered <code>vessel_age</code> from build year and fiscal year, then grouped vessels into four age bands.",
        "Compared median move duration and handling speed (containers per minute) across bands.",
        "First pass on the <i>mean</i> was misleading — new vessels showed an average speed of "
        f"{new_avg_speed:.1f}, far above every other band — so we checked the distribution before trusting it.",
        "Switching to the <i>median</i> resolved the anomaly: it dropped to "
        f"{new_med_speed:.2f}, in line with every other age band, confirming the mean was distorted by a handful of extreme outliers.",
    ],
    render_chart=chart_age,
    finding_text=f"Median move duration ranges only from {age_stats['median_duration'].min():.0f} to "
                 f"{age_stats['median_duration'].max():.0f} minutes across age bands — a spread of "
                 f"{spread1_pct:.0f}% of the network median. Median handling speed is essentially "
                 "identical across all four bands once outliers are accounted for.",
    status="Not Supported",
    conclusion_text="Vessel age is not a meaningful driver of cargo movement performance. "
                     "Fleet-renewal spend justified on handling-speed grounds would not be supported by this data.",
    metric_caption="Box plot of move duration by vessel age band — overlapping ranges and near-identical medians.",
)

# ---- H-02 Vessel Category --------------------------------------------------
cat_stats = df.groupby("vessel_category", observed=True).agg(
    median_duration=("move_duration", "median"),
    n=("movement_id", "count"),
).sort_values("median_duration", ascending=False)
slowest_cat = cat_stats.index[0]
fastest_cat = cat_stats.index[-1]
cat_spread = cat_stats["median_duration"].iloc[0] - cat_stats["median_duration"].iloc[-1]

def chart_category():
    ordered = cat_stats.reset_index()
    colors = [CAT_COLORS.get(c, NAVY_MED) for c in ordered["vessel_category"]]
    fig = go.Figure(go.Bar(
        x=ordered["median_duration"], y=ordered["vessel_category"], orientation="h",
        marker_color=colors, text=[f"{v:.0f} min" for v in ordered["median_duration"]],
        textposition="outside",
    ))
    fig.add_vline(x=overall_median_duration, line_dash="dot", line_color=SLATE, opacity=0.6,
                   annotation_text="network median", annotation_font_size=10, annotation_font_color=SLATE)
    fig.update_layout(xaxis_title="Median move duration (min)")
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(style_fig(fig, height=300), use_container_width=True, config={"displayModeBar": False})

hypothesis_card(
    number=2, chapter_tag="Efficiency Anomaly",
    question="Does cargo-type vessel handling take longer than tanker handling?",
    hypothesis_stmt="Cargo-category vessels have longer move durations than tankers, "
                     "because container/cargo handling is mechanically more complex than fluid transfer.",
    why_matters="If certain vessel categories are structurally slower, berth scheduling and crane "
                "allocation could be re-weighted by vessel type to smooth network throughput.",
    approach_bullets=[
        "Grouped all movements by <code>vessel_category</code> (Cargo, Container, Passenger, Tanker).",
        "Compared median move duration and median handling speed across categories.",
        "Checked whether any one category sat meaningfully outside the network median.",
    ],
    render_chart=chart_category,
    finding_text=f"{slowest_cat} vessels are the slowest category at {cat_stats.loc[slowest_cat,'median_duration']:.0f} "
                 f"minutes and {fastest_cat} vessels the fastest at {cat_stats.loc[fastest_cat,'median_duration']:.0f} — "
                 f"a gap of only {cat_spread:.0f} minutes, all four categories sitting within a narrow band around the network median.",
    status="Not Supported",
    conclusion_text=f"Vessel category has only a marginal effect on move duration. {slowest_cat} vessels run "
                     "slightly slower, but the gap is too small to explain the inconsistency leadership flagged.",
)

# ---- H-03 Container Volume -------------------------------------------------
corr3 = df["container_count"].corr(df["move_duration"])
rng = np.random.default_rng(42)
sample_idx = rng.choice(df.index, size=min(1800, len(df)), replace=False)
sample = df.loc[sample_idx]
trend_coef = np.polyfit(df["container_count"], df["move_duration"], 1)

def chart_volume():
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sample["container_count"], y=sample["move_duration"], mode="markers",
        marker=dict(color=NAVY_MED, size=5, opacity=0.32, line=dict(width=0)),
        name="Movements (sampled)",
    ))
    xs = np.linspace(df["container_count"].min(), df["container_count"].max(), 50)
    ys = trend_coef[0] * xs + trend_coef[1]
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=SIGNAL_RED, width=2.5), name="Linear fit"))
    fig.update_layout(xaxis_title="Container count", yaxis_title="Move duration (min)")
    st.plotly_chart(style_fig(fig, height=340, showlegend=True), use_container_width=True, config={"displayModeBar": False})

hypothesis_card(
    number=3, chapter_tag="Efficiency Anomaly",
    question="Does carrying more containers slow a movement down?",
    hypothesis_stmt="Higher container counts lead to longer move duration, since more "
                     "units mean more crane cycles and handling time.",
    why_matters="If volume drives duration, congestion at high-traffic terminals would be expected "
                "and predictable — and capacity planning could focus purely on throughput volume.",
    approach_bullets=[
        "Computed the Pearson correlation between <code>container_count</code> and <code>move_duration</code> across all movements.",
        "Visualised the full relationship on a scatter plot with a fitted linear trend.",
        "Cross-checked against descriptive statistics for both variables to rule out a non-linear relationship hiding in the correlation.",
    ],
    render_chart=chart_volume,
    finding_text=f"The correlation between container count and move duration is {corr3:.4f} — "
                 "statistically and practically zero. The fitted trend line is essentially flat across "
                 "the full range of cargo volumes observed.",
    status="Not Supported",
    conclusion_text="Cargo volume does not influence movement duration in this network. Whatever is "
                     "driving inconsistent handling times, it isn't how much cargo is on board.",
)

# ---- H-04 Shift Timing ------------------------------------------------------
shift_stats = df.groupby("shift", observed=True).agg(
    median_duration=("move_duration", "median"), n=("movement_id", "count")
)
shift_diff = shift_stats.loc["Day", "median_duration"] - shift_stats.loc["Night", "median_duration"]

def chart_shift():
    ordered = shift_stats.reindex(["Day", "Night"]).reset_index()
    fig = go.Figure(go.Bar(
        x=ordered["shift"], y=ordered["median_duration"],
        marker_color=[BRASS, NAVY_MED],
        text=[f"{v:.0f} min" for v in ordered["median_duration"]], textposition="outside",
        width=0.5,
    ))
    fig.update_layout(yaxis_title="Median move duration (min)")
    fig.update_yaxes(range=[0, max(shift_stats["median_duration"]) * 1.25])
    st.plotly_chart(style_fig(fig, height=300), use_container_width=True, config={"displayModeBar": False})

hypothesis_card(
    number=4, chapter_tag="Efficiency Anomaly",
    question="Are night shifts slower than day shifts?",
    hypothesis_stmt="Night shifts have longer move duration than day shifts, due to reduced "
                     "staffing, lighting constraints, or fatigue.",
    why_matters="If night operations are measurably slower, shifting more volume to day shifts — "
                "or investing in night-shift staffing and lighting — would be a direct, low-risk fix.",
    approach_bullets=[
        "Split all movements by the <code>shift</code> flag (Day / Night) carried in the time dimension.",
        "Compared median move duration and median handling speed between the two groups.",
        "Checked record counts to confirm both shifts were comparably represented in the data.",
    ],
    render_chart=chart_shift,
    finding_text=f"Night shift actually runs slightly <i>faster</i> than day shift — "
                 f"{shift_stats.loc['Night','median_duration']:.0f} vs {shift_stats.loc['Day','median_duration']:.0f} minutes "
                 f"median, a difference of only {shift_diff:.1f} minutes — the opposite direction of the hypothesis.",
    status="Not Supported",
    conclusion_text="Shift timing is not a contributor to terminal inefficiency. Operational performance "
                     "is consistent around the clock, so staffing reallocation by shift wouldn't move the KPI.",
)

# ══════════════════════════════════════════════════════════════════════════
# CHAPTER 2 — INFRASTRUCTURE BOTTLENECK ANALYSIS
# ══════════════════════════════════════════════════════════════════════════
chapter_header(
    "2", "Where the Network Actually Diverges",
    "With vessel- and cargo-level explanations ruled out, we turned to the terminals "
    "themselves — is the network's inconsistency a property of specific locations rather than ships?"
)

terminal_stats = df.groupby(["terminal_id", "terminal_name"]).agg(
    median_duration=("move_duration", "median"), n=("movement_id", "count")
).reset_index()
t_min, t_max = terminal_stats["median_duration"].min(), terminal_stats["median_duration"].max()
t_spread = t_max - t_min
t_spread_pct = t_spread / overall_median_duration * 100
slowest5 = terminal_stats.sort_values("median_duration", ascending=False).head(5)
fastest5 = terminal_stats.sort_values("median_duration", ascending=True).head(5)

def chart_terminals():
    combined = pd.concat([
        fastest5.assign(group="Fastest 5"),
        slowest5.sort_values("median_duration").assign(group="Slowest 5"),
    ])
    colors = [SEAFOAM if g == "Fastest 5" else SIGNAL_RED for g in combined["group"]]
    fig = go.Figure(go.Bar(
        x=combined["median_duration"], y=combined["terminal_name"], orientation="h",
        marker_color=colors, text=[f"{v:.0f} min" for v in combined["median_duration"]],
        textposition="outside",
    ))
    fig.add_vline(x=overall_median_duration, line_dash="dot", line_color=SLATE, opacity=0.6,
                   annotation_text="network median", annotation_font_size=10, annotation_font_color=SLATE)
    fig.update_layout(xaxis_title="Median move duration (min)")
    st.plotly_chart(style_fig(fig, height=420), use_container_width=True, config={"displayModeBar": False})

hypothesis_card(
    number=5, chapter_tag="Infrastructure Bottleneck",
    question="Do some terminals consistently operate slower than others?",
    hypothesis_stmt="Certain terminals in the network are structurally slower than others, "
                     "independent of which vessels or cargo pass through them.",
    why_matters="Terminal-level slowness is the most directly actionable type of bottleneck — it "
                "points straight at specific equipment, layout, or staffing investments rather than "
                "fleet-wide policy changes.",
    approach_bullets=[
        f"Aggregated median move duration across all {len(terminal_stats)} terminals in the network.",
        "Ranked terminals from fastest to slowest and measured the spread against the network median.",
        "Pulled out the five fastest and five slowest terminals by name as concrete investigation candidates.",
    ],
    render_chart=chart_terminals,
    finding_text=f"Terminal-level median duration ranges from {t_min:.0f} to {t_max:.0f} minutes — a "
                 f"{t_spread_pct:.0f}% spread between the fastest and slowest terminal. That's real "
                 f"variation, but most of the {len(terminal_stats)} terminals cluster tightly around the "
                 f"network median of {overall_median_duration:.0f} minutes; only a handful sit clearly out on either tail.",
    status="Partially Supported",
    conclusion_text="Terminal identity does explain some of the inconsistency — meaningfully more than "
                     "vessel age, category, volume, or shift did — but it's a tail effect, not a network-wide "
                     "pattern. The named terminals above are the right starting point for a site-level operational audit.",
)


# ══════════════════════════════════════════════════════════════════════════
# CHAPTER 3 — SUEZ CANAL DISRUPTION ANALYSIS
# ══════════════════════════════════════════════════════════════════════════
chapter_header(
    "3", "The Real Story: Suez Canal Disruption",
    "Five conventional explanations down, one partial lead from the terminals — we went back "
    "to the event that triggered this entire review, and this is where the data finally talks back."
)

# ---- H-06 EMEA regional impact --------------------------------------------
region_suez = df.groupby(["regional_hub", "suez_period"], observed=True).agg(
    median_duration=("move_duration", "median"), n=("movement_id", "count")
).reset_index()
pivot6 = region_suez.pivot(index="regional_hub", columns="suez_period", values="median_duration").reindex(columns=SUEZ_ORDER)
pivot6["pre_to_during_pct"] = (pivot6["During-Suez"] - pivot6["Pre-Suez"]) / pivot6["Pre-Suez"] * 100
emea_jump = pivot6.loc["EMEA", "pre_to_during_pct"]
next_best_region = pivot6.drop("EMEA")["pre_to_during_pct"].idxmax()
next_best_jump = pivot6.drop("EMEA")["pre_to_during_pct"].max()
normal_baseline = df.loc[df["suez_period"] == "Normal", "move_duration"].median()

def chart_region_suez():
    fig = go.Figure()
    period_colors = {"Pre-Suez": BRASS, "During-Suez": SIGNAL_RED, "Post-Suez": SEAFOAM}
    for period in ["Pre-Suez", "During-Suez", "Post-Suez"]:
        fig.add_trace(go.Bar(
            x=pivot6.index, y=pivot6[period], name=period, marker_color=period_colors[period],
        ))
    fig.add_hline(y=normal_baseline, line_dash="dot", line_color=SLATE, opacity=0.7,
                   annotation_text="Normal-period baseline", annotation_font_size=10, annotation_font_color=SLATE)
    fig.update_layout(barmode="group", yaxis_title="Median move duration (min)", xaxis_title="Regional hub")
    st.plotly_chart(style_fig(fig, height=380, showlegend=True), use_container_width=True, config={"displayModeBar": False})

hypothesis_card(
    number=6, chapter_tag="Suez Disruption",
    question="Were EMEA terminals hit harder by the Suez disruption than other regions?",
    hypothesis_stmt="EMEA terminals — geographically closest to the canal — were more affected "
                     "by the disruption than APAC, AMER, or LATAM.",
    why_matters="Confirming a regional concentration tells us exactly where to build disruption "
                "contingency capacity for the next chokepoint event, rather than spreading "
                "resilience investment evenly across a global network.",
    approach_bullets=[
        "Cross-tabulated <code>regional_hub</code> against <code>suez_period</code> (Pre / During / Post / Normal).",
        "Compared each region's median move duration moving from Pre-Suez into During-Suez.",
        "Benchmarked all four regions against the long-run Normal-period baseline to judge relative severity.",
    ],
    render_chart=chart_region_suez,
    finding_text=f"EMEA's median move duration jumped {emea_jump:.0f}% from Pre-Suez to During-Suez "
                 f"({pivot6.loc['EMEA','Pre-Suez']:.0f} → {pivot6.loc['EMEA','During-Suez']:.0f} min) — "
                 f"more than double the next-largest regional swing ({next_best_region} at {next_best_jump:.0f}%). "
                 "LATAM, by contrast, saw no increase at all over the same window.",
    status="Supported",
    conclusion_text="EMEA absorbed the disruption disproportionately, exactly as proximity to the canal "
                     "would predict. Treat this as confirmed, with the caveat that the During-Suez window "
                     "is only eight days of data per region, so the magnitude (not the direction) carries some uncertainty.",
)

# ---- H-07 Disruption spike --------------------------------------------------
monthly = df.groupby(df["date_id"].dt.to_period("M")).agg(
    avg_duration=("move_duration", "mean"), n=("movement_id", "count")
).reset_index()
monthly["date_id"] = monthly["date_id"].dt.to_timestamp()
suez_overall = df.groupby("suez_period", observed=True).agg(
    median_duration=("move_duration", "median"), n=("movement_id", "count")
).reindex(SUEZ_ORDER)
pre_med = suez_overall.loc["Pre-Suez", "median_duration"]
during_med = suez_overall.loc["During-Suez", "median_duration"]
pct_spike = (during_med - pre_med) / pre_med * 100
during_n = int(suez_overall.loc["During-Suez", "n"])

def chart_monthly_trend():
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["date_id"], y=monthly["avg_duration"], mode="lines",
        line=dict(color=NAVY_MED, width=2.2), fill="tozeroy",
        fillcolor="rgba(17,49,79,0.08)", name="Avg move duration",
    ))
    fig.add_vrect(x0="2021-03-23", x1="2021-06-30", fillcolor=SIGNAL_RED, opacity=0.10, line_width=0)
    fig.add_shape(
        type="line", x0="2021-03-23", x1="2021-03-23", y0=0, y1=1, yref="paper",
        line=dict(color=SIGNAL_RED, width=1.5, dash="dash"),
    )
    fig.add_annotation(x=pd.Timestamp("2021-03-23"), y=monthly["avg_duration"].max(),
                        text="Ever Given blocked", showarrow=False, yshift=14,
                        font=dict(color=SIGNAL_RED, size=11, family="IBM Plex Mono"))
    fig.update_layout(yaxis_title="Avg move duration (min)", xaxis_title="Month")
    fig.update_yaxes(rangemode="tozero")
    st.plotly_chart(style_fig(fig, height=380), use_container_width=True, config={"displayModeBar": False})

hypothesis_card(
    number=7, chapter_tag="Suez Disruption",
    question="Did move duration spike during the canal blockage itself?",
    hypothesis_stmt="Move duration increased significantly during the acute disruption "
                     "window of March 23–31, 2021.",
    why_matters="This is the load-bearing hypothesis of the whole review — if the disruption "
                "didn't actually move the KPI, the entire premise of the operational review needs revisiting.",
    approach_bullets=[
        "Aggregated move duration by month across the full 2021–2024 window to visualise the shape of the disruption.",
        "Compared median move duration specifically across Pre-Suez, During-Suez, and Post-Suez sub-periods.",
        f"Flagged the small sample size of the During-Suez window ({during_n} records) so the finding is read with appropriate caution.",
    ],
    render_chart=chart_monthly_trend,
    finding_text=f"Median move duration rose {pct_spike:.1f}% during the disruption window versus the "
                 f"Pre-Suez baseline ({pre_med:.0f} → {during_med:.0f} minutes), visible as a clear, if brief, "
                 "spike in the monthly trend. Duration eased back toward baseline in the Post-Suez period.",
    status="Supported",
    conclusion_text="The Suez disruption is associated with a real, measurable increase in cargo movement "
                     f"duration. With only {during_n} observations in the During-Suez window, treat the exact "
                     "percentage as directionally right rather than precise — but the effect itself is real.",
)

# ---- H-08 Post-disruption volume surge -------------------------------------
vol_suez = df.groupby("suez_period", observed=True).agg(
    median_containers=("container_count", "median"),
    total_containers=("container_count", "sum"),
    n=("movement_id", "count"),
).reindex(SUEZ_ORDER)
vol_range = vol_suez["median_containers"].max() - vol_suez["median_containers"].min()

def chart_volume_suez():
    ordered = vol_suez.reset_index()
    period_colors = {"Pre-Suez": BRASS, "During-Suez": SIGNAL_RED, "Post-Suez": SEAFOAM, "Normal": NAVY_MED}
    fig = go.Figure(go.Bar(
        x=ordered["suez_period"], y=ordered["median_containers"],
        marker_color=[period_colors[p] for p in ordered["suez_period"]],
        text=[f"{v:.0f}" for v in ordered["median_containers"]], textposition="outside",
    ))
    fig.update_layout(yaxis_title="Median containers per movement", xaxis_title="Period")
    fig.update_yaxes(range=[0, vol_suez["median_containers"].max() * 1.3])
    st.plotly_chart(style_fig(fig, height=340), use_container_width=True, config={"displayModeBar": False})

hypothesis_card(
    number=8, chapter_tag="Suez Disruption",
    question="Did cargo volume surge after the canal reopened, as ships caught up on backlog?",
    hypothesis_stmt="Cargo volume per movement increased in the Post-Suez period as terminals "
                     "absorbed a backlog of delayed shipments.",
    why_matters="A genuine backlog surge would mean the disruption's real cost was concentrated "
                "in the weeks after reopening, not just during the blockage — changing how recovery "
                "capacity should be planned and staffed.",
    approach_bullets=[
        "Compared median and total container counts per movement across Pre-, During-, and Post-Suez periods.",
        "Benchmarked all three against the long-run Normal-period baseline to isolate a disruption-specific effect.",
    ],
    render_chart=chart_volume_suez,
    finding_text=f"Median containers per movement stayed within a {vol_range:.0f}-container band across all "
                 f"four periods ({vol_suez['median_containers'].min():.0f}–{vol_suez['median_containers'].max():.0f}), "
                 "with no step-up in the Post-Suez period relative to Normal operations.",
    status="Not Supported",
    conclusion_text="There was no backlog-driven volume surge. The Suez disruption's cost was concentrated "
                     "in operational delay during the blockage itself (Hypothesis 7), not in a wave of "
                     "extra cargo afterward — a meaningfully different recovery story than leadership assumed.",
)

# ══════════════════════════════════════════════════════════════════════════
# SUMMARY — JOURNEY IN REVIEW
# ══════════════════════════════════════════════════════════════════════════
chapter_header(
    "4", "Journey in Review",
    "Eight hypotheses tested, three lenses applied. Here's what survived, what didn't, "
    "and what it means for the network's 15% move-duration target."
)

hyp_summary = [
    (1, "Older vessels cause slower handling", "Efficiency Anomaly", "Not Supported",
     f"{spread1_pct:.0f}% spread across age bands; effectively flat."),
    (2, "Cargo-type vessels slower than tankers", "Efficiency Anomaly", "Not Supported",
     f"{slowest_cat} slowest, but only {cat_spread:.0f} min above {fastest_cat}."),
    (3, "Higher container counts slow movements", "Efficiency Anomaly", "Not Supported",
     f"Correlation of {corr3:.4f} — no relationship."),
    (4, "Night shifts slower than day shifts", "Efficiency Anomaly", "Not Supported",
     f"Night is {abs(shift_diff):.1f} min faster, not slower."),
    (5, "Some terminals consistently slower", "Infrastructure Bottleneck", "Partially Supported",
     f"{t_spread_pct:.0f}% spread, concentrated in a handful of outlier terminals."),
    (6, "EMEA hit harder by the Suez disruption", "Suez Disruption", "Supported",
     f"EMEA +{emea_jump:.0f}% vs. next-largest regional swing of +{next_best_jump:.0f}%."),
    (7, "Move duration spiked during the blockage", "Suez Disruption", "Supported",
     f"+{pct_spike:.1f}% vs. Pre-Suez baseline (n={during_n})."),
    (8, "Cargo volume surged after reopening", "Suez Disruption", "Not Supported",
     f"Median containers stayed within a {vol_range:.0f}-unit band throughout."),
]

status_counts = pd.Series([h[3] for h in hyp_summary]).value_counts()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Hypotheses tested", len(hyp_summary))
m2.metric("Supported", int(status_counts.get("Supported", 0)))
m3.metric("Partially supported", int(status_counts.get("Partially Supported", 0)))
m4.metric("Not supported", int(status_counts.get("Not Supported", 0)))

row_parts = []
for num, q, chap, status, note in hyp_summary:
    cls = {"Supported": "stamp-supported", "Not Supported": "stamp-not-supported", "Partially Supported": "stamp-partial"}[status]
    row_parts.append(
        "<tr>"
        f'<td style="font-family:\'IBM Plex Mono\',monospace; color:#A6792B;">H{num:02d}</td>'
        f"<td>{q}</td>"
        f'<td style="color:#8493A6; font-size:0.82rem;">{chap}</td>'
        f'<td><span class="stamp {cls}" style="transform:none; font-size:0.68rem; padding:0.25rem 0.55rem;">{status}</span></td>'
        f'<td style="color:#8493A6; font-size:0.82rem;">{note}</td>'
        "</tr>"
    )
rows_html = "".join(row_parts)

table_html = (
    '<table class="summary-table">'
    "<tr><th>ID</th><th>Hypothesis</th><th>Lens</th><th>Outcome</th><th>Note</th></tr>"
    + rows_html +
    "</table>"
)
# NOTE: deliberately a single-line string with no embedded newlines/indentation —
# Streamlit's markdown parser will mis-render multi-line indented HTML as a code
# block (4+ leading spaces triggers Markdown's "indented code block" rule), which
# is what caused the dark unstyled box. Flattening to one line sidesteps that.
st.markdown(table_html, unsafe_allow_html=True)

st.markdown('<div style="height:1.8rem;"></div>', unsafe_allow_html=True)
insight_l, insight_r = st.columns([1, 1], gap="large")
with insight_l:
    st.markdown('<div class="section-label">Key Business Insights</div>', unsafe_allow_html=True)
    st.markdown("""
    <p class="hyp-body">
    <b>1. The "obvious" culprits weren't.</b> Vessel age, vessel category, cargo volume, and
    shift timing — four hypotheses any terminal manager would propose first — explain almost
    none of the variability in move duration. Resources currently aimed at these levers are
    unlikely to move the KPI.
    </p>
    <p class="hyp-body">
    <b>2. The disruption was real, but narrow.</b> The Suez Canal blockage produced a genuine,
    EMEA-concentrated spike in handling time — confirming leadership's original instinct — but
    it resolved within the Post-Suez window and never showed up as a volume backlog.
    </p>
    <p class="hyp-body">
    <b>3. The terminal layer is the most promising lever found.</b> A modest but real spread
    between the fastest and slowest terminals is the one efficiency factor in this dataset
    that's both real and actionable at a specific, named location.
    </p>
    """, unsafe_allow_html=True)
with insight_r:
    st.markdown('<div class="section-label">What This Means for the 15% Target</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <p class="hyp-body">
    None of the variables available in this dataset — vessel, cargo, or shift-level — explain
    the bulk of move-duration variability. The {t_spread_pct:.0f}% terminal-level spread is real
    but is concentrated in a small number of sites, not the whole network. That means the path
    to a 15% reduction in average move duration runs primarily through <b>site-specific
    operational fixes</b> at the slowest terminals and <b>disruption-readiness planning</b> for
    chokepoint events — not through fleet, cargo-mix, or staffing-schedule policy changes.
    </p>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-label" style="margin-top:1.8rem;">Final Recommendations</div>', unsafe_allow_html=True)
recs = [
    ("Audit the five slowest terminals by name",
     f"{', '.join(slowest5['terminal_name'].tolist())} run consistently above the network median. "
     "Investigate equipment, layout, and staffing at these sites before any fleet- or schedule-level change."),
    ("Stand down age- and category-based scheduling rules",
     "Vessel age and vessel category are not supported drivers of move duration. Reallocate any "
     "operational effort currently weighted toward these factors."),
    ("Build a chokepoint disruption playbook, anchored on EMEA",
     "The Suez event showed a clear, regionally concentrated, short-lived spike with no backlog "
     "surge. Pre-position contingency berth capacity and rapid-response staffing for EMEA "
     "specifically ahead of the next chokepoint disruption."),
    ("Instrument what this dataset can't see",
     "Vessel, cargo, and shift variables together explain very little of the remaining variance. "
     "The next data investment should capture crane allocation, berth scheduling, labor staffing "
     "levels, and customs/clearance time — the likely real drivers of the unexplained gap."),
]
for i, (title, text) in enumerate(recs, start=1):
    st.markdown(
        '<div class="rec-card">'
        f'<span class="rec-num">{i:02d}</span>'
        f'<div class="rec-title">{title}</div>'
        f'<div class="rec-text">{text}</div>'
        "</div>",
        unsafe_allow_html=True,
    )

st.markdown("""
<div style="margin-top:2.2rem; padding-top:1rem; border-top:1px solid #DCE3E6; font-size:0.8rem; color:#8493A6;">
    Analysis Journey · Global Maritime Solutions Q1 2025 Operational Review · </div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown(
"""
<div style="text-align:center; color:#64748B; font-size:0.82rem; line-height:1.7;">

<br>

Developed by <b>Dea Ramanda</b> |
Data Analyst • Machine Learning Enthusiast

<br>

<a href="https://github.com/USERNAME" target="_blank">GitHub</a>
&nbsp;&nbsp;•&nbsp;&nbsp;
<a href="https://linkedin.com/in/USERNAME" target="_blank">LinkedIn</a>

</div>
""",
unsafe_allow_html=True
)
