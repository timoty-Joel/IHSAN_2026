import streamlit as st
import pandas as pd
import re
import uuid
import math
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
from config_evaluasi import analisis_sub_bidang_kurang

spreadsheet_url = "https://docs.google.com/spreadsheets/d/1RTlhOLxdXShS2UAdp2JFgUQyXe2ufEJ8xgGOgCnRdsk/edit"

st.set_page_config(page_title="Coba Survei", layout="centered")

# Inisialisasi koneksi Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
def save_to_gsheet(worksheet_name:str, new_df: pd.DataFrame):
    try:
        # Bersihkan data baru dari nilai NaN/None
        clean_new_df = new_df.fillna("").astype(str)

        try:
            existing_df = conn.read(
                spreadsheet=spreadsheet_url,
                worksheet=worksheet_name,
                ttl="0s"
            )
        except Exception:
            existing_df = pd.DataFrame()

        if existing_df is None or existing_df.empty or len(existing_df.columns) == 0:
            updated_df = clean_new_df
        else:
            clean_existing_df = existing_df.fillna("").astype(str)
            updated_df = pd.concat([clean_existing_df, clean_new_df], ignore_index=True)
            updated_df = updated_df.fillna("")

        # Kirim data yang sudah bersih dari tipe NaN/null
        conn.update(
            spreadsheet=spreadsheet_url,
            worksheet=worksheet_name,
            data=updated_df
        )
        return True
    except Exception as e:
        st.exception(e)
        st.error(f"Gagal menyimpan ke worksheet '{worksheet_name}': {e}")
        return False


if 'step' not in st.session_state:
    st.session_state.step = 'isi_data_lembaga'
if 'company_key' not in st.session_state:
    st.session_state.company_key = ''
if 'lembaga_data' not in st.session_state:
    st.session_state.lembaga_data = {}
if 'company_data' not in st.session_state:
    st.session_state.company_data = {}
if 'gedung_data' not in st.session_state:
    st.session_state.gedung_data = []
if 'current_gedung' not in st.session_state:
    st.session_state.current_gedung = {}

punya_bawah_tanah = False
punya_halaman = False

opt_standar = [
    "Tidak memenuhi / kotor / rusak",
    "1% - /25% /dari jumlah keseluruhan objek memenuhi",
    "26% - /50% /dari jumlah keseluruhan objek memenuhi",
    "51% - /75% /dari jumlah keseluruhan objek memenuhi",
    "76% - /100% /dari jumlah keseluruhan objek memenuhi"
]

# Fungsi Navigasi
def next_step(step_name):
    st.session_state.step = step_name

def valid_email(email: str)-> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+"
    return bool(re.match(pattern, email.strip()))

# 
def render_question(q_id, question_text, options):
    nomor_gedung = st.session_state.current_gedung.get("Nomor Gedung", 1)
    ans = st.radio(f"{q_id}, {question_text}", options, key=f"radio_{nomor_gedung}_{q_id}")
    score = options.index(ans) + 1

    # Simpan jawaban teks dan skornya
    st.session_state.current_gedung[f"{q_id}_Jawaban"] = ans
    #st.session_state.current_gedung[f"{q_id}_Skor"] = score
    st.session_state.current_gedung[f"{q_id}_Poin"] = score
    return ans

# Untuk render pertanyaan checkbox
def render_checbox_q(q_id, question_text, options:list):
    st.markdown(f"{question_text}")

    selected_items = []
    cols = st.columns(min(len(options), 3))

    for idx, item in enumerate(options):
        with cols[idx % len(cols)]:
            checked = st.checkbox(
                item,
                key = f"cb_{q_id}_{idx}_{len(st.session_state.gedung_data)}"
            )
            if checked:
                selected_items.append(item)

    score = len(selected_items)
    max_possible = len(options)

    # Simpan jawaban ke data gedung
    st.session_state.current_gedung[f"{q_id}_Jawaban"] = ", ".join(selected_items) if selected_items else "Tidak terpenuhi"
    st.session_state.current_gedung[f"{q_id}_Poin"] = score
        
    return None

def render_header_gedung():
    if "Nama Gedung" in st.session_state.current_gedung:
        nama = st.session_state.current_gedung.get("Nama Gedung", "")
        nomor = st.session_state.current_gedung.get("Nomor Gedung", "")
        st.info(f"🏢 **Objek ke-{nomor}:** {nama}")

def hitung_kebutuhan_toilet(total_pekerja: int):
    if total_pekerja <= 0:
        return 0
    elif total_pekerja <= 15:
        return 1
    elif total_pekerja <= 30:
        return 2
    elif total_pekerja <= 45:
        return 3
    elif total_pekerja <= 60:
        return 4
    elif total_pekerja <= 80:
        return 5
    elif total_pekerja <= 100:
        return 6
    else:
        return 6 + math.ceil((total_pekerja - 100)/40)

def evaluasi_toilet(daftar_gedung: list):
    if not daftar_gedung:
        return daftar_gedung

    total_toilet = sum(int(g.get("Jumlah Toilet", 0)) for g in daftar_gedung)
    total_semua_pekerja = sum(
        int(g.get("Total Pekerja", 0)) for g in daftar_gedung
    )
    syarat_total = hitung_kebutuhan_toilet(total_semua_pekerja)

    kumulatif_memenuhi = total_toilet >= syarat_total

    rincian_tiap_gedung = ", ".join([
        f"{g.get('Nama Gedung', f'Gedung {idx+1}')}: {g.get('Jumlah Toilet', 0)}/{hitung_kebutuhan_toilet(int(g.get('Total Pekerja', 0)))}"
        for idx, g in enumerate(daftar_gedung)
    ])

    for g in daftar_gedung:
        toilet_gedung = int(g.get("Jumlah Toilet", 0))
        pekerja_gedung = int(g.get("Total Pekerja", 0))
        syarat_mandiri = hitung_kebutuhan_toilet(pekerja_gedung)
        mandiri_memenuhi = toilet_gedung >= syarat_mandiri

        if len(daftar_gedung) == 1:
            if mandiri_memenuhi:
                g["Q33_Jawaban"] = f"Memenuhi syarat ({toilet_gedung}/{syarat_mandiri} toilet)"
                g["Q33_Poin"] = 1
            else:
                g["Q33_Jawaban"] = f"Tidak memenuhi syarat (Tersedia {toilet_gedung}, butuh {syarat_mandiri})"
                g["Q33_Poin"] = 0
        else:
            status_mandiri = "Memenuhi" if mandiri_memenuhi else "Tidak Memenuhi"
            status_kumulatif = "Memenuhi" if kumulatif_memenuhi else "Tidak Memenuhi"

            # Format teks menampilkan status gedung ini, rincian tiap gedung, dan kumulatifnya
            g["Q33_Jawaban"] = (
                f"{status_mandiri} mandiri ({toilet_gedung}/{syarat_mandiri}) | "
                f"Kumulatif {status_kumulatif} ({total_toilet}/{syarat_total}) | "
                f"Rincian ({rincian_tiap_gedung})"
            )
            g["Q33_Poin"] = 1 if kumulatif_memenuhi else 0

    return daftar_gedung

