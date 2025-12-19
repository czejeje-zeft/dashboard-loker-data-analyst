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

# --- [FIX VISUAL FINAL: SMART VARIABLES] ---
st.markdown("""
<style>
    /* 1. Reset Jarak Atas */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    
    /* 2. KARTU METRIC (KPI) - SOLUSI ANTI BENTROK */
    /* Kita gunakan var(--secondary-background-color) agar warnanya otomatis menyesuaikan tema */
    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color) !important;
        border: 1px solid rgba(128, 128, 128, 0.1); /* Border transparan halus */
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); /* Shadow lembut */
        text-align: center;
        transition: transform 0.2s;
    }
    
    /* Efek Hover */
    div[data-testid="stMetric"]:hover {
        transform: scale(1.02);
        border-color: #00A8E8; /* Border jadi biru saat disentuh */
    }
    
    /* 3. LABEL (Judul Kecil) */
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        /* Gunakan warna teks bawaan tema dengan transparansi agar tidak terlalu mencolok */
        color: var(--text-color) !important;
        opacity: 0.7; 
    }

    /* 4. VALUE (Angka Besar) */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700;
        /* Warna Biru Cerah (Cyan) yang aman di Background Hitam MAUPUN Putih */
        color: #0077b6 !important; 
    }
    
    /* 5. TABS Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: var(--secondary-background-color);
        border-radius: 4px;
        padding: 10px 20px;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0077b6;
        color: white;
    }
    
    /* 6. Fix untuk tulisan di grafik agar mengikuti tema */
    .js-plotly-plot .plotly .modebar {
        orientation: v;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('gsearch_jobs_lite.csv')
        if 'date_time' in df.columns:
            df['date_time'] = pd.to_datetime(df['date_time'], errors='coerce')
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
    st.warning("Dataframe kosong. Cek file CSV Anda.")
    st.stop()

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("🎛️ Filter Menu")
    search = st.text_input("🔍 Cari Posisi", placeholder="Ex: Data Analyst")
    
    tipe_kerja = st.multiselect("⏳ Tipe Jadwal:", options=df['schedule_type'].unique(), default=df['schedule_type'].unique())
    
    if 'via' in df.columns:
        platform_options = df['via'].value_counts().head(10).index.tolist()
        pilih_platform = st.multiselect("🌐 Platform:", options=platform_options, default=platform_options[:3])
    else:
        pilih_platform = []
    
    wfh_option = st.radio("🏠 Mode Kerja:", ["Semua", "Remote Only", "On-site Only"])
    st.markdown("---")

# --- 4. LOGIKA FILTERING ---
filtered_df = df.copy()

if search:
    filtered_df = filtered_df[filtered_df['title'].str.contains(search, case=False, na=False)]
filtered_df = filtered_df[filtered_df['schedule_type'].isin(tipe_kerja)]
if pilih_platform and 'via' in df.columns:
    filtered_df = filtered_df[filtered_df['via'].isin(pilih_platform)]
if wfh_option == "Remote Only":
    filtered_df = filtered_df[filtered_df['work_from_home'] == True]
elif wfh_option == "On-site Only":
    filtered_df = filtered_df[filtered_df['work_from_home'] != True]

# --- 5. DASHBOARD HEADER ---
st.title("🚀 Dashboard Pasar Kerja & Analisis Gaji")

# Banner Status (Menggunakan variable --secondary-background-color)
st.markdown(f"""
<div style="
    background-color: var(--secondary-background-color); 
    padding: 15px; 
    border-left: 5px solid #0077b6; 
    border-radius: 5px; 
    margin-bottom: 25px;">
    <span style="font-size:16px; color: var(--text-color);">📊 <strong>Status Data:</strong> Menampilkan <b>{len(filtered_df):,}</b> lowongan pekerjaan hasil filter.</span>
</div>
""", unsafe_allow_html=True)

# --- 6. TABS CONTENT ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🧠 Skill Analysis", "💰 Salary Insights", "📋 Raw Data"])

# === TAB 1: OVERVIEW ===
with tab1:
    st.markdown("### 📈 Key Performance Indicators")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Lowongan", f"{len(filtered_df):,}")
    
    if 'salary_yearly' in filtered_df.columns:
        gaji_valid = filtered_df[filtered_df['salary_yearly'] > 0]
        avg_gaji = gaji_valid['salary_yearly'].mean() if not gaji_valid.empty else 0
        c2.metric("Rata-rata Gaji", f"${avg_gaji:,.0f}")
    else:
        c2.metric("Rata-rata Gaji", "N/A")
    
    platform_top = filtered_df['via'].mode()[0] if not filtered_df.empty and 'via' in filtered_df.columns else "-"
    c3.metric("Platform Terbanyak", platform_top)
    
    comp_unique = filtered_df['company_name'].nunique() if 'company_name' in filtered_df.columns else 0
    c4.metric("Perusahaan Unik", f"{comp_unique:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    # CHARTS ROW
    col_l, col_r = st.columns(2)
    
    # Chart Lokasi
    with col_l:
        st.subheader("📍 Persebaran Lokasi")
        if 'location' in filtered_df.columns:
            top_loc = filtered_df['location'].value_counts().head(10).reset_index()
            top_loc.columns = ['Lokasi', 'Jumlah']
            
            fig_loc = px.bar(top_loc, x='Jumlah', y='Lokasi', orientation='h', 
                             text='Jumlah', color='Jumlah', 
                             color_continuous_scale='Blues')
            fig_loc.update_layout(
                yaxis={'categoryorder':'total ascending'},
                xaxis_title=None, yaxis_title=None,
                # Background transparan agar menyatu dengan tema apapun
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400
            )
            st.plotly_chart(fig_loc, use_container_width=True)
        
    # Chart Perusahaan
    with col_r:
        st.subheader("🏢 Top Perusahaan")
        if 'company_name' in filtered_df.columns:
            top_comp = filtered_df['company_name'].value_counts().head(10).reset_index()
            top_comp.columns = ['Perusahaan', 'Jumlah']
            
            fig_comp = px.bar(top_comp, x='Jumlah', y='Perusahaan', orientation='h',
                              text='Jumlah', color='Jumlah', 
                              color_continuous_scale='Teal')
            fig_comp.update_layout(
                yaxis={'categoryorder':'total ascending'},
                xaxis_title=None, yaxis_title=None,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400
            )
            st.plotly_chart(fig_comp, use_container_width=True)

# === TAB 2: SKILL ===
with tab2:
    st.subheader("🔥 Skill Paling Banyak Dicari")
    if 'required_skills' in filtered_df.columns:
        all_skills = filtered_df['required_skills'].str.split(', ').explode().tolist()
        all_skills = [s for s in all_skills if s]
        
        if all_skills:
            skill_counts = pd.DataFrame(Counter(all_skills).most_common(15), columns=['Skill', 'Jumlah'])
            fig_skill = px.bar(skill_counts, x='Jumlah', y='Skill', orientation='h', 
                               color='Jumlah', color_continuous_scale='Magma', text='Jumlah')
            fig_skill.update_layout(
                yaxis={'categoryorder':'total ascending'},
                xaxis_title="Frekuensi", yaxis_title=None,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=500
            )
            st.plotly_chart(fig_skill, use_container_width=True)
        else:
            st.warning("Tidak ada data skill.")

# === TAB 3: GAJI ===
with tab3:
    st.subheader("💰 Analisis Distribusi Gaji")
    if 'salary_yearly' in filtered_df.columns and not gaji_valid.empty:
        col_chart, col_stat = st.columns([2,1])
        with col_chart:
            fig_hist = px.histogram(
                gaji_valid, 
                x="salary_yearly", 
                nbins=30,
                color_discrete_sequence=['#4cc9f0'],
                opacity=0.8
            )
            fig_hist.update_layout(
                title_text=None,
                xaxis_title="Gaji Tahunan (USD)",
                yaxis_title="Jumlah",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                bargap=0.1
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        with col_stat:
            st.markdown("#### Statistik Ringkas")
            st.markdown(f"""
            - **Tertinggi:** ${gaji_valid['salary_yearly'].max():,.0f}
            - **Rata-rata:** ${gaji_valid['salary_yearly'].mean():,.0f}
            - **Terendah:** ${gaji_valid['salary_yearly'].min():,.0f}
            """)
    else:
        st.warning("Data gaji tidak tersedia.")

# === TAB 4: DATA DETAIL ===
with tab4:
    st.subheader("📋 Eksplorasi Data Detail")
    show_cols = ['title', 'company_name', 'location', 'salary_yearly', 'via', 'date_time', 'schedule_type']
    valid_cols = [c for c in show_cols if c in filtered_df.columns]
    
    st.dataframe(
        filtered_df[valid_cols].head(1000), 
        use_container_width=True,
        column_config={
            "salary_yearly": st.column_config.NumberColumn("Gaji (USD)", format="$%d"),
            "date_time": st.column_config.DatetimeColumn("Diposting", format="D MMM YYYY")
        },
        height=500
    )