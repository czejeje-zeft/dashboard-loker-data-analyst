import pandas as pd
import os
import re  # Import modul Regex

input_file = 'gsearch_jobs.csv'
output_file = 'gsearch_jobs_lite.csv'

# Daftar Skill
SKILL_KEYWORDS = [
    'python', 'sql', 'excel', 'tableau', 'power bi', 'aws', 'azure', 
    'google cloud', 'machine learning', 'spark', 'hadoop', 'java', 
    'scala', 'r', 'sas', 'looker', 'snowflake', 'databricks', 'tensorflow',
    'pytorch', 'scikit-learn', 'pandas', 'numpy'
]

print("⏳ Sedang membaca data asli...")

try:
    # 1. Baca data
    cols_to_read = [
        'title', 'company_name', 'location', 'via', 'schedule_type', 
        'work_from_home', 'date_time', 'salary_yearly', 'description' 
    ]
    
    df = pd.read_csv(input_file, usecols=lambda c: c in cols_to_read)
    
    # 2. Ambil Sampel
    if len(df) > 50000:
        df = df.sample(n=50000, random_state=42)

    print("🔍 Sedang mengekstrak skill (Mode Akurat - Regex)...")

    # 3. Fungsi deteksi skill YANG SUDAH DIPERBAIKI
    def detect_skills(text):
        if not isinstance(text, str):
            return ""
        text = text.lower()
        found_skills = []
        
        for skill in SKILL_KEYWORDS:
            # \b artinya "Word Boundary" (batas kata)
            # Jadi dia mencari kata yang berdiri sendiri
            # \b(r)\b akan match " r " tapi TIDAK match "your"
            pattern = r'\b' + re.escape(skill) + r'\b'
            
            if re.search(pattern, text):
                found_skills.append(skill)
                
        return ", ".join(found_skills)

    # Terapkan fungsi
    df['required_skills'] = df['description'].apply(detect_skills)

    # 4. HAPUS kolom description
    df.drop(columns=['description'], inplace=True)

    # 5. Simpan hasil
    df.to_csv(output_file, index=False)
    
    size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"✅ Berhasil! Dataset '{output_file}' diperbarui.")
    print(f"📉 Ukuran file: {size_mb:.2f} MB")

except Exception as e:
    print(f"❌ Error: {e}")