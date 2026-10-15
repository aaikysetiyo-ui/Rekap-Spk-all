import os
import json
import streamlit as st
from datetime import datetime

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Arsip & Data SPK Asuransi",
    page_icon="📄",
    layout="wide",
)

# File penyimpanan lokal untuk data SPK
DATA_FILE = "spk_database.json"
UPLOAD_DIR = "uploaded_spk_files"

# Pastikan folder upload ada
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Load data awal & pastikan semua data tersimpan permanen tanpa batas kapasitas (>10 data)
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception as e:
            st.error(f"Gagal memuat database: {e}")
    
    # Default Dummy Data awal jika file belum ada
    return [
        {
            "id": 1,
            "no_spk": "SPK/2027/001",
            "plat_nomor": "B 1234 SKP",
            "tertanggung": "PT Sentosa Abadi",
            "jenis": "Kendaraan Comprehensive",
            "tahun": "2027",
            "bulan": "Januari",
            "status": "Aktif",
            "file_name": "SPK_B1234SKP_Jan2027.pdf",
            "file_path": None
        },
        {
            "id": 2,
            "no_spk": "SPK/2027/002",
            "plat_nomor": "D 8888 RFS",
            "tertanggung": "Budi Santoso",
            "jenis": "Total Loss Only (TLO)",
            "tahun": "2027",
            "bulan": "Januari",
            "status": "Proses",
            "file_name": "SPK_D8888RFS_Jan2027.pdf",
            "file_path": None
        }
    ]

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if "spk_list" not in st.session_state:
    st.session_state.spk_list = load_data()

MONTHS = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
YEARS = ["2025", "2026", "2027"]

# --- HEADER APLIKASI ---
st.title("📄 Arsip & Manajemen SPK Asuransi")
st.markdown("Kelola dokumen SPK tanpa batas kapasitas, folder arsip tahun 2025-2027, plat nomor kendaraan, dan akses unduh berkas PDF.")
st.markdown("---")

# --- SIDEBAR: INPUT & UPLOAD SPK BARU ---
st.sidebar.header("📥 Upload / Input SPK Baru")
with st.sidebar.form("form_upload_spk", clear_on_submit=True):
    no_spk = st.text_input("Nomor SPK", placeholder="Contoh: SPK/2027/015")
    plat_nomor = st.text_input("Plat Nomor Kendaraan", placeholder="Contoh: B 1234 ABC").upper()
    tertanggung = st.text_input("Nama Tertanggung / Pemilik")
    jenis = st.selectbox("Jenis Asuransi", ["Kendaraan Comprehensive", "Total Loss Only (TLO)", "Asuransi Jiwa & Kesehatan", "Properti & Kebakaran"])
    status = st.selectbox("Status SPK", ["Aktif", "Proses", "Klaim"])
    
    col_y, col_m = st.columns(2)
    with col_y:
        tahun = st.selectbox("Tahun Folder", YEARS, index=2) # Default 2027
    with col_m:
        bulan = st.selectbox("Bulan Folder", MONTHS)
        
    uploaded_file = st.file_uploader("Upload File Berkas PDF SPK", type=["pdf"])
    
    submit_btn = st.form_submit_button("Simpan Berkas SPK")
    
    if submit_btn:
        if not no_spk or not plat_nomor or not tertanggung:
            st.sidebar.error("Nomor SPK, Plat Nomor, dan Nama Tertanggung wajib diisi!")
        else:
            file_path = None
            file_name = f"{no_spk.replace('/', '_')}_{plat_nomor.replace(' ', '')}.pdf"
            
            if uploaded_file is not None:
                file_name = uploaded_file.name
                file_path = os.path.join(UPLOAD_DIR, file_name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            new_record = {
                "id": int(datetime.now().timestamp() * 1000), # Unique ID milidetik
                "no_spk": no_spk,
                "plat_nomor": plat_nomor,
                "tertanggung": tertanggung,
                "jenis": jenis,
                "tahun": tahun,
                "bulan": bulan,
                "status": status,
                "file_name": file_name,
                "file_path": file_path
            }
            
            st.session_state.spk_list.insert(0, new_record)
            save_data(st.session_state.spk_list)
            st.sidebar.success(f"Berkas SPK {no_spk} berhasil disimpan!")
            st.rerun()

# --- STATISTIK RINGKASAN ---
total_berkas = len(st.session_state.spk_list)
count_2025 = sum(1 for x in st.session_state.spk_list if x["tahun"] == "2025")
count_2026 = sum(1 for x in st.session_state.spk_list if x["tahun"] == "2026")
count_2027 = sum(1 for x in st.session_state.spk_list if x["tahun"] == "2027")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Berkas SPK", total_berkas)
c2.metric("Arsip 2025", count_2025)
c3.metric("Arsip 2026", count_2026)
c4.metric("Folder Baru 2027", count_2027)

st.markdown("---")

# --- NAVIGASI TAHUN & FOLDER BULAN ---
selected_year = st.radio("Pilih Folder Tahun:", YEARS, horizontal=True, index=2)

st.markdown(f"**Pilih Folder Bulan untuk Tahun {selected_year}:**")
month_cols = st.columns(6)
selected_month = st.session_state.get("selected_month", None)

for i, m in enumerate(MONTHS):
    col_idx = i % 6
    count_m = sum(1 for x in st.session_state.spk_list if x["tahun"] == selected_year and x["bulan"] == m)
    label = f"📁 {m} ({count_m})"
    
    with month_cols[col_idx]:
        is_active = (selected_month == m)
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, key=f"btn_m_{m}", use_container_width=True, type=btn_type):
            if st.session_state.get("selected_month") == m:
                st.session_state.selected_month = None # Toggle off
            else:
                st.session_state.selected_month = m
            st.rerun()

