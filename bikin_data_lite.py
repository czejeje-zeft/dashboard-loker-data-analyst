import pandas as pd
import os
import numpy as np

input_file = 'gsearch_jobs.csv'
output_file = 'gsearch_jobs_lite.csv'

# Daftar Skill yang mau dideteksi (bisa ditambah)
SKILL_KEYWORDS = [
    'python', 'sql', 'excel', 'tableau', 'power bi', 'aws', 'azure', 
    'google cloud', 'machine learning', 'spark', 'hadoop', 'java', 
    'scala', 'r', 'sas', 'looker', 'snowflake', 'databricks'
]

print("⏳ Sedang membaca data asli (ini mungkin butuh beberapa detik)...")

try:
    # 1. Baca data (kali ini kita BUTUH description dulu)
    cols_to_read = [
        'title', 'company_name', 'location', 'via', 'schedule_type', 
        'work_from_home', 'date_time', 'salary_yearly', 'description' 
    ]
    
    df = pd.read_csv(input_file, usecols=lambda c: c in cols_to_read)
    
    # 2. Ambil Sampel (misal 50rb baris) biar proses cepat & file kecil
    if len(df) > 50000:
        df = df.sample(n=50000, random_state=42)

    print("🔍 Sedang mengekstrak skill dari deskripsi...")

    # 3. Fungsi deteksi skill sederhana
    def detect_skills(text):
        if not isinstance(text, str):
            return ""
        text_lower = text.lower()
        found_skills = [skill for skill in SKILL_KEYWORDS if skill in text_lower]
        return ", ".join(found_skills)

    # Terapkan fungsi (agak lama dikit, tunggu ya)
    df['required_skills'] = df['description'].apply(detect_skills)

    # 4. HAPUS kolom description yang berat
    df.drop(columns=['description'], inplace=True)

    # 5. Simpan hasil
    df.to_csv(output_file, index=False)
    
    size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"✅ Berhasil! File '{output_file}' update dengan kolom Skill.")
    print(f"📉 Ukuran file baru: {size_mb:.2f} MB")

except Exception as e:
    print(f"❌ Error: {e}")