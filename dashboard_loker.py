import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter

# --- 1. SETUP HALAMAN ---
st.set_page_config(
    page_title="Dashboard Loker Pro 2025",
    page_icon="🚀",
    layout="wide"
)

# --- 2. LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('gsearch_jobs_lite.csv')
        
        # Konversi tanggal
        if 'date_time' in df.columns:
            df['date_time'] = pd.to_datetime(df['date_time'], errors='coerce')
        
        # Bersihkan skill & WFH
        if 'required_skills' in df.columns:
            df['required_skills'] = df['required_skills'].fillna("")
        if 'work_from_home' in df.columns:
            df['work_from_home'] = df['work_from_home'].fillna(False)
            
        return df
    except Exception as e:
        st.error(f"Gagal load data: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.stop()

# --- 3. SIDEBAR FILTER (UPGRADED) ---
st.sidebar.header("🎛️ Filter Canggih")

# A. Pencarian Keyword
search = st.sidebar.text_input("🔍 Cari Posisi (misal: Analyst)", placeholder="Ketik posisi...")

# B. Filter Tipe Jadwal
tipe_kerja = st.sidebar.multiselect(
    "⏳ Tipe Jadwal:",
    options=df['schedule_type'].unique(),
    default=df['schedule_type'].unique()
)

# C. Filter Platform (BARU)
platform_options = df['via'].value_counts().head(10).index.tolist()
pilih_platform = st.sidebar.multiselect(
    "🌐 Platform (Via):",
    options=platform_options,
    default=platform_options[:3] # Default pilih top 3
)

# D. Filter Gaji Minimum (BARU)
# Ambil max gaji untuk batas slider
max_salary = int(df['salary_yearly'].max()) if df['salary_yearly'].max() > 0 else 200000
gaji_min = st.sidebar.slider(
    "💰 Gaji Minimum (USD/Tahun):",
    min_value=0,
    max_value=max_salary,
    value=0,
    step=5000,
    help="Geser untuk menyaring lowongan dengan gaji tinggi"
)

# E. Filter WFH
wfh_option = st.sidebar.radio("🏠 Mode Kerja:", ["Semua", "Remote Only", "On-site Only"])

# --- 4. LOGIKA FILTERING ---
filtered_df = df.copy()

# Terapkan Filter
if search:
    filtered_df = filtered_df[filtered_df['title'].str.contains(search, case=False, na=False)]

filtered_df = filtered_df[filtered_df['schedule_type'].isin(tipe_kerja)]

# Filter Platform (Jika user memilih sesuatu)
if pilih_platform:
    filtered_df = filtered_df[filtered_df['via'].isin(pilih_platform)]

# Filter Gaji
if gaji_min > 0:
    filtered_df = filtered_df[filtered_df['salary_yearly'] >= gaji_min]

# Filter WFH
if wfh_option == "Remote Only":
    filtered_df = filtered_df[filtered_df['work_from_home'] == True]
elif wfh_option == "On-site Only":
    filtered_df = filtered_df[filtered_df['work_from_home'] != True]

# --- 5. DASHBOARD HEADER ---
st.title("🚀 Dashboard Pasar Kerja & Analisis Gaji")
st.markdown(f"""
<div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
    <strong>Status:</strong> Menampilkan <b>{len(filtered_df):,}</b> lowongan dari total database.
</div>
""", unsafe_allow_html=True)

# --- 6. TABS CONTENT ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🧠 Skill", "💰 Analisis Gaji", "📋 Data Detail"])

# === TAB 1: OVERVIEW ===
with tab1:
    # Kartu Metrik
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Lowongan", f"{len(filtered_df):,}", help="Jumlah lowongan setelah filter")
    
    # Rata2 Gaji (Hanya yg ada datanya)
    gaji_valid = filtered_df[filtered_df['salary_yearly'] > 0]
    avg_gaji = gaji_valid['salary_yearly'].mean() if not gaji_valid.empty else 0
    c2.metric("Rata-rata Gaji", f"${avg_gaji:,.0f}", delta_color="normal")
    
    c3.metric("Platform Terbanyak", filtered_df['via'].mode()[0] if not filtered_df.empty else "-")
    c4.metric("Perusahaan Unik", f"{filtered_df['company_name'].nunique():,}")

    st.divider()

    # Charts Row 1
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("📍 Persebaran Lokasi")
        top_loc = filtered_df['location'].value_counts().head(10).reset_index()
        top_loc.columns = ['Lokasi', 'Jumlah']
        fig_loc = px.bar(top_loc, x='Jumlah', y='Lokasi', orientation='h', 
                         color='Jumlah', color_continuous_scale='Blues')
        fig_loc.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_loc, use_container_width=True)
        
    with col_r:
        st.subheader("🏢 Top Perusahaan")
        top_comp = filtered_df['company_name'].value_counts().head(10).reset_index()
        top_comp.columns = ['Perusahaan', 'Jumlah']
        fig_comp = px.bar(top_comp, x='Jumlah', y='Perusahaan', orientation='h',
                          color='Jumlah', color_continuous_scale='Greens')
        fig_comp.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_comp, use_container_width=True)

# === TAB 2: SKILL ===
with tab2:
    st.subheader("🔥 Skill Populer")
    all_skills = filtered_df['required_skills'].str.split(', ').explode().tolist()
    all_skills = [s for s in all_skills if s]
    
    if all_skills:
        skill_counts = pd.DataFrame(Counter(all_skills).most_common(15), columns=['Skill', 'Jumlah'])
        fig_skill = px.bar(skill_counts, x='Jumlah', y='Skill', orientation='h', 
                           color='Jumlah', color_continuous_scale='Magma', text='Jumlah')
        fig_skill.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_skill, use_container_width=True)
    else:
        st.warning("Tidak ada data skill untuk filter ini.")

# === TAB 3: GAJI (UPGRADED) ===
with tab3:
    st.subheader("💰 Distribusi Gaji Tahunan")
    
    if not gaji_valid.empty:
        # Histogram Cantik
        fig_hist = px.histogram(
            gaji_valid, 
            x="salary_yearly", 
            nbins=40,
            title="Sebaran Gaji (USD)",
            color_discrete_sequence=['#3366CC'], # Warna solid elegan
            opacity=0.8
        )
        # Menambahkan garis batas antar bar agar tidak menempel
        fig_hist.update_traces(marker_line_color='white', marker_line_width=1.5)
        fig_hist.update_layout(bargap=0.1) # Jarak antar bar
        
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # Statistik Tambahan
        st.info(f"💡 Lowongan dengan gaji tertinggi: **${gaji_valid['salary_yearly'].max():,.0f}**")
    else:
        st.warning("Data gaji tidak tersedia atau semua bernilai 0/NaN.")

# === TAB 4: DATA DETAIL (UPGRADED) ===
with tab4:
    st.subheader("📋 Tabel Detail Lowongan")
    
    # Pilih kolom untuk ditampilkan
    show_cols = ['title', 'company_name', 'location', 'salary_yearly', 'via', 'date_time', 'schedule_type']
    
    # Filter kolom yang benar-benar ada di data
    valid_cols = [c for c in show_cols if c in filtered_df.columns]
    
    # Tampilkan dataframe dengan formatting khusus
    st.dataframe(
        filtered_df[valid_cols].head(2000), # Batasi 2000 baris di UI
        use_container_width=True,
        column_config={
            "title": "Posisi",
            "company_name": "Perusahaan",
            "location": "Lokasi",
            "salary_yearly": st.column_config.NumberColumn(
                "Gaji (USD)",
                format="$%d", # Format mata uang
            ),
            "date_time": st.column_config.DatetimeColumn(
                "Tanggal Posting",
                format="D MMM YYYY, HH:mm"
            ),
            "via": "Platform"
        }
    )
    
    # Tombol Download
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data Lengkap (CSV)",
        data=csv,
        file_name="data_loker_terfilter.csv",
        mime="text/csv",
        type="primary" # Tombol berwarna
    )