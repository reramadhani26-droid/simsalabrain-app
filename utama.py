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
        with urllib.request.urlopen(req, timeout=10) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            parser = HTMLTextExtractor()
            parser.feed(html_content)
            return " ".join(parser.text_result)
    except Exception as e:
        return ""

def sanitize_json_response(raw_text):
    """Pembersih JSON otomatis dari AI."""
    try:
        idx_start = raw_text.find('{')
        idx_end = raw_text.rfind('}')
        if idx_start != -1 and idx_end != -1:
            return json.loads(raw_text[idx_start:idx_end+1])
        
        idx_start_arr = raw_text.find('[')
        idx_end_arr = raw_text.rfind(']')
        if idx_start_arr != -1 and idx_end_arr != -1:
            return json.loads(raw_text[idx_start_arr:idx_end_arr+1])
            
        return None
    except:
        return None

# --- MESIN PINTAR ANTI-ERROR (FALLBACK OTOMATIS) ---
def panggil_ai_dengan_fallback(paket_data):
    """Fungsi ajaib ini akan mencoba SEMUA model Google sampai berhasil, mencegah error 404."""
    daftar_mesin = [
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash",
        "gemini-1.5-pro-latest",
        "gemini-pro",
        "gemini-1.0-pro"
    ]
    error_terakhir = ""
    for nama_mesin in daftar_mesin:
        try:
            model_ai = genai.GenerativeModel(nama_mesin)
            respons = model_ai.generate_content(paket_data)
            return respons
        except Exception as e:
            error_terakhir = str(e)
            continue
    raise Exception(error_terakhir)

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
            3. "kuis": Buat kuis pilihan ganda. WAJIB MINIMAL 10 SOAL komprehensif.
            
            ATURAN KUIS SANGAT PENTING: Nilai dari "jawaban_benar" HARUS SAMA PERSIS dengan teks opsi yang benar.

            KEMBALIKAN OUTPUT HANYA FORMAT JSON MURNI:
            {"topik_utama": "...", "ringkasan": [{"topik": "...", "penjelasan": "...", "jembatan_keledai": "..."}], "kuis": [{"pertanyaan": "...", "opsi": ["Pilihan 1", "Pilihan 2", "Pilihan 3", "Pilihan 4"], "jawaban_benar": "Pilihan 2", "pembahasan": "..."}]}
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
                    try:
                        respons = panggil_ai_dengan_fallback(paket_data_ai)
                        data_ai = sanitize_json_response(respons.text)
                        
                        if data_ai:
                            st.session_state['data_hasil'] = data_ai
                            st.session_state['skor'] = 0
                            st.balloons()
                            st.success("✨ Modul Belajar Siap!")
                        else:
                            st.error("Mesin gagal menyusun struktur data. Silakan klik tombol analisis sekali lagi.")
                    except Exception as err:
                        if "429" in str(err) or "quota" in str(err).lower():
                            st.error("❌ Kuota API Google kamu sepertinya habis. Solusi: Buat API Key baru dari akun Gmail yang berbeda.")
                        else:
                            st.error(f"Terjadi kesalahan koneksi AI: {err}")

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
            
            KEMBALIKAN OUTPUT HANYA DALAM FORMAT JSON MURNI ARRAY SEPERTI INI:
            [
              {{"nama_sumber": "...", "url": "https://...", "deskripsi_singkat": "..."}},
              {{"nama_sumber": "...", "url": "https://...", "deskripsi_singkat": "..."}},
              {{"nama_sumber": "...", "url": "https://...", "deskripsi_singkat": "..."}}
            ]
            """
            with st.spinner("🔍 Mencari sumber referensi website terbaik di internet..."):
                try:
                    respons = panggil_ai_dengan_fallback([prompt_rekomendasi])
                    rekomendasi_list = sanitize_json_response(respons.text)
                    
                    if rekomendasi_list and isinstance(rekomendasi_list, list):
                        st.session_state['list_rekomendasi'] = rekomendasi_list
                        st.session_state['topik_aktif'] = topik_cari
                        st.success("✨ Rekomendasi website berhasil ditemukan!")
                    else:
                        st.error("Gagal memuat format rekomendasi dari server
