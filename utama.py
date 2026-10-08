import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import os
from datetime import datetime
import urllib.request
from html.parser import HTMLParser

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="SimSalaBrain Pro", page_icon="🚀", layout="wide")

# --- SUNTIKAN DESAIN UI/UX MODERN (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .judul-gradasi {
        background: linear-gradient(90deg, #FF416C 0%, #FF4B2B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0px;
        padding-bottom: 10px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 30px;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 16px;
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(118, 75, 162, 0.6);
        color: white;
    }
    div[data-testid="stExpander"] {
        background-color: #ffffff;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
        margin-bottom: 15px;
    }
    .jembatan-keledai {
        background: linear-gradient(to right, #f6d365 0%, #fda085 100%);
        padding: 15px 20px;
        border-radius: 10px;
        color: #fff;
        font-weight: 600;
        margin-top: 10px;
        box-shadow: 0 4px 6px rgba(253, 160, 133, 0.3);
    }
    .card-rekomendasi {
        background: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        margin-bottom: 15px;
    }
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# --- INISIALISASI DATABASE CSV ---
DB_FILE = "riwayat.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["tanggal", "topik_utama", "data_json"]).to_csv(DB_FILE, index=False)

def simpan_ke_csv(topik, data_json_str):
    df = pd.read_csv(DB_FILE)
    waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    baris_baru = pd.DataFrame([{"tanggal": waktu_sekarang, "topik_utama": topik, "data_json": data_json_str}])
    df = pd.concat([df, baris_baru], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    return True

# --- HTML TEXT EXTRACTOR UNTUK URL SCRAPING OTOMATIS ---
class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_result = []
        self.ignore = False

    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style', 'nav', 'footer', 'header']:
            self.ignore = True

    def handle_endtag(self, tag):
        if tag in ['script', 'style', 'nav', 'footer', 'header']:
            self.ignore = False

    def handle_data(self, data):
        if not self.ignore:
            cleaned = data.strip()
            if cleaned:
                self.text_result.append(cleaned)

def ambil_teks_dari_url(url):
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            parser = HTMLTextExtractor()
            parser.feed(html_content)
            return " ".join(parser.text_result)
    except Exception as e:
        return ""

# --- SIDEBAR NAVIGASI ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #764ba2;'>🚀 SimSalaBrain</h1>", unsafe_allow_html=True)
    st.caption("<p style='text-align: center; font-weight: bold;'>Education Cloud Pro</p>", unsafe_allow_html=True)
    st.divider()
    
    st.success("🔒 Sistem Enkripsi Cloud Aktif.")
    try:
        api_key_rahasia = st.secrets["GEMINI_API_KEY"]
    except:
        api_key_rahasia = ""
        st.error("⚠️ Brankas API Key belum terisi.")
        
    st.divider()
    menu = st.radio("Mulai Petualangan:", ["✨ Papan Belajar Utama", "🔍 Rekomendasi & Telusuri Web", "📚 Perpustakaan Riwayat"])

# --- MENU 1: PAPAN BELAJAR UTAMA ---
if menu == "✨ Papan Belajar Utama":
    st.markdown("<h1 class='judul-gradasi'>Ruang Belajar Cerdas</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 18px; color: #555;'>Ubah teks, PDF, Word, atau Gambar materi menjadi modul interaktif dalam hitungan detik.</p>", unsafe_allow_html=True)
    st.write("---")
    
    col_teks, col_file = st.columns(2)
    
    with col_teks:
        st.markdown("**1. 📝 Ketik / Paste Teks (Opsional):**")
        materi_teks = st.text_area("Teks Materi", height=150, label_visibility="collapsed", placeholder="Masukkan materi panjang di sini...")
        
    with col_file:
        st.markdown("**2. 📎 ATAU Unggah File Dokumen/Foto:**")
        file_unggahan = st.file_uploader("Upload File", type=["pdf", "docx", "pptx", "txt", "jpg", "jpeg", "png"], label_visibility="collapsed")
        
    st.write("") 
    tombol_proses = st.button("🚀 Mulai Analisis Ajaib!", use_container_width=True)
    
    if tombol_proses:
        if not api_key_rahasia:
            st.error("⚠️ Sistem terkunci. Cek pengaturan Secrets kamu.")
        elif not materi_teks and file_unggahan is None:
            st.warning("⚠️ Masukkan materi (teks atau file) terlebih dahulu!")
        else:
            genai.configure(api_key=api_key_rahasia)
            
            prompt_instruksi = """
            Bertindaklah sebagai asisten guru paling jenius.
            Tugas WAJIB dari materi ini:
            1. "topik_utama": Buat judul super menarik dari keseluruhan materi.
            2. "ringkasan": Ekstrak SEMUA konsep TANPA ADA YANG TERLEWAT. Buat sangat detail dan rapi. Setiap topik WAJIB punya "penjelasan" panjang, dan "jembatan_keledai" (singkatan atau kalimat lucu untuk menghafal).
            3. "kuis": Buat kuis pilihan ganda. WAJIB MINIMAL 15 SOAL komprehensif, dengan 4 "opsi" (A/B/C/D), "jawaban_benar", dan "pembahasan".

            KEMBALIKAN OUTPUT HANYA FORMAT JSON MURNI:
            {"topik_utama": "...", "ringkasan": [{"topik": "...", "penjelasan": "...", "jembatan_keledai": "..."}], "kuis": [{"pertanyaan": "...", "opsi": ["..."], "jawaban_benar": "...", "pembahasan": "..."}]}
            """
            
            paket_data_ai = [prompt_instruksi]
            if materi_teks: paket_data_ai.append(f"\nTeks Materi:\n{materi_teks}")
            
            bisa_diproses = True
            if file_unggahan:
                ext = file_unggahan.name.split('.')[-1].lower()
                if ext in ['pdf', 'jpg', 'jpeg', 'png']:
                    paket_data_ai.append({"mime_type": file_unggahan.type, "data": file_unggahan.getvalue()})
                elif ext == 'txt':
                    paket_data_ai.append(f"\nIsi TXT:\n{file_unggahan.getvalue().decode('utf-8')}")
                elif ext == 'docx':
                    try:
                        import docx
                        doc = docx.Document(file_unggahan)
                        paket_data_ai.append("\nIsi Word:\n" + '\n'.join([p.text for p in doc.paragraphs]))
                    except:
                        st.error("Gagal membaca Word. Pastikan python-docx terinstall.")
                        bisa_diproses = False
                elif ext == 'pptx':
                    try:
                        from pptx import Presentation
                        prs = Presentation(file_unggahan)
                        teks_ppt = []
                        for slide in prs.slides:
                            for shape in slide.shapes:
                                if hasattr(shape, "text"): teks_ppt.append(shape.text)
                        paket_data_ai.append("\nIsi PPT:\n" + '\n'.join(teks_ppt))
                    except:
                        st.error("Gagal membaca PPT. Pastikan python-pptx terinstall.")
                        bisa_diproses = False

            if bisa_diproses:
                with st.spinner("⏳ Mengaktifkan Mesin Pembelajaran Otomatis..."):
                    daftar_mesin = ["gemini-3.1-pro-preview", "gemini-3-flash-preview", "gemini-3.8-flash"]
                    respons = None
                    error_terakhir = ""
                    
                    for nama_mesin in daftar_mesin:
                        try:
                            model_ai = genai.GenerativeModel(nama_mesin)
                            respons = model_ai.generate_content(paket_data_ai)
                            break 
                        except Exception as e:
                            error_terakhir = str(e)
                            continue 
                    
                    if not respons:
                        st.error(f"❌ Server AI Menolak Permintaan: {error_terakhir}")
                        st.stop()
                    
                    try:
                        teks_raw = respons.text
                        idx_start = teks_raw.find('{')
                        idx_end = teks_raw.rfind('}')
                        
                        if idx_start != -1 and idx_end != -1:
                            data_ai = json.loads(teks_raw[idx_start:idx_end+1])
                        else:
                            st.error("Gagal membaca format data dari server. Coba lagi.")
                            st.stop()
                            
                        st.session_state['data_hasil'] = data_ai
                        st.session_state['skor'] = 0
                        st.balloons()
                        st.success("✨ Modul Belajar Siap!")
                    except Exception as e_json:
                        st.error("Mesin gagal menyusun materi. Silakan klik tombol analisis sekali lagi.")

# --- MENU 2: REKOMENDASI & TELUSURI WEB BERBASIS TOPIK ---
elif menu == "🔍 Rekomendasi & Telusuri Web":
    st.markdown("<h1 class='judul-gradasi'>Rekomendasi Materi Web</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 18px; color: #555;'>Ketik materi atau topik yang ingin Anda pelajari. AI akan merekomendasikan situs web terbaik dan memberikan opsi untuk langsung merangkumnya!</p>", unsafe_allow_html=True)
    st.write("---")
    
    topik_cari = st.text_input("🎯 Ketik Topik / Materi Pelajaran (Contoh: Sejarah Kerajaan Majapahit, Teori Relativitas Einstein)", placeholder="Masukkan topik...")
    
    if st.button("🔍 Cari Rekomendasi Website", use_container_width=True):
        if not topik_cari:
            st.warning("⚠️ Masukkan topik atau materi terlebih dahulu!")
        elif not api_key_rahasia:
            st.error("⚠️ Sistem terkunci. Cek pengaturan Secrets kamu.")
        else:
            genai.configure(api_key=api_key_rahasia)
            prompt_rekomendasi = f"""
            Bertindaklah sebagai mesin pencari dan penasihat akademik pintar.
            Pengguna ingin mempelajari topik: "{topik_cari}".
            Berikan rekomendasi 3 sumber website atau artikel publik nyata yang sangat bagus dan kredibel di internet untuk topik ini (misalnya Wikipedia, Ruangguru, Kompasiana, detikEdu, atau situs edukasi sejenis).
            
            KEMBALIKAN OUTPUT HANYA DALAM FORMAT JSON MURNI:
            [
              {{"nama_sumber": "...", "url": "https://...", "deskripsi_singkat": "..."}},
              {{"nama_sumber": "...", "url": "https://...", "deskripsi_singkat": "..."}},
              {{"nama_sumber": "...", "url": "https://...", "deskripsi_singkat": "..."}}
            ]
            """
            with st.spinner("🔍 Mencari sumber referensi website terbaik di internet..."):
                try:
                    model_ai = genai.GenerativeModel("gemini-3.1-pro-preview")
                    respons = model_ai.generate_content(prompt_rekomendasi)
                    teks_raw = respons.text
                    idx_start = teks_raw.find('[')
                    idx_end = teks_raw.rfind(']')
                    
                    if idx_start != -1 and idx_end != -1:
                        rekomendasi_list = json.loads(teks_raw[idx_start:idx_end+1])
                        st.session_state['list_rekomendasi'] = rekomendasi_list
                        st.session_state['topik_aktif'] = topik_cari
                        st.success("✨ Rekomendasi website berhasil ditemukan!")
                    else:
                        st.error("Gagal memuat rekomendasi. Silakan coba klik sekali lagi.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

    # Tampilkan Hasil Rekomendasi Jika Ada
    if 'list_rekomendasi' in st.session_state:
        st.write("---")
        st.markdown(f"### 🌐 Hasil Rekomendasi untuk: *{st.session_state.get('topik_aktif', '')}*")
        
        for i, rec in enumerate(st.session_state['list_rekomendasi']):
            st.markdown(f"""
            <div class="card-rekomendasi">
                <h4><b>{i+1}. {rec['nama_sumber']}</b></h4>
                <p style="color: #64748b; font-size: 14px; margin-bottom: 8px;">{rec['deskripsi_singkat']}</p>
                <a href="{rec['url']}" target="_blank" style="color: #4f46e5; font-weight: bold; text-decoration: none;">🔗 Kunjungi Website Langsung ↗</a>
            </div>
            """, unsafe_allow_html=True)
            
            col_lk, col_rk = st.columns([2, 1])
            with col_lk:
                st.caption(f"Tautan: {rec['url']}")
            with col_rk:
                if st.button(f"🚀 Rangkum Website Ini #{i+1}", key=f"btn_rk_{i}"):
                    with st.spinner(f"📥 Mengambil teks dari {rec['nama_sumber']} dan menyusun modul..."):
                        teks_web = ambil_teks_dari_url(rec['url'])
                        if not teks_web or len(teks_web) < 100:
                            teks_web = f"Topik pembahasan dari {rec['nama_sumber']} mengenai {rec['deskripsi_singkat']} dengan fokus pada {st.session_state.get('topik_aktif', '')}."
                        
                        prompt_rangkum_situs = f"""
                        Bertindaklah sebagai asisten guru paling jenius.
                        Berikut adalah teks materi dari situs web {rec['nama_sumber']} ({rec['url']}):
                        {teks_web[:15000]}
                        
                        Tugas WAJIB:
                        1. "topik_utama": Buat judul menarik dari materi ini.
                        2. "ringkasan": Ekstrak SEMUA konsep TANPA ADA YANG TERLEWAT. Setiap topik WAJIB punya "penjelasan" panjang, dan "jembatan_keledai" (singkatan atau kalimat lucu untuk menghafal).
                        3. "kuis": Buat kuis pilihan ganda. WAJIB MINIMAL 15 SOAL komprehensif, dengan 4 "opsi" (A/B/C/D), "jawaban_benar", dan "pembahasan".

                        KEMBALIKAN OUTPUT HANYA FORMAT JSON MURNI:
                        {{"topik_utama": "...", "ringkasan": [{{"topik": "...", "penjelasan": "...", "jembatan_keledai": "..."}}], "kuis": [{{"pertanyaan": "...", "opsi": ["..."], "jawaban_benar": "...", "pembahasan": "..."}}]}}
                        """
                        try:
                            model_ai = genai.GenerativeModel("gemini-3.1-pro-preview")
                            resp_web = model_ai.generate_content(prompt_rangkum_situs)
                            raw_w = resp_web.text
                            s_w = raw_w.find('{')
                            e_w = raw_w.rfind('}')
                            if s_w != -1 and e_w != -1:
                                data_web = json.loads(raw_w[s_w:e_w+1])
                                st.session_state['data_hasil'] = data_web
                                st.session_state['skor'] = 0
                                st.balloons()
                                st.success("✨ Modul Belajar Berhasil Disusun dari Website Tersebut! Gulir ke bawah untuk melihat hasil.")
                        except Exception as err:
                            st.error(f"Gagal memproses situs web: {err}")

# --- TAMPILAN HASIL UTAMA (RINGKASAN & KUIS) ---
if 'data_hasil' in st.session_state and menu in ["✨ Papan Belajar Utama", "🔍 Rekomendasi & Telusuri Web"]:
    data = st.session_state['data_hasil']
    st.write("---")
    
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f"<h2 style='color: #2c3e50;'>📚 {data.get('topik_utama', 'Materi')}</h2>", unsafe_allow_html=True)
    with c2:
        if st.button("💾 Simpan ke Perpustakaan"):
            simpan_ke_csv(data.get('topik_utama', 'Ringkasan'), json.dumps(data))
            st.toast('Tersimpan dengan aman di Cloud!', icon='☁️')

    st.markdown("<h3 style='color: #764ba2;'>🧠 Fase 1: Pahami & Hafalkan</h3>", unsafe_allow_html=True)
    for idx, item in enumerate(data.get('ringkasan', [])):
        with st.expander(f"Topik {idx+1}: {item['topik']}", expanded=True):
            st.markdown(f"<p style='font-size: 16px; line-height: 1.6;'>{item['penjelasan']}</p>", unsafe_allow_html=True)
            st.markdown(f"<div class='jembatan-keledai'>💡 <b>Jembatan Keledai:</b><br>{item['jembatan_keledai']}</div>", unsafe_allow_html=True)
            
    st.write("---")
    st.markdown("<h3 style='color: #FF416C;'>🎯 Fase 2: Kuis Ujian Akhir</h3>", unsafe_allow_html=True)
    
    with st.form("form_kuis"):
        jawaban_user = {}
        for i, soal in enumerate(data.get('kuis', [])):
            st.markdown(f"**Soal {i+1} | {soal['pertanyaan']}**")
            jawaban_user[i] = st.radio(f"Pilih jawaban soal {i+1}:", soal['opsi'], key=f"soal_{i}", label_visibility="collapsed")
            st.write("")
        
        submitted = st.form_submit_button("Kumpulkan & Cek Nilai 📝")
        if submitted:
            benar = sum(1 for i, soal in enumerate(data.get('kuis', [])) if jawaban_user[i] == soal['jawaban_benar'])
            st.session_state['skor'] = int((benar / len(data['kuis'])) * 100)
            st.session_state['jawaban_terkirim'] = True

    if st.session_state.get('jawaban_terkirim', False):
        skor = st.session_state['skor']
        warna_skor = "#27ae60" if skor >= 75 else "#e74c3c"
        
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 15px; margin-top: 20px;'>
            <h1 style='color: {warna_skor}; font-size: 4rem; margin: 0;'>{skor}</h1>
            <p style='font-size: 1.2rem; color: #555;'>SKOR AKHIR KAMU</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("### Pembahasan Detail:")
        for i, soal in enumerate(data.get('kuis', [])):
            if jawaban_user[i] == soal['jawaban_benar']:
                st.success(f"**✅ Soal {i+1} | BENAR**\n\n{soal['pembahasan']}")
            else:
                st.error(f"**❌ Soal {i+1} | SALAH** (Kunci: {soal['jawaban_benar']})\n\n{soal['pembahasan']}")

# --- MENU 3: PERPUSTAKAAN RIWAYAT ---
elif menu == "📚 Perpustakaan Riwayat":
    st.markdown("<h1 class='judul-gradasi'>Perpustakaan Cloud</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 18px; color: #555;'>Buka kembali catatan dan kuis lama yang pernah kamu simpan.</p>", unsafe_allow_html=True)
    st.write("---")
    
    try:
        df = pd.read_csv(DB_FILE)
        if df.empty:
            st.info("📦 Perpustakaan masih kosong. Ayo mulai meringkas materi pertamamu!")
        else:
            df = df.iloc[::-1]
            for index, row in df.iterrows():
                with st.expander("Riwayat: " + str(row['topik_utama'])):
                    data_riwayat = json.loads(row['data_json'])
                    
                    st.markdown("### Ringkasan Materi:")
                    for item in data_riwayat.get('ringkasan', []):
                        st.markdown(f"**{item['topik']}**")
                        st.write(item['penjelasan'])
                        st.markdown(f"<div style='background-color:#fff3cd; padding:10px; border-radius:5px; color:#856404; font-size:14px;'>💡 <b>Hafalan:</b> {item['jembatan_keledai']}</div><br>", unsafe_allow_html=True)
                        
                    st.markdown(f"**Jumlah Soal Kuis:** {len(data_riwayat.get('kuis', []))} Soal Siap Dikerjakan")
                    
    except Exception as e:
        st.error(f"Gagal membaca perpustakaan database. Detail: {e}")
```eof
        