def get_standar_bidang(punya_bawah_tanah: bool, punya_halaman: bool):
    return {
        "Kondisi Fisik": (90 if punya_bawah_tanah else 70) - (0 if punya_halaman else 20),
        "Fasilitas Kebersihan": 55,
        "Kebutuhan Udara": 15,
        "Tata Laksana Kerumahtanggaan": 10
    }

def load_existing_gedung_from_sheets(company_key: str):
    """Membaca daftar nama gedung yang sudah terdaftar di Google Sheets untuk Company Key tertentu"""
    if not company_key:
        return []
    try:
        df_survei = conn.read(
            spreadsheet=spreadsheet_url,
            worksheet="Hasil_Survei",
            ttl="5s"
        )
        if df_survei is not None and not df_survei.empty:
            df_survei.columns = [str(c).strip() for c in df_survei.columns]
            if "Company Key" in df_survei.columns and "Nama Gedung" in df_survei.columns:
                filtered = df_survei[df_survei["Company Key"].astype(str).str.strip().str.upper() == str(company_key).strip().upper()]
                names = [str(val).strip() for val in filtered["Nama Gedung"].dropna() if str(val).strip()]
                
                return list(dict.fromkeys(names))

    except Exception:
        pass

    return []

# Flow 1: Form Data Lembaga Uji K3
if st.session_state.step == 'isi_data_lembaga':
    st.title("Data Lembaga Uji K3")
    st.markdown("Silakan isi data identitas lembaga / perusahaan penguji K3 terlebih dahulu.")

    with st.form("form_data_lembaga"):
        col1, col2 = st.columns(2)
        with col1:
            pengisi_opts = ["Pihak perusahaan", "Penguji K3"]
            curr_pengisi = st.session_state.lembaga_data.get("Pengisi Form", pengisi_opts[0])
            pengisi_idx = pengisi_opts.index(curr_pengisi) if curr_pengisi in pengisi_opts else 0
            pengisi_form = st.radio(
                "Pengisi form: (Pihak perusahaan atau Penguji K3)*",
                pengisi_opts,
                index=pengisi_idx,
                horizontal=True
            )

            nama_lembaga = st.text_input(
                "Nama Perusahaan / Lembaga Uji K3*",
                value=st.session_state.lembaga_data.get("Nama Lembaga K3", ""),
                placeholder="Contoh: PT Graha Mutu K3"
            )
            no_induk_lembaga = st.text_input(
                "No. Induk Perusahaan*",
                value=st.session_state.lembaga_data.get("No Induk Lembaga", ""),
                placeholder="Contoh: 1234567890123"
            )
            no_telp_lembaga = st.text_input(
                "No. Perusahaan yang Dapat Dihubungi*",
                value=st.session_state.lembaga_data.get("No Telp Lembaga", ""),
                placeholder="Contoh: 021-12345678 / 08123456789"
            )
            
        with col2:
            no_skp_lembaga = st.text_input(
                "Nomor SKP Perusahaan / PJK3*",
                value=st.session_state.lembaga_data.get("Nomor SKP Lembaga", ""),
                placeholder="Contoh: 5/123/AS.02.04/V/2023"
            )
            
            nama_ahli = st.text_input(
                "Nama Ahli K3*",
                value=st.session_state.lembaga_data.get("Nama Ahli K3", ""),
                placeholder="Contoh: Budi Santoso, S.T."
            )
            no_skp_ahli = st.text_input(
                "Nomor SKP Ahli K3*",
                value=st.session_state.lembaga_data.get("Nomor SKP Ahli", ""),
                placeholder="Contoh: KEP.P.123/BINWASK3-PNK3/XII/2022"
            )

            alamat_lembaga = st.text_area(
                "Alamat Lembaga Uji K3*",
                value=st.session_state.lembaga_data.get("Alamat Lembaga K3", ""),
                placeholder="Contoh: Jl. Jend. Sudirman No. 123, Jakarta",
                height=106
            )
            

        submitted_lembaga = st.form_submit_button("Lanjut ke Data Perusahaan yang Diuji ➔", use_container_width=True)

        if submitted_lembaga:
            if (
                not nama_lembaga.strip() 
                or not no_induk_lembaga.strip() 
                or not no_telp_lembaga.strip() 
                or not alamat_lembaga.strip() 
                or not no_skp_lembaga.strip() 
                or not nama_ahli.strip() 
                or not no_skp_ahli.strip()
            ):
                st.error("Semua field Data Lembaga Uji K3 wajib diisi!")
            else:
                st.session_state.lembaga_data = {
                    "Nama Lembaga K3": nama_lembaga.strip(),
                    "No Induk Lembaga": no_induk_lembaga.strip(),
                    "No Telp Lembaga": no_telp_lembaga.strip(),
                    "Alamat Lembaga K3": alamat_lembaga.strip(),
                    "Nomor SKP Lembaga": no_skp_lembaga.strip(),
                    "Nama Ahli K3": nama_ahli.strip(),
                    "Nomor SKP Ahli": no_skp_ahli.strip(),
                    "Pengisi Form": pengisi_form,
                }
                next_step('isi_data_perusahaan')
                st.rerun()

# Flow 2: Form Data Umum Perusahaan yang Diuji
elif st.session_state.step == 'isi_data_perusahaan':
    st.title("Data Umum Perusahaan yang Diuji")
    
    # Ringkasan info Lembaga Uji K3
    nama_lembaga_info = st.session_state.lembaga_data.get("Nama Lembaga K3", "-")
    nama_ahli_info = st.session_state.lembaga_data.get("Nama Ahli K3", "-")
    skp_ahli_info = st.session_state.lembaga_data.get("Nomor SKP Ahli", "-")
    pengisi_info = st.session_state.lembaga_data.get("Pengisi Form", "-")
    st.info(f"🏢 **Lembaga Uji K3:** {nama_lembaga_info} | **Ahli K3:** {nama_ahli_info} (`{skp_ahli_info}`) | **Pengisi:** {pengisi_info}")

    with st.form("form_data_perusahaan"):
        col1, col2 = st.columns(2)
        with col1:
            nama_perusahaan = st.text_input(
                "Nama Perusahaan yang Diuji*",
                value=st.session_state.company_data.get("Nama Perusahaan", ""),
                placeholder="Contoh: PT Sumber Sejahtera"
            )
            legalitas_opts = ["PT", "CV", "Lainnya"]
            curr_legalitas = st.session_state.company_data.get("Legalitas", "PT")
            leg_idx = legalitas_opts.index(curr_legalitas) if curr_legalitas in legalitas_opts else 0
            legalitas = st.selectbox("Bentuk Legalitas", legalitas_opts, index=leg_idx)

            no_induk_perusahaan = st.text_input(
                "No. Induk Perusahaan*",
                value=st.session_state.company_data.get("No Induk Perusahaan", ""),
                placeholder="Contoh: 0123456789012"
            )

            no_telp_perusahaan = st.text_input(
                "No. yang Bisa Dihubungi*",
                value=st.session_state.company_data.get("No Telp Perusahaan", ""),
                placeholder="Contoh: 021-87654321 / 08129876543"
            )

            lokasi_uji = st.text_input(
                "Lokasi / Alamat Pengujian*",
                value=st.session_state.company_data.get("Lokasi Pengujian", ""),
                placeholder="Contoh: Plant Cikarang / Jl. Industri Raya No. 45"
            )

        with col2:
            nama_responden = st.text_input(
                "Nama Responden*",
                value=st.session_state.company_data.get("Nama Responden", ""),
                placeholder="Nama Penanggung Jawab / Pengisi"
            )

            jabatan = st.text_input(
                "Posisi / Jabatan",
                value=st.session_state.company_data.get("Jabatan", ""),
                placeholder="Ahli K3 / Manajer HSE"
            )

            email_responden = st.text_input(
                "Alamat Email Perusahaan / Responden*", 
                value=st.session_state.company_data.get("Email Responden", ""),
                placeholder="hse@perusahaan.co.id",
                help="Email aktif untuk pengiriman salinan Company Key dan hasil asesmen"
            )

            kbli_list = [
                "Industri Pengolahan",
                "Pertanian, Kehutanan, dan Perikanan",
                "Pertambangan dan Penggalian",
                "Konstruksi",
                "Pengangkutan dan Pergudangan",
                "Perdagangan Besar dan Eceran",
                "Penyediaan Akomodasi dan Makan Minum",
                "Informasi dan Komunikasi",
                "Aktivitas Kesehatan Manusia",
                "Lainnya"
            ]
            curr_kbli = st.session_state.company_data.get("Jenis Usaha (KBLI)", kbli_list[0])
            kbli_idx = kbli_list.index(curr_kbli) if curr_kbli in kbli_list else 0
            jenis_usaha = st.selectbox("Jenis Usaha (KBLI)", kbli_list, index=kbli_idx)

            karyawan_opts = [
                "Industri Besar (≥ 100 orang)",
                "Industri Sedang (20 - 99 orang)",
                "Industri Kecil (5 - 19 orang)",
                "Industri Rumah Tangga (1 - 4 orang)"
            ]
            curr_karyawan = st.session_state.company_data.get("Kategori Pekerja", karyawan_opts[0])
            karyawan_idx = karyawan_opts.index(curr_karyawan) if curr_karyawan in karyawan_opts else 0
            jumlah_karyawan = st.selectbox("Kategori Jumlah Tenaga Kerja", karyawan_opts, index=karyawan_idx)

            punya_key = st.text_input(
                "Company Key Lama (Kosongkan jika baru pertama kali)",
                value=st.session_state.company_key if st.session_state.company_key else "",
                placeholder="Misal: A1B2C3D4"
            )

        submitted_perusahaan = st.form_submit_button("Lanjut ke Penilaian Objek ➔", use_container_width=True)
        
        if submitted_perusahaan:
            if (
                not nama_perusahaan.strip() 
                or not no_induk_perusahaan.strip() 
                or not no_telp_perusahaan.strip() 
                or not lokasi_uji.strip() 
                or not nama_responden.strip()
            ):
                st.error("Nama Perusahaan, No. Induk Perusahaan, No. yang Bisa Dihubungi, Lokasi Pengujian, dan Nama Responden wajib diisi!")
            elif email_responden.strip() and not valid_email(email_responden.strip()):
                st.error("Format email perusahaan/responden tidak valid!")
            else:
                key = punya_key.strip().upper() if punya_key.strip() else str(uuid.uuid4().hex)[:8].upper()
                st.session_state.company_key = key
                st.session_state.company_data = {
                    "Company Key": key,
                    "Waktu Pengisian": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    # Data Lembaga Uji K3
                    "Nama Lembaga K3": st.session_state.lembaga_data.get("Nama Lembaga K3", ""),
                    "No Induk Lembaga": st.session_state.lembaga_data.get("No Induk Lembaga", ""),
                    "No Telp Lembaga": st.session_state.lembaga_data.get("No Telp Lembaga", ""),
                    "Alamat Lembaga K3": st.session_state.lembaga_data.get("Alamat Lembaga K3", ""),
                    "Nomor SKP Lembaga": st.session_state.lembaga_data.get("Nomor SKP Lembaga", ""),
                    "Nama Ahli K3": st.session_state.lembaga_data.get("Nama Ahli K3", ""),
                    "Nomor SKP Ahli": st.session_state.lembaga_data.get("Nomor SKP Ahli", ""),
                    "Pengisi Form": st.session_state.lembaga_data.get("Pengisi Form", ""),
                    # Data Umum Perusahaan yang Diuji
                    "Nama Perusahaan": nama_perusahaan.strip(),
                    "No Induk Perusahaan": no_induk_perusahaan.strip(),
                    "No Telp Perusahaan": no_telp_perusahaan.strip(),
                    "Legalitas": legalitas,
                    "Lokasi Pengujian": lokasi_uji.strip(),
                    "Nama Responden": nama_responden.strip(),
                    "Email Responden": email_responden.strip(),
                    "Jabatan": jabatan.strip(),
                    "Jenis Usaha (KBLI)": jenis_usaha,
                    "Kategori Pekerja": jumlah_karyawan
                }
                next_step('identifikasi_objek')
                st.rerun()

    if st.button("⬅ Kembali ke Data Lembaga Uji K3"):
        next_step('isi_data_lembaga')
        st.rerun()

elif st.session_state.step == 'identifikasi_objek':
    nomor_gedung = len(st.session_state.gedung_data) + 1
    st.title(f"Bagian II. Penilaian Objek Survei ke-{nomor_gedung}")
    st.info(f"Company Key: **{st.session_state.company_key}** | Perusahaan: **{st.session_state.company_data.get('Nama Perusahaan')}**")

    # Ambil nama gedung pada sesi sekarang
    current_session_names = [
        g.get("Nama Gedung", "").strip() for g in st.session_state.gedung_data if g.get("Nama Gedung")
    ]

    # Ambil nama gedung dari gsheets
    if "Nama Gedung" not in st.session_state or st.session_state.get("last_checked_key") != st.session_state.company_key:
        st.session_state.sheets_gedung_names = load_existing_gedung_from_sheets(st.session_state.company_key)
        st.session_state.last_checked_key = st.session_state.company_key
    
    sheet_names = list(st.session_state.get("sheets_gedung_names", []))

    all_registered = list(dict.fromkeys(current_session_names + [s for s in sheet_names if s.lower() not in [c.lower() for c in current_session_names]]))
    if all_registered:
        st.caption(f"Gedung yang sudah terdaftar: {', '.join(all_registered)}")

    with st.form("form_identifikasi_objek"):
        nama_gedung = st.text_input(
            f"Nama / Identitas Gedung ke-{nomor_gedung}*",
            placeholder="Contoh: Gedung A, Gedung Produksi Utama, Kantor Direksi"
        )

        jenis_objek = st.selectbox("Pilih Jenis Bangunan / Objek Survei:", [
            "1. Perkantoran",
            "2. Pabrik / Area Produksi",
            "3. Workshop",
            "4. Kantin & Dapur",
            "5. Pergudangan / Warehouse",
            "6. Bangunan Bawah Tanah",
            "7. Tempat Kerja Lainnya"
        ])

        col_a, col_b = st.columns(2)
        with col_a:
            total_pekerja = st.number_input("Jumlah Total Pekerja pada Objek Ini", min_value=0, step=1)
            pekerja_laki = st.number_input("Jumlah Pekerja Laki-laki", min_value=0, step=1)
        with col_b:
            pekerja_perempuan = st.number_input("Jumlah Pekerja Perempuan", min_value=0, step=1)
            pekerja_disabilitas = st.number_input("Jumlah Pekerja Disabilitas", min_value=0, step=1)

        if st.form_submit_button("Mulai Instrumen Topik 1 (Bangunan) ➔", use_container_width=True):
            nama_gedung_clean = nama_gedung.strip()
            if not nama_gedung_clean:
                st.error(f"Nama / Identitas Gedung ke-{nomor_gedung} wajib diisi agar tidak tertukar saat pengujian ulang!")
            elif any(nama_gedung_clean.lower() == s.lower() for s in current_session_names+sheet_names):
                st.error(f"Gedung dengan nama '{nama_gedung_clean}' sudah ada untuk sesi ini. Harap periksa kembali daftar gedung yang sudah ada.")            
            else:
                st.session_state.current_gedung = {
                    "Company Key": st.session_state.company_key,
                    "Nomor Gedung": nomor_gedung,
                    "Nama Gedung": nama_gedung.strip(),
                    "Waktu Penilaian Gedung": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Jenis Objek": jenis_objek,
                    "Total Pekerja": total_pekerja,
                    "Pekerja Laki-laki": pekerja_laki,
                    "Pekerja Perempuan": pekerja_perempuan,
                    "Pekerja Disabilitas": pekerja_disabilitas
                }
                next_step('topik_1')
                st.rerun()

    if st.button("⬅ Kembali ke Data Umum Perusahaan"):
        next_step('isi_data_perusahaan')
        st.rerun()

# ==========================================
# FLOW 3: TOPIK 1 - KONDISI FISIK
# ==========================================
elif st.session_state.step == "topik_1":
    st.title("Kondisi Fisik")
    render_header_gedung()

    nomor_gedung = st.session_state.current_gedung.get("Nomor Gedung", 1)

    # Pertanyaan tentang halaman
    st.markdown("### A. Area Halaman")
    ada_halaman = st.radio("1. Apakah lingkungan kerja memiliki halaman?", ["Ya", "Tidak"], key=f"radio_{nomor_gedung}_q1")
    st.session_state.current_gedung["Halaman"] = ada_halaman
    #st.session_state.current_gedung["Halaman"] = 1 if ada_halaman == "Ya" else 0
    punya_halaman = False

    if ada_halaman == "Ya":
        punya_halaman = True
        q_1_5 = [
            ("Q1", "Apakah halaman bersih?", opt_standar),
            ("Q2", "Apakah halaman tertata rapi?", opt_standar),
            ("Q3", "Apakah halaman rata atau tidak berlubang-lubang?", opt_standar),
            ("Q4", "Apakah halaman tidak becek?", opt_standar),
            ("Q5", "Apakah halaman cukup luas untuk lalu lintas orang dan barang?", opt_standar),
        ]

        for q_id, question_text, option in q_1_5:
            render_question(q_id, question_text, option)
    else:
        st.info("ℹ️ Sesuai pedoman: Melewati pertanyaan 1 - 5 karena tidak memiliki halaman.")
        for q_skip in ["Q1", "Q2", "Q3", "Q4", "Q5"]:
            st.session_state.current_gedung[f"{q_skip}_Jawaban"] = "N/A (Tidak Ada Halaman)"
            st.session_state.current_gedung[f"{q_skip}_Poin"] = 0

    render_question("Q6", "Apakah saluran air pembuangan tertutup dengan bahan yang kuat?", [
        "Tidak ada saluran air pembuangan",
        "Ada, 0% - /25% /saluran tertutup bahan kuat",
        "Ada, 26% - /50% /saluran tertutup bahan kuat",
        "Ada, 51% - /75% /saluran tertutup bahan kuat",
        "Ada, 76% - /100% /saluran tertutup bahan kuat"
    ])

    st.markdown("---")
    st.markdown("### B. Kondisi Fisik Gedung (Dinding, Lantai, Langit-langit, Atap)")

    q_7_26 = [
        ("Q7", "Apakah Gedung terpelihara sehingga bersih?", opt_standar),
        ("Q8", "Apakah struktur gedung kuat dan kokoh (tidak retak/rusak berisiko)?", opt_standar),
        ("Q9", "Apakah Gedung cukup luas sehingga memberikan ruang Gerak paling sedikit 2 m2 per orang", opt_standar),
        ("Q10", "Apakah dinding kering / tidak lembap / tidak korosi?", opt_standar),
        ("Q11", "Apakah langit-langit kering atau tidak lembab?", opt_standar),
        ("Q12", "Apakah dinding dicat, bersih dan mudah dibersihkan", opt_standar),
        ("Q13", "Apakah langit-langit dicat?", opt_standar),
        ("Q14", "Apakah langit-langit bersih dan mudah dibersihkan", opt_standar),
        ("Q15", "Apakah dinding dilakukan pengecatan ulang", opt_standar),
        ("Q16", "Apakah dinding dibersihkan secara rutin", opt_standar),
        ("Q17", "Apakah langit-langit dibersihkan secara rutin", opt_standar),
        ("Q18", "Apakah lantai terbuat dari bahan yang keras", opt_standar),
        ("Q19", "Apakah lantai terbuat dari bahan yang tahan air?", opt_standar),
        ("Q20", "Apakah lantai terbuat dari bahan yang tahan dari bahan kimia yang merusak?", opt_standar),
        ("Q21", "Apakah lantai datar dan mudah dibersihkan?", opt_standar),
        ("Q22", "Apakah lantai tidak licin?", opt_standar),
        ("Q23", "Apakah lantai dibersihkan secara teratur?", opt_standar),
        ("Q24", "Apakah keseluruhan atap mampu memberi perlindungan dari panas matahari dan hujan?", opt_standar),
        ("Q25", "Apakah keseluruhan atap tidak bocor, tidak berlubang?", opt_standar),
        ("Q26", "Apakah keseluruhan atap tidak berjamur?", opt_standar)
    ]

    for q_id, question_text, option in q_7_26:
        render_question(q_id, question_text, option)

    # Bangunan Bawah Tanah
    bawah_tanah = st.radio("Apakah tempat anda memiliki bangunan bawah tanah?", ["Ya", "Tidak"], key=f"radio_{nomor_gedung}_bt")

    # Jika iya
    if bawah_tanah == "Ya":
        punya_bawah_tanah = True
        q_27_32 = [
            ("Q27", "Apakah bangunan bawah tanah memiliki struktur yang kuat?", opt_standar),
            ("Q28", "Apakah bangunan bawah tanah memiliki sistem ventilasi udara?", opt_standar),
            ("Q29", "Apakah bangunan bawah tanah memiliki sumber pencahayaan?", opt_standar),
            ("Q30", "Apakah saluran pembuangan air mengalir dengan baik?", opt_standar),
            ("Q31", "Apakah bangunan bawah tanah bersih dan terawat", opt_standar),
            ("Q32", "Apakah bangunan bawah tanah mengikuti syarat Ruang Terbatas", ["Ya", "Tidak"])
        ]

        for q_id, question_text, option in q_27_32:
            render_question(q_id, question_text, option)
    
    else:
        st.info(" Pertanyaan 27 sampai dengan 32 dilewati karena tidak ada ruang bawah tanah")
        for q_skip in ["Q27", "Q28", "Q29", "Q30", "Q31", "Q32"]:
            st.session_state.current_gedung[f"{q_skip}_Jawaban"] = "Tidak ada"
            st.session_state.current_gedung[f"{q_skip}_Poin"] = 0

    # Skor akumulatif topik 1
    subtotal_1 = sum(int(v) for k, v in st.session_state.current_gedung.items() 
                        if k.endswith("_Poin") and any(k.startswith(f"Q{i}_") for i in range(1, 33)))
    st.session_state.current_gedung["Skor_Topik_1"] = subtotal_1

    if st.button("Lanjut ke Topik 2 (Fasilitas Kebersihan) ➔", type="primary", use_container_width=True):
        next_step('topik_2')
        st.rerun()

elif st.session_state.step == "topik_2":
    st.title("Fasilitas Kebersihan")
    render_header_gedung()

    st.markdown("### A. Toilet & Kelengkapannya")
    opt_toilet = [
        "Keseluruhan tidak memenuhi syarat / buruk",
        "0% - /25% keseluruhan memenuhi syarat",
        "26% - /50% keseluruhan memenuhi syarat",
        "51% - /75% keseluruhan memenuhi syarat",
        "76% - /100% keseluruhan memenuhi syarat"
    ]

    # Input banyak toilet
    nomor_gedung = st.session_state.current_gedung.get("Nomor Gedung", 1)
    total_pekerja_gedung = int(st.session_state.current_gedung.get("Total Pekerja", 0))

    jumlah_toilet = st.number_input(
        "Jumlah toilet di gedung ini",
        min_value=0,
        step=1,
        value=int(st.session_state.current_gedung.get("Jumlah Toilet", 0)),
        key=f"input_toilet_{nomor_gedung}"
    )

    syarat_toilet_gedung = hitung_kebutuhan_toilet(total_pekerja_gedung)
    poin_toilet, status = (1, "Memenuhi standar") if jumlah_toilet >= syarat_toilet_gedung else (0, "Tidak memenuhi")

    # Simpan ke current gedung
    st.session_state.current_gedung["Jumlah Toilet"] = jumlah_toilet
    st.session_state.current_gedung["Q33_Jawaban"] = status
    st.session_state.current_gedung["Q33_Poin"] = poin_toilet

    q_34_44 = [
        ("Q34", "Apakah toilet bersih dan tidak menimbulkan bau?", opt_toilet),
        ("Q35", "Apakah toilet tidak terdapat lalat, nyamuk, atau serangga lainnya?", opt_toilet),
        ("Q36", "Apakah toilet tersedia saluran pembuangan air yang mengalir dengan baik", opt_toilet),
        ("Q37", "Apakah toilet tersedia air bersih?", opt_toilet),
        ("Q38", "Apakah toilet dilengkapi dengan pintu?", opt_toilet),
        ("Q39", "Apakah toilet memiliki penerangan yang cukup", opt_toilet),
        ("Q40", "Apakah toilet memiliki sirkulasi udara yang baik", opt_toilet),
        ("Q41", "Apakah toilet dibersihkan setiap hari secara periodik", opt_toilet),
        ("Q42", "Apakah toilet dapat digunakan selama jam kerja?", opt_toilet),
        ("Q43", "Apakah toilet terpisah antara laki-laki dan perempuan, serta penyandang cacat?", ["Tidak terpisah", "Terpisah"]),
        ("Q44", "Apakah toilet diberikan tanda yang jelas?", opt_toilet)
    ]

    for q_id, question_text, option in q_34_44:
        render_question(q_id, question_text, option)
    
    fasilitas_check = [
        "Jamban", 
        "Alat pembilas (flush/gayung)", 
        "Tempat sampah", 
        "Tempat cuci tangan (wastafel)", 
        "Sabun"
    ]
    render_checbox_q("Q45", "Kelengkapan fasilitas toilet meliputi", fasilitas_check)

    st.markdown("---")
    st.markdown("### B. Tempat Sampah & Pakaian Kerja")

    q_46_53 = [
        ("Q46", "Apakah Perusahaan menyediakan pakaian kerja?", ["Tidak Menyediakan", "Menyediakan sesuai aturan K3"]),
        ("Q47", "Apakah Perusahaan menyediakan ruang ganti yang terpisah antara laki-laki dan perempuan?", [
            "Tidak ada ruang ganti",
            "Tidak terpisah",
            "Terpisah"
        ]),
        ("Q48", "Apakah Perusahaan menyediakan tempat penyimpanan atau loker untuk setiap pekerja yang terjamin keamanannya?", [
            "Tidak menyediakan",
            "Menyediakan tapi tidak terjamin keamanannya",
            "Menyediakan dan terjamin keamanannya"
        ]),
        ("Q49", "Apakah Perusahaan menyediakan tempat sampah terpisah yang diberikan label sesuai ketentuan?", opt_standar),
        ("Q50", "Apakah tempat sampah terpisah diberikan label sesuai ketentuan?", opt_toilet),
        ("Q51", "Apakah tempat sampah terpisah dalam kondisi tertutup?", opt_toilet),
        ("Q52", "Apakah tutup tempat sampah terpisah terbuat dari bahan yang kedap air?", opt_toilet),
        ("Q53", "Apakah tempat sampah terpisah menjadi sarang lalat atau binatang serangga lain?", [
            "Keseluruhan menjadi sarang serangga",
            "0% - /25% tidak menjadi sarang serangga",
            "26% - /50% tidak menjadi sarang serangga",
            "51% - /75% tidak menjadi sarang serangga",
            "76% - /100% tidak menjadi sarang serangga"
        ])
    ]

    for q_id, question_text, option in q_46_53:
        render_question(q_id, question_text, option)
    
    pembalut_check = [
        "Disediakan di ruang toilet perempuan", "Terbuat dari bahan yang kedap air",
        "Dilengkapi dengan penutup", "Diberikan label yang jelas", "Dibersihkan setiap hari"
    ]

    render_checbox_q("Q54", "Tempat Pembuangan Pembalut (Jika ada toilet perempuan): ", pembalut_check)

    subtotal_2 = sum(int(v) for k, v in st.session_state.current_gedung.items()
                        if k.endswith("_Poin") and any(k.startswith(f"Q{i}_") for i in range(35, 57)))
    st.session_state.current_gedung["Skor_Topik_2"] = subtotal_2

    if st.button("Lanjut ke Topik Kebutuhan Udara ➔", type="primary", use_container_width=True):
        next_step('topik_3')
        st.rerun()

elif st.session_state.step == 'topik_3':
    st.title("Kebutuhan Udara")
    render_header_gedung()

    st.markdown("---")
    st.markdown("### C. Kebutuhan Udara & Housekeeping Singkat")

    q_55_58 = [
        ("Q55", "Apakah suhu ruangan nyaman antara 23 – 26 derajat Celcius dengan perbedaan suhu antar ruangan tidak boleh melebihi 5 derajat Celcius?", opt_standar),
        ("Q56", "Apakah kelembaban ruangan antara 40-60%?", opt_standar),
        ("Q57", "Apakah kadar oksigen dalam ruang antara 19,5% - 23,5%?", opt_standar),
        ("Q58", "Apakah terdapat sistem ventilasi (alami, buatan, atau kombinasi) dalam ruang??", opt_standar),
    ]

    for q_id, question_text, option in q_55_58:
        render_question(q_id, question_text, option)

    render_question("Q59", "Apakah sistem ventilasi dibersihkan secara berkala minimal 3 bulan sekali?", [
        "Ventilasi tidak pernah dibersihkan ",
        "Ventilasi dibersihkan secara berkala min. 1 tahun sekali",
        "Ventilasi dibersihkan secara berkala min. 6 bulan sekali",
        "Ventilasi dibersihkan secara berkala min. 3 bulan sekali",
        "Ventilasi dibersihkan secara berkala min. 1 bulan sekali"
    ])

    render_question("Q60", "Apakah setiap orang bekerja dalam ruangan mendapat ruang udara (cubic space) paling sedikit 10 m3?", opt_standar)

    subtotal_3 = sum(int(v) for k, v in st.session_state.current_gedung.items()
                        if k.endswith("_Poin") and any (k.startswith(f"Q{i}_") for i in range(56, 61)))
    st.session_state.current_gedung["Skor_Topik_3"] = subtotal_3
    

    if st.button("Lanjut ke Topik Tata Laksana Kerumahtanggaan ➔", type="primary", use_container_width=True):
        next_step('topik_4')
        st.rerun()

