# 💼 Job Market Analysis Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://dashboard-loker.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue&logo=python&logoColor=white)](https://www.python.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive-green)](https://plotly.com/)

Dashboard interaktif untuk menganalisis pasar kerja global, tren gaji, dan skill yang paling banyak dicari di industri data. Dibangun menggunakan **Python** dan **Streamlit**.

🔗 **Live Demo:** [Klik di sini untuk melihat Dashboard](https://dashboard-loker.streamlit.app/)

![Dashboard Overview](screenshot_overview.png)

## 📌 Fitur Utama

*   **📊 Overview Metrics:** Ringkasan total lowongan, rata-rata gaji, dan peluang kerja remote (WFH).
*   **🧠 Skill Tracker:** Menganalisis deskripsi pekerjaan untuk menemukan *top skills* yang dibutuhkan (misal: Python, SQL, Tableau).
*   **💰 Analisis Gaji:** Histogram distribusi gaji tahunan (USD) dengan visualisasi yang detail.
*   **🌍 Peta Persebaran:** Melihat lokasi dengan jumlah lowongan terbanyak.
*   **🎛️ Filter Canggih:** Filter berdasarkan Gaji Minimum, Tipe Pekerjaan, Platform, dan Keyword.

## 🛠️ Teknologi yang Digunakan

| Komponen | Teknologi | Kegunaan |
| :--- | :--- | :--- |
| **Core** | Python | Bahasa pemrograman utama |
| **Framework** | Streamlit | Membangun web apps interaktif |
| **Data Processing** | Pandas | Manipulasi dan pembersihan data |
| **Visualization** | Plotly Express | Membuat grafik interaktif |
| **Data Source** | GSearch Jobs | Dataset lowongan kerja (Sampled & Cleaned) |

## 📂 Struktur Folder

```text
dashboard-loker-2025/
├── 📄 dashboard_loker.py    # Main Application Code
├── 📄 bikin_data_lite.py    # Script untuk cleaning & sampling data
├── 📄 gsearch_jobs_lite.csv # Dataset (Lightweight version)
├── 📄 requirements.txt      # Dependencies list
├── 📄 README.md             # Dokumentasi Proyek
└── 🖼️ screenshot_overview.png
