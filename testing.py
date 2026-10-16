from fsspec.utils import other_paths
from streamlit import session_state
import streamlit as st
import uuid
import pandas as pd 
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

spreadsheet_url = "https://docs.google.com/spreadsheets/d/13tRTSmDoRLNbgcP53GxO-IN0a9AXNRyPiB1e2UBtFgw/edit"

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
    st.session_state.step = 'registrasi'
if 'company_key' not in st.session_state:
    st.session_state.company_key = ''
if 'company_data' not in st.session_state:
    st.session_state.company_data = {}
if 'gedung_data' not in st.session_state:
    st.session_state.gedung_data = []
if 'current_gedung' not in st.session_state:
    st.session_state.current_gedung = {}

# Fungsi Navigasi
def next_step(step_name):
    st.session_state.step = step_name

# 
def render_question(q_id, question_text, options):
    nomor_gedung = st.session_state.current_gedung.get("Nomor Gedung", 1)
    ans = st.radio(f"{q_id}, {question_text}", options, key=f"radio_{nomor_gedung}_{q_id}")
    score = options.index(ans) + 1

    # Simpan jawaban teks dan skornya
    st.session_state.current_gedung[f"{q_id}_Jawaban"] = ans
    st.session_state.current_gedung[f"{q_id}_Skor"] = score
    st.session_state.current_gedung[f"{q_id}_Poin"] = score
    return ans

def render_header_gedung():
    if "Nama Gedung" in st.session_state.current_gedung:
        nama = st.session_state.current_gedung.get("Nama Gedung", "")
        nomor = st.session_state.current_gedung.get("Nomor Gedung", "")
        st.info(f"🏢 **Objek ke-{nomor}:** {nama}")

# Flow 1
if st.session_state.step == 'registrasi':
    st.title("Isi Data Diri Perusahaan")

    with st.form("form_registrasi"):
        col1, col2 = st.columns(2)
        with col1:
            nama_perusahaan = st.text_input("Nama Perusahaan*", placeholder="Contoh: PT Sumber Sejahtera")
            legalitas = st.selectbox("Bentuk Legalitas", ["PT", "CV", "Lainnya"])
            nama_responden = st.text_input("Nama Responden*", placeholder="Nama Penanggung Jawab / Pengisi")
            jabatan = st.text_input("Posisi / Jabatan", placeholder="Ahli K3 / Manajer HSE")
        with col2:
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
            jenis_usaha = st.selectbox("Jenis Usaha (KBLI)", kbli_list)
            jumlah_karyawan = st.selectbox("Kategori Jumlah Tenaga Kerja", [
                "Industri Besar (≥ 100 orang)",
                "Industri Sedang (20 - 99 orang)",
                "Industri Kecil (5 - 19 orang)",
                "Industri Rumah Tangga (1 - 4 orang)"
            ])

            punya_key = st.text_input("Company Key Lama (Kosongkan jika baru pertama kali)", placeholder="Misal: A1B2C3D4")

        submitted = st.form_submit_button("Lanjut ke Survei Langsung ➔", use_container_width=True)
        
        if submitted:
            if not nama_perusahaan.strip() or not nama_responden.strip():
                st.error("Nama Perusahaan dan Nama Responden wajib diisi!")
            else:
                key = punya_key.strip().upper() if punya_key.strip() else str(uuid.uuid4().hex)[:8].upper()
                st.session_state.company_key = key
                st.session_state.company_data = {
                    "Company Key": key,
                    "Waktu Pengisian": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Nama Perusahaan": nama_perusahaan,
                    "Legalitas": legalitas,
                    "Nama Responden": nama_responden,
                    "Jabatan": jabatan,
                    "Jenis Usaha (KBLI)": jenis_usaha,
                    "Kategori Pekerja": jumlah_karyawan
                }
                next_step('identifikasi_objek')
                st.rerun()

elif st.session_state.step == 'identifikasi_objek':
    nomor_gedung = len(st.session_state.gedung_data) + 1
    st.title(f"Bagian II. Penilaian Objek Survei ke-{nomor_gedung}")
    st.info(f"Company Key: **{st.session_state.company_key}** | Perusahaan: **{st.session_state.company_data.get('Nama Perusahaan')}**")

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

        bawah_tanah_sirkulasi = "-"
        if "Bangunan Bawah Tanah" in jenis_objek:
            bawah_tanah_sirkulasi = st.text_input("Keterangan Tambahan Sistem Sirkulasi / Izin Masuk Bangunan Bawah Tanah:")

        if st.form_submit_button("Mulai Instrumen Topik 1 (Bangunan) ➔", use_container_width=True):
            if not nama_gedung.strip():
                st.error(f"Nama / Identitas Gedung ke-{nomor_gedung} wajib diisi agar tidak tertukar saat pengujian ulang!")
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
                    "Pekerja Disabilitas": pekerja_disabilitas,
                    "Catatan Bawah Tanah": bawah_tanah_sirkulasi
                }
                next_step('topik_1')
                st.rerun()