elif st.session_state.step == 'topik_4':
    st.title("Tata Laksana Kerumahtanggaan")
    render_header_gedung()

    render_question("Q61", "Apakah terdapat pemisahan antara alat, perkakas, dan bahan yang diperlukan atau digunakan?", [
        "Tidak ada pemisahan", "Ada tapi tidak signifikan", "Ada pemisahan rapi dan menyeluruh"
    ])
    render_question("Q62", "Apakah terdapat penataan antara alat, perkakas, dan bahan yang diperlukan atau digunakan?", [
        "Tidak ada penataan", "Ada sebagian kecil penataan", "Ada sebagian besar penataan"
    ])
    render_question("Q63", "Apakah terdapat aktivitas pembersihan antara alat, perkakas, dan bahan yang diperlukan atau digunakan?", [
        "Tidak ada jadwal", "Ada pembersihan tapi tidak rutin", "Ada pembersihan rutin dengan jadwal"
    ])
    render_question("Q64", "Apakah terdapat prosedur kebersihan, penempatan dan penataan untuk alat, perkakas dan bahan dan secara berkala prosedur dikembangkan?",[
        "Tidak terdapat prosedur", "Prosedur terdapat namun belum dikembangkan secara berkala", "Prosedur terdapat dan telah dikembangkan"
    ])
    render_question("Q65", "Apakah terdapat pelabelan yang jelas?", ["Tidak ada pelabelan", "Ada tapi tidak merata", "Ada dan diterapkan merata"])

    if st.button("Simpan Data Gedung Ini 💾", type="primary", use_container_width=True):
        subtotal_4 = sum(int(v) for k, v in st.session_state.current_gedung.items()
                            if k.endswith("_Poin") and any(k.startswith(f"Q{i}_") for i in range(62, 67)))
        st.session_state.current_gedung["Skor_Topik_4"] = subtotal_4

        standar = get_standar_bidang(punya_bawah_tanah, punya_halaman)

        skor_aktual = {
            "Kondisi Fisik": st.session_state.current_gedung.get("Skor_Topik_1", 0),
            "Fasilitas Kebersihan": st.session_state.current_gedung.get("Skor_Topik_2", 0),
            "Kebutuhan Udara": st.session_state.current_gedung.get("Skor_Topik_3", 0),
            "Tata Laksana Kerumahtanggaan": st.session_state.current_gedung.get("Skor_Topik_4", 0),
        }

        bidang_perlu_perbaikan = []
        for nama_bidang, target in standar.items():
            aktual = skor_aktual[nama_bidang]
            if aktual < target:
                bidang_perlu_perbaikan.append(f"{nama_bidang}: {aktual}/{target}")

        st.session_state.current_gedung["Status Pemenuhan"] = "Tidak perlu perbaikan" if not bidang_perlu_perbaikan else "Perlu perbaikan"
        st.session_state.current_gedung["Bidang perlu diperbaiki"] = (
            ", ".join(bidang_perlu_perbaikan) if bidang_perlu_perbaikan else "Tidak ada"
        )

        # Kalkulasi total skor pada gedung ini
        total_skor = sum(v for k, v in st.session_state.current_gedung.items() if k.endswith("_Poin"))
        st.session_state.current_gedung["Total Poin Gedung"] = total_skor

        # Masukkan ke daftar gedung
        st.session_state.gedung_data.append(st.session_state.current_gedung)
        next_step('loop_decision')
        st.rerun()


