import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Dashboard Analitik UMKM",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #F8F9FA; }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #1E3A5F; }
    .metric-label { font-size: 0.85rem; color: #6B7280; margin-top: 4px; }
    .section-title { font-size: 1.2rem; font-weight: 600; color: #1E3A5F; margin: 16px 0 8px 0; }
    [data-testid="stSidebar"] { background-color: #1E3A5F; }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] .stSelectbox label { color: white !important; }
    h1 { color: #1E3A5F; }
    h2, h3 { color: #2C5282; }
</style>
""", unsafe_allow_html=True)

# ── Load Data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    import os
    base = os.path.dirname(__file__)

    products    = pd.read_csv(os.path.join(base, "data/products.csv"), parse_dates=["created_at", "updated_at"])
    users       = pd.read_csv(os.path.join(base, "data/users.csv"),    parse_dates=["created_at", "updated_at"])
    umkms       = pd.read_csv(os.path.join(base, "data/umkms.csv"),    parse_dates=["created_at", "updated_at"])
    members     = pd.read_csv(os.path.join(base, "data/umkm_members.csv"), parse_dates=["created_at"])
    transactions= pd.read_csv(os.path.join(base, "data/transactions.csv"),  parse_dates=["occurred_at"])
    profiles    = pd.read_csv(os.path.join(base, "data/profiles.csv"), parse_dates=["created_at", "updated_at", "date_of_birth"])
    return products, users, umkms, members, transactions, profiles

products, users, umkms, members, transactions, profiles = load_data()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏪 UMKM Analytics")
    st.markdown("---")
    page = st.radio(
        "Navigasi",
        ["🏠 Overview", "💸 Transaksi", "📦 Produk & UMKM", "👥 Pengguna", "📖 Data Dictionary"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("**Dataset**")
    st.markdown(f"- {len(umkms):,} UMKM")
    st.markdown(f"- {len(users):,} Pengguna")
    st.markdown(f"- {len(products):,} Produk")
    st.markdown(f"- {len(transactions):,} Transaksi")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 – OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.title("🏪 Dashboard Analitik UMKM")
    st.markdown("Ringkasan performa platform UMKM digital secara keseluruhan.")
    st.markdown("---")

    # KPI row
    total_revenue  = transactions[transactions["type"] == "income"]["amount"].sum()
    total_expense  = transactions[transactions["type"] == "expense"]["amount"].sum()
    net_profit     = total_revenue - total_expense
    avg_tx         = transactions["amount"].mean()

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label in [
        (c1, f"Rp {total_revenue/1e9:.2f}M", "Total Pendapatan (M)"),
        (c2, f"Rp {total_expense/1e9:.2f}M", "Total Pengeluaran (M)"),
        (c3, f"Rp {net_profit/1e6:.0f}Jt",   "Net Profit (Juta)"),
        (c4, f"Rp {avg_tx:,.0f}",             "Rata-rata Transaksi"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{val}</div>
            <div class="metric-label">{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    col_l, col_r = st.columns(2)

    # Monthly income trend
    with col_l:
        st.markdown('<div class="section-title">📈 Tren Pendapatan Bulanan</div>', unsafe_allow_html=True)
        income_df = transactions[transactions["type"] == "income"].copy()
        income_df["month"] = income_df["occurred_at"].dt.to_period("M").dt.to_timestamp()
        monthly = income_df.groupby("month")["amount"].sum().reset_index()
        monthly.columns = ["Bulan", "Total Pendapatan"]
        fig = px.area(monthly, x="Bulan", y="Total Pendapatan",
                      color_discrete_sequence=["#3182CE"],
                      template="plotly_white")
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=280,
                          yaxis_tickprefix="Rp ", yaxis_tickformat=",.0f")
        st.plotly_chart(fig, use_container_width=True)

    # Sector distribution
    with col_r:
        st.markdown('<div class="section-title">🏭 Distribusi Sektor UMKM</div>', unsafe_allow_html=True)
        sector_cnt = umkms["sector"].value_counts().reset_index()
        sector_cnt.columns = ["Sektor", "Jumlah"]
        fig2 = px.bar(sector_cnt, x="Jumlah", y="Sektor", orientation="h",
                      color="Jumlah", color_continuous_scale="Blues",
                      template="plotly_white")
        fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=280,
                           coloraxis_showscale=False, yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig2, use_container_width=True)

    col_l2, col_r2 = st.columns(2)

    # Income vs Expense
    with col_l2:
        st.markdown('<div class="section-title">⚖️ Pendapatan vs Pengeluaran per Bulan</div>', unsafe_allow_html=True)
        tx_monthly = transactions.copy()
        tx_monthly["month"] = tx_monthly["occurred_at"].dt.to_period("M").dt.to_timestamp()
        grouped = tx_monthly.groupby(["month", "type"])["amount"].sum().reset_index()
        fig3 = px.bar(grouped, x="month", y="amount", color="type",
                      barmode="group",
                      color_discrete_map={"income": "#38A169", "expense": "#E53E3E"},
                      labels={"amount": "Jumlah (Rp)", "month": "Bulan", "type": "Tipe"},
                      template="plotly_white")
        fig3.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=260,
                           yaxis_tickprefix="Rp ", yaxis_tickformat=",.0f",
                           legend_title_text="")
        st.plotly_chart(fig3, use_container_width=True)

    # UMKM growth
    with col_r2:
        st.markdown('<div class="section-title">🚀 Pertumbuhan UMKM Terdaftar</div>', unsafe_allow_html=True)
        umkms_m = umkms.copy()
        umkms_m["month"] = umkms_m["created_at"].dt.to_period("M").dt.to_timestamp()
        umkm_growth = umkms_m.groupby("month").size().cumsum().reset_index()
        umkm_growth.columns = ["Bulan", "Kumulatif UMKM"]
        fig4 = px.line(umkm_growth, x="Bulan", y="Kumulatif UMKM",
                       color_discrete_sequence=["#805AD5"], template="plotly_white")
        fig4.update_traces(line_width=2.5)
        fig4.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=260)
        st.plotly_chart(fig4, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 – TRANSAKSI
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💸 Transaksi":
    st.title("💸 Analisis Transaksi")
    st.markdown("---")

    # Filter
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        tipe = st.selectbox("Filter Tipe Transaksi", ["Semua", "income", "expense"])
    with col_f2:
        years = sorted(transactions["occurred_at"].dt.year.unique())
        year_sel = st.selectbox("Filter Tahun", ["Semua"] + [str(y) for y in years])

    tx_filtered = transactions.copy()
    if tipe != "Semua":
        tx_filtered = tx_filtered[tx_filtered["type"] == tipe]
    if year_sel != "Semua":
        tx_filtered = tx_filtered[tx_filtered["occurred_at"].dt.year == int(year_sel)]

    # Stats row
    c1, c2, c3 = st.columns(3)
    c1.metric("Jumlah Transaksi", f"{len(tx_filtered):,}")
    c2.metric("Total Nominal", f"Rp {tx_filtered['amount'].sum()/1e6:.1f}Jt")
    c3.metric("Rata-rata Nominal", f"Rp {tx_filtered['amount'].mean():,.0f}")

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-title">📊 Distribusi Nominal Transaksi</div>', unsafe_allow_html=True)
        fig = px.histogram(tx_filtered, x="amount", nbins=50,
                           color_discrete_sequence=["#3182CE"], template="plotly_white",
                           labels={"amount": "Nominal (Rp)"})
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=280)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">🥧 Proporsi Income vs Expense</div>', unsafe_allow_html=True)
        pie_df = transactions.groupby("type")["amount"].sum().reset_index()
        pie_df.columns = ["Tipe", "Total"]
        fig2 = px.pie(pie_df, names="Tipe", values="Total",
                      color_discrete_sequence=["#38A169", "#E53E3E"],
                      template="plotly_white")
        fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=280)
        st.plotly_chart(fig2, use_container_width=True)

    # Top UMKM by revenue
    st.markdown('<div class="section-title">🏆 Top 10 UMKM Berdasarkan Pendapatan</div>', unsafe_allow_html=True)
    top_umkm = (
        transactions[transactions["type"] == "income"]
        .groupby("umkm_id")["amount"].sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    top_umkm = top_umkm.merge(umkms[["id", "name", "sector"]], left_on="umkm_id", right_on="id", how="left")
    top_umkm.columns = ["umkm_id", "Total Pendapatan", "id", "Nama UMKM", "Sektor"]
    fig3 = px.bar(top_umkm, x="Total Pendapatan", y="Nama UMKM",
                  orientation="h", color="Sektor",
                  template="plotly_white",
                  labels={"Total Pendapatan": "Total Pendapatan (Rp)"})
    fig3.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=340,
                       yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig3, use_container_width=True)

    # Product name analysis
    st.markdown('<div class="section-title">📦 Top 10 Produk Terlaris (berdasarkan transaksi)</div>', unsafe_allow_html=True)
    prod_tx = transactions[transactions["product_name"].notna()]["product_name"].value_counts().head(10).reset_index()
    prod_tx.columns = ["Produk", "Jumlah Transaksi"]
    fig4 = px.bar(prod_tx, x="Jumlah Transaksi", y="Produk", orientation="h",
                  color_discrete_sequence=["#805AD5"], template="plotly_white")
    fig4.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300,
                       yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig4, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 – PRODUK & UMKM
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📦 Produk & UMKM":
    st.title("📦 Analisis Produk & UMKM")
    st.markdown("---")

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-title">🏷️ Jumlah Produk per Kategori (Top 15)</div>', unsafe_allow_html=True)
        cat_cnt = products["category"].value_counts().head(15).reset_index()
        cat_cnt.columns = ["Kategori", "Jumlah"]
        fig = px.bar(cat_cnt, x="Jumlah", y="Kategori", orientation="h",
                     color="Jumlah", color_continuous_scale="Teal",
                     template="plotly_white")
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=380,
                          coloraxis_showscale=False,
                          yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">💰 Rata-rata Harga per Kategori (Top 15)</div>', unsafe_allow_html=True)
        avg_price = products.groupby("category")["base_price"].mean().sort_values(ascending=False).head(15).reset_index()
        avg_price.columns = ["Kategori", "Rata-rata Harga"]
        fig2 = px.bar(avg_price, x="Rata-rata Harga", y="Kategori", orientation="h",
                      color_discrete_sequence=["#ED8936"],
                      template="plotly_white")
        fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=380,
                           xaxis_tickprefix="Rp ", xaxis_tickformat=",.0f",
                           yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig2, use_container_width=True)

    col_l2, col_r2 = st.columns(2)

    with col_l2:
        st.markdown('<div class="section-title">🏭 Sektor UMKM</div>', unsafe_allow_html=True)
        sector_pie = umkms["sector"].value_counts().reset_index()
        sector_pie.columns = ["Sektor", "Jumlah"]
        fig3 = px.pie(sector_pie, names="Sektor", values="Jumlah",
                      template="plotly_white", hole=0.4)
        fig3.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300)
        st.plotly_chart(fig3, use_container_width=True)

    with col_r2:
        st.markdown('<div class="section-title">📅 Pertumbuhan Produk Baru per Bulan</div>', unsafe_allow_html=True)
        prod_m = products.copy()
        prod_m["month"] = prod_m["created_at"].dt.to_period("M").dt.to_timestamp()
        prod_monthly = prod_m.groupby("month").size().reset_index(name="Jumlah Produk Baru")
        fig4 = px.bar(prod_monthly, x="month", y="Jumlah Produk Baru",
                      color_discrete_sequence=["#3182CE"], template="plotly_white",
                      labels={"month": "Bulan"})
        fig4.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300)
        st.plotly_chart(fig4, use_container_width=True)

    # Product price distribution
    st.markdown('<div class="section-title">📦 Distribusi Harga Produk</div>', unsafe_allow_html=True)
    fig5 = px.box(products, x="category", y="base_price",
                  color="category", template="plotly_white",
                  labels={"category": "Kategori", "base_price": "Harga (Rp)"})
    fig5.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=360,
                       showlegend=False, xaxis_tickangle=-45)
    st.plotly_chart(fig5, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 – PENGGUNA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👥 Pengguna":
    st.title("👥 Analisis Pengguna")
    st.markdown("---")

    # Merge profiles with users
    user_full = users.merge(profiles, left_on="id", right_on="user_id", how="left")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Pengguna", f"{len(users):,}")
    c2.metric("Punya Profil", f"{profiles['user_id'].nunique():,}")
    c3.metric("Owner UMKM", f"{members[members['role']=='owner']['user_id'].nunique():,}")
    c4.metric("Role Member", f"{members[members['role']=='member']['user_id'].nunique():,}" if 'member' in members['role'].values else "0")

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-title">⚧ Distribusi Gender</div>', unsafe_allow_html=True)
        gender = profiles["gender"].value_counts().reset_index()
        gender.columns = ["Gender", "Jumlah"]
        fig = px.pie(gender, names="Gender", values="Jumlah",
                     color_discrete_sequence=["#3182CE", "#F687B3", "#A0AEC0"],
                     template="plotly_white")
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=280)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">📅 Registrasi Pengguna per Bulan</div>', unsafe_allow_html=True)
        users_m = users.copy()
        users_m["month"] = users_m["created_at"].dt.to_period("M").dt.to_timestamp()
        user_monthly = users_m.groupby("month").size().reset_index(name="Pengguna Baru")
        fig2 = px.bar(user_monthly, x="month", y="Pengguna Baru",
                      color_discrete_sequence=["#38A169"], template="plotly_white",
                      labels={"month": "Bulan"})
        fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=280)
        st.plotly_chart(fig2, use_container_width=True)

    # Age distribution
    st.markdown('<div class="section-title">🎂 Distribusi Umur Pengguna</div>', unsafe_allow_html=True)
    prof_age = profiles.dropna(subset=["date_of_birth"]).copy()
    prof_age["age"] = (pd.Timestamp("today") - prof_age["date_of_birth"]).dt.days // 365
    prof_age = prof_age[(prof_age["age"] > 10) & (prof_age["age"] < 80)]
    fig3 = px.histogram(prof_age, x="age", nbins=30, color="gender",
                        color_discrete_sequence=["#3182CE", "#F687B3"],
                        barmode="overlay", template="plotly_white",
                        labels={"age": "Umur", "gender": "Gender"},
                        opacity=0.8)
    fig3.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300)
    st.plotly_chart(fig3, use_container_width=True)

    # Role distribution
    st.markdown('<div class="section-title">🎭 Distribusi Role di UMKM</div>', unsafe_allow_html=True)
    role_cnt = members["role"].value_counts().reset_index()
    role_cnt.columns = ["Role", "Jumlah"]
    fig4 = px.bar(role_cnt, x="Role", y="Jumlah",
                  color_discrete_sequence=["#805AD5"], template="plotly_white")
    fig4.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=260)
    st.plotly_chart(fig4, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 – DATA DICTIONARY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📖 Data Dictionary":
    st.title("📖 Data Dictionary")
    st.markdown("Dokumentasi lengkap untuk setiap tabel dan kolom dalam dataset UMKM.")
    st.markdown("---")

    tables = {
        "🧾 users": pd.DataFrame([
            ["id", "VARCHAR", "Primary key unik pengguna", "USR001"],
            ["email", "VARCHAR", "Alamat email pengguna (unique)", "user@example.com"],
            ["password_hash", "VARCHAR", "Hash password (tidak plain text)", "hashed_xxx"],
            ["name", "VARCHAR", "Nama lengkap pengguna", "Budi Santoso"],
            ["role", "VARCHAR", "Role global: 'user' atau 'admin'", "user"],
            ["created_at", "DATETIME", "Waktu registrasi akun", "2022-07-16 18:43:51"],
            ["updated_at", "DATETIME", "Waktu update terakhir", "2023-05-07 18:43:51"],
        ], columns=["Kolom", "Tipe", "Deskripsi", "Contoh"]),

        "🏪 umkms": pd.DataFrame([
            ["id", "VARCHAR", "Primary key unik UMKM", "UMKM001"],
            ["name", "VARCHAR", "Nama usaha UMKM", "Rental Panji"],
            ["sector", "VARCHAR", "Sektor bisnis (Kuliner, Fashion, dll.)", "Transportasi"],
            ["description", "TEXT", "Deskripsi singkat usaha", "Layanan same-day delivery..."],
            ["created_at", "DATETIME", "Tanggal UMKM terdaftar", "2022-07-17 18:43:51"],
            ["updated_at", "DATETIME", "Tanggal update terakhir", "2023-02-22 18:43:51"],
            ["photo_url", "VARCHAR", "URL foto profil UMKM (nullable)", "https://cdn..."],
        ], columns=["Kolom", "Tipe", "Deskripsi", "Contoh"]),

        "📦 products": pd.DataFrame([
            ["id", "VARCHAR", "Primary key unik produk", "PRD001"],
            ["umkm_id", "VARCHAR", "FK ke tabel umkms", "UMKM001"],
            ["name", "VARCHAR", "Nama produk/jasa", "Jasa Packing Barang"],
            ["category", "VARCHAR", "Kategori produk (Catering, Sepatu, dll.)", "Logistik"],
            ["base_price", "INTEGER", "Harga dasar produk dalam Rupiah", "1359000"],
            ["created_at", "DATETIME", "Tanggal produk ditambahkan", "2022-07-17 18:43:51"],
            ["updated_at", "DATETIME", "Tanggal produk diperbarui", "2022-12-19 18:43:51"],
        ], columns=["Kolom", "Tipe", "Deskripsi", "Contoh"]),

        "💸 transactions": pd.DataFrame([
            ["id", "VARCHAR", "Primary key unik transaksi", "TRX001"],
            ["umkm_id", "VARCHAR", "FK ke tabel umkms", "UMKM001"],
            ["type", "VARCHAR", "Tipe transaksi: 'income' atau 'expense'", "income"],
            ["amount", "FLOAT", "Nominal transaksi dalam Rupiah", "105000.0"],
            ["note", "VARCHAR", "Keterangan transaksi (nullable)", "Pembayaran tunai"],
            ["occurred_at", "DATETIME", "Waktu transaksi terjadi", "2023-03-21 18:43:51"],
            ["product_name", "VARCHAR", "Nama produk terkait transaksi (nullable)", "Jasa Packing Barang"],
        ], columns=["Kolom", "Tipe", "Deskripsi", "Contoh"]),

        "👥 umkm_members": pd.DataFrame([
            ["id", "VARCHAR", "Primary key keanggotaan", "ROLE001"],
            ["user_id", "VARCHAR", "FK ke tabel users", "USR001"],
            ["umkm_id", "VARCHAR", "FK ke tabel umkms", "UMKM001"],
            ["role", "VARCHAR", "Role di UMKM: 'owner', 'admin', 'member'", "owner"],
            ["created_at", "DATETIME", "Tanggal bergabung", "2022-07-17 19:09:51"],
        ], columns=["Kolom", "Tipe", "Deskripsi", "Contoh"]),

        "👤 profiles": pd.DataFrame([
            ["id", "VARCHAR", "Primary key profil", "PRFL593"],
            ["user_id", "VARCHAR", "FK ke tabel users (unique)", "USR593"],
            ["gender", "VARCHAR", "Jenis kelamin: Laki-laki / Perempuan", "Laki-laki"],
            ["phone_number", "VARCHAR", "Nomor HP (format 62xxx)", "628570320203"],
            ["address", "TEXT", "Alamat lengkap", "Jalan Suryakencana No.88..."],
            ["date_of_birth", "DATE", "Tanggal lahir", "2007-09-03"],
            ["photo_url", "VARCHAR", "URL foto profil (nullable)", "https://cdn..."],
            ["created_at", "DATETIME", "Tanggal profil dibuat", "2021-01-13 12:35:39"],
            ["updated_at", "DATETIME", "Tanggal profil diperbarui", "2021-01-30 12:35:39"],
        ], columns=["Kolom", "Tipe", "Deskripsi", "Contoh"]),
    }

    for table_name, df_dict in tables.items():
        with st.expander(table_name, expanded=False):
            st.dataframe(df_dict, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 🔗 Relasi Antar Tabel")
    st.markdown("""
    ```
    users ──────────────────────────── profiles  (users.id = profiles.user_id)
    users ──────────────────────────── umkm_members (users.id = umkm_members.user_id)
    umkms ──────────────────────────── umkm_members (umkms.id = umkm_members.umkm_id)
    umkms ──────────────────────────── products   (umkms.id = products.umkm_id)
    umkms ──────────────────────────── transactions (umkms.id = transactions.umkm_id)
    ```
    """)

    st.markdown("### 📊 Ringkasan Dataset")
    summary = pd.DataFrame([
        ["users", len(users), 7, "2022 – 2024", "Pengguna terdaftar pada platform"],
        ["umkms", len(umkms), 7, "2022 – 2024", "Usaha UMKM yang terdaftar"],
        ["products", len(products), 7, "2022 – 2024", "Produk/jasa yang ditawarkan UMKM"],
        ["transactions", len(transactions), 7, "2023 – 2024", "Catatan keuangan pemasukan & pengeluaran"],
        ["umkm_members", len(members), 5, "2022 – 2024", "Relasi user & UMKM beserta rolnya"],
        ["profiles", len(profiles), 9, "2021 – 2024", "Detail profil pengguna"],
    ], columns=["Tabel", "Jumlah Baris", "Jumlah Kolom", "Rentang Waktu", "Keterangan"])
    st.dataframe(summary, use_container_width=True, hide_index=True)
