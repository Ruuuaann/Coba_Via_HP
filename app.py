import streamlit as st
import pandas as pd

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Dashboard Data Aset BMN",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Dashboard Data Aset BMN")
st.write("Aplikasi visualisasi dan pencarian data aset Barang Milik Negara (BMN).")

FILE_PATH = "daftar-aset-1.xlsx"

# Daftar target kolom yang ingin diambil
TARGET_KOLOM = [
    "Jenis BMN",
    "Nama Satker",
    "Kode Barang",
    "NUP",
    "Nama Barang",
    "Merk",
    "Tipe",
    "Kondisi"
]

@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel(file_path)
        
        # Bersihkan nama kolom dari spasi berlebih
        df.columns = df.columns.str.strip()
        
        # Mapping kolom tanpa membedakan huruf besar/kecil (case-insensitive)
        existing_cols = {col.lower(): col for col in df.columns}
        selected_cols = []
        
        for target in TARGET_KOLOM:
            target_lower = target.lower()
            if target_lower in existing_cols:
                selected_cols.append(existing_cols[target_lower])
            elif target_lower == "merk" and "merek" in existing_cols:
                selected_cols.append(existing_cols["merek"])
                
        df_filtered = df[selected_cols].dropna(how="all")
        return df_filtered
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
        return pd.DataFrame()

# 2. Load Data
df = load_data(FILE_PATH)

if not df.empty:
    # --- SIDEBAR FILTER ---
    st.sidebar.header("🔍 Filter Data")
    
    # Filter Jenis BMN
    col_jenis = [c for c in df.columns if "jenis bmn" in c.lower()]
    if col_jenis:
        jenis_col = col_jenis[0]
        list_jenis = ["Semua"] + sorted([str(x) for x in df[jenis_col].dropna().unique()])
        selected_jenis = st.sidebar.selectbox("Pilih Jenis BMN:", list_jenis)
    else:
        selected_jenis = "Semua"

    # Filter Kondisi
    col_kondisi = [c for c in df.columns if "kondisi" in c.lower()]
    if col_kondisi:
        kondisi_col = col_kondisi[0]
        list_kondisi = ["Semua"] + sorted([str(x) for x in df[kondisi_col].dropna().unique()])
        selected_kondisi = st.sidebar.selectbox("Pilih Kondisi:", list_kondisi)
    else:
        selected_kondisi = "Semua"

    # Filter Pencarian Kata Kunci
    search_query = st.sidebar.text_input("Cari Kata Kunci (Nama Barang/Satker/Merk):")

    # --- PROSES FILTER DATA ---
    df_display = df.copy()

    if selected_jenis != "Semua" and col_jenis:
        df_display = df_display[df_display[col_jenis[0]].astype(str) == selected_jenis]

    if selected_kondisi != "Semua" and col_kondisi:
        df_display = df_display[df_display[col_kondisi[0]].astype(str) == selected_kondisi]

    if search_query:
        mask = df_display.astype(str).apply(
            lambda x: x.str.contains(search_query, case=False, na=False)
        ).any(axis=1)
        df_display = df_display[mask]

    # --- STATISTIK RINGKAS ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Aset", len(df_display))
    if col_jenis:
        col2.metric("Jumlah Jenis BMN", df_display[col_jenis[0]].nunique())
    if col_kondisi:
        kondisi_baik = len(df_display[df_display[col_kondisi[0]].astype(str).str.contains("Baik", case=False, na=False)])
        col3.metric("Kondisi Baik", kondisi_baik)

    st.markdown("---")

    # --- TABEL DATA ---
    st.subheader("📋 Tabel Data Aset BMN")
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # --- TOMBOL UNDUH DATA ---
    csv_data = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data Terfilter (CSV)",
        data=csv_data,
        file_name="data_aset_terfilter.csv",
        mime="text/csv",
    )
else:
    st.warning("Data tidak berhasil dimuat.")
