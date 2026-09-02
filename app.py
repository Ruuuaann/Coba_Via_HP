import streamlit as st
import pandas as pd

# Pengaturan Halaman Streamlit
st.set_page_config(
    page_title="Dashboard Data Aset BMN",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Dashboard Data Aset BMN")
st.write("Aplikasi visualisasi dan pencarian data aset Barang Milik Negara (BMN).")

# Nama file Excel yang tepat
FILE_PATH = "daftar-aset-1.xlsx"

# Kolom yang ingin ditampilkan
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
        # Membaca file Excel (otomatis mengambil sheet pertama / Master Aset)
        df = pd.read_excel(file_path)
        
        # Bersihkan nama kolom dari spasi berlebih di awal/akhir
        df.columns = df.columns.str.strip()
        
        # Cocokkan nama kolom (case-insensitive)
        column_mapping = {col.lower(): col for col in df.columns}
        target_cols = []
        for target in KOLOM_PILIHAN:
            if target.lower() in column_mapping:
                target_cols.append(column_mapping[target.lower()])
        
        df_filtered = df[target_cols]
        
        # Hapus baris yang seluruh kolom nilainya kosong
        df_filtered = df_filtered.dropna(how='all')
        
        return df_filtered
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
        return pd.DataFrame()

# Load Data
df = load_data(FILE_PATH)

if not df.empty:
    # --- SIDEBAR FILTER ---
    st.sidebar.header("🔍 Filter Data")
    
    # Filter Jenis BMN
    col_jenis = [c for c in df.columns if c.lower() == "jenis bmn"]
    if col_jenis:
        jenis_col = col_jenis[0]
        list_jenis = ["Semua"] + sorted([str(x) for x in df[jenis_col].dropna().unique()])
        selected_jenis = st.sidebar.selectbox("Pilih Jenis BMN:", list_jenis)
    else:
        selected_jenis = "Semua"

    # Filter Kondisi
    col_kondisi = [c for c in df.columns if c.lower() == "kondisi"]
    if col_kondisi:
        kondisi_col = col_kondisi[0]
        list_kondisi = ["Semua"] + sorted([str(x) for x in df[kondisi_col].dropna().unique()])
        selected_kondisi = st.sidebar.selectbox("Pilih Kondisi:", list_kondisi)
    else:
        selected_kondisi = "Semua"

    # Search Box
    search_query = st.sidebar.text_input("Cari Kata Kunci:")

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
    col1.metric("Total Aset Ditampilkan", len(df_display))
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
    st.warning("Data kosong atau gagal dimuat.")