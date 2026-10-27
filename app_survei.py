

import uuid
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

# Import modul instrumen survei & evaluasi
from daftar_pertanyaan import (
    KELOMPOK_FASILITAS,
    MASTER_PERTANYAAN,
    INFOGRAFIS_DATA,
    hitung_kebutuhan_toilet,
    evaluasi_toilet_daftar_gedung,
    analisis_evaluasi_gedung,
    hitung_evaluasi_toilet_lengkap
)

from daftar_pertanyaan import to_int

#from Inst_Survei import hitung_evaluasi_toilet_lengkap, to_int
import database_manager as db

# ==============================================================================
# KONFIGURASI HALAMAN STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Sistem Survei K3 Lingkungan Kerja (HIBB)",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# KODE AKSES RESMI PJK3 / BALAI K3
K3_PASSCODES = ["K3-BALAI-2026", "K3NASIONAL", "PJK3-2026", "BALAIK3", "K32026"]

# Custom CSS modern & premium
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Header & Metric Styling */
.main-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0369a1 100%);
    color: white;
    padding: 24px 32px;
    border-radius: 16px;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.25);
}
.main-header h1 {
    color: #ffffff !important;
    font-weight: 800;
    font-size: 1.85rem;
    margin-bottom: 6px;
}
.main-header p {
    color: #cbd5e1 !important;
    font-size: 0.95rem;
    margin: 0;
}

/* Card Badge & Container */
.k3-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 18px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.k3-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
}

/* Deficit Card untuk Poin Kurang */
.k3-deficit-card {
    background: #fff1f2;
    border-left: 4px solid #e11d48;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 12px;
    box-shadow: 0 2px 4px rgba(225, 29, 72, 0.08);
}

/* Toilet Summary Card */
.k3-toilet-card {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
}

