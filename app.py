from pathlib import Path
import json
import textwrap

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

st.set_page_config(
    page_title="Estate | Sales Intelligence",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Visual identity: Futuristic 3D / purple glass ----------
BG = "#09051B"
PAPER = "#17102E"
INK = "#F5F0FF"
MUTED = "#B7A9D8"
GREEN = "#A56BFF"
GREEN_LIGHT = "#2A1B49"
GOLD = "#F2B6FF"
GRID = "#38265A"

st.markdown(
    f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
      :root {{ --ink:{INK}; --muted:{MUTED}; --accent:{GREEN}; --gold:{GOLD}; --paper:{PAPER}; --bg:{BG}; }}
      .stApp {{ background:radial-gradient(ellipse at 15% 0%, #32145B 0%, #120A2B 36%, #09051B 78%); color:var(--ink); font-family:'DM Sans',sans-serif; }}
      [data-testid="stHeader"] {{ background:rgba(9,5,27,.78); }}
      [data-testid="stSidebar"] {{ background:linear-gradient(180deg,#160B30 0%,#0D0820 100%); border-right:1px solid #49316F; }}
      [data-testid="stSidebar"] * {{ color:var(--ink); }}
      .block-container {{ max-width:1500px; padding-top:1.6rem; padding-bottom:3rem; }}
      h1,h2,h3 {{ color:var(--ink); font-family:'Space Grotesk',sans-serif !important; }}
      h1 {{ letter-spacing:-.8px; }}
      p, label, span {{ font-family:'DM Sans',sans-serif; }}
      div[data-testid="stMetric"] {{ background:linear-gradient(145deg,rgba(53,29,91,.92),rgba(22,14,48,.94)); border:1px solid #7046A5; border-radius:18px; padding:17px 18px; box-shadow:0 0 22px rgba(151,76,255,.13), inset 0 1px 0 rgba(255,255,255,.09); }}
      div[data-testid="stMetricLabel"] p {{ color:#C9B7E8 !important; font-size:.76rem !important; font-weight:700 !important; letter-spacing:.08em; text-transform:uppercase; }}
      div[data-testid="stMetricValue"] {{ color:#FFFFFF !important; font-weight:700; text-shadow:0 0 16px rgba(188,127,255,.35); }}
      div[data-testid="stTabs"] button {{ color:#B7A9D8; font-weight:650; }}
      div[data-testid="stTabs"] button[aria-selected="true"] {{ color:#E6C7FF !important; border-bottom-color:#C17BFF !important; }}
      div[data-testid="stDataFrame"] {{ border:1px solid #49316F; border-radius:14px; overflow:hidden; }}
      .hero {{ position:relative; overflow:hidden; background:linear-gradient(112deg,rgba(37,15,72,.98) 0%,rgba(86,35,142,.94) 55%,rgba(36,19,78,.98) 100%); border:1px solid #A66BFF; border-radius:24px; padding:32px 36px; color:#FFF; margin:4px 0 25px 0; box-shadow:0 0 34px rgba(151,76,255,.22), inset 0 1px 0 rgba(255,255,255,.18); }}
      .hero:after {{ content:'⌂'; position:absolute; right:4%; bottom:-68px; font-size:245px; line-height:1; color:rgba(226,190,255,.10); text-shadow:0 0 35px rgba(201,135,255,.28); pointer-events:none; }}
      .hero-kicker {{ color:#E5B9FF; font-size:.72rem; font-weight:700; letter-spacing:.2em; text-transform:uppercase; margin-bottom:9px; }}
      .hero-title {{ color:#FFFFFF; font-family:'Space Grotesk',sans-serif; font-size:clamp(1.9rem,4vw,2.8rem); line-height:1.08; font-weight:700; margin:0 0 10px 0; text-shadow:0 0 24px rgba(211,157,255,.28); }}
      .hero-sub {{ color:#E6D9FA; font-size:.96rem; max-width:780px; line-height:1.55; margin:0; }}
      .section-kicker {{ color:#D99BFF; font-size:.70rem; font-weight:700; letter-spacing:.17em; text-transform:uppercase; margin:4px 0 5px 0; }}
      .section-title {{ font-family:'Space Grotesk',sans-serif; font-size:1.48rem; font-weight:650; color:var(--ink); margin:0 0 12px 0; }}
      .note {{ background:rgba(39,25,67,.86); border:1px solid #513576; border-left:3px solid #C17BFF; padding:12px 15px; border-radius:0 10px 10px 0; color:#D1C3E9; font-size:.86rem; line-height:1.5; }}
      .pill {{ display:inline-block; background:#352052; color:#E8C9FF; border:1px solid #8054B5; border-radius:30px; padding:5px 10px; font-size:.72rem; font-weight:700; letter-spacing:.04em; }}
      .stButton button, .stDownloadButton button {{ border-radius:10px; border:1px solid #B879FF; background:linear-gradient(100deg,#7C35D6,#B34DDB); color:white; font-weight:700; box-shadow:0 0 16px rgba(164,80,255,.18); }}
      .stButton button:hover, .stDownloadButton button:hover {{ background:linear-gradient(100deg,#914BEA,#CA65EC); color:white; border-color:#D7A3FF; }}
      [data-baseweb="select"] > div, [data-baseweb="input"] > div {{ background:#21143A; border-color:#604080; }}
      [data-testid="stExpander"] {{ background:rgba(25,15,47,.72); border:1px solid #49316F; border-radius:14px; }}
      hr {{ border-color:#49316F; }}
      footer {{ visibility:hidden; }}
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def load_data():
    leads = pd.read_csv(DATA / "leads_clean.csv", parse_dates=["lead_date"])
    sales = pd.read_csv(DATA / "sales.csv", parse_dates=["closing_date"])
    results = json.loads((ROOT / "results.json").read_text(encoding="utf-8"))
    return leads, sales, results


leads, sales, results = load_data()

# ---------- Sidebar filters ----------
with st.sidebar:
    st.markdown("<div class='section-kicker'>ESTATE INTELLIGENCE</div>", unsafe_allow_html=True)
    st.markdown("## Explore the data")
    st.caption("Refine the portfolio view using the filters below.")
    st.divider()
    city_opts = sorted(leads.city.dropna().unique())
    source_opts = sorted(leads.lead_source.dropna().unique())
    type_opts = sorted(leads.property_type.dropna().unique())
    cities = st.multiselect("Markets / cities", city_opts, default=city_opts)
    sources = st.multiselect("Acquisition channels", source_opts, default=source_opts)
    types = st.multiselect("Property category", type_opts, default=type_opts)
    dmin, dmax = leads.lead_date.min().date(), leads.lead_date.max().date()
    date_range = st.date_input("Lead creation period", value=(dmin, dmax), min_value=dmin, max_value=dmax)
    st.divider()
    st.markdown("<span class='pill'>LIVE FILTERS</span>", unsafe_allow_html=True)
    st.caption("All KPIs and charts update with your selections.")

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    d1, d2 = date_range
else:
    d1, d2 = dmin, dmax

f = leads[
    leads.city.isin(cities)
    & leads.lead_source.isin(sources)
    & leads.property_type.isin(types)
    & leads.lead_date.dt.date.between(d1, d2)
].copy()
f_sales = sales[sales.lead_id.isin(f.loc[f.converted.eq(1), "lead_id"])].copy()
n = len(f)
bookings = int(f.converted.sum()) if n else 0
rev = float(f_sales.sale_price.sum()) if len(f_sales) else 0.0
conv = 100 * bookings / n if n else 0.0
avg_deal = f_sales.sale_price.mean() / 1e5 if len(f_sales) else 0.0

# ---------- Hero ----------
st.markdown(
    """
    <div class="hero">
      <div class="hero-kicker">REAL ESTATE · SALES INTELLIGENCE</div>
      <div class="hero-title">Performance, viewed<br>with a clearer perspective.</div>
      <p class="hero-sub">A data-led view of lead quality, customer conversion and sales performance across markets, channels and property categories.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([3, 1])
with left:
    st.markdown("<div class='section-kicker'>PORTFOLIO SNAPSHOT</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Your performance at a glance</div>", unsafe_allow_html=True)
with right:
    st.markdown(f"<div style='text-align:right;padding-top:18px;color:{MUTED};font-size:.8rem'>Selected period<br><b style='color:{INK}'>{d1:%d %b %Y} — {d2:%d %b %Y}</b></div>", unsafe_allow_html=True)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total leads", f"{n:,}")
m2.metric("Bookings", f"{bookings:,}")
m3.metric("Conversion rate", f"{conv:.2f}%")
m4.metric("Sales revenue", f"₹{rev/1e7:,.1f} Cr")
m5.metric("Average deal", f"₹{avg_deal:,.1f} L")

st.markdown("<div class='note'>Academic demonstration using a simulated CRM dataset. The results illustrate the analytical workflow and must not be interpreted as actual real-estate market statistics.</div>", unsafe_allow_html=True)
st.write("")

# ---------- Chart helper ----------
def aesthetic_bar(series, title, ylabel="", percent=False, horizontal=False):
    series = series.dropna()
    fig, ax = plt.subplots(figsize=(8, 3.35), dpi=150)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    if len(series):
        values = series.values
        labels = [str(x) for x in series.index]
        if horizontal:
            bars = ax.barh(labels[::-1], values[::-1], color="#A56BFF", height=.58)
            ax.invert_yaxis()
            for bar, value in zip(bars, values[::-1]):
                label = f"{value:.1f}%" if percent else (f"₹{value:,.1f} Cr" if "revenue" in title.lower() else f"{value:,.0f}")
                ax.text(bar.get_width(), bar.get_y()+bar.get_height()/2, f"  {label}", va="center", color=INK, fontsize=8)
        else:
            bars = ax.bar(labels, values, color="#A56BFF", width=.62)
            for bar, value in zip(bars, values):
                label = f"{value:.1f}%" if percent else f"{value:,.1f}"
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height(), label, ha="center", va="bottom", color=INK, fontsize=8)
            ax.tick_params(axis="x", rotation=20)
        ax.set_ylabel(ylabel, color=MUTED, fontsize=8)
        ax.grid(axis="x" if horizontal else "y", color=GRID, linewidth=.8)
        ax.set_axisbelow(True)
    else:
        ax.text(.5, .5, "No records for the selected filters", ha="center", va="center", color=MUTED, transform=ax.transAxes)
    ax.set_title(title, loc="left", color=INK, fontsize=11, fontweight="bold", pad=14)
    ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=8, length=0)
    ax.margins(y=.18)
    fig.tight_layout(pad=1.3)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


# ---------- Main analysis sections ----------
tab1, tab2, tab3, tab4 = st.tabs(["  Overview  ", "  Conversion journey  ", "  Markets & properties  ", "  Predictive insights  "])

with tab1:
    st.markdown("<div class='section-kicker'>01 / REVENUE PERFORMANCE</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Where is the revenue coming from?</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if len(f_sales):
            monthly = f_sales.assign(month=f_sales.closing_date.dt.to_period("M").astype(str)).groupby("month").sale_price.sum() / 1e7
        else:
            monthly = pd.Series(dtype=float)
        aesthetic_bar(monthly, "Monthly revenue trend", "Revenue (₹ crore)")
    with c2:
        city_revenue = f_sales.groupby("city").sale_price.sum().sort_values(ascending=False) / 1e7 if len(f_sales) else pd.Series(dtype=float)
        aesthetic_bar(city_revenue, "Revenue by city", "Revenue (₹ crore)", horizontal=True)
    st.markdown("<div class='note'>Use the filters on the left to compare selected cities, channels and property categories over a chosen lead period.</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='section-kicker'>02 / CUSTOMER CONVERSION</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Understand the journey from inquiry to booking</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    stages = ["Inquiry", "Site Visit", "Negotiation", "Booking"]
    rank = {s: i for i, s in enumerate(stages)}
    counts = [n] + [int(f.furthest_stage.map(rank).ge(i).sum()) for i in range(1, 4)]
    with c1:
        aesthetic_bar(pd.Series(counts, index=stages), "Lead funnel by stage", "Number of leads")
    with c2:
        source_conversion = f.groupby("lead_source").converted.mean().mul(100).sort_values(ascending=False) if n else pd.Series(dtype=float)
        aesthetic_bar(source_conversion, "Conversion by acquisition channel", "Conversion (%)", percent=True, horizontal=True)
    st.markdown("<div class='note'>The funnel shows the furthest recorded stage reached by each lead. Conversion rates are calculated from the currently filtered lead records.</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='section-kicker'>03 / MARKET MIX</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Explore city and property performance</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        property_revenue = f_sales.groupby("property_type").sale_price.sum().sort_values(ascending=False) / 1e7 if len(f_sales) else pd.Series(dtype=float)
        aesthetic_bar(property_revenue, "Revenue by property category", "Revenue (₹ crore)")
    with c2:
        if len(f_sales):
            psf = f_sales.assign(psf=f_sales.sale_price / f_sales.area_sqft).groupby("city").psf.mean().sort_values(ascending=False)
        else:
            psf = pd.Series(dtype=float)
        aesthetic_bar(psf, "Average sale price per sq. ft.", "₹ per sq. ft.", horizontal=True)

with tab4:
    st.markdown("<div class='section-kicker'>04 / MODEL EVALUATION</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Predictive model performance</div>", unsafe_allow_html=True)
    model_df = pd.DataFrame(results["models"]).set_index("model")
    st.dataframe(model_df.style.format({c: "{:.3f}" for c in model_df.select_dtypes(include="number").columns}), use_container_width=True)
    if "importance" in results:
        importance = pd.Series(results["importance"]).sort_values(ascending=False).head(10)
        aesthetic_bar(importance, "Top model features", "Relative importance", horizontal=True)
    st.markdown("<div class='note'>Logistic regression has higher recall in this run, while both models show moderate AUC. The model is intended as decision support, not a guarantee that a lead will convert.</div>", unsafe_allow_html=True)

# ---------- Records ----------
st.divider()
with st.expander("Explore filtered lead records", expanded=False):
    st.caption(f"Showing {len(f):,} records based on the selected filters.")
    st.dataframe(f, use_container_width=True, hide_index=True)
    st.download_button(
        "Download filtered leads (CSV)",
        f.to_csv(index=False).encode("utf-8"),
        "filtered_leads.csv",
        "text/csv",
    )

st.markdown(
    f"<div style='text-align:center;color:{MUTED};font-size:.76rem;padding:22px 0 4px'>ESTATE INTELLIGENCE · FINAL YEAR DATA ANALYTICS PROJECT · SIMULATED DATASET</div>",
    unsafe_allow_html=True,
)
