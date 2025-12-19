import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter

# --- 1. SETUP ---
st.set_page_config(page_title="Dashboard Loker GSearch", page_icon="💼", layout="wide")

# --- 2. LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('gsearch_jobs_lite.csv')
        
        # Konversi tanggal
        if 'date_time' in df.columns:
            df['date_time'] = pd.to_datetime(df['date_time'], errors='coerce')
        
        # Bersihkan skill
        if 'required_skills' in df.columns:
            df['required_skills'] = df['required_skills'].fillna("")
            
        # Bersihkan WFH (Boolean)
        if 'work_from_home' in df.columns:
            df['work_from_home'] = df['work_from_home'].fillna(False)

        return df
    except Exception as e:
        st.error(f"Gagal load data: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.stop()

# --- 3. SIDEBAR ---
st.sidebar.header("🎛️ Filter Pencarian")
search = st.sidebar.text_input("Cari Posisi (misal: Data Analyst)")

# Filter Data Global
filtered_df = df.copy()
if search:
    filtered_df = filtered_df[filtered_df['title'].str.contains(search, case=False, na=False)]

# --- 4. HEADER ---
st.title("💼 Dashboard Pasar Kerja & Skill Tracker")
st.markdown(f"Menampilkan **{len(filtered_df):,}** lowongan aktif.")
st.markdown("---")

# --- 5. TABS VISUALISASI ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview Lengkap", "🧠 Analisis Skill", "💰 Gaji", "📋 Data Detail"])

# ==========================================
# TAB 1: OVERVIEW (YANG DI-UPGRADE)
# ==========================================
with tab1:
    # --- ROW 1: METRICS (4 Kolom) ---
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.metric("Total Lowongan", f"{len(filtered_df):,}")
    
    with c2:
        # Hitung % Remote
        remote_count = filtered_df['work_from_home'].sum()
        remote_pct = (remote_count / len(filtered_df)) * 100
        st.metric("Peluang Remote (WFH)", f"{remote_pct:.1f}%")
        
    with c3:
        # Top Platform
        top_platform = filtered_df['via'].mode()[0]
        st.metric("Platform Terpopuler", top_platform)
        
    with c4:
        # Perusahaan
        total_comp = filtered_df['company_name'].nunique()
        st.metric("Jumlah Perusahaan", f"{total_comp:,}")

    st.markdown("---")

    # --- ROW 2: CHART TYPE & LOCATION (2 Kolom) ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📍 Top 10 Lokasi")
        top_loc = filtered_df['location'].value_counts().head(10).reset_index()
        top_loc.columns = ['Lokasi', 'Jumlah']
        
        fig_loc = px.bar(
            top_loc, x='Jumlah', y='Lokasi', orientation='h',
            color='Jumlah', color_continuous_scale='Blues',
            text='Jumlah'
        )
        fig_loc.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_loc, use_container_width=True)

    with col_right:
        st.subheader("🌐 Platform (Via) Lowongan")
        top_via = filtered_df['via'].value_counts().head(8).reset_index()
        top_via.columns = ['Platform', 'Jumlah']
        
        fig_via = px.pie(
            top_via, values='Jumlah', names='Platform', 
            hole=0.4, color_discrete_sequence=px.colors.qualitative.Prism
        )
        st.plotly_chart(fig_via, use_container_width=True)

    # --- ROW 3: WORK STYLE & SCHEDULE (2 Kolom) ---
    c_l, c_r = st.columns(2)
    
    with c_l:
        st.subheader("🏠 Remote vs On-site")
        # Buat dataframe ringkas untuk WFH
        wfh_counts = filtered_df['work_from_home'].value_counts().reset_index()
        wfh_counts.columns = ['Status', 'Jumlah']
        wfh_counts['Status'] = wfh_counts['Status'].map({True: 'Remote / WFH', False: 'On-site / Hybrid'})
        
        fig_wfh = px.pie(
            wfh_counts, values='Jumlah', names='Status', 
            color='Status',
            color_discrete_map={'Remote / WFH':'#00CC96', 'On-site / Hybrid':'#EF553B'}
        )
        st.plotly_chart(fig_wfh, use_container_width=True)

    with c_r:
        st.subheader("⏳ Tipe Jadwal Kerja")
        schedule_counts = filtered_df['schedule_type'].value_counts().head(5).reset_index()
        schedule_counts.columns = ['Tipe', 'Jumlah']
        
        fig_sch = px.bar(
            schedule_counts, x='Tipe', y='Jumlah', 
            color='Jumlah', color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_sch, use_container_width=True)

# ==========================================
# TAB 2: SKILL
# ==========================================
with tab2:
    st.subheader("🔥 Skill Paling Banyak Dicari")
    
    all_skills_list = filtered_df['required_skills'].str.split(', ').explode().tolist()
    all_skills_list = [s for s in all_skills_list if s] # Filter kosong
    
    if all_skills_list:
        skill_counts = pd.DataFrame(Counter(all_skills_list).most_common(15), columns=['Skill', 'Jumlah'])
        
        fig_skill = px.bar(
            skill_counts, x='Jumlah', y='Skill', orientation='h', 
            title=f"Top 15 Skill ({search if search else 'Semua Data'})",
            text='Jumlah', color='Jumlah', color_continuous_scale='Magma'
        )
        fig_skill.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_skill, use_container_width=True)
    else:
        st.warning("Tidak ada skill terdeteksi.")

# ==========================================
# TAB 3: GAJI
# ==========================================
with tab3:
    st.subheader("💰 Analisis Gaji Tahunan (USD)")
    df_gaji = filtered_df[filtered_df['salary_yearly'] > 0]
    
    if not df_gaji.empty:
        c1, c2 = st.columns(2)
        c1.metric("Rata-rata", f"${df_gaji['salary_yearly'].mean():,.0f}")
        c2.metric("Median", f"${df_gaji['salary_yearly'].median():,.0f}")
        
        fig_hist = px.histogram(df_gaji, x="salary_yearly", nbins=30, color_discrete_sequence=['#636EFA'])
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("Data gaji tidak tersedia untuk filter ini.")

# ==========================================
# TAB 4: DATA DETAIL
# ==========================================
with tab4:
    st.dataframe(filtered_df.head(1000), use_container_width=True)
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV Full", csv, "loker_full.csv", "text/csv")