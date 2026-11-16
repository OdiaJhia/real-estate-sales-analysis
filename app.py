from pathlib import Path
import json
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
st.set_page_config(page_title="Real Estate Analytics", page_icon="🏠", layout="wide")
st.title("Real Estate Sales Performance & Customer Conversion Analysis")
st.caption("Academic demonstration using a simulated CRM dataset. Results are illustrative, not actual market statistics.")

@st.cache_data
def load_data():
    leads = pd.read_csv(DATA / "leads_clean.csv", parse_dates=["lead_date"])
    sales = pd.read_csv(DATA / "sales.csv", parse_dates=["closing_date"])
    results = json.loads((ROOT / "results.json").read_text(encoding="utf-8"))
    return leads, sales, results

leads, sales, results = load_data()
with st.sidebar:
    st.header("Dashboard filters")
    city_opts = sorted(leads.city.dropna().unique())
    source_opts = sorted(leads.lead_source.dropna().unique())
    type_opts = sorted(leads.property_type.dropna().unique())
    cities = st.multiselect("City", city_opts, default=city_opts)
    sources = st.multiselect("Lead source", source_opts, default=source_opts)
    types = st.multiselect("Property type", type_opts, default=type_opts)
    dmin, dmax = leads.lead_date.min().date(), leads.lead_date.max().date()
    date_range = st.date_input("Lead date range", value=(dmin, dmax), min_value=dmin, max_value=dmax)

if isinstance(date_range, tuple) and len(date_range) == 2:
    d1, d2 = date_range
else:
    d1, d2 = dmin, dmax
f = leads[leads.city.isin(cities) & leads.lead_source.isin(sources) &
          leads.property_type.isin(types) &
          leads.lead_date.dt.date.between(d1, d2)].copy()
f_sales = sales[sales.lead_id.isin(f.loc[f.converted.eq(1), "lead_id"])].copy()
n = len(f); bookings = int(f.converted.sum())
rev = float(f_sales.sale_price.sum())
conv = 100 * bookings / n if n else 0
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Leads", f"{n:,}")
c2.metric("Bookings", f"{bookings:,}")
c3.metric("Conversion", f"{conv:.2f}%")
c4.metric("Revenue", f"₹{rev/1e7:,.1f} Cr")
c5.metric("Avg deal", f"₹{(f_sales.sale_price.mean()/1e5 if len(f_sales) else 0):,.1f} Lakh")

tab1,tab2,tab3,tab4 = st.tabs(["Overview", "Funnel & Sources", "Property & City", "Predictive model"])
with tab1:
    st.subheader("Monthly revenue by closing month")
    if len(f_sales):
        monthly = f_sales.assign(month=f_sales.closing_date.dt.to_period("M").astype(str)).groupby("month").sale_price.sum()/1e7
        st.bar_chart(monthly)
    st.subheader("Sales by city")
    st.bar_chart(f_sales.groupby("city").sale_price.sum().sort_values(ascending=False)/1e7)
with tab2:
    st.subheader("Lead funnel")
    stages = ["Inquiry","Site Visit","Negotiation","Booking"]
    rank = {s:i for i,s in enumerate(stages)}
    counts = [n] + [int(f.furthest_stage.map(rank).ge(i).sum()) for i in range(1,4)]
    st.bar_chart(pd.Series(counts,index=stages))
    st.subheader("Conversion by lead source")
    if n:
        source = f.groupby("lead_source").converted.mean().mul(100).sort_values(ascending=False)
        st.bar_chart(source)
with tab3:
    st.subheader("Revenue by property type")
    if len(f_sales):
        st.bar_chart(f_sales.groupby("property_type").sale_price.sum().sort_values(ascending=False)/1e7)
    st.subheader("Average sale price per square foot by city")
    if len(f_sales):
        psf = f_sales.assign(psf=f_sales.sale_price/f_sales.area_sqft).groupby("city").psf.mean().sort_values(ascending=False)
        st.bar_chart(psf)
with tab4:
    st.subheader("Held-out model evaluation")
    model_df = pd.DataFrame(results["models"]).set_index("model")
    st.dataframe(model_df, use_container_width=True)
    st.info("Logistic regression has higher recall in this run, while both models have moderate AUC. A lead-scoring model is decision support, not a guarantee of conversion.")
st.subheader("Filtered lead records")
st.dataframe(f, use_container_width=True, hide_index=True)
st.download_button("Download filtered leads (CSV)", f.to_csv(index=False).encode("utf-8"),
                   "filtered_leads.csv", "text/csv")