if st.session_state.get("selected_month"):
    st.info(f"Menampilkan filter aktif untuk Bulan: **{st.session_state.selected_month} {selected_year}**")
    if st.button("Reset Filter Bulan"):
        st.session_state.selected_month = None
        st.rerun()

st.markdown("---")

# --- PENCARIAN & FILTER ---
col_search, col_status = st.columns([3, 1])
with col_search:
    search_query = st.text_input("🔍 Cari No. SPK, Plat Nomor, Nama Tertanggung, atau Asuransi", "")
with col_status:
    status_filter = st.selectbox("Filter Status", ["Semua", "Aktif", "Proses", "Klaim"])

# Filter Logic
filtered_list = []
for item in st.session_state.spk_list:
    if item["tahun"] != selected_year:
        continue
    if st.session_state.get("selected_month") and item["bulan"] != st.session_state.get("selected_month"):
        continue
    if status_filter != "Semua" and item["status"] != status_filter:
        continue
    
    q = search_query.lower()
    if q and not (q in item["no_spk"].lower() or q in item["plat_nomor"].lower() or q in item["tertanggung"].lower() or q in item["jenis"].lower()):
        continue
        
    filtered_list.append(item)

st.subheader(f"Daftar Arsip SPK ({len(filtered_list)} Berkas Ditemukan)")

# --- DAFTAR DATA & AKSI ---
if not filtered_list:
    st.info("Belum ada data SPK pada filter atau folder ini.")
else:
    for item in filtered_list:
        with st.container():
            cols = st.columns([2, 2, 2, 2, 1, 1, 1])
            with cols[0]:
                st.markdown(f"**{item['no_spk']}**")
                st.caption(f"{item['bulan']} {item['tahun']}")
            with cols[1]:
                st.code(item['plat_nomor'], language=None)
            with cols[2]:
                st.write(item['tertanggung'])
            with cols[3]:
                st.write(item['jenis'])
            with cols[4]:
                if item['status'] == 'Aktif':
                    st.success(item['status'])
                elif item['status'] == 'Proses':
                    st.warning(item['status'])
                else:
                    st.error(item['status'])
            with cols[5]:
                if st.button("👁️ Detail", key=f"view_{item['id']}"):
                    st.session_state.active_pdf = item
            with cols[6]:
                if st.button("🗑️ Hapus", key=f"del_{item['id']}"):
                    st.session_state.spk_list = [x for x in st.session_state.spk_list if x["id"] != item["id"]]
                    save_data(st.session_state.spk_list)
                    st.success("Berkas berhasil dihapus!")
                    st.rerun()
            st.divider()

# --- PANEL DETAIL & DOWNLOAD PDF AMAN (ANTI BLOKIR BROWSER) ---
if "active_pdf" in st.session_state and st.session_state.active_pdf:
    item = st.session_state.active_pdf
    st.markdown("---")
    col_p1, col_p2 = st.columns([4, 1])
    with col_p1:
        st.subheader(f"Detail Berkas SPK: {item['no_spk']}")
    with col_p2:
        if st.button("Tutup Detail"):
            st.session_state.active_pdf = None
            st.rerun()
            
    st.info("💡 Informasi lengkap dokumen dan tombol unduh aman (bebas blokir iframe browser).")
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.markdown(f"""
        - **Nomor SPK:** {item['no_spk']}
        - **Plat Nomor:** `{item['plat_nomor']}`
        - **Nama Tertanggung:** {item['tertanggung']}
        """)
    with col_info2:
        st.markdown(f"""
        - **Jenis Asuransi:** {item['jenis']}
        - **Periode Folder:** {item['bulan']} {item['tahun']}
        - **Status Polis:** {item['status']}
        """)

    # Tombol Download File PDF Asli
    if item['file_path'] and os.path.exists(item['file_path']):
        with open(item['file_path'], "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label="📥 Download Berkas PDF Asli",
            data=pdf_bytes,
            file_name=item['file_name'],
            mime="application/pdf",
            type="primary"
        )
    else:
        st.warning("File PDF fisik tidak di-upload saat input data ini. Sistem hanya menyimpan data teks arsip.")