# ==========================================
# FLOW 3: TOPIK 1 - KONDISI FISIK
# ==========================================
elif st.session_state.step == "topik_1":
    st.title("Kondisi Bangunan:")
    render_header_gedung()

    nomor_gedung = st.session_state.current_gedung.get("Nomor Gedung", 1)

    # Pertanyaan tentang halaman
    st.markdown("### A. Area Halaman")
    q1 = st.radio("1. Apakah lingkungan kerja memiliki halaman?", ["Ya", "Tidak"], key=f"radio_{nomor_gedung}_q1")
    st.session_state.current_gedung["Q1_Jawaban"] = q1
    st.session_state.current_gedung["Q1_Poin"] = 1 if q1 == "Ya" else 0

    opt_standar = [
        "Tidak memenuhi / kotor / rusak",
        "1% - /25% /dari jumlah keseluruhan objek memenuhi",
        "26% - /50% /dari jumlah keseluruhan objek memenuhi",
        "51% - /75% /dari jumlah keseluruhan objek memenuhi",
        "76% - /100% /dari jumlah keseluruhan objek memenuhi"
    ]

    if q1 == "Ya":
        render_question("Q2", "Apakah halaman bersih?", opt_standar)
        render_question("Q3", "Apakah halaman tertata rapi?", opt_standar)
        render_question("Q4", "Apakah halaman rata atau tidak berlubang-lubang?", opt_standar)
        render_question("Q5", "Apakah halaman tidak becek?", opt_standar)
        render_question("Q6", "Apakah halaman cukup luas untuk lalu lintas orang dan barang?", opt_standar)
    else:
        st.info("ℹ️ Sesuai pedoman: Melewati pertanyaan 2 - 6 karena tidak memiliki halaman.")
        for q_skip in ["Q2", "Q3", "Q4", "Q5", "Q6"]:
            st.session_state.current_gedung[f"{q_skip}_Jawaban"] = "N/A (Tidak Ada Halaman)"
            st.session_state.current_gedung[f"{q_skip}_Poin"] = 0

    render_question("Q7", "Apakah saluran air pembuangan tertutup dengan bahan yang kuat?", [
        "Tidak ada saluran air pembuangan",
        "Ada, 0% - /25% /saluran tertutup bahan kuat",
        "Ada, 26% - /50% /saluran tertutup bahan kuat",
        "Ada, 51% - /75% /saluran tertutup bahan kuat",
        "Ada, 76% - /100% /saluran tertutup bahan kuat"
    ])

    st.markdown("---")
    st.markdown("### B. Kondisi Fisik Gedung (Dinding, Lantai, Langit-langit, Atap)")
    render_question("Q8", "Apakah Gedung terpelihara sehingga bersih?", opt_standar)
    render_question("Q9", "Apakah struktur gedung kuat dan kokoh (tidak retak/rusak berisiko)?", opt_standar)
    render_question("Q10", "Apakah Gedung cukup luas sehingga memberikan ruang Gerak paling sedikit 2 m2 per orang", opt_standar)
    render_question("Q11", "Apakah dinding kering / tidak lembap / tidak korosi?", opt_standar)
    render_question("Q12", "Apakah langit-langit kering atau tidak lembab?", opt_standar)
    render_question("Q13", "Apakah dinding dicat, bersih dan mudah dibersihkan", opt_standar)
    render_question("Q14", "Apakah langit-langit dicat?", opt_standar)
    render_question("Q15", "Apakah langit-langit bersih dan mudah dibersihkan", opt_standar)
    render_question("Q16", "Apakah dinding dilakukan pengecatan ulang", opt_standar)
    render_question("Q17", "Apakah dinding dibersihkan secara rutin", opt_standar)
    render_question("Q18", "Apakah langit-langit dibersihkan secara rutin", opt_standar)

    # Tentang Lantai
    render_question("Q19", "Apakah lantai terbuat dari bahan yang keras", opt_standar)
    render_question("Q20", "Apakah lantai terbuat dari bahan yang tahan air?", opt_standar)
    render_question("Q21", "Apakah lantai terbuat dari bahan yang tahan dari bahan kimia yang merusak?", opt_standar)
    render_question("Q22", "Apakah lantai datar dan mudah dibersihkan?", opt_standar)
    render_question("Q23", "Apakah lantai tidak licin?", opt_standar)
    render_question("Q24", "Apakah lantai dibersihkan secara teratur?", opt_standar)

    # Atap
    render_question("Q25", "Apakah keseluruhan atap mampu memberi perlindungan dari panas matahari dan hujan?", opt_standar)
    render_question("Q26", "Apakah keseluruhan atap tidak bocor, tidak berlubang?", opt_standar)
    render_question("Q27", "Apakah keseluruhan atap tidak berjamur?", opt_standar)

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
    render_question("Q36", "Apakah toilet bersih dan tidak menimbulkan bau?", opt_toilet)
    render_question("Q39", "Apakah toilet tersedia air bersih yang cukup?", opt_toilet)
    render_question("Q45", "Apakah toilet terpisah antara laki-laki, perempuan, dan penyandang disabilitas?", [
        "Tidak terpisah",
        "Terpisah sebagian",
        "Terpisah lengkap sesuai ketentuan"
    ])

    st.markdown("---")
    st.markdown("### B. Tempat Sampah & Pakaian Kerja")
    q52 = render_question("Q52", "Apakah Perusahaan menyediakan tempat sampah terpisah?", [
        "Tidak menyediakan tempat sampah",
        "Menyediakan namun tidak terpisah",
        "Menyediakan dan terpisah"
    ])

    if q52 == "Menyediakan dan terpisah":
        render_question("Q53", "Apakah tempat sampah terpisah diberikan label sesuai ketentuan?", opt_toilet)
        render_question("Q54", "Apakah tempat sampah terpisah dalam kondisi tertutup?", opt_toilet)
    else:
        st.info("ℹ️ Pertanyaan 53-54 dilewati karena tempat sampah tidak terpisah / tidak tersedia.")
        for q_sampah in ["Q53", "Q54"]:
            st.session_state.current_gedung[f"{q_sampah}_Jawaban"] = "N/A (Tempat sampah tidak terpisah)"
            st.session_state.current_gedung[f"{q_sampah}_Poin"] = 0

    if st.button("Lanjut ke Topik Kebutuhan Udara ➔", type="primary", use_container_width=True):
        next_step('topik_3')
        st.rerun()

elif st.session_state.step == 'topik_3':
    st.title("Kebutuhan Udara")
    render_header_gedung()

    st.markdown("---")
    st.markdown("### C. Kebutuhan Udara & Housekeeping Singkat")

    opt_standar = [
        "Tidak memenuhi / kotor / rusak",
        "1% - /25% /dari jumlah keseluruhan objek memenuhi",
        "26% - /50% /dari jumlah keseluruhan objek memenuhi",
        "51% - /75% /dari jumlah keseluruhan objek memenuhi",
        "76% - /100% /dari jumlah keseluruhan objek memenuhi"
    ]

    render_question("Q58", "Apakah suhu ruangan nyaman (23 - 26°C)?", opt_standar)

    if st.button("Lanjut ke Topik Tata Laksana Kerumahtanggaan ➔", type="primary", use_container_width=True):
        next_step('topik_4')
        st.rerun()

elif st.session_state.step == 'topik_4':
    st.title("Tata Laksana Kerumahtanggaan")
    render_header_gedung()

    opt_standar = [
        "Tidak memenuhi / kotor / rusak",
        "1% - /25% /dari jumlah keseluruhan objek memenuhi",
        "26% - /50% /dari jumlah keseluruhan objek memenuhi",
        "51% - /75% /dari jumlah keseluruhan objek memenuhi",
        "76% - /100% /dari jumlah keseluruhan objek memenuhi"
    ]
    render_question("Q61", "Apakah terdapat sistem ventilasi yang memadai (alami/buatan)?", opt_standar)
    render_question("Q64", "Apakah terdapat pemisahan antara alat, perkakas, dan bahan kerja?", [
        "Tidak ada pemisahan",
        "Ada pemisahan sebagian kecil",
        "Ada pemisahan rapi dan menyeluruh"
    ])

    if st.button("Simpan Data Gedung Ini 💾", type="primary", use_container_width=True):
        # Kalkulasi total skor pada gedung ini
        total_skor = sum(v for k, v in st.session_state.current_gedung.items() if k.endswith("_Poin"))
        st.session_state.current_gedung["Total Poin Gedung"] = total_skor

        # Masukkan ke daftar gedung
        st.session_state.gedung_data.append(st.session_state.current_gedung)
        next_step('loop_decision')
        st.rerun()


elif st.session_state.step == "loop_decision":
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
        - **Nama Perusahaan**: {st.session_state.company_data.get('Nama Perusahaan')}
        - **Jumlah Objek/Gedung**: {len(st.session_state.gedung_data)} unit
        """)
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