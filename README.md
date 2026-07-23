# 🏪 Dashboard Analitik UMKM

Dashboard interaktif berbasis **Streamlit** untuk menganalisis performa platform UMKM digital.

## Struktur Folder

```
dashboard/
├── app.py              # File utama Streamlit
├── requirements.txt    # Dependensi Python
├── README.md           # Dokumentasi ini
└── data/               # Dataset CSV
    ├── products.csv
    ├── users.csv
    ├── umkms.csv
    ├── umkm_members.csv
    ├── transactions.csv
    └── profiles.csv
```

## Cara Menjalankan

### 1. Install dependensi

```bash
pip install -r requirements.txt
```

### 2. Jalankan dashboard

```bash
streamlit run app.py
```

Dashboard akan terbuka otomatis di browser: `http://localhost:8501`

## Halaman Dashboard

| Halaman         | Konten                                                          |
| --------------- | --------------------------------------------------------------- |
| Overview        | KPI utama, tren pendapatan, distribusi sektor, pertumbuhan UMKM |
| Transaksi       | Analisis income vs expense, top UMKM, produk terlaris           |
| Produk & UMKM   | Kategori produk, harga, distribusi sektor                       |
| Pengguna        | Demografi gender, usia, registrasi bulanan                      |
| Data Dictionary | Dokumentasi lengkap semua tabel & kolom                         |

## 🗃️ Dataset

| Tabel        | Baris | Deskripsi          |
| ------------ | ----- | ------------------ |
| products     | 2.119 | Produk/jasa UMKM   |
| users        | 664   | Pengguna terdaftar |
| umkms        | 731   | Data UMKM          |
| umkm_members | 682   | Relasi user-UMKM   |
| transactions | 5.537 | Catatan keuangan   |
| profiles     | 647   | Profil pengguna    |