/* Pop-up Infografis on Hover */
.k3-hover-container {
    position: relative;
    display: inline-block;
    margin: 6px 0 12px 0;
}
.k3-badge-pill {
    background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
    color: #ffffff !important;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 5px 12px;
    border-radius: 9999px;
    cursor: help;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    box-shadow: 0 2px 4px rgba(2, 132, 199, 0.25);
    transition: all 0.2s ease;
}
.k3-badge-pill:hover {
    background: linear-gradient(135deg, #0369a1 0%, #0c4a6e 100%);
    transform: scale(1.02);
}
.hover-hint {
    font-size: 0.72rem;
    opacity: 0.85;
    font-weight: 400;
}
.k3-popover-card {
    visibility: hidden;
    opacity: 0;
    position: absolute;
    top: calc(100% + 10px);
    left: 0;
    width: 380px;
    max-width: 90vw;
    background: #ffffff;
    color: #0f172a;
    border: 1px solid #94a3b8;
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1);
    z-index: 9999999;
    transition: opacity 0.25s ease, visibility 0.25s ease, transform 0.25s ease;
    transform: translateY(8px);
    pointer-events: none;
}
.k3-hover-container:hover .k3-popover-card {
    visibility: visible;
    opacity: 1;
    transform: translateY(0);
}
.k3-popover-header {
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 8px;
    margin-bottom: 10px;
}
.k3-popover-header h5 {
    color: #0369a1;
    font-size: 1rem;
    font-weight: 700;
    margin: 4px 0 2px 0;
}
.k3-tag {
    background: #e0f2fe;
    color: #0369a1;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 6px;
    display: inline-block;
}
.k3-regulasi {
    font-size: 0.75rem;
    color: #64748b;
    font-style: italic;
}
.k3-ringkasan {
    font-size: 0.85rem;
    line-height: 1.45;
    color: #334155;
    margin-bottom: 10px;
}
.k3-poin-box {
    background: #f8fafc;
    border-left: 3px solid #0284c7;
    padding: 8px 12px;
    border-radius: 0 8px 8px 0;
}
.k3-poin-box strong {
    font-size: 0.78rem;
    color: #0f172a;
}
.k3-poin-box ul {
    margin: 4px 0 0 0;
    padding-left: 18px;
    font-size: 0.8rem;
    color: #475569;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==============================================================================
# INISIALISASI SESSION STATE
# ==============================================================================
if "active_role" not in st.session_state:
    st.session_state.active_role = "🏢 Perusahaan"

if "k3_authenticated" not in st.session_state:
    st.session_state.k3_authenticated = False

if "perusahaan_step" not in st.session_state:
    st.session_state.perusahaan_step = "info_perusahaan"

if "company_data" not in st.session_state:
    st.session_state.company_data = {}

if "daftar_gedung" not in st.session_state:
    st.session_state.daftar_gedung = []

if "current_gedung" not in st.session_state:
    st.session_state.current_gedung = {}

if "selected_facilities" not in st.session_state:
    st.session_state.selected_facilities = ["struktur_gedung", "toilet_sanitasi", "sampah_pakaian", "kebutuhan_udara", "housekeeping"]

if "penguji_kode_input" not in st.session_state:
    st.session_state.penguji_kode_input = ""

if "pjk3_menu_choice" not in st.session_state:
    st.session_state.pjk3_menu_choice = "Verifikasi Asesmen"


# ==============================================================================
# HELPER: POP-UP INFOGRAFIS
# ==============================================================================
def render_infografis_hover_html(q_id: str):
    """Menampilkan tombol info dan kartu hover infografis sesuai q_id."""
    info = INFOGRAFIS_DATA.get(q_id)
    if not info:
        return

    poin_items = "".join([f"<li>{p}</li>" for p in info.get("poin_kunci", [])])
    html_code = f"""
    <div class="k3-hover-container">
      <div class="k3-badge-pill">
        💡 <b>Infografis Istilah:</b> {info['istilah']} <span class="hover-hint">(Arahkan kursor)</span>
      </div>
      <div class="k3-popover-card">
        <div class="k3-popover-header">
          <span class="k3-tag">{info['visual_badge']}</span>
          <h5>{info['istilah']}</h5>
          <div class="k3-regulasi">⚖️ {info['regulasi']}</div>
        </div>
        <p class="k3-ringkasan">{info['ringkasan']}</p>
        <div class="k3-poin-box">
          <strong>📌 Ketentuan Baku Regulasi:</strong>
          <ul>
            {poin_items}
          </ul>
        </div>
      </div>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)


# ==============================================================================
# HELPER: EVALUASI TOILET MANDIRI & KUMULATIF
# ==============================================================================
def render_evaluasi_toilet_card(daftar_gedung: list):
    """Menampilkan analisis kepatuhan standar rasio toilet mandiri & kumulatif."""
    if not daftar_gedung:
        return

    eval_t = hitung_evaluasi_toilet_lengkap(daftar_gedung)

    st.markdown("### 🚻 Evaluasi Pemenuhan Standar Toilet (Permenaker No. 5/2018)")
    st.caption("Permenaker No. 5/2018 mensyaratkan pemenuhan toilet dinilai secara **Mandiri per Gedung** (kemudahan akses kerja) dan **Kumulatif** (rasio total kapasitas seluruh tempat kerja).")

    # Kartu Metrik
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Tenaga Kerja", f"{eval_t['total_pekerja']} Orang")
    c2.metric("Total Toilet Tersedia", f"{eval_t['total_toilet']} Unit")
    c3.metric("Kebutuhan Kumulatif", f"{eval_t['syarat_kumulatif']} Unit")
    status_kum = "✅ Memenuhi Standar" if eval_t["kumulatif_memenuhi"] else f"⚠️ Kurang {eval_t['selisih_kumulatif']} Unit"
    c4.metric("Status Kumulatif", status_kum)

    # Tabel Evaluasi Mandiri vs Kumulatif
    df_t = pd.DataFrame(eval_t["rincian_gedung"])
    tampil_cols = ["No", "Nama Gedung", "Jenis Objek", "Total Pekerja", "Toilet Ada", "Standar Mandiri", "Status Mandiri"]
    st.dataframe(df_t[tampil_cols], width="stretch")

    if not eval_t["kumulatif_memenuhi"]:
        st.warning(
            f"⚠️ **Kekurangan Toilet Kumulatif:** Jumlah total toilet yang tersedia ({eval_t['total_toilet']} unit) masih kurang **{eval_t['selisih_kumulatif']} unit** "
            f"dari kebutuhan baku minimal ({eval_t['syarat_kumulatif']} unit) untuk total populasi {eval_t['total_pekerja']} tenaga kerja."
        )
    else:
        st.success(f"🎉 **Standar Toilet Kumulatif Terpenuhi:** Tersedia total {eval_t['total_toilet']} unit toilet dari ambang batas minimal {eval_t['syarat_kumulatif']} unit.")


# ==============================================================================
# HELPER: RINCIAN POIN-POIN DEFISIT / KURANG
# ==============================================================================
def render_poin_kurang_gedung(gedung: dict, fasilitas_ids: list = None):
    """Menampilkan daftar butir pertanyaan atau parameter K3 yang bernilai di bawah standar."""
    eval_res = analisis_evaluasi_gedung(gedung, fasilitas_ids)
    pertanyaan_kurang = eval_res.get("pertanyaan_kurang", [])

    st.markdown("#### 🔍 Rincian Poin & Parameter K3 yang Perlu Perbaikan:")

    if not pertanyaan_kurang:
        raw_bidang = str(gedung.get("Bidang perlu diperbaiki", "Tidak ada"))
        if raw_bidang != "Tidak ada" and raw_bidang.strip():
            st.warning(f"⚠️ **Bidang di Bawah Target Standar:** {raw_bidang}")
        else:
            st.success("🎉 **Luar Biasa!** Tidak ada butir pertanyaan yang berada di bawah standar pemenuhan K3 pada objek ini.")
        return

    st.markdown(f"Ditemukan **{len(pertanyaan_kurang)} parameter** yang belum memenuhi standar baku Permenaker No. 5/2018:")

    for p in pertanyaan_kurang:
        st.markdown(f"""
        <div class="k3-deficit-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#b91c1c; font-size:0.95rem;">🔴 [{p['id']}] {p.get('teks', '')}</span>
                <span style="font-size:0.75rem; background:#fee2e2; color:#991b1b; padding:2px 8px; border-radius:6px; font-weight:600;">Skor Aktual: {p['skor']}</span>
            </div>
            <div style="font-size:0.82rem; color:#475569; margin: 4px 0;">
                <b>Topik:</b> {p.get('topik', '-')} &nbsp;|&nbsp; <b>Sub-Bidang:</b> {p.get('sub_bidang', '-')}
            </div>
            <div style="font-size:0.84rem; color:#1e293b; margin: 4px 0;">
                <b>Jawaban Tercatat:</b> <i>"{p.get('jawaban', '-')}"</i>
            </div>
            <div style="font-size:0.82rem; color:#0369a1; margin-top:4px;">
                ⚖️ <b>Rujukan Regulasi:</b> {p.get('regulasi', 'Permenaker No. 5/2018')}
            </div>
            <div style="font-size:0.82rem; color:#b91c1c; margin-top:2px;">
                💡 <b>Rekomendasi Tindakan Korektif:</b> {p.get('rekomendasi', '-')}
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# SIDEBAR ROUTING: HANYA DUA PILIHAN PERAN
# (Sesuai Permintaan: Perusahaan dan PJK3/BalaiK3)
# ==============================================================================
with st.sidebar:
    st.title("🛡️ Navigasi Sistem")
    st.caption("Survei & Asesmen Mandiri K3 Lingkungan Kerja")

    # HANYA 2 PILIHAN UTAMA
    role_options = [
        "🏢 Perusahaan",
        "🛡️ PJK3 / Balai K3"
    ]
    selected_role = st.radio(
        "Pilih Peran / Akses Utama:",
        role_options,
        index=role_options.index(st.session_state.active_role) if st.session_state.active_role in role_options else 0
    )
    if selected_role != st.session_state.active_role:
        st.session_state.active_role = selected_role
        st.rerun()

    st.markdown("---")
    st.info("💡 **Dasar Regulasi:**  \nPermenaker No. 5 Tahun 2018 tentang Keselamatan dan Kesehatan Kerja Lingkungan Kerja.")

    if st.session_state.active_role == "🛡️ PJK3 / Balai K3" and st.session_state.k3_authenticated:
        if st.button("🔒 Keluar Akses K3", width="stretch"):
            st.session_state.k3_authenticated = False
            st.rerun()


# ==============================================================================
# BANNER HEADER UTAMA
# ==============================================================================
if st.session_state.active_role == "🏢 Perusahaan":
    header_title = "Portal Self-Assessment K3 Perusahaan"
    header_desc = "Pengisian instrumen survei mandiri K3 lingkungan kerja berdasarkan fasilitas nyata gedung perusahaan."
else:
    header_title = "Portal Penguji PJK3 & Pengawasan Balai K3"
    header_desc = "Verifikasi teknis lapangan berbasis asesmen, pengujian kesesuaian standar K3, dan analisis tren wilayah."

st.markdown(f"""
<div class="main-header">
    <h1>{header_title}</h1>
    <p>{header_desc}</p>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# PERAN 1: PERUSAHAAN (SELF ASSESSMENT)
# Fitur: Mengisi data baru ATAU memasukkan Company Key (jika sudah pernah asesmen)
# ==============================================================================
if st.session_state.active_role == "🏢 Perusahaan":

    # STEP 1: FORM IDENTITAS / PILIHAN COMPANY KEY
    if st.session_state.perusahaan_step == "info_perusahaan":
        st.subheader("Langkah 1: Identitas Perusahaan")
        st.write("Silakan pilih apakah Anda akan memulai asesmen baru atau melanjutkan asesmen yang sudah ada menggunakan **Company Key**.")

        tab_baru, tab_key_lama = st.tabs([
            "📝 Asesmen Baru (Isi Profil Perusahaan)",
            "🔑 Sudah Pernah Asesmen (Masukkan Company Key)"
        ])

        # TAB 1: ASESMEN BARU
        with tab_baru:
            with st.form("form_info_perusahaan_baru"):
                c1, c2 = st.columns(2)
                with c1:
                    nama_pt = st.text_input(
                        "Nama Perusahaan*",
                        value=st.session_state.company_data.get("Nama Perusahaan", ""),
                        placeholder="Contoh: PT Sumber Sejahtera Abadi"
                    )
                    legalitas = st.selectbox(
                        "Bentuk Legalitas",
                        ["PT", "CV", "BUMN/BUMD", "Koperasi", "Lainnya"],
                        index=0
                    )
                    nib = st.text_input(
                        "No. Induk Berusaha (NIB) / No. Induk*",
                        value=st.session_state.company_data.get("No Induk Perusahaan", ""),
                        placeholder="Contoh: 9120001234567"
                    )
                    telepon = st.text_input(
                        "No. Telepon Perusahaan*",
                        value=st.session_state.company_data.get("No Telp Perusahaan", ""),
                        placeholder="Contoh: 021-89765432"
                    )
                    lokasi = st.text_area(
                        "Lokasi / Alamat Pengujian*",
                        value=st.session_state.company_data.get("Lokasi Pengujian", ""),
                        placeholder="Contoh: Kawasan Industri Jababeka Blok C No. 10, Cikarang"
                    )

                with c2:
                    responden = st.text_input(
                        "Nama Responden (Penanggung Jawab)*",
                        value=st.session_state.company_data.get("Nama Responden", ""),
                        placeholder="Nama Pengisi / Penanggung Jawab K3"
                    )
                    jabatan = st.text_input(
                        "Jabatan Responden",
                        value=st.session_state.company_data.get("Jabatan", ""),
                        placeholder="Contoh: Ahli K3 Umum / HSE Supervisor"
                    )
                    email = st.text_input(
                        "Email Responden*",
                        value=st.session_state.company_data.get("Email Responden", ""),
                        placeholder="hse@perusahaan.co.id"
                    )
                    kbli_list = [
                        "Industri Pengolahan",
                        "Konstruksi",
                        "Pertambangan dan Penggalian",
                        "Pengangkutan dan Pergudangan",
                        "Pertanian, Kehutanan, dan Perikanan",
                        "Perdagangan Besar dan Eceran",
                        "Penyediaan Akomodasi dan Makan Minum",
                        "Informasi dan Komunikasi",
                        "Aktivitas Kesehatan Manusia",
                        "Lainnya"
                    ]
                    kbli = st.selectbox("Jenis Usaha (KBLI)", kbli_list)
                    kategori_pekerja = st.selectbox("Kategori Jumlah Tenaga Kerja", [
                        "Industri Besar (≥ 100 orang)",
                        "Industri Sedang (20 - 99 orang)",
                        "Industri Kecil (5 - 19 orang)",
                        "Industri Rumah Tangga (1 - 4 orang)"
                    ])

                btn_lanjut_baru = st.form_submit_button("Mulai Penilaian Gedung ➔", width="stretch", type="primary")

                if btn_lanjut_baru:
                    if not nama_pt.strip() or not nib.strip() or not responden.strip() or not email.strip():
                        st.error("Nama Perusahaan, No. Induk, Responden, dan Email wajib diisi!")
                    else:
                        new_key = f"HIBB-{uuid.uuid4().hex[:6].upper()}"
                        st.session_state.company_data = {
                            "Company Key": new_key,
                            "Waktu Pengisian": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Nama Perusahaan": nama_pt.strip(),
                            "Legalitas": legalitas,
                            "No Induk Perusahaan": nib.strip(),
                            "No Telp Perusahaan": telepon.strip(),
                            "Lokasi Pengujian": lokasi.strip(),
                            "Nama Responden": responden.strip(),
                            "Jabatan": jabatan.strip(),
                            "Email Responden": email.strip(),
                            "Jenis Usaha (KBLI)": kbli,
                            "Kategori Pekerja": kategori_pekerja,
                            "Nama Lembaga K3": "-",
                            "Nama Ahli K3": "-",
                            "Nomor SKP Ahli": "-",
                            "Status Verifikasi": "Menunggu Verifikasi",
                            "Catatan Verifikator": ""
                        }
                        st.session_state.daftar_gedung = []
                        st.session_state.perusahaan_step = "info_gedung"
                        st.rerun()

        # TAB 2: SUDAH PERNAH ASESMEN (MASUKKAN COMPANY KEY)
        with tab_key_lama:
            st.info("ℹ️ Masukkan **Company Key** yang telah Anda terima pada asesmen sebelumnya untuk memuat profil perusahaan dan riwayat objek gedung yang telah terdaftar.")

            df_p_all, df_s_all = db.load_all_surveys()
            list_keys_tersedia = []
            if not df_p_all.empty and "Company Key" in df_p_all.columns:
                list_keys_tersedia = [str(k).strip() for k in df_p_all["Company Key"].dropna().unique() if str(k).strip()]

            col_in1, col_in2 = st.columns([2, 1])
            with col_in1:
                key_input = st.text_input(
                    "Masukkan Company Key Anda:",
                    placeholder="Contoh: HIBB-DEMO-01 atau HIBB-XXXXXX"
                )
            with col_in2:
                if list_keys_tersedia:
                    pilih_cepat_key = st.selectbox("Atau Pilih dari Asesmen Tersedia:", ["-- Pilih --"] + list_keys_tersedia)
                    if pilih_cepat_key != "-- Pilih --":
                        key_input = pilih_cepat_key

            if st.button("🔍 Cari & Muat Data Asesmen", type="primary", width="stretch"):
                if not key_input or not key_input.strip():
                    st.error("Masukkan Company Key terlebih dahulu!")
                else:
                    target_key = key_input.strip().upper()
                    match_p = df_p_all[df_p_all["Company Key"].astype(str).str.strip().str.upper() == target_key] if not df_p_all.empty else pd.DataFrame()

                    if match_p.empty:
                        st.warning(f"⚠️ Company Key '{target_key}' tidak ditemukan dalam basis data survei. Pastikan Anda telah menginput kode dengan benar, atau gunakan tab 'Asesmen Baru'.")
                    else:
                        row_p = match_p.iloc[0].to_dict()
                        st.session_state.company_data = row_p

                        # Muat daftar gedung
                        match_s = df_s_all[df_s_all["Company Key"].astype(str).str.strip().str.upper() == target_key] if not df_s_all.empty else pd.DataFrame()
                        loaded_gedung = match_s.to_dict(orient="records") if not match_s.empty else []
                        st.session_state.daftar_gedung = loaded_gedung

                        st.success(f"✅ Data perusahaan **{row_p.get('Nama Perusahaan')}** berhasil dimuat! Ditemukan **{len(loaded_gedung)} objek gedung** tersimpan.")

            # Jika data sudah dimuat
            if st.session_state.company_data and st.session_state.company_data.get("Company Key"):
                c_data = st.session_state.company_data
                st.markdown(f"""
                <div class="k3-card">
                    <h4>🏢 {c_data.get('Nama Perusahaan')} ({c_data.get('Legalitas', 'PT')})</h4>
                    <p><b>Company Key:</b> <code>{c_data.get('Company Key')}</code> | <b>Waktu Asesmen:</b> {c_data.get('Waktu Pengisian', '-')} | <b>Status:</b> <b>{c_data.get('Status Verifikasi', 'Menunggu Verifikasi')}</b></p>
                    <p><b>Lokasi:</b> {c_data.get('Lokasi Pengujian', '-')} | <b>Penanggung Jawab:</b> {c_data.get('Nama Responden', '-')} ({c_data.get('Email Responden', '-')})</p>
                    <p><b>Jumlah Gedung Terdaftar:</b> {len(st.session_state.daftar_gedung)} Gedung</p>
                </div>
                """, unsafe_allow_html=True)

                col_lanjut_a, col_lanjut_b = st.columns(2)
                with col_lanjut_a:
                    if st.button("➕ Tambah / Lanjutkan Penilaian Gedung Baru ➔", width="stretch", type="primary"):
                        st.session_state.perusahaan_step = "info_gedung"
                        st.rerun()
                with col_lanjut_b:
                    if st.button("📊 Lihat Hasil Asesmen Lengkap & Evaluasi Toilet ➔", width="stretch"):
                        st.session_state.perusahaan_step = "submit_kuisioner"
                        st.rerun()

    # STEP 2: ISI INFO GEDUNG (NAMA, JUMLAH PEKERJA, CHECKLIST FASILITAS)
    elif st.session_state.perusahaan_step == "info_gedung":
        nomor_gedung = len(st.session_state.daftar_gedung) + 1
        st.subheader(f"Langkah 2: Isi Info Gedung (Objek ke-{nomor_gedung})")
        st.caption(f"Perusahaan: **{st.session_state.company_data.get('Nama Perusahaan')}** | Kode: `{st.session_state.company_data.get('Company Key')}`")

        with st.form("form_info_gedung"):
            col_a, col_b = st.columns([1.5, 1])
            with col_a:
                nama_gedung = st.text_input(
                    f"Nama / Identitas Gedung ke-{nomor_gedung}*",
                    placeholder="Contoh: Gedung Perkantoran Pusat / Pabrik Line 1 / Gudang Logistik"
                )
                jenis_objek = st.selectbox("Klasifikasi Objek Bangunan:", [
                    "1. Perkantoran",
                    "2. Pabrik / Area Produksi",
                    "3. Workshop / Bengkel Kerja",
                    "4. Pergudangan / Warehouse",
                    "5. Kantin & Dapur Kerja",
                    "6. Bangunan Bawah Tanah / Basement",
                    "7. Tempat Kerja Lainnya"
                ])

            with col_b:
                total_pekerja = st.number_input("Total Pekerja di Gedung Ini*", min_value=1, value=25, step=1)
                c_p1, c_p2 = st.columns(2)
                with c_p1:
                    pekerja_pria = st.number_input("Pekerja Laki-laki", min_value=0, value=15, step=1)
                with c_p2:
                    pekerja_wanita = st.number_input("Pekerja Perempuan", min_value=0, value=10, step=1)
                pekerja_disabilitas = st.number_input("Pekerja Penyandang Disabilitas", min_value=0, value=0, step=1)

            st.markdown("---")
            st.markdown("#### 📋 Checklist Fasilitas yang Ada di Gedung Ini:")
            st.write("Centang fasilitas yang benar-benar ada. Kuesioner hanya akan menampilkan pertanyaan sesuai fasilitas yang Anda pilih.")

            selected_fac_ids = []
            cols_fac = st.columns(2)
            for idx, fac in enumerate(KELOMPOK_FASILITAS):
                with cols_fac[idx % 2]:
                    checked = st.checkbox(
                        f"**{fac['icon']} {fac['nama']}**",
                        value=fac["default_checked"],
                        key=f"fac_{fac['id']}_{nomor_gedung}",
                        help=fac["deskripsi"]
                    )
                    st.caption(f"_{fac['deskripsi']}_")
                    if checked:
                        selected_fac_ids.append(fac["id"])

            st.markdown("---")
            btn_mulai_soal = st.form_submit_button("Lanjut ke Pertanyaan Fasilitas ➔", type="primary", width="stretch")

            if btn_mulai_soal:
                if not nama_gedung.strip():
                    st.error("Nama Gedung wajib diisi!")
                elif not selected_fac_ids:
                    st.error("Pilih minimal satu kelompok fasilitas yang ada di gedung ini!")
                else:
                    st.session_state.current_gedung = {
                        "Company Key": st.session_state.company_data.get("Company Key"),
                        "Nomor Gedung": nomor_gedung,
                        "Nama Gedung": nama_gedung.strip(),
                        "Jenis Objek": jenis_objek,
                        "Total Pekerja": total_pekerja,
                        "Pekerja Laki-laki": pekerja_pria,
                        "Pekerja Perempuan": pekerja_wanita,
                        "Pekerja Disabilitas": pekerja_disabilitas,
                        "Fasilitas Terpilih": selected_fac_ids,
                        "Waktu Penilaian Gedung": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.selected_facilities = selected_fac_ids
                    st.session_state.perusahaan_step = "kuesioner_fasilitas"
                    st.rerun()

        if st.button("⬅ Kembali ke Identitas Perusahaan"):
            st.session_state.perusahaan_step = "info_perusahaan"
            st.rerun()

    # STEP 3: KUESIONER SESUAI FASILITAS YANG ADA
    elif st.session_state.perusahaan_step == "kuesioner_fasilitas":
        current_g = st.session_state.current_gedung
        st.subheader(f"Langkah 3: Pertanyaan Sesuai Fasilitas — {current_g.get('Nama Gedung')}")
        st.caption(f"Jumlah Pekerja: {current_g.get('Total Pekerja')} orang | Fasilitas Terpilih: {len(st.session_state.selected_facilities)} Kelompok")

        # Khusus input jumlah toilet jika fasilitas toilet dipilih
        if "toilet_sanitasi" in st.session_state.selected_facilities:
            st.markdown("### 🚻 Evaluasi Rasio Jumlah Toilet Gedung:")
            syarat_toilet = hitung_kebutuhan_toilet(to_int(current_g.get("Total Pekerja", 0)))
            col_t1, col_t2 = st.columns([1, 2])
            with col_t1:
                jml_toilet = st.number_input(
                    "Jumlah jamban/toilet di gedung ini:*",
                    min_value=0,
                    value=to_int(current_g.get("Jumlah Toilet", max(1, syarat_toilet))),
                    step=1
                )
                current_g["Jumlah Toilet"] = jml_toilet
            with col_t2:
                status_toilet = "✅ Memenuhi Standar Minimal" if jml_toilet >= syarat_toilet else f"⚠️ Kurang dari Standar Minimal (Butuh {syarat_toilet} toilet)"
                st.info(f"**Standar Permenaker No. 5/2018:** Kebutuhan minimal untuk {current_g.get('Total Pekerja')} pekerja adalah **{syarat_toilet} toilet**.  \nStatus: **{status_toilet}**")

        st.markdown("---")

        # Kelompokkan pertanyaan hanya untuk fasilitas yang dicentang
        fasilitas_aktif = [f for f in KELOMPOK_FASILITAS if f["id"] in st.session_state.selected_facilities]
        tabs = st.tabs([f"{f['icon']} {f['nama']}" for f in fasilitas_aktif])

        for idx, fac in enumerate(fasilitas_aktif):
            with tabs[idx]:
                st.markdown(f"#### {fac['icon']} {fac['nama']}")
                st.caption(fac["deskripsi"])

                for q_id in fac["soal_ids"]:
                    q_data = MASTER_PERTANYAAN.get(q_id)
                    if not q_data:
                        continue

                    st.markdown(f"**[{q_id}] {q_data['teks']}**")

                    # Pop-up Infografis jika pertanyaan memiliki istilah khusus
                    if q_data.get("has_infografis") or q_id in INFOGRAFIS_DATA:
                        render_infografis_hover_html(q_id)

                    # Widget sesuai tipe pertanyaan
                    if q_data["tipe"] == "radio":
                        curr_ans = current_g.get(f"{q_id}_Jawaban", q_data["opsi"][0])
                        ans_idx = q_data["opsi"].index(curr_ans) if curr_ans in q_data["opsi"] else 0
                        
                        penjelasan_help = None
                        if q_id == 'Q9':
                            penjelasan_help = "Ruang gerak bebas yang dimaksudnya adalah..."
                        
                        chosen = st.radio(
                            label=f"Pilihan untuk {q_id}:",
                            options=q_data["opsi"],
                            index=ans_idx,
                            key=f"radio_{q_id}_{current_g.get('Nomor Gedung')}",
                            label_visibility="collapsed",
                            help = penjelasan_help
                        )
                        score = q_data["opsi"].index(chosen)
                        current_g[f"{q_id}_Jawaban"] = chosen
                        current_g[f"{q_id}_Poin"] = score

                    elif q_data["tipe"] == "checkbox":
                        st.write("Centang kelengkapan yang terpenuhi:")
                        c_boxes = st.columns(min(len(q_data["opsi"]), 3))
                        selected_cb = []
                        for cb_i, cb_opt in enumerate(q_data["opsi"]):
                            with c_boxes[cb_i % len(c_boxes)]:
                                is_checked = st.checkbox(
                                    cb_opt,
                                    key=f"cb_{q_id}_{cb_i}_{current_g.get('Nomor Gedung')}"
                                )
                                if is_checked:
                                    selected_cb.append(cb_opt)

                        current_g[f"{q_id}_Jawaban"] = ", ".join(selected_cb) if selected_cb else "Tidak terpenuhi"
                        current_g[f"{q_id}_Poin"] = len(selected_cb)

                    elif q_data["tipe"] == "auto_toilet":
                        t_avail = to_int(current_g.get("Jumlah Toilet", 0))
                        t_need = hitung_kebutuhan_toilet(to_int(current_g.get("Total Pekerja", 0)))
                        lulus = t_avail >= t_need
                        current_g[f"{q_id}_Jawaban"] = f"{'Memenuhi' if lulus else 'Tidak memenuhi'} ({t_avail}/{t_need} toilet)"
                        current_g[f"{q_id}_Poin"] = 1 if lulus else 0
                        st.caption(f"Evaluasi rasio: {current_g[f'{q_id}_Jawaban']}")

                    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        st.markdown("---")
        c_btn1, c_btn2 = st.columns([1, 1])
        with c_btn1:
            if st.button("⬅ Ubah Checklist Fasilitas Gedung"):
                st.session_state.perusahaan_step = "info_gedung"
                st.rerun()

        with c_btn2:
            if st.button("Simpan Data Gedung & Lanjut ke Hasil ➔", type="primary", width="stretch"):
                # Hitung subtotal skor per topik
                topik_1_score = sum(to_int(current_g.get(f"Q{i}_Poin", 0)) for i in range(1, 33))
                topik_2_score = sum(to_int(current_g.get(f"Q{i}_Poin", 0)) for i in range(33, 55))
                topik_3_score = sum(to_int(current_g.get(f"Q{i}_Poin", 0)) for i in range(55, 61))
                topik_4_score = sum(to_int(current_g.get(f"Q{i}_Poin", 0)) for i in range(61, 66))

                current_g["Skor_Topik_1"] = topik_1_score
                current_g["Skor_Topik_2"] = topik_2_score
                current_g["Skor_Topik_3"] = topik_3_score
                current_g["Skor_Topik_4"] = topik_4_score
                current_g["Total Poin Gedung"] = topik_1_score + topik_2_score + topik_3_score + topik_4_score

                # Evaluasi pemenuhan standar & butir kurang
                eval_res = analisis_evaluasi_gedung(current_g, st.session_state.selected_facilities)
                current_g["Status Pemenuhan"] = eval_res["status_pemenuhan"]
                current_g["Bidang perlu diperbaiki"] = ", ".join(eval_res["bidang_perlu_perbaikan"]) if eval_res["bidang_perlu_perbaikan"] else "Tidak ada"

                # Masukkan ke daftar gedung sesi ini
                st.session_state.daftar_gedung.append(current_g)
                st.session_state.perusahaan_step = "submit_kuisioner"
                st.rerun()

    # STEP 4: HASIL ASESMEN, POIN KURANG & STANDAR TOILET MANDIRI + KUMULATIF
    elif st.session_state.perusahaan_step == "submit_kuisioner":
        # Evaluasi toilet kumulatif
        st.session_state.daftar_gedung = evaluasi_toilet_daftar_gedung(st.session_state.daftar_gedung)

        st.subheader("Hasil Asesmen Mandiri K3 Perusahaan")
        st.success(f"🎉 Sebanyak **{len(st.session_state.daftar_gedung)} objek gedung** telah dinilai dalam asesmen ini.")

        c_info1, c_info2 = st.columns(2)
        with c_info1:
            st.markdown(f"""
            **Profil Perusahaan:**
            - **Perusahaan:** {st.session_state.company_data.get('Nama Perusahaan')}
            - **NIB:** `{st.session_state.company_data.get('No Induk Perusahaan')}`
            - **Responden:** {st.session_state.company_data.get('Nama Responden')}
            - **Jenis Usaha (KBLI):** {st.session_state.company_data.get('Jenis Usaha (KBLI)')}
            """)
        with c_info2:
            st.markdown(f"""
            **Kode Asesmen (Company Key) Anda:**
            # `{st.session_state.company_data.get('Company Key')}`
            _Simpan kode ini untuk melanjutkan survei atau diberikan kepada Penguji K3 (PJK3 / Balai K3)._
            """)

        # Tampilkan Evaluasi Toilet Mandiri + Kumulatif
        render_evaluasi_toilet_card(st.session_state.daftar_gedung)

        st.markdown("---")
        st.markdown("### 📊 Ringkasan Skor & Evaluasi K3 Per Objek Gedung:")

        # Tampilkan tabel ringkasan gedung
        ringkas_list = []
        for g in st.session_state.daftar_gedung:
            ringkas_list.append({
                "No": g.get("Nomor Gedung"),
                "Nama Gedung": g.get("Nama Gedung"),
                "Jenis Objek": g.get("Jenis Objek"),
                "Total Pekerja": g.get("Total Pekerja"),
                "Fisik (T1)": g.get("Skor_Topik_1"),
                "Sanitasi (T2)": g.get("Skor_Topik_2"),
                "Udara (T3)": g.get("Skor_Topik_3"),
                "Housekeeping (T4)": g.get("Skor_Topik_4"),
                "Total Skor": g.get("Total Poin Gedung"),
                "Status": g.get("Status Pemenuhan")
            })
        st.dataframe(pd.DataFrame(ringkas_list), width="stretch")

        st.markdown("---")
        st.markdown("### 📋 Detail Poin-Poin Defisit Per Gedung:")

        # Tampilkan poin-poin yang kurang untuk setiap gedung
        for idx, g in enumerate(st.session_state.daftar_gedung):
            nama_g = g.get("Nama Gedung", f"Gedung {idx+1}")
            with st.expander(f"🏢 **{nama_g}** — Skor: {g.get('Total Poin Gedung')} ({g.get('Status Pemenuhan')})", expanded=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Kondisi Fisik", g.get("Skor_Topik_1", "-"))
                c2.metric("Sanitasi Kebersihan", g.get("Skor_Topik_2", "-"))
                c3.metric("Kebutuhan Udara", g.get("Skor_Topik_3", "-"))
                c4.metric("Housekeeping", g.get("Skor_Topik_4", "-"))

                fac_ids = g.get("Fasilitas Terpilih")
                render_poin_kurang_gedung(g, fac_ids)

        st.markdown("---")
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if st.button("➕ Tambah Gedung Lain", width="stretch"):
                st.session_state.current_gedung = {}
                st.session_state.perusahaan_step = "info_gedung"
                st.rerun()

        with col_act2:
            if st.button("🚀 Simpan / Submit Kuisioner ke Database", type="primary", width="stretch"):
                with st.spinner("Menyimpan data survei ke Google Sheets & penyimpanan lokal..."):
                    berhasil = db.save_survey_submission(st.session_state.company_data, st.session_state.daftar_gedung)

                if berhasil:
                    st.balloons()
                    st.success("✅ Seluruh data kuisioner berhasil dikirim dan tersimpan!")
                    st.info(f"Berikan Kode Asesmen: **{st.session_state.company_data.get('Company Key')}** kepada Penguji PJK3 / Balai K3 untuk tahap verifikasi.")

        if st.button("🔄 Mulai Survei Baru dari Awal"):
            st.session_state.perusahaan_step = "info_perusahaan"
            st.session_state.daftar_gedung = []
            st.session_state.company_data = {}
            st.session_state.current_gedung = {}
            st.rerun()


# ==============================================================================
# PERAN 2: PJK3 / BALAI K3
# Fitur:
# 1. Masukkan Kode Akses Khusus K3
# 2. Pilihan: Verifikasi Asesmen ATAU Lihat Hasil Asesmen (Historis)
# 3. Isi Verifikasi: Sama seperti Asesmen, diisi oleh Penguji K3
# 4. Hasil Asesmen: Diperlihatkan poin-poin yang kurang & standar toilet mandiri + kumulatif
# ==============================================================================
elif st.session_state.active_role == "🛡️ PJK3 / Balai K3":

    # CEK AUTENTIKASI KODE AKSES KHUSUS K3
    if not st.session_state.k3_authenticated:
        st.subheader("🔐 Autentikasi Penguji K3 & Balai K3")
        st.write("Portal ini dikhususkan bagi Pengawas K3, Penguji K3 (PJK3), dan Tim Balai Keselamatan dan Kesehatan Kerja. Masukkan **Kode Akses Khusus K3** untuk membuka instrumen verifikasi.")

        with st.form("form_auth_k3"):
            c_auth1, c_auth2 = st.columns([2, 1])
            with c_auth1:
                input_pass = st.text_input("Kode Akses Khusus K3:*", type="password", placeholder="Masukkan kode otorisasi K3...")
            with c_auth2:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                btn_login = st.form_submit_button("🔓 Buka Portal K3", type="primary", width="stretch")

            if btn_login:
                if input_pass.strip().upper() in [p.upper() for p in K3_PASSCODES]:
                    st.session_state.k3_authenticated = True
                    st.success("✅ Otorisasi berhasil! Selamat datang di Portal Penguji K3 & Balai K3.")
                    st.rerun()
                else:
                    st.error("❌ Kode akses tidak valid! Pastikan Anda memiliki wewenang pengujian K3.")

        st.caption("💡 *Kode akses demo pengujian resmi:* `K3-BALAI-2026`")

    # JIKA SUDAH TERAUTENTIKASI
    else:
        st.markdown("""
        <div style="background: #f0fdf4; border: 1px solid #86efac; border-radius: 10px; padding: 12px 18px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 1.1rem;">👤</span> <b>Petugas Penguji K3 Terverifikasi</b> &nbsp;|&nbsp; Akses Pengawasan Resmi K3 Lingkungan Kerja
            </div>
            <span style="background: #22c55e; color: white; padding: 3px 10px; border-radius: 9999px; font-size: 0.78rem; font-weight: 700;">AKTIF</span>
        </div>
        """, unsafe_allow_html=True)

        # DUA PILIHAN UTAMA: VERIFIKASI ASESMEN vs LIHAT HASIL ASESMEN (HISTORIS)
        tab_verif_k3, tab_historis_k3 = st.tabs([
            "✅ Verifikasi Asesmen (Lapangan)",
            "📊 Lihat Hasil Asesmen (Historis & Monitoring Waktu)"
        ])

        df_p_all, df_s_all = db.load_all_surveys()

        # ----------------------------------------------------------------------
        # PILIHAN 1: VERIFIKASI ASESMEN
        # Isi dari verifikasi: SAMA SEPERTI ASESMEN, HANYA SAJA DIISI OLEH K3
        # ----------------------------------------------------------------------
        with tab_verif_k3:
            st.subheader("Verifikasi Lapangan Hasil Asesmen Mandiri Perusahaan")
            st.write("Penguji K3 memvalidasi dan mengisi instrumen pengujian langsung di lapangan (sama seperti kuesioner asesmen) untuk membandingkan temuan riil dengan klaim perusahaan.")

            list_keys_submitted = []
            if not df_p_all.empty and "Company Key" in df_p_all.columns:
                list_keys_submitted = [str(k).strip() for k in df_p_all["Company Key"].dropna().unique() if str(k).strip()]

            col_vk1, col_vk2 = st.columns([2, 1])
            with col_vk1:
                pjk3_key_in = st.text_input(
                    "Masukkan Company Key Perusahaan yang Diverifikasi:",
                    value=st.session_state.penguji_kode_input,
                    placeholder="Contoh: HIBB-DEMO-01"
                )
            with col_vk2:
                if list_keys_submitted:
                    pilih_cepat_verif = st.selectbox("Atau Pilih dari Daftar Asesmen Masuk:", ["-- Pilih Kode --"] + list_keys_submitted)
                    if pilih_cepat_verif != "-- Pilih Kode --":
                        pjk3_key_in = pilih_cepat_verif

            if pjk3_key_in:
                st.session_state.penguji_kode_input = pjk3_key_in.strip().upper()

            active_key = st.session_state.penguji_kode_input.strip().upper()
            comp_row = None
            gedung_rows = pd.DataFrame()

            if active_key and not df_p_all.empty and "Company Key" in df_p_all.columns:
                matching_p = df_p_all[df_p_all["Company Key"].astype(str).str.strip().str.upper() == active_key]
                if not matching_p.empty:
                    comp_row = matching_p.iloc[0].to_dict()

                if not df_s_all.empty and "Company Key" in df_s_all.columns:
                    gedung_rows = df_s_all[df_s_all["Company Key"].astype(str).str.strip().str.upper() == active_key]

            if not active_key:
                st.info("ℹ️ Silakan masukkan atau pilih Company Key di atas untuk membuka lembar verifikasi teknis.")
            elif comp_row is None:
                st.warning(f"⚠️ Company Key '{active_key}' tidak ditemukan. Pastikan pihak perusahaan telah melakukan submit asesmen.")
            else:
                # Ringkasan Profil Perusahaan
                st_verif = comp_row.get("Status Verifikasi", "Menunggu Verifikasi")
                st.markdown(f"""
                <div class="k3-card">
                    <h4>🏢 {comp_row.get('Nama Perusahaan')} ({comp_row.get('Legalitas', 'PT')})</h4>
                    <p><b>Company Key:</b> <code>{active_key}</code> | <b>Waktu Survei Mandiri:</b> {comp_row.get('Waktu Pengisian', '-')} | <b>Status Saat Ini:</b> <b>{st_verif}</b></p>
                    <p><b>Lokasi:</b> {comp_row.get('Lokasi Pengujian', '-')} | <b>Sektor:</b> {comp_row.get('Jenis Usaha (KBLI)', '-')} | <b>Responden:</b> {comp_row.get('Nama Responden', '-')} ({comp_row.get('Email Responden', '-')})</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("---")
                st.markdown("### 📝 Identitas Lembaga & Ahli K3 Penguji")

                c_vinfo1, c_vinfo2, c_vinfo3 = st.columns(3)
                with c_vinfo1:
                    nama_lembaga_k3 = st.text_input(
                        "Nama Lembaga PJK3 / Balai K3*",
                        value=comp_row.get("Nama Lembaga K3", "Balai K3 / PT Mitra K3 Prima") if comp_row.get("Nama Lembaga K3") != "-" else "Balai K3 / PT Mitra K3 Prima"
                    )
                with c_vinfo2:
                    nama_ahli_k3 = st.text_input(
                        "Nama Ahli K3 Penguji*",
                        value=comp_row.get("Nama Ahli K3", "Ir. Hendra Gunawan, S.T., M.KKK") if comp_row.get("Nama Ahli K3") != "-" else "Ir. Hendra Gunawan, S.T., M.KKK"
                    )
                with c_vinfo3:
                    skp_ahli_k3 = st.text_input(
                        "Nomor SKP Ahli K3 Penguji*",
                        value=comp_row.get("Nomor SKP Ahli", "KEP.123/BINWASK3/2024") if comp_row.get("Nomor SKP Ahli") != "-" else "KEP.123/BINWASK3/2024"
                    )

                st.markdown("---")
                st.markdown("### 📋 Kuesioner Verifikasi Teknis Lapangan (Diisi oleh K3)")
                st.write("Sama seperti asesmen mandiri, Penguji K3 melakukan inspeksi langsung pada setiap objek gedung dan mengisi instrumen penilaian baku berikut:")

                list_gedung_asli = gedung_rows.to_dict(orient="records") if not gedung_rows.empty else []

                if not list_gedung_asli:
                    st.warning("Belum ada data gedung yang disubmit oleh perusahaan untuk kode ini.")
                else:
                    # Tabs per gedung untuk verifikasi
                    tab_gedung_names = [f"🏢 {g.get('Nama Gedung', f'Gedung {idx+1}')}" for idx, g in enumerate(list_gedung_asli)]
                    tabs_gedung_verif = st.tabs(tab_gedung_names)

                    list_gedung_terverifikasi = []

                    for g_idx, g_data in enumerate(list_gedung_asli):
                        with tabs_gedung_verif[g_idx]:
                            g_verif = g_data.copy()
                            nama_g = g_verif.get("Nama Gedung", f"Gedung {g_idx+1}")
                            total_pekerja_g = to_int(g_verif.get("Total Pekerja", 20))

                            st.markdown(f"#### Evaluasi Lapangan: {nama_g}")
                            st.caption(f"Klasifikasi: {g_verif.get('Jenis Objek', '-')} | Tenaga Kerja: {total_pekerja_g} orang (Pria: {g_verif.get('Pekerja Laki-laki', 0)}, Wanita: {g_verif.get('Pekerja Perempuan', 0)})")

                            # 1. Verifikasi Toilet di Lapangan
                            st.markdown("##### 🚻 1. Verifikasi Ketersediaan & Rasio Jamban/Toilet:")
                            syarat_toilet_g = hitung_kebutuhan_toilet(total_pekerja_g)
                            c_vt1, c_vt2 = st.columns([1, 2])
                            with c_vt1:
                                toilet_fisik_k3 = st.number_input(
                                    f"Jumlah toilet hasil verifikasi fisik K3 ({nama_g}):*",
                                    min_value=0,
                                    value=to_int(g_verif.get("Jumlah Toilet", max(1, syarat_toilet_g))),
                                    step=1,
                                    key=f"verif_toilet_{g_idx}_{active_key}"
                                )
                                g_verif["Jumlah Toilet"] = toilet_fisik_k3
                            with c_vt2:
                                st_toilet_k3 = "✅ Memenuhi Standar Minimal" if toilet_fisik_k3 >= syarat_toilet_g else f"⚠️ Kurang dari Standar Minimal (Butuh {syarat_toilet_g} toilet)"
                                st.info(f"**Klaim Perusahaan:** {g_data.get('Jumlah Toilet', '-')} toilet.  \n**Verifikasi Fisik K3:** {toilet_fisik_k3} toilet (Standar Permenaker 5/2018: **min. {syarat_toilet_g} toilet**).  \nStatus: **{st_toilet_k3}**")

                            st.markdown("---")

                            # 2. Verifikasi Fasilitas (Checklist)
                            fasilitas_terpilih = g_verif.get("Fasilitas Terpilih", ["struktur_gedung", "toilet_sanitasi", "sampah_pakaian", "kebutuhan_udara", "housekeeping"])
                            fasilitas_aktif_v = [f for f in KELOMPOK_FASILITAS if f["id"] in fasilitas_terpilih]

                            tabs_sub_soal = st.tabs([f"{f['icon']} {f['nama']}" for f in fasilitas_aktif_v])

                            for f_idx, fac in enumerate(fasilitas_aktif_v):
                                with tabs_sub_soal[f_idx]:
                                    st.markdown(f"**Verifikasi Bidang:** {fac['nama']}")

                                    for q_id in fac["soal_ids"]:
                                        q_data = MASTER_PERTANYAAN.get(q_id)
                                        if not q_data:
                                            continue

                                        st.markdown(f"**[{q_id}] {q_data['teks']}**")

                                        # Pop-up Infografis
                                        if q_data.get("has_infografis") or q_id in INFOGRAFIS_DATA:
                                            render_infografis_hover_html(q_id)

                                        # Tampilkan jawaban mandiri perusahaan sebagai referensi penguji
                                        jawaban_awal_pt = g_verif.get(f"{q_id}_Jawaban", "Belum terisi")
                                        st.caption(f"📌 *Jawaban Mandiri Perusahaan:* **{jawaban_awal_pt}**")

                                        # Input Verifikasi oleh Penguji K3
                                        if q_data["tipe"] == "radio":
                                            # Ambil jawaban eksisting jika ada
                                            curr_v_ans = g_verif.get(f"{q_id}_Jawaban", q_data["opsi"][0])
                                            v_idx = q_data["opsi"].index(curr_v_ans) if curr_v_ans in q_data["opsi"] else 0
                                            chosen_v = st.radio(
                                                label=f"Hasil Pengujian Lapangan K3 ({q_id}):",
                                                options=q_data["opsi"],
                                                index=v_idx,
                                                key=f"pjk3_radio_{q_id}_{g_idx}_{active_key}"
                                            )
                                            score_v = q_data["opsi"].index(chosen_v)
                                            g_verif[f"{q_id}_Jawaban"] = chosen_v
                                            g_verif[f"{q_id}_Poin"] = score_v

                                        elif q_data["tipe"] == "checkbox":
                                            st.write("Verifikasi kelengkapan yang nyata ada di lapangan:")
                                            c_boxes_v = st.columns(min(len(q_data["opsi"]), 3))
                                            sel_cb_v = []
                                            for cb_i, cb_opt in enumerate(q_data["opsi"]):
                                                with c_boxes_v[cb_i % len(c_boxes_v)]:
                                                    checked_v = st.checkbox(
                                                        cb_opt,
                                                        key=f"pjk3_cb_{q_id}_{cb_i}_{g_idx}_{active_key}"
                                                    )
                                                    if checked_v:
                                                        sel_cb_v.append(cb_opt)

                                            g_verif[f"{q_id}_Jawaban"] = ", ".join(sel_cb_v) if sel_cb_v else "Tidak terpenuhi"
                                            g_verif[f"{q_id}_Poin"] = len(sel_cb_v)

                                        elif q_data["tipe"] == "auto_toilet":
                                            t_ok = toilet_fisik_k3 >= syarat_toilet_g
                                            g_verif[f"{q_id}_Jawaban"] = f"{'Memenuhi' if t_ok else 'Tidak memenuhi'} ({toilet_fisik_k3}/{syarat_toilet_g} toilet)"
                                            g_verif[f"{q_id}_Poin"] = 1 if t_ok else 0
                                            st.caption(f"Verifikasi rasio toilet: {g_verif[f'{q_id}_Jawaban']}")

                                        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

                            # Hitung ulang skor terverifikasi untuk gedung ini
                            t1_v = sum(to_int(g_verif.get(f"Q{i}_Poin", 0)) for i in range(1, 33))
                            t2_v = sum(to_int(g_verif.get(f"Q{i}_Poin", 0)) for i in range(33, 55))
                            t3_v = sum(to_int(g_verif.get(f"Q{i}_Poin", 0)) for i in range(55, 61))
                            t4_v = sum(to_int(g_verif.get(f"Q{i}_Poin", 0)) for i in range(61, 66))

                            g_verif["Skor_Topik_1"] = t1_v
                            g_verif["Skor_Topik_2"] = t2_v
                            g_verif["Skor_Topik_3"] = t3_v
                            g_verif["Skor_Topik_4"] = t4_v
                            g_verif["Total Poin Gedung"] = t1_v + t2_v + t3_v + t4_v

                            eval_res_v = analisis_evaluasi_gedung(g_verif, fasilitas_terpilih)
                            g_verif["Status Pemenuhan"] = eval_res_v["status_pemenuhan"]
                            g_verif["Bidang perlu diperbaiki"] = ", ".join(eval_res_v["bidang_perlu_perbaikan"]) if eval_res_v["bidang_perlu_perbaikan"] else "Tidak ada"

                            list_gedung_terverifikasi.append(g_verif)

                    st.markdown("---")
                    st.markdown("### ⚖️ Keputusan Hasil Verifikasi & Rekomendasi Teknis K3")

                    with st.form("form_keputusan_verifikasi"):
                        c_dec1, c_dec2 = st.columns(2)
                        with c_dec1:
                            pilihan_status_k3 = [
                                "Terverifikasi Memenuhi Standar",
                                "Perlu Tindakan Perbaikan",
                                "Menunggu Verifikasi Lanjutan"
                            ]
                            curr_status_idx = pilihan_status_k3.index(st_verif) if st_verif in pilihan_status_k3 else 0
                            status_keputusan = st.selectbox("Keputusan Status Verifikasi K3:*", pilihan_status_k3, index=curr_status_idx)

                        with c_dec2:
                            st.write("Keputusan ini akan memperbarui status kepatuhan perusahaan di database resmi.")

                        catatan_lapangan_k3 = st.text_area(
                            "Catatan Temuan Lapangan & Rekomendasi Tindakan Korektif K3:*",
                            value=comp_row.get("Catatan Verifikator", ""),
                            placeholder="Tuliskan temuan deviasi hasil inspeksi lapangan dibanding klaim self-assessment, serta tindakan teknis korektif yang wajib dipenuhi perusahaan...",
                            height=120
                        )

                        btn_simpan_verif_k3 = st.form_submit_button("💾 Simpan & Terbitkan Hasil Verifikasi K3", type="primary", width="stretch")

                        if btn_simpan_verif_k3:
                            if not nama_lembaga_k3.strip() or not nama_ahli_k3.strip() or not catatan_lapangan_k3.strip():
                                st.error("Nama Lembaga K3, Nama Ahli K3 Penguji, dan Catatan Rekomendasi wajib diisi!")
                            else:
                                verif_payload = {
                                    "Nama Lembaga K3": nama_lembaga_k3.strip(),
                                    "Nama Ahli K3": nama_ahli_k3.strip(),
                                    "Nomor SKP Ahli": skp_ahli_k3.strip(),
                                    "Status Verifikasi": status_keputusan,
                                    "Catatan Verifikator": catatan_lapangan_k3.strip(),
                                    "Nama Verifikator": nama_ahli_k3.strip()
                                }

                                # Evaluasi toilet kumulatif untuk list gedung terverifikasi
                                list_gedung_final = evaluasi_toilet_daftar_gedung(list_gedung_terverifikasi)

                                with st.spinner("Menyimpan hasil verifikasi teknis ke basis data..."):
                                    sukses_v = db.update_verification_comprehensive(active_key, verif_payload, list_gedung_final)

                                if sukses_v:
                                    st.balloons()
                                    st.success(f"✅ Hasil verifikasi teknis untuk Company Key **{active_key}** berhasil diterbitkan dengan status: **{status_keputusan}**!")
                                    st.rerun()

        # ----------------------------------------------------------------------
        # PILIHAN 2: LIHAT HASIL ASESMEN (HISTORIS & MONITORING WAKTU)
        # Menampilkan:
        # - Filter waktu & monitoring analitik wilayah
        # - Rincian Hasil Asesmen: Poin-poin apa saja yang kurang
        # - Standar Pemenuhan Toilet Mandiri + Kumulatif
        # ----------------------------------------------------------------------
        with tab_historis_k3:
            st.subheader("Monitoring Historis & Analisis Hasil Asesmen K3 Berbasis Waktu")
            st.write("Fasilitas pengawasan terpadu bagi PJK3 dan Balai K3 untuk meninjau riwayat asesmen seluruh perusahaan, tren keselamatan kerja, serta audit parameter defisit.")

            # FILTER BERBASIS WAKTU
            st.markdown("#### 🔍 Filter Rentang Waktu & Status:")
            filter_cols = st.columns([1.5, 1, 1, 1])

            with filter_cols[0]:
                preset_waktu = st.selectbox(
                    "Pilih Preset Waktu:",
                    ["Semua Waktu", "7 Hari Terakhir", "30 Hari Terakhir", "Bulan Ini", "Tahun Berjalan (YTD)", "Kustom Tanggal"]
                )

            today = datetime.now().date()
            if preset_waktu == "7 Hari Terakhir":
                start_filter = today - timedelta(days=7)
                end_filter = today
            elif preset_waktu == "30 Hari Terakhir":
                start_filter = today - timedelta(days=30)
                end_filter = today
            elif preset_waktu == "Bulan Ini":
                start_filter = today.replace(day=1)
                end_filter = today
            elif preset_waktu == "Tahun Berjalan (YTD)":
                start_filter = today.replace(month=1, day=1)
                end_filter = today
            elif preset_waktu == "Kustom Tanggal":
                start_filter = today - timedelta(days=60)
                end_filter = today
            else:
                start_filter = today - timedelta(days=365)
                end_filter = today + timedelta(days=1)

            if preset_waktu == "Kustom Tanggal":
                with filter_cols[1]:
                    start_filter = st.date_input("Tanggal Mulai:", value=start_filter)
                with filter_cols[2]:
                    end_filter = st.date_input("Tanggal Selesai:", value=end_filter)

            with filter_cols[3]:
                status_filter = st.selectbox("Status Verifikasi:", ["Semua", "Terverifikasi Memenuhi Standar", "Perlu Tindakan Perbaikan", "Menunggu Verifikasi"])

            # Terapkan filter waktu
            filtered_p, filtered_s = db.filter_surveys_by_time(df_p_all, df_s_all, start_filter, end_filter)

            if status_filter != "Semua" and not filtered_p.empty and "Status Verifikasi" in filtered_p.columns:
                filtered_p = filtered_p[filtered_p["Status Verifikasi"] == status_filter]
                if not filtered_s.empty and "Company Key" in filtered_s.columns:
                    valid_keys = set(filtered_p["Company Key"].astype(str).str.strip().str.upper())
                    filtered_s = filtered_s[filtered_s["Company Key"].astype(str).str.strip().str.upper().isin(valid_keys)]

            st.markdown("---")

            # KARTU METRIK UTAMA BERDASARKAN WAKTU
            total_perusahaan = len(filtered_p)
            total_gedung = len(filtered_s)
            total_pekerja_tercover = 0
            if not filtered_s.empty and "Total Pekerja" in filtered_s.columns:
                total_pekerja_tercover = filtered_s["Total Pekerja"].apply(lambda x: to_int(x)).sum()

            rata_skor = 0
            if not filtered_s.empty and "Total Poin Gedung" in filtered_s.columns:
                rata_skor = filtered_s["Total Poin Gedung"].apply(lambda x: float(to_int(x))).mean()

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Perusahaan Terdaftar", f"{total_perusahaan} PT", delta=f"{preset_waktu}")
            m2.metric("Total Objek Gedung", f"{total_gedung} Gedung")
            m3.metric("Tenaga Kerja Terlindungi", f"{total_pekerja_tercover:,} Jiwa")
            m4.metric("Rata-rata Skor K3", f"{rata_skor:.1f} Poin")

            st.markdown("---")

            # GRAFIK ANALITIK & TREN BERDASARKAN WAKTU
            if not filtered_p.empty and not filtered_s.empty:
                c_chart1, c_chart2 = st.columns(2)
                with c_chart1:
                    st.markdown("##### 📈 Tren Survei Masuk Berdasarkan Waktu")
                    df_chart = filtered_p.copy()
                    if "Waktu Pengisian" in df_chart.columns:
                        df_chart["Tanggal"] = pd.to_datetime(df_chart["Waktu Pengisian"], errors="coerce").dt.date
                        trend_df = df_chart.groupby("Tanggal").size().reset_index(name="Jumlah Survei")
                        trend_df = trend_df.sort_values("Tanggal")
                        st.line_chart(trend_df.set_index("Tanggal"))
                    else:
                        st.caption("Data tanggal tidak tersedia.")

                with c_chart2:
                    st.markdown("##### 🏢 Distribusi Survei per Sektor (KBLI)")
                    if "Jenis Usaha (KBLI)" in filtered_p.columns:
                        kbli_counts = filtered_p["Jenis Usaha (KBLI)"].value_counts()
                        st.bar_chart(kbli_counts)

                # TABEL REKAPITULASI
                st.markdown("### 📋 Rekapitulasi Data Survei Perusahaan")
                tampil_p_cols = [
                    c for c in [
                        "Waktu Pengisian", "Company Key", "Nama Perusahaan", "Legalitas",
                        "Jenis Usaha (KBLI)", "Lokasi Pengujian", "Nama Responden", "Status Verifikasi", "Catatan Verifikator"
                    ] if c in filtered_p.columns
                ]
                st.dataframe(filtered_p[tampil_p_cols], width="stretch")

                # Ekspor CSV
                csv_data = filtered_p[tampil_p_cols].to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Unduh Rekapitulasi Survei (CSV)",
                    data=csv_data,
                    file_name=f"Rekap_Survei_K3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    width="content"
                )

                st.markdown("---")
                # AUDIT DETAIL HASIL ASESMEN PERUSAHAAN (POIN KURANG & STANDAR TOILET)
                st.markdown("### 🔎 Audit Detail Hasil Asesmen Perusahaan")
                st.write("Pilih salah satu perusahaan untuk meninjau secara mendalam **poin-poin apa saja yang kurang** serta **evaluasi standar toilet mandiri + kumulatif**.")

                list_pt_keys = [str(k).strip() for k in filtered_p["Company Key"].dropna().unique() if str(k).strip()]
                selected_pt_key = st.selectbox("Pilih Company Key untuk Diaudit:", list_pt_keys)

                if selected_pt_key:
                    pt_match = filtered_p[filtered_p["Company Key"].astype(str).str.strip().str.upper() == selected_pt_key]
                    pt_row = pt_match.iloc[0].to_dict() if not pt_match.empty else {}

                    pt_gedung_df = df_s_all[df_s_all["Company Key"].astype(str).str.strip().str.upper() == selected_pt_key] if not df_s_all.empty else pd.DataFrame()
                    pt_gedung_list = pt_gedung_df.to_dict(orient="records") if not pt_gedung_df.empty else []

                    st.markdown(f"""
                    <div class="k3-card">
                        <h4>🏢 {pt_row.get('Nama Perusahaan')} ({pt_row.get('Legalitas', 'PT')})</h4>
                        <p><b>Company Key:</b> <code>{selected_pt_key}</code> | <b>Status:</b> <b>{pt_row.get('Status Verifikasi', 'Menunggu Verifikasi')}</b></p>
                        <p><b>Catatan Verifikator:</b> {pt_row.get('Catatan Verifikator', '-')}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # 1. Tampilkan Evaluasi Toilet Mandiri + Kumulatif
                    render_evaluasi_toilet_card(pt_gedung_list)

                    st.markdown("---")
                    st.markdown("#### 📋 Rincian Poin yang Kurang Per Gedung:")

                    if not pt_gedung_list:
                        st.info("Tidak ada data gedung untuk perusahaan ini.")
                    else:
                        for idx_g, g_item in enumerate(pt_gedung_list):
                            nama_bg = g_item.get("Nama Gedung", f"Gedung {idx_g+1}")
                            st_pemenuhan = g_item.get("Status Pemenuhan", "-")
                            with st.expander(f"🏢 **{nama_bg}** — Skor Total: {g_item.get('Total Poin Gedung', 0)} ({st_pemenuhan})", expanded=True):
                                c_m1, c_m2, c_m3, c_m4 = st.columns(4)
                                c_m1.metric("Kondisi Fisik", g_item.get("Skor_Topik_1", "-"))
                                c_m2.metric("Sanitasi Kebersihan", g_item.get("Skor_Topik_2", "-"))
                                c_m3.metric("Kebutuhan Udara", g_item.get("Skor_Topik_3", "-"))
                                c_m4.metric("Housekeeping", g_item.get("Skor_Topik_4", "-"))

                                render_poin_kurang_gedung(g_item)

            else:
                st.info("ℹ️ Tidak ada data survei yang memenuhi kriteria filter waktu saat ini.")
