import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dashboard Data Aset BMN",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Dashboard Data Aset BMN")
st.write("Aplikasi visualisasi dan pencarian data aset Barang Milik Negara (BMN).")

# Menggunakan file CSV
FILE_PATH = "daftar-aset.csv"

KOLOM_PILIHAN = [
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
        df = pd.read_csv(file_path)
        
        # Bersihkan nama kolom
        df.columns = df.columns.str.strip()
        
        # Ambil hanya kolom yang diminta
        cols = [c for c in KOLOM_PILIHAN if c in df.columns]
        df_filtered = df[cols].dropna(how="all")
        
        # Rapikan Kode Barang dan NUP agar tidak berbentuk desimal (.0)
        for col in ["Kode Barang", "NUP"]:
            if col in df_filtered.columns:
                df_filtered[col] = df_filtered[col].apply(
                    lambda x: f"{int(x)}" if pd.notnull(x) and isinstance(x, (int, float)) else str(x) if pd.notnull(x) else ""
                )
                
        return df_filtered
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
        return pd.DataFrame()

df = load_data(FILE_PATH)

if not df.empty:
    # --- SIDEBAR FILTER ---
    st.sidebar.header("🔍 Filter Data")
    
    selected_jenis = st.sidebar.selectbox(
        "Pilih Jenis BMN:", 
        ["Semua"] + sorted([str(x) for x in df["Jenis BMN"].dropna().unique()])
    )
    
    selected_kondisi = st.sidebar.selectbox(
        "Pilih Kondisi:", 
        ["Semua"] + sorted([str(x) for x in df["Kondisi"].dropna().unique()])
    )
    
    search_query = st.sidebar.text_input("Cari Kata Kunci (Nama Barang/Satker/Merk/NUP):")

    # --- PROSES FILTER DATA ---
    df_display = df.copy()

    if selected_jenis != "Semua":
        df_display = df_display[df_display["Jenis BMN"].astype(str) == selected_jenis]

    if selected_kondisi != "Semua":
        df_display = df_display[df_display["Kondisi"].astype(str) == selected_kondisi]

    if search_query:
        mask = df_display.astype(str).apply(
            lambda x: x.str.contains(search_query, case=False, na=False)
        ).any(axis=1)
        df_display = df_display[mask]

    # --- METRIK STATISTIK ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Aset Ditampilkan", len(df_display))
    col2.metric("Jumlah Jenis BMN", df_display["Jenis BMN"].nunique())
    
    kondisi_baik = len(df_display[df_display["Kondisi"].astype(str).str.contains("Baik", case=False, na=False)])
    col3.metric("Kondisi Baik", kondisi_baik)

    st.markdown("---")

    # --- TABEL DATA ---
    st.subheader("📋 Tabel Data Aset BMN")
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # --- TOMBOL DOWNLOAD ---
    csv_data = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data Terfilter (CSV)",
        data=csv_data,
        file_name="data_aset_terfilter.csv",
        mime="text/csv",
    )
else:
    st.warning("Data belum dimuat. Pastikan file 'daftar-aset.csv' tersimpan di folder yang sama.")
