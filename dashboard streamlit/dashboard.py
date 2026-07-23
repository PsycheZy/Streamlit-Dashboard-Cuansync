import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Cuansync UMKM",
    page_icon="📊",
    layout="wide",
)

# ── Color palette ─────────────────────────────────────────────────────────────
PRIMARY   = "#5B7DB1"
ACCENT    = "#F2B880"
SUCCESS   = "#6DBF8A"
DANGER    = "#E07070"
BG_CARD   = "#F8F9FB"

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(__file__)
    transactions = pd.read_csv(os.path.join(base, "data/transactions.csv"))
    umkms        = pd.read_csv(os.path.join(base, "data/umkms.csv"))
    products     = pd.read_csv(os.path.join(base, "data/products.csv"))
    

    transactions["occurred_at"] = pd.to_datetime(transactions["occurred_at"], errors="coerce")
    transactions["amount"]      = pd.to_numeric(transactions["amount"], errors="coerce")
    transactions["type"] = transactions["type"].replace({
        "income": 1,
        "expense": 0
    })
    transactions["tahun_bulan"] = transactions["occurred_at"].dt.to_period("M")
    transactions["tahun"]       = transactions["occurred_at"].dt.year
    transactions["bulan"]       = transactions["occurred_at"].dt.month
    transactions["nama_bulan"]  = transactions["occurred_at"].dt.strftime("%b")
    transactions["hari"]        = transactions["occurred_at"].dt.day_name()

    return transactions, umkms, products

transactions, umkms, products = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📊 Cuansync UMKM")
    st.markdown("Dashboard Analisis Bisnis UMKM")
    st.divider()

    # Ambil range tanggal dari data
    min_date = transactions["occurred_at"].min().date()
    max_date = transactions["occurred_at"].max().date()

    # ── Quick Filter ─────────────────────────────────────
    st.markdown("**Quick Filter**")

    preset = st.selectbox(
        "Pilih Periode",
        [
            "Semua Data",
            "2021",
            "2022",
            "2023",
            "2024",
            "2025",
            "Custom Range"
        ],
        key="periode_filter"
    )

    # Default value
    start_date = min_date
    end_date = max_date

    if preset == "2021":
        start_date = pd.to_datetime("2021-02-07").date()
        end_date = pd.to_datetime("2021-12-31").date()

    elif preset == "2022":
        start_date = pd.to_datetime("2022-01-01").date()
        end_date = pd.to_datetime("2022-12-31").date()

    elif preset == "2023":
        start_date = pd.to_datetime("2023-01-01").date()
        end_date = pd.to_datetime("2023-12-31").date()

    elif preset == "2024":
        start_date = pd.to_datetime("2024-01-01").date()
        end_date = pd.to_datetime("2024-12-31").date()

    elif preset == "2025":
        start_date = pd.to_datetime("2025-01-01").date()
        end_date = pd.to_datetime("2025-12-05").date()

    elif preset == "Custom Range":

        st.markdown("**Pilih Rentang Tanggal**")

        date_range = st.date_input(
            label="Rentang Tanggal",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            label_visibility="collapsed",
            key="custom_date_range"
        )

        # kalau user baru pilih 1 tanggal
        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = min_date, max_date

    # ── Filter sektor ───────────────────────────────────
    sektor_list = sorted(umkms["sector"].dropna().unique().tolist())

    selected_sectors = st.multiselect(
        "Filter Sektor",
        options=sektor_list,
        default=sektor_list,
        key="sector_filter"
    )

    st.divider()

    st.caption(
        f"Data: {start_date.strftime('%d %b %Y')} – "
        f"{end_date.strftime('%d %b %Y')}"
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📊 Dashboard Analisis Bisnis UMKM – Cuansync")
st.markdown("Analisis performa keuangan dan penjualan UMKM berdasarkan data transaksi.")
st.divider()
# ── Filter data ───────────────────────────────────────────────────────────────
import datetime
start_dt = pd.Timestamp(start_date)
end_dt   = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

trx_filtered = transactions[
    (transactions["occurred_at"] >= start_dt) &
    (transactions["occurred_at"] <= end_dt)
]

umkms_filtered = umkms[umkms["sector"].isin(selected_sectors)]

trx_sector_all = pd.merge(
    transactions,
    umkms[["id", "sector"]],
    left_on="umkm_id", right_on="id",
    how="left",
    suffixes=("", "_umkm"),
)

trx_sector = pd.merge(
    trx_filtered,
    umkms_filtered[["id", "sector"]],
    left_on="umkm_id", right_on="id",
    how="inner",
    suffixes=("", "_umkm"),
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("Dashboard Analisis Bisnis UMKM – Cuansync")
st.markdown("Analisis performa keuangan dan penjualan UMKM berdasarkan data transaksi.")
st.divider()

# ── KPI Cards ─────────────────────────────────────────────────────────────────
income_total  = trx_sector[trx_sector["type"] == 1]["amount"].sum()
expense_total = trx_sector[trx_sector["type"] == 0]["amount"].sum()
net_profit    = income_total - expense_total
trx_count     = len(trx_sector)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Pendapatan", f"Rp {income_total/1e6:,.1f} Jt")
with col2:
    st.metric("Total Pengeluaran", f"Rp {expense_total/1e6:,.1f} Jt")
with col3:
    margin = (net_profit / income_total * 100) if income_total > 0 else 0
    st.metric("Laba Bersih", f"Rp {net_profit/1e6:,.1f} Jt", delta=f"{margin:.1f}% margin")
with col4:
    st.metric("Total Transaksi", f"{trx_count:,}")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# PB 1 — Sektor dengan pendapatan & profit terbesar
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("1. Sektor Usaha dengan Pendapatan & Profit Terbesar")

sector_income  = trx_sector[trx_sector["type"] == 1].groupby("sector")["amount"].sum()
sector_expense = trx_sector[trx_sector["type"] == 0].groupby("sector")["amount"].sum()

sector_summary = pd.DataFrame({
    "total_income":  sector_income,
    "total_expense": sector_expense,
}).fillna(0)
sector_summary["net_profit"]    = sector_summary["total_income"] - sector_summary["total_expense"]
sector_summary["profit_margin"] = (sector_summary["net_profit"] / sector_summary["total_income"] * 100).round(1)
sector_summary = sector_summary.sort_values("total_income", ascending=False)

col_a, col_b = st.columns(2)

with col_a:
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.barh(sector_summary.index, sector_summary["total_income"] / 1e6, color=PRIMARY, edgecolor="none")
    ax.set_xlabel("Total Pendapatan (Juta Rp)")
    ax.set_title("Pendapatan per Sektor")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Rp {x:.0f}"))
    ax.invert_yaxis()
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col_b:
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = [SUCCESS if v >= 0 else DANGER for v in sector_summary["net_profit"]]
    ax.barh(sector_summary.index, sector_summary["net_profit"] / 1e6, color=colors, edgecolor="none")
    ax.axvline(0, color="gray", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Laba Bersih (Juta Rp)")
    ax.set_title("Laba Bersih per Sektor")
    ax.invert_yaxis()
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

top_income_sector = sector_summary["total_income"].idxmax()
top_profit_sector = sector_summary["net_profit"].idxmax()
top_margin_sector = sector_summary["profit_margin"].idxmax()

st.info(
    f"**Insight:** Sektor **{top_income_sector}** mencatatkan pendapatan tertinggi "
    f"(Rp {sector_summary.loc[top_income_sector, 'total_income']/1e6:,.1f} Jt). "
    f"Sektor dengan laba bersih terbesar adalah **{top_profit_sector}**, "
    f"sementara profit margin tertinggi dimiliki **{top_margin_sector}** "
    f"({sector_summary.loc[top_margin_sector, 'profit_margin']:.1f}%)."
)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# PB 2 — Tren pendapatan, pengeluaran, laba bersih dari waktu ke waktu
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("2. Tren Keuangan UMKM dari Waktu ke Waktu")

monthly = (
    trx_sector
    .groupby(["tahun_bulan", "type"])["amount"]
    .sum()
    .unstack(fill_value=0)
    .reset_index()
)
monthly["tahun_bulan_dt"] = monthly["tahun_bulan"].dt.to_timestamp()
monthly = monthly.sort_values("tahun_bulan_dt")
monthly["net_profit"] = monthly.get(1, 0) - monthly.get(0, 0)

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(
    monthly["tahun_bulan_dt"],
    monthly.get(1, pd.Series(0, index=monthly.index)) / 1e6,
    label="Pendapatan",
    color=PRIMARY,
    linewidth=2,
    marker="o",
    markersize=3
)

ax.plot(monthly["tahun_bulan_dt"], monthly.get(0, pd.Series(0, index=monthly.index)) / 1e6, label="Pengeluaran", color=DANGER, linewidth=2, marker="o", markersize=3)
ax.fill_between(monthly["tahun_bulan_dt"], monthly["net_profit"] / 1e6, 0, where=monthly["net_profit"] >= 0, alpha=0.15, color=SUCCESS, label="Laba Bersih (+)")
ax.fill_between(monthly["tahun_bulan_dt"], monthly["net_profit"] / 1e6, 0, where=monthly["net_profit"] < 0, alpha=0.15, color=DANGER, label="Laba Bersih (-)")
ax.set_ylabel("Jumlah (Juta Rp)")
ax.set_title("Tren Bulanan: Pendapatan, Pengeluaran & Laba Bersih")
ax.legend(loc="upper left", fontsize=8)
ax.spines[["top", "right"]].set_visible(False)
plt.xticks(rotation=30, ha="right", fontsize=8)
plt.tight_layout()
st.pyplot(fig)
plt.close()

# Growth tabel ringkas
if len(monthly) >= 2:
    latest = monthly.iloc[-1]
    prev   = monthly.iloc[-2]
    income_growth = ((latest.get(1, 0) - prev.get(1, 0)) / prev.get(1, 1) * 100)
    st.info(
        f"**Insight:** Rentang data dari "
        f"**{monthly['tahun_bulan_dt'].min().strftime('%b %Y')}** hingga "
        f"**{monthly['tahun_bulan_dt'].max().strftime('%b %Y')}**. "
        f"Pertumbuhan pendapatan bulan terakhir: "
        f"{'▲' if income_growth >= 0 else '▼'} **{abs(income_growth):.1f}%** dibanding bulan sebelumnya."
    )

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# PB 3 — Produk & kategori paling berkontribusi terhadap pendapatan
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("3. Produk & Kategori Paling Berkontribusi terhadap Pendapatan")

income_trx = trx_sector[
    (trx_sector["type"] == 1) &
    (trx_sector["product_name"].notna()) &
    (trx_sector["product_name"].astype(str).str.strip() != "")
].copy()

income_trx = income_trx.merge(
    products[["name", "category"]].drop_duplicates(subset="name"),
    left_on="product_name", right_on="name",
    how="left",
    suffixes=("", "_prod"),
)

col_c, col_d = st.columns(2)

with col_c:
    category_summary = (
        income_trx.groupby("category")
        .agg(revenue=("amount", "sum"), jumlah_transaksi=("amount", "count"))
        .sort_values("jumlah_transaksi", ascending=False)
        .head(15)
    )
    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.barh(category_summary.index[::-1], category_summary["jumlah_transaksi"][::-1],
                   color=PRIMARY, edgecolor="none")
    ax.set_xlabel("Jumlah Transaksi")
    ax.set_title("Top 15 Kategori berdasarkan Volume Transaksi")
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col_d:
    product_summary = (
        income_trx.groupby("product_name")
        .agg(revenue=("amount", "sum"), jumlah_transaksi=("amount", "count"))
        .sort_values("revenue", ascending=False)
    )
    total_rev = product_summary["revenue"].sum()
    product_summary["kontribusi_pct"] = product_summary["revenue"] / total_rev * 100
    product_summary["kumulatif_pct"]  = product_summary["kontribusi_pct"].cumsum()

    top15 = product_summary.head(15).reset_index()

    fig, ax1 = plt.subplots(figsize=(6, 5))
    ax2 = ax1.twinx()
    x_pos = range(len(top15))
    ax1.bar(x_pos, top15["revenue"] / 1e6, color=ACCENT, edgecolor="none", label="Revenue")
    ax2.plot(x_pos, top15["kumulatif_pct"], color=PRIMARY, marker="o", markersize=4, linewidth=2, label="Kumulatif %")
    ax2.axhline(80, color="gray", linestyle="--", linewidth=1)
    ax2.set_ylim(0, 105)
    ax2.set_ylabel("Kumulatif %")
    ax1.set_ylabel("Revenue (Juta Rp)")
    ax1.set_title("Pareto Chart – Top 15 Produk")
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(top15["product_name"], rotation=45, ha="right", fontsize=7)
    ax1.spines[["top"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

pareto_products = product_summary[product_summary["kumulatif_pct"] <= 80]
n_pareto = len(pareto_products)
top_cat = category_summary["revenue"].idxmax() if not category_summary.empty else "-"

st.info(
    f"**Insight:** Kategori **{top_cat}** mendominasi volume transaksi. "
    f"Sekitar **{n_pareto} produk teratas** menyumbang ~80% total revenue (Pareto 80/20)."
)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# PB 4 — Periode penjualan tertinggi & terendah
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("4. Periode Penjualan Tertinggi dan Terendah")

income_time = trx_sector[trx_sector["type"] == 1].copy()

col_e, col_f = st.columns(2)

with col_e:
    # Per bulan (agregasi semua tahun)
    bulan_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Mei",6:"Jun",
                 7:"Jul",8:"Agt",9:"Sep",10:"Okt",11:"Nov",12:"Des"}
    monthly_agg = (
        income_time.groupby("bulan")["amount"]
        .sum()
        .reset_index()
        .sort_values("bulan")
    )
    monthly_agg["nama_bulan"] = monthly_agg["bulan"].map(bulan_map)

    max_bulan = monthly_agg.loc[monthly_agg["amount"].idxmax(), "nama_bulan"]
    min_bulan = monthly_agg.loc[monthly_agg["amount"].idxmin(), "nama_bulan"]
    bar_colors = [
        SUCCESS if r["nama_bulan"] == max_bulan else
        DANGER  if r["nama_bulan"] == min_bulan else
        PRIMARY
        for _, r in monthly_agg.iterrows()
    ]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(monthly_agg["nama_bulan"], monthly_agg["amount"] / 1e6, color=bar_colors, edgecolor="none")
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Total Pendapatan (Juta Rp)")
    ax.set_title("Pola Penjualan per Bulan (Semua Tahun)")
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col_f:
    # Per hari dalam seminggu
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    day_label = ["Sen","Sel","Rab","Kam","Jum","Sab","Min"]
    daily_agg = (
        income_time.groupby("hari")["amount"]
        .sum()
        .reindex(day_order, fill_value=0)
        .reset_index()
    )
    daily_agg["label"] = day_label

    max_hari = daily_agg.loc[daily_agg["amount"].idxmax(), "label"]
    min_hari = daily_agg.loc[daily_agg["amount"].idxmin(), "label"]
    hari_colors = [
        SUCCESS if r["label"] == max_hari else
        DANGER  if r["label"] == min_hari else
        ACCENT
        for _, r in daily_agg.iterrows()
    ]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(daily_agg["label"], daily_agg["amount"] / 1e6, color=hari_colors, edgecolor="none")
    ax.set_xlabel("Hari")
    ax.set_ylabel("Total Pendapatan (Juta Rp)")
    ax.set_title("Pola Penjualan per Hari dalam Seminggu")
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# Periode tahunan
yearly_income = (
    income_time.groupby("tahun")["amount"].sum()
    .sort_index()
    .reset_index()
)
if len(yearly_income) > 1:
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(yearly_income["tahun"].astype(str), yearly_income["amount"] / 1e6,
            marker="o", color=PRIMARY, linewidth=2.5)
    ax.fill_between(yearly_income["tahun"].astype(str), yearly_income["amount"] / 1e6, alpha=0.15, color=PRIMARY)
    ax.set_ylabel("Total Pendapatan (Juta Rp)")
    ax.set_title("Tren Penjualan per Tahun")
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

peak_bulan_val = monthly_agg.loc[monthly_agg["amount"].idxmax(), "amount"] / 1e6
low_bulan_val  = monthly_agg.loc[monthly_agg["amount"].idxmin(), "amount"] / 1e6

st.info(
    f"**Insight:** Penjualan tertinggi terjadi di bulan **{max_bulan}** "
    f"(Rp {peak_bulan_val:,.1f} Jt) dan terendah di bulan **{min_bulan}** "
    f"(Rp {low_bulan_val:,.1f} Jt). "
    f"Hari dengan volume penjualan tertinggi adalah **{max_hari}**, "
    f"sedangkan terendah di hari **{min_hari}**."
)

st.divider()
st.caption("Dashboard ini dibuat sebagai bagian dari Proyek Capstone – Cuansync UMKM Analytics")