elif st.session_state.step == "loop_decision":
    st.session_state.gedung_data = evaluasi_toilet(st.session_state.gedung_data)

    st.title("Data berhasil disimpan")

    st.write(f"Total objek yang telah dinilai: {len(st.session_state.gedung_data)}")



    if st.session_state.gedung_data:
        st.markdown("### Daftar Objek yang Telah Dinilai:")
        ringkasan = []
        for g in st.session_state.gedung_data:
            ringkasan.append({
                "No": g.get("Nomor Gedung", "-"),
                "Nama Gedung": g.get("Nama Gedung", "-"),
                "Jenis Objek": g.get("Jenis Objek", "-"),
                "Waktu Penilaian": g.get("Waktu Penilaian Gedung", "-"),
                "Total Poin": g.get("Total Poin Gedung", 0)
            })
        st.dataframe(pd.DataFrame(ringkasan), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Tambah Gedung Lain", use_container_width=True):
            st.session_state.current_gedung = {}
            next_step('identifikasi_objek')
            st.rerun()
    with col2:
        if st.button("🏁 Selesai & Kirim Seluruh Data ke Spreadsheet", type="primary", use_container_width=True):
            next_step('submit_sheets')
            st.rerun()

elif st.session_state.step == "submit_sheets":
    st.title("Mengirim data ke spreadsheet...")

    with st.spinner("Menghubungkan ke basis data Google Sheets..."):
        # Siapkan dataframe perusahaan
        df_perusahaan = pd.DataFrame([st.session_state.company_data])

        # Dataframe hasil survei
        df_survei = pd.DataFrame(st.session_state.gedung_data)

        # Simpan ke masing masing worksheet
        status_perusahaan = save_to_gsheet("Data_Perusahaan", df_perusahaan)
        status_survei = save_to_gsheet("Hasil_Survei", df_survei)
        
    if status_perusahaan and status_survei:
        st.balloons()
        st.success("✅ Seluruh data survei berhasil dikirim ke Google Sheets!")
        st.markdown(f"""
        ### Ringkasan Pengisian:
        - **Company Key**: `{st.session_state.company_key}`
        - **Lembaga Uji K3**: {st.session_state.company_data.get('Nama Lembaga K3', '-')}
        - **Nama Ahli K3**: {st.session_state.company_data.get('Nama Ahli K3', '-')}
        - **Pengisi Form**: {st.session_state.company_data.get('Pengisi Form', '-')}
        - **Nama Perusahaan**: {st.session_state.company_data.get('Nama Perusahaan', '-')}
        - **No. Induk Perusahaan**: {st.session_state.company_data.get('No Induk Perusahaan', '-')}
        - **No. Telepon Perusahaan**: {st.session_state.company_data.get('No Telp Perusahaan', '-')}
        - **Lokasi Pengujian**: {st.session_state.company_data.get('Lokasi Pengujian', '-')}
        - **Jumlah Objek/Gedung**: {len(st.session_state.gedung_data)} unit
        """)

        for g in st.session_state.gedung_data:
            nama = g.get("Nama Gedung", "-")
            nomor = g.get("Nomor Gedung", "-")
            status = g.get("Status Pemenuhan", "-")
            total = g.get("Total Poin Gedung", "-")
            perbaikan_str = g.get("Bidang perlu diperbaiki", "")

            with st.expander(f"🏢 **{nama}** — Status: **{status}** (Total Skor: {total})", expanded=True):
                st.write(f"Nomor Gedung: {nomor}")

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Kondisi Fisik", g.get("Skor_Topik_1", "-"))
                c2.metric("Kebersihan", g.get("Skor_Topik_2", "-"))
                c3.metric("Kebutuhan Udara", g.get("Skor_Topik_3", "-"))
                c4.metric("Housekeeping", g.get("Skor_Topik_4", "-"))
                
                st.write("")
                # 3. Kumpulkan & Tampilkan Pertanyaan Kurang Menggunakan Dropdown (st.expander)
                # 3. Kumpulkan & Tampilkan Pertanyaan Kurang Menggunakan Dropdown (st.expander)
                # Evaluasi parameter kondisi fisik khusus
                punya_bt = g.get("Q28_Jawaban") != "Tidak ada"
                punya_halaman = g.get("Q1_Jawaban") == "Ya"

                # Ambil nilai acuan standar sesuai fungsi yang tersedia
                try:
                    target_standar = get_standar_bidang(punya_bt, punya_halaman)
                except TypeError:
                    target_standar = get_standar_bidang(punya_bt)
                    if not punya_halaman:
                        target_standar["Kondisi Fisik"] -= 25

                # Pemetaan skor riil per bidang gedung
                skor_aktual_bidang = {
                    "Kondisi Fisik": int(g.get("Skor_Topik_1", 0)),
                    "Fasilitas Kebersihan": int(g.get("Skor_Topik_2", 0)),
                    "Kebutuhan Udara": int(g.get("Skor_Topik_3", 0)),
                    "Tata Laksana Kerumahtanggaan": int(g.get("Skor_Topik_4", 0))
                }

                # Evaluasi bidang-bidang mana saja yang di bawah standar
                bidang_di_bawah_standar = []
                for bidang_nama, target_skor in target_standar.items():
                    skor_riil = skor_aktual_bidang.get(bidang_nama, 0)
                    if skor_riil < target_skor:
                        bidang_di_bawah_standar.append(f"{bidang_nama} ({skor_riil}/{target_skor} Poin)")

                # A. TAMPILKAN STATUS BIDANG YANG DI BAWAH STANDAR
                if bidang_di_bawah_standar:
                    st.error("⚠️ **Bidang yang Berada di Bawah Standar Minimal:**")
                    for b_kurang in bidang_di_bawah_standar:
                        st.markdown(f"- 🛑 **{b_kurang}**")
                else:
                    st.success("🎉 **Luar biasa!** Seluruh skor bidang sudah memenuhi batas standar minimal.")

                st.write("")

                # B. KUMPULKAN KESELURUHAN ITEM PERTANYAAN YANG KURANG DARI SEMUA BIDANG
                semua_bidang = ["Kondisi Fisik", "Fasilitas Kebersihan", "Kebutuhan Udara", "Tata Laksana Kerumahtanggaan"]
                temuan_per_bidang = {}

                for bidang in semua_bidang:
                    detail_sub = analisis_sub_bidang_kurang(g, bidang)
                    
                    # Jika gedung tidak punya halaman, jangan masukkan pertanyaan halaman
                    if not punya_halaman and bidang == "Kondisi Fisik" and "Halaman & Area Terbuka" in detail_sub:
                        del detail_sub["Halaman & Area Terbuka"]

                    if detail_sub:
                        temuan_per_bidang[bidang] = detail_sub

                # C. TAMPILKAN DROPDOWN RINCIAN PERTANYAAN SECARA MENYELURUH
                if not temuan_per_bidang:
                    st.info("ℹ️ Tidak ditemukan butir pertanyaan yang bernilai rendah pada objek ini.")
                else:
                    st.warning("🔍 **Rincian Butir Pertanyaan yang Perlu Perbaikan (Semua Bidang):**")

                    for bidang, dict_sub in temuan_per_bidang.items():
                        total_item_kurang = sum(len(list_soal) for list_soal in dict_sub.values())
                        skor_b = skor_aktual_bidang.get(bidang, 0)
                        std_b = target_standar.get(bidang, 0)

                        # Indikator status bidang pada judul dropdown
                        status_tag = "🔴 Di Bawah Standar" if skor_b < std_b else "🟢 Memenuhi Standar"
                        label_expander = f"📌 **Bidang: {bidang}** [{status_tag}] — Skor: {skor_b}/{std_b} ({total_item_kurang} item perlu perbaikan)"

                        with st.expander(label_expander, expanded=False):
                            for nama_sub, list_soal in dict_sub.items():
                                st.markdown(f"**🔧 Sub Bidang: {nama_sub}**")
                                for item in list_soal:
                                    st.markdown(
                                        f"- ❌ **[{item['id']}] {item['deskripsi']}**  \n"
                                        f"  *Jawaban terpilih:* `{item['jawaban_user']}` *(Skor: {item['skor']})*"
                                    )
                                st.write("")
                
    else:
        st.warning("⚠️ Data belum berhasil terkirim ke Google Sheets. Pastikan konfigurasi `.streamlit/secrets.toml` sudah sesuai.")

    st.markdown("---")
    st.subheader("Preview Data yang Disimpan:")
    tab1, tab2 = st.tabs(["Data Profil Perusahaan", "Hasil Nilai Survei"])
    with tab1:
        st.dataframe(df_perusahaan, use_container_width=True)
    with tab2:
        st.dataframe(df_survei, use_container_width=True)

    if st.button("Mulai Survei Baru"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()