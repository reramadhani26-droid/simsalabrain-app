import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import os
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="SimSalaBrain Premium", page_icon="🧠", layout="wide")

# --- INISIALISASI DATABASE CSV ---
DB_FILE = "riwayat.csv"
if not os.path.exists(DB_FILE):
    df_awal = pd.DataFrame(columns=["tanggal", "topik_utama", "data_json"])
    df_awal.to_csv(DB_FILE, index=False)

# --- FUNGSI SIMPAN KE DATABASE ---
def simpan_ke_csv(topik, data_json_str):
    df = pd.read_csv(DB_FILE)
    waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    baris_baru = pd.DataFrame([{"tanggal": waktu_sekarang, "topik_utama": topik, "data_json": data_json_str}])
    df = pd.concat([df, baris_baru], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    return True

# --- SIDEBAR NAVIGASI & KEAMANAN SISTEM ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🧠 SimSalaBrain</h1>", unsafe_allow_html=True)
    st.caption("<p style='text-align: center;'>Premium Education Cloud</p>", unsafe_allow_html=True)
    st.divider()
    
    st.info("🔐 Koneksi ke Server AI Pusat dienkripsi dan aman.")
    # Mengambil API key langsung dari Secrets (Brankas) tanpa menampilkannya di layar
    try:
        api_key_rahasia = st.secrets["GEMINI_API_KEY"]
    except:
        api_key_rahasia = ""
        st.error("⚠️ Sistem belum terhubung ke brankas rahasia.")
        
    st.divider()
    menu = st.radio("Navigasi Menu", ["✨ Buat Ringkasan", "📚 Riwayat Belajar"])

# --- MENU 1: BUAT RINGKASAN ---
if menu == "✨ Buat Ringkasan":
    st.title("Ruang Belajar Cerdas")
    st.markdown("Ubah materi panjang jadi ringkasan & kuis dalam sekejap.")
    
    kolom_input, kolom_kosong = st.columns([2, 1])
    with kolom_input:
        materi_teks = st.text_area("1. Masukkan Teks Materi:", height=200, placeholder="Ketik atau paste materi pelajaran di sini...")
        
    tombol_proses = st.button("🚀 Analisis & Buat Sekarang!", type="primary", use_container_width=True)
    
    if tombol_proses:
        if not api_key_rahasia:
            st.error("⚠️ Sistem tidak bisa berjalan. Cek koneksi server pusat.")
        elif not materi_teks:
            st.warning("⚠️ Teks materi tidak boleh kosong!")
        else:
            try:
                genai.configure(api_key=api_key_rahasia)
                
                # Menggunakan mesin paling stabil dan kuat saat ini
                model_aktif = 'gemini-1.5-flash'
                st.success("✅ Terhubung ke Mesin Pembelajaran Otomatis.")
                
                model = genai.GenerativeModel(model_aktif)
                
                prompt = f"""
                Bertindaklah sebagai asisten guru terbaik.
                Tugas WAJIB dari teks yang diberikan:
                1. "topik_utama": Buat judul singkat dari keseluruhan materi.
                2. "ringkasan": Ekstrak SEMUA konsep dari teks HINGGA TUNTAS. JANGAN ADA materi yang dihilangkan. Buat ringkasan yang SANGAT LENGKAP mencakup seluruh isi teks. Setiap topik WAJIB memiliki "penjelasan" mendalam, dan "jembatan_keledai" (singkatan lucu/unik untuk mempermudah hafalan).
                3. "kuis": Buat kuis pilihan ganda. WAJIB MINIMAL 15 SOAL komprehensif, memiliki 4 "opsi" (A/B/C/D), "jawaban_benar", dan "pembahasan".

                KEMBALIKAN OUTPUT HANYA DALAM FORMAT JSON murni, tanpa markdown.
                Struktur JSON: {{"topik_utama": "...", "ringkasan": [{{"topik": "...", "penjelasan": "...", "jembatan_keledai": "..."}}], "kuis": [{{"pertanyaan": "...", "opsi": ["..."], "jawaban_benar": "...", "pembahasan": "..."}}]}}
                
                Materi:
                {materi_teks}
                """
                
                with st.spinner("🧠 Mesin sedang membaca, merumuskan metode hafalan, dan menyusun kuis..."):
                    respons = model.generate_content(prompt)
                    teks_mentah = respons.text
                    
                    # --- PENYARING DATA CERDAS (Mencegah Error) ---
                    # Mencari kurung kurawal pembuka dan penutup untuk memastikan format JSON bersih
                    awal_json = teks_mentah.find('{')
                    akhir_json = teks_mentah.rfind('}')
                    
                    if awal_json != -1 and akhir_json != -1:
                        teks_json_bersih = teks_mentah[awal_json:akhir_json+1]
                        data_ai = json.loads(teks_json_bersih)
                    else:
                        # Jika tidak ditemukan, coba parse paksa
                        data_ai = json.loads(teks_mentah)
                
                st.session_state['data_hasil'] = data_ai
                st.session_state['skor'] = 0
                st.success("✅ Analisis Materi Selesai!")
                
            except Exception as e:
                # Sekarang pesan error aslinya akan dimunculkan ke layar
                st.error(f"⚠️ Proses Gagal! Detail Error: {str(e)}")
                st.info("💡 Jika error bertuliskan 'JSON', coba ubah teks materi menjadi lebih singkat. Jika '404', API Key mungkin perlu diperiksa.")

    if 'data_hasil' in st.session_state:
        data = st.session_state['data_hasil']
        st.divider()
        
        col_judul, col_simpan = st.columns([3, 1])
        with col_judul:
            st.header(f"📑 {data.get('topik_utama', 'Materi Pelajaran')}")
        with col_simpan:
            if st.button("💾 Simpan ke Database"):
                simpan_ke_csv(data.get('topik_utama', 'Ringkasan'), json.dumps(data))
                st.toast('Tersimpan ke Riwayat!', icon='✅')

        st.subheader("Fase 1: Pahami Intisari & Hafalkan")
        for idx, item in enumerate(data.get('ringkasan', [])):
            with st.expander(f"{idx+1}. {item['topik']}", expanded=True):
                st.write(item['penjelasan'])
                st.info(f"💡 **Jembatan Keledai:** {item['jembatan_keledai']}")
                
        st.divider()
        st.subheader("Fase 2: Kuis Evaluasi")
        
        with st.form("form_kuis"):
            jawaban_user = {}
            for i, soal in enumerate(data.get('kuis', [])):
                st.markdown(f"**{i+1}. {soal['pertanyaan']}**")
                jawaban_user[i] = st.radio(f"Pilih jawaban soal {i+1}:", soal['opsi'], key=f"soal_{i}", label_visibility="collapsed")
                st.write("---")
            
            submitted = st.form_submit_button("Kumpulkan Jawaban")
            if submitted:
                benar = 0
                for i, soal in enumerate(data.get('kuis', [])):
                    if jawaban_user[i] == soal['jawaban_benar']:
                        benar += 1
                
                nilai_akhir = int((benar / len(data['kuis'])) * 100)
                st.session_state['skor'] = nilai_akhir
                st.session_state['jawaban_terkirim'] = True

        if st.session_state.get('jawaban_terkirim', False):
            st.success(f"🎉 SKOR AKHIR KAMU: {st.session_state['skor']}")
            st.subheader("Cek Pembahasan:")
            for i, soal in enumerate(data.get('kuis', [])):
                if jawaban_user[i] == soal['jawaban_benar']:
                    st.success(f"**No {i+1}: BENAR** - {soal['pembahasan']}")
                else:
                    st.error(f"**No {i+1}: SALAH** (Kunci: {soal['jawaban_benar']}) - {soal['pembahasan']}")

# --- MENU 2: RIWAYAT BELAJAR ---
elif menu == "📚 Riwayat Belajar":
    st.title("Database Cloud (Riwayat)")
    st.markdown("Semua ringkasan yang kamu simpan tercatat di sini.")
    
    try:
        df = pd.read_csv(DB_FILE)
        if df.empty:
            st.info("Riwayat masih kosong. Yuk buat ringkasan pertamamu!")
        else:
            df = df.iloc[::-1]
            for index, row in df.iterrows():
                with st.expander(f"🕰️ {row['tanggal']} | {row['topik_utama']}"):
                    data_riwayat = json.loads(row['data_json'])
                    
                    st.markdown("**Ringkasan:**")
                    for item in data_riwayat.get('ringkasan', []):
                        st.write(f"- **{item['topik']}**: {item['penjelasan']}")
                        st.caption(f"💡 Hafalan: {item['jembatan_keledai']}")
                        
                    st.markdown("**Soal Kuis Tersedia:** " + str(len(data_riwayat.get('kuis', []))) + " Soal")
                    
    except Exception as e:
        st.error("Gagal membaca database. Pastikan file riwayat.csv tersedia.")
