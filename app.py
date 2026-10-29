import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sales & Customer Analytics", page_icon="📊", layout="wide")

NAVY = "#10243A"
TEAL = "#16B8A6"
st.markdown("""
<style>
    .stApp { background: #f4f7fb; }
    [data-testid="stMetric"] { background: white; padding: 16px; border-radius: 12px; border: 1px solid #e4eaf2; }
    h1, h2, h3 { color: #10243A; }
    div[data-testid="stSidebar"] { background: #eaf0f7; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Sales & Customer Analytics Dashboard")
st.caption("Python • Pandas • NumPy • Matplotlib • Streamlit | Demo data based on the internship report's data dictionary")

DATA_PATH = Path(__file__).parent / "data" / "sales_data.csv"

@st.cache_data
def load_data(file_bytes=None):
    if file_bytes is not None:
        data = pd.read_csv(file_bytes)
    else:
        data = pd.read_csv(DATA_PATH)
    data.columns = data.columns.str.strip().str.lower().str.replace(" ", "_")
    required = ["order_id", "order_date", "customer_id", "category", "region", "quantity", "price", "revenue"]
    missing_cols = [c for c in required if c not in data.columns]
    if missing_cols:
        raise ValueError("Missing required columns: " + ", ".join(missing_cols))
    data["order_date"] = pd.to_datetime(data["order_date"], errors="coerce")
    for c in ["quantity", "price", "revenue"]:
        data[c] = pd.to_numeric(data[c], errors="coerce")
    data["region"] = data["region"].fillna("Unknown")
    data["category"] = data["category"].fillna("Unknown")
    data = data.dropna(subset=["order_date", "order_id", "quantity", "price"])
    data = data.drop_duplicates(subset=["order_id"])
    # Revenue is recalculated from quantity and price for a consistent demo pipeline.
    data["revenue"] = data["quantity"] * data["price"]
    data["month"] = data["order_date"].dt.to_period("M").dt.to_timestamp()
    return data

st.sidebar.header("Data and filters")
uploaded = st.sidebar.file_uploader("Optional: upload your own CSV", type=["csv"])
try:
    df = load_data(uploaded) if uploaded is not None else load_data()
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

min_date, max_date = df["order_date"].min().date(), df["order_date"].max().date()
date_range = st.sidebar.date_input("Order date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

regions = sorted(df["region"].dropna().unique().tolist())
categories = sorted(df["category"].dropna().unique().tolist())
sel_regions = st.sidebar.multiselect("Region", regions, default=regions)
sel_categories = st.sidebar.multiselect("Category", categories, default=categories)

mask = (
    df["order_date"].dt.date.between(start_date, end_date)
    & df["region"].isin(sel_regions)
    & df["category"].isin(sel_categories)
)
filtered = df.loc[mask].copy()

st.markdown("#### Key performance indicators")
total_revenue = filtered["revenue"].sum()
orders = filtered["order_id"].nunique()
aov = total_revenue / orders if orders else 0
customers = filtered["customer_id"].nunique()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
c2.metric("Total Orders", f"{orders:,}")
c3.metric("Average Order Value", f"₹{aov:,.0f}")
c4.metric("Unique Customers", f"{customers:,}")

if filtered.empty:
    st.warning("No records match these filters. Change the date range, region, or category.")
    st.stop()

left, right = st.columns(2)
with left:
    st.subheader("Monthly revenue trend")
    monthly = filtered.groupby("month", as_index=False)["revenue"].sum().sort_values("month")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(monthly["month"], monthly["revenue"], marker="o", linewidth=2, color=TEAL)
    ax.set_ylabel("Revenue (₹)")
    ax.set_xlabel("Month")
    ax.grid(alpha=.25)
    fig.autofmt_xdate()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with right:
    st.subheader("Revenue by product category")
    by_cat = filtered.groupby("category")["revenue"].sum().sort_values()
    fig, ax = plt.subplots(figsize=(8, 4))
    by_cat.plot(kind="barh", ax=ax, color="#3677B8")
    ax.set_xlabel("Revenue (₹)")
    ax.set_ylabel("")
    ax.grid(axis="x", alpha=.2)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

left, right = st.columns(2)
with left:
    st.subheader("Regional performance")
    by_region = filtered.groupby("region", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
    st.dataframe(by_region.style.format({"revenue": "₹{:,.2f}"}), use_container_width=True, hide_index=True)
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(by_region["region"], by_region["revenue"], color="#F0A34A")
    ax.set_ylabel("Revenue (₹)")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(axis="y", alpha=.2)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with right:
    st.subheader("Customer insights")
    customer_summary = filtered.groupby("customer_id").agg(
        orders=("order_id", "nunique"),
        total_spend=("revenue", "sum")
    ).sort_values("total_spend", ascending=False)
    st.metric("Repeat customers", f"{int((customer_summary['orders'] > 1).sum()):,}")
    st.metric("Top customer spend", f"₹{customer_summary['total_spend'].max():,.0f}" if not customer_summary.empty else "₹0")
    st.caption("Customer metrics are calculated from the currently selected filters.")

st.subheader("Filtered transaction data")
st.dataframe(filtered.drop(columns=["month"]).sort_values("order_date", ascending=False), use_container_width=True, hide_index=True)
csv = filtered.drop(columns=["month"]).to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download filtered data as CSV", data=csv, file_name="filtered_sales_data.csv", mime="text/csv")

st.info("Demo notice: The bundled CSV is synthetic sample data created for demonstration. Replace it with authorized project data to produce genuine business findings.")
with st.expander("Data quality summary"):
    original = pd.read_csv(DATA_PATH)
    st.write(f"Rows in bundled raw file: **{len(original):,}**")
    st.write(f"Rows after cleaning: **{len(df):,}**")
    st.write(f"Duplicate order IDs removed: **{original['order_id'].duplicated().sum():,}**")
    st.write(f"Invalid or missing dates removed: **{pd.to_datetime(original['order_date'], errors='coerce').isna().sum():,}**")
    st.write("Missing regions are labeled as `Unknown`; duplicate order IDs are removed; date values are standardized; revenue is recalculated as quantity × price.")
