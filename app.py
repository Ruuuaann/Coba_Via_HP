import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dashboard Data Aset BMN",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Dashboard Data Aset BMN")
st.write("Visualisasi dan pencarian data aset Barang Milik Negara (BMN).")

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

# --- FITUR UPLOAD FILE ---
uploaded_file = st.sidebar.file_uploader(
    "Unggah File Excel/CSV BMN", 
    type=["xlsx", "csv"]
)

@st.cache_data
def process_data(file):
    try:
        # Membaca file berdasarkan formatnya
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
            
        df.columns = df.columns.str.strip()
        
        # Ambil hanya kolom yang diminta dan ada di dataset
        cols = [c for c in KOLOM_PILIHAN if c in df.columns]
        df_filtered = df[cols].dropna(how="all")
        
        # Format Kode Barang dan NUP agar tidak berbentuk angka desimal (.0)
        for col in ["Kode Barang", "NUP"]:
            if col in df_filtered.columns:
                df_filtered[col] = df_filtered[col].apply(
                    lambda x: f"{int(x)}" if pd.notnull(x) and isinstance(x, (int, float)) else str(x) if pd.notnull(x) else ""
                )
                
        return df_filtered
    except Exception as e:
        st.error(f"Gagal memproses file: {e}")
        return pd.DataFrame()

# Jika pengguna tidak mengunggah file, coba baca file lokal 'daftar-aset-1.xlsx'
if uploaded_file is not None:
    df = process_data(uploaded_file)
else:
    try:
        # Mencoba membaca file bawaan secara otomatis jika tersedia
        df_raw = pd.read_excel("daftar-aset-1.xlsx")
        df_raw.columns = df_raw.columns.str.strip()
        cols = [c for c in KOLOM_PILIHAN if c in df_raw.columns]
        df = df_raw[cols].dropna(how="all")
        
        for col in ["Kode Barang", "NUP"]:
            if col in df.columns:
                df[col] = df[col].apply(
                    lambda x: f"{int(x)}" if pd.notnull(x) and isinstance(x, (int, float)) else str(x) if pd.notnull(x) else ""
                )
    except Exception:
        df = pd.DataFrame()

# --- TAMPILAN FILTER DAN DATA ---
if not df.empty:
    st.sidebar.markdown("---")
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

    # Filter proses
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

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Aset", len(df_display))
    col2.metric("Jumlah Jenis BMN", df_display["Jenis BMN"].nunique())
    
    kondisi_baik = len(df_display[df_display["Kondisi"].astype(str).str.contains("Baik", case=False, na=False)])
    col3.metric("Kondisi Baik", kondisi_baik)

    st.markdown("---")

    # Tabel Data
    st.subheader("📋 Tabel Data Aset BMN")
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # Download Button
    csv_data = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data Terfilter (CSV)",
        data=csv_data,
        file_name="data_aset_terfilter.csv",
        mime="text/csv",
    )
else:
    st.info("💡 Silakan unggah file Excel/CSV data BMN Anda melalui sidebar di sebelah kiri.")
