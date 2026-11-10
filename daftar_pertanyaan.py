import math

def to_int(val, default=0) -> int:
    """Konversi nilai aman ke integer (mendukung float string seperti '8.0', int, float, None, string kosong)."""
    if val is None:
        return default
    s = str(val).strip()
    if not s or s.lower() == "nan" or s == "-":
        return default
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return default


# ==============================================================================
# PILIHAN JAWABAN & PANDUAN PENGISIAN
# (Sesuai Sheet 'Panduan Pengisian' & Revisi Instrumen HIBB)
# ==============================================================================
OPT_3_TINGKAT = [
    "Memenuhi",
    "Memenuhi Sebagian",
    "Tidak Memenuhi"
]

OPT_YA_TIDAK = [
    "Ya",
    "Tidak"
]

NILAI_OPSI = {
    "Memenuhi": 2,
    "Memenuhi Sebagian": 1,
    "Tidak Memenuhi": 0,
    "Ya": 2,
    "Tidak": 0,
    "Iya": 2,
}

PANDUAN_PENGISIAN = {
    "Memenuhi": {
        "skor": 2,
        "makna": "Terpenuhi / Memenuhi",
        "kriteria": "Persyaratan diterapkan, berfungsi, dan didukung bukti objektif yang memadai."
    },
    "Memenuhi Sebagian": {
        "skor": 1,
        "makna": "Terpenuhi Sebagian / Memenuhi Sebagian",
        "kriteria": "Ada sebagian pelaksanaan tetapi belum konsisten, belum mencakup seluruh area/shift, atau tindak lanjut belum lengkap."
    },
    "Tidak Memenuhi": {
        "skor": 0,
        "makna": "Tidak Terpenuhi / Tidak Memenuhi",
        "kriteria": "Tidak tersedia, tidak berfungsi, atau tidak ada bukti yang memadai."
    },
    "Ya": {
        "skor": 2,
        "makna": "Ya",
        "kriteria": "Memenuhi ketentuan secara penuh dan didukung bukti objektif."
    },
    "Tidak": {
        "skor": 0,
        "makna": "Tidak",
        "kriteria": "Belum / tidak memenuhi ketentuan yang dipersyaratkan."
    }
}


# ==============================================================================
# DAFTAR ASPEK / KELOMPOK FASILITAS (Kolom C Matriks Penilaian)
# Dijadikan daftar fasilitas untuk dipilih jika gedung memiliki fasilitas tsb
# ==============================================================================
KELOMPOK_FASILITAS = [
    {
        "id": "halaman",
        "aspek": "Halaman",
        "kategori": "A. Bangunan Tempat Kerja",
        "nama": "Area Halaman & Saluran Pembuangan Luar",
        "icon": "🌳",
        "deskripsi": "Kebersihan, kerapian, kerataan, genangan air, serta kelancaran saluran pembuangan air halaman",
        "topik": "Bangunan Tempat Kerja",
        "default_checked": True,
        "soal_ids": ["A2", "A3", "A4", "A5", "A6", "A7"]
    },
    {
        "id": "gedung",
        "aspek": "Gedung",
        "kategori": "A. Bangunan Tempat Kerja",
        "nama": "Bangunan Gedung (Struktur, Dinding, Lantai, Langit-langit & Atap)",
        "icon": "🏢",
        "deskripsi": "Kekokohan struktur, ruang gerak 2 m², kelembapan/kebersihan dinding, lantai tahan air/kimia, dan atap",
        "topik": "Bangunan Tempat Kerja",
        "default_checked": True,
        "soal_ids": ["A8", "A9", "A10", "A11", "A12", "A13", "A14", "A15", "A16", "A17", "A18", "A19"]
    },
    {
        "id": "bawah_tanah",
        "aspek": "Ruang Bawah Tanah",
        "kategori": "A. Bangunan Tempat Kerja",
        "nama": "Bangunan Bawah Tanah (Basement / Underground)",
        "icon": "⛏️",
        "deskripsi": "Kekuatan struktur bawah tanah, ventilasi, pencahayaan, saluran pembuangan, dan kebersihan",
        "topik": "Bangunan Tempat Kerja",
        "default_checked": False,
        "soal_ids": ["A21", "A22", "A23", "A24", "A25"]
    },
    {
        "id": "toilet",
        "aspek": "Toilet",
        "kategori": "B. Fasilitas Kebersihan",
        "nama": "Fasilitas Toilet & Sanitasi",
        "icon": "🚻",
        "deskripsi": "Kecukupan rasio jumlah toilet terhadap pekerja, kebersihan, bebas bau, dan toilet ramah disabilitas",
        "topik": "Fasilitas Kebersihan",
        "default_checked": True,
        "soal_ids": ["B1", "B2", "B3", "B4"]
    },
    {
        "id": "loker",
        "aspek": "Loker",
        "kategori": "B. Fasilitas Kebersihan",
        "nama": "Loker Penyimpanan & Ruang Ganti Pakaian",
        "icon": "🚪",
        "deskripsi": "Ketersediaan loker penyimpanan barang pekerja dan ruang ganti pakaian yang aman dan tertib",
        "topik": "Fasilitas Kebersihan",
        "default_checked": True,
        "soal_ids": ["B5", "B6"]
    },
    {
        "id": "tempat_sampah",
        "aspek": "Tempat Sampah",
        "kategori": "B. Fasilitas Kebersihan",
        "nama": "Tempat Sampah & Pemilahan Limbah",
        "icon": "🗑️",
        "deskripsi": "Wadah penampungan sampah sementara serta pemilahan sampah organik, anorganik, dan limbah B3",
        "topik": "Fasilitas Kebersihan",
        "default_checked": True,
        "soal_ids": ["B7", "B8"]
    },
    {
        "id": "peralatan_kebersihan",
        "aspek": "Peralatan Kebersihan",
        "kategori": "B. Fasilitas Kebersihan",
        "nama": "Peralatan & Perlengkapan Kebersihan",
        "icon": "🧽",
        "deskripsi": "Kondisi fisik, kelayakan fungsi, dan tempat penyimpanan peralatan kebersihan",
        "topik": "Fasilitas Kebersihan",
        "default_checked": True,
        "soal_ids": ["B9"]
    },
    {
        "id": "kudr",
        "aspek": "KUDR",
        "kategori": "C. Kebutuhan Udara",
        "nama": "KUDR (Suhu & Kelembapan Udara Kerja)",
        "icon": "🌡️",
        "deskripsi": "Suhu udara ruang kerja dalam rentang 23–26°C dan kelembapan relatif 40–60%",
        "topik": "Kebutuhan Udara",
        "default_checked": True,
        "soal_ids": ["C1", "C2"]
    },
    {
        "id": "ventilasi",
        "aspek": "Ventilasi",
        "kategori": "C. Kebutuhan Udara",
        "nama": "Sistem Ventilasi Udara",
        "icon": "💨",
        "deskripsi": "Kelancaran sirkulasi dan fungsi pertukaran udara ruangan (alami maupun mekanis)",
        "topik": "Kebutuhan Udara",
        "default_checked": True,
        "soal_ids": ["C3"]
    },
    {
        "id": "ruang_udara",
        "aspek": "Ruang Udara",
        "kategori": "C. Kebutuhan Udara",
        "nama": "Ruang Udara (Cubic Space ≥ 10 m³)",
        "icon": "📦",
        "deskripsi": "Kecukupan volume ruang udara paling sedikit 10 m³ untuk setiap pekerja",
        "topik": "Kebutuhan Udara",
        "default_checked": True,
        "soal_ids": ["C4"]
    },
    {
        "id": "housekeeping",
        "aspek": "Tata Laksana Kerumahtanggaan",
        "kategori": "D. Tata Laksana Kerumahtanggaan (Housekeeping)",
        "nama": "Tata Laksana Kerumahtanggaan (5R / Housekeeping)",
        "icon": "🧹",
        "deskripsi": "Pemisahan, penataan, pembersihan berkala alat/bahan kerja, serta SOP yang dikembangkan teratur",
        "topik": "Tata Laksana Kerumahtanggaan",
        "default_checked": True,
        "soal_ids": ["D1", "D2", "D3", "D4"]
    }
]


# ==============================================================================
# MASTER DAFTAR PERTANYAAN (MATRIKS PENILAIAN IHSAN)
# Kolom A = Kategori, Kolom B = Kode, Kolom C = Aspek, Kolom D = Pertanyaan
# Definisi Operasional & Bukti Objektif dijadikan isi Pop-up Konteks
# ==============================================================================
MASTER_PERTANYAAN = {
    # --------------------------------------------------------------------------
    # KATEGORI A: BANGUNAN TEMPAT KERJA (Total Bobot 25%)
    # --------------------------------------------------------------------------
    # Aspek: Halaman (Bobot: 10%, Skor Maks: 10)
    "A2": {
        "id": "A2",
        "kode": "A2",
        "aspek": "Halaman",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Halaman",
        "kelompok": "halaman",
        "teks": "Apakah halaman tertata rapi dan bersih?",
        "definisi": "Halaman yang tertata rapi dan bersih merupakan halaman yang bebas dari sampah atau kotoran yang mengganggu serta memiliki barang dan material yang ditempatkan secara teratur, tidak berserakan.",
        "bukti": "Observasi langsung terhadap kebersihan halaman, penataan barang/material, kondisi jalur akses, dan drainase.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "A3": {
        "id": "A3",
        "kode": "A3",
        "aspek": "Halaman",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Halaman",
        "kelompok": "halaman",
        "teks": "Apakah halaman rata?",
        "definisi": "Halaman yang rata dan bebas lubang, benjolan, serta hambatan merupakan halaman dengan permukaan yang relatif rata.",
        "bukti": "Kondisi permukaan halaman, keberadaan lubang atau tonjolan, permukaan amblas, serta dampaknya terhadap mobilitas pekerja dan kendaraan.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "A4": {
        "id": "A4",
        "kode": "A4",
        "aspek": "Halaman",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Halaman",
        "kelompok": "halaman",
        "teks": "Apakah halaman tidak becek dan terbebas dari genangan air?",
        "definisi": "Halaman yang tidak becek dan bebas genangan merupakan halaman dengan permukaan yang tidak berlumpur atau basah hingga mengganggu aktivitas, serta tidak terdapat air yang terkumpul dan menetap di permukaan secara lama.",
        "bukti": "Keberadaan genangan air atau lumpur di permukaan secara lama.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "A5": {
        "id": "A5",
        "kode": "A5",
        "aspek": "Halaman",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Halaman",
        "kelompok": "halaman",
        "teks": "Apakah terdapat saluran air pembuangan pada halaman?",
        "definisi": "Saluran air pembuangan pada halaman merupakan saluran yang berfungsi menampung dan mengalirkan air buangan dari area halaman menuju tempat pembuangan. Butir ini digunakan untuk mengidentifikasi keberadaan saluran; apabila tidak tersedia, butir terkait kondisi saluran tidak berlaku.",
        "bukti": "Pemeriksaan fisik ketersediaan saluran drainase/pembuangan air di area halaman.",
        "tipe": "screening_saluran",
        "opsi": ["Ya, terdapat saluran pembuangan air", "Tidak ada saluran pembuangan air"],
        "bobot_max": 0
    },
    "A6": {
        "id": "A6",
        "kode": "A6",
        "aspek": "Halaman",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Halaman",
        "kelompok": "halaman",
        "teks": "Apakah saluran tersebut tertutup dan terbuat dari bahan yang cukup kuat?",
        "definisi": "Saluran air pembuangan yang tertutup dan cukup kuat merupakan saluran yang bagian atasnya terlindungi penutup serta memiliki badan dan penutup yang kokoh untuk penggunaan normal.",
        "bukti": "Keberadaan dan kondisi penutup saluran, kestabilan pemasangan, kondisi fisik material, serta kesesuaian kekuatan penutup terhadap beban di area tersebut.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2,
        "depends_on": "A5"
    },
    "A7": {
        "id": "A7",
        "kode": "A7",
        "aspek": "Halaman",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Halaman",
        "kelompok": "halaman",
        "teks": "Apakah saluran tersebut mengalir dan tidak tergenang?",
        "definisi": "Saluran air pembuangan yang mengalir dan tidak tergenang merupakan saluran yang memungkinkan air buangan bergerak menuju tempat pembuangan tanpa sumbatan nyata atau genangan yang menetap.",
        "bukti": "Kelancaran aliran air, keberadaan genangan, sumbatan, endapan lumpur.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2,
        "depends_on": "A5"
    },

    # Aspek: Gedung (Bobot: 10%, Skor Maks: 10)
    "A8": {
        "id": "A8",
        "kode": "A8",
        "aspek": "Gedung",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Gedung",
        "kelompok": "gedung",
        "teks": "Apakah kondisi gedung terpelihara dan bersih?",
        "definisi": "Gedung yang terpelihara dan bersih merupakan bangunan Tempat Kerja yang kebersihan ruang dan bagian bangunannya dijaga serta tidak menunjukkan kerusakan atau kondisi terbengkalai yang nyata.",
        "bukti": "Kebersihan lantai, dinding, dan langit-langit; kondisi fisik bangunan; kebocoran atau rembesan; serta tanda pertumbuhan jamur dan keberadaan hama.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "A9": {
        "id": "A9",
        "kode": "A9",
        "aspek": "Gedung",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Gedung",
        "kelompok": "gedung",
        "teks": "Apakah kondisi gedung memiliki struktur yang kuat dan kokoh?",
        "definisi": "Struktur gedung yang kuat dan kokoh merupakan bagian struktur bangunan yang mampu menopang bangunan sebagaimana fungsinya dan tidak menunjukkan tanda kerusakan yang mengindikasikan gangguan kekokohan, seperti retak signifikan atau deformasi. Kepastian kekuatan struktur perlu didukung pemeriksaan teknis bila diperlukan.",
        "bukti": "Kondisi visual kolom, balok, dinding, lantai, fondasi yang terlihat, serta rangka dan atap bangunan. Dokumen layak fungsi atau dokumen bukti lainnya.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "A10": {
        "id": "A10",
        "kode": "A10",
        "aspek": "Gedung",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Gedung",
        "kelompok": "gedung",
        "teks": "Apakah luas ruang gerak di dalam gedung minimal 2 (dua) meter persegi untuk setiap orang?",
        "definisi": "Luas ruang gerak merupakan area yang tersedia bagi pekerja untuk bergerak dan melakukan pekerjaan di dalam gedung. Luas ruang gerak paling sedikit 2 m² untuk setiap orang, dihitung berdasarkan jumlah pekerja yang berada atau bekerja secara bersamaan pada ruang tersebut.",
        "bukti": "Luas lantai ruangan dan perbandingan jumlah pekerja yang beraktivitas di dalamnya.",
        "tipe": "ya_tidak",
        "opsi": OPT_YA_TIDAK,
        "bobot_max": 2
    },
    "A11": {
        "id": "A11",
        "kode": "A11",
        "aspek": "Gedung",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Gedung",
        "kelompok": "gedung",
        "teks": "Apakah dinding dan langit - langit dalam kondisi kering atau tidak lembab?",
        "definisi": "Dinding dan langit-langit merupakan permukaan pembatas vertikal dan bagian atas ruang gedung. Kondisi kering atau tidak lembap berarti permukaan tidak menunjukkan kebasahan, rembesan, atau tanda kelembapan yang masih berlangsung.",
        "bukti": "Kondisi permukaan dinding dan langit-langit, keberadaan bercak air, rembesan, kebocoran, pengembunan, cat mengelupas, serta pertumbuhan jamur.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "A12": {
        "id": "A12",
        "kode": "A12",
        "aspek": "Gedung",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Gedung",
        "kelompok": "gedung",
        "teks": "Apakah dinding dan langit-langit dicat dan/atau memiliki permukaan yang mudah dibersihkan?",
        "definisi": "Dinding merupakan permukaan pembatas ruang gedung, sedangkan langit-langit merupakan permukaan bagian atas ruang. Permukaan memenuhi kriteria apabila dicat dan/atau memiliki lapisan yang mudah dibersihkan dengan cara perawatan normal. Jenis cat tertentu tidak ditetapkan dalam ketentuan ini.",
        "bukti": "Kondisi cat atau pelapis, tingkat kehalusan permukaan, keberadaan debu dan kotoran.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "A13": {
        "id": "A13",
        "kode": "A13",
        "aspek": "Gedung",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Gedung",
        "kelompok": "gedung",
        "teks": "Apakah pengecatan ulang dinding dan langit-langit dilakukan paling sedikit 1 (satu) kali dalam setiap 5 (lima) tahun?",
        "definisi": "Pengecatan ulang merupakan kegiatan memperbarui lapisan cat pada dinding dan langit-langit agar permukaannya tetap terpelihara. Pengecatan ulang dilakukan paling sedikit satu kali dalam setiap periode lima tahun.",
        "bukti": "Dokumen riwayat pemeliharaan gedung, tanggal pengecatan terakhir, bukti pembelian cat atau jasa pengecatan, serta dokumentasi pelaksanaan.",
        "tipe": "ya_tidak",
        "opsi": OPT_YA_TIDAK,
        "bobot_max": 2
    },
    "A14": {
        "id": "A14",
        "kode": "A14",
        "aspek": "Gedung",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Gedung",
        "kelompok": "gedung",
        "teks": "Apakah dinding dan langit-langit dibersihkan paling sedikit 1 (satu) kali dalam setahun?",
        "definisi": "Pembersihan dinding dan langit-langit merupakan kegiatan menghilangkan debu, kotoran, atau noda dari permukaan tersebut. Pembersihan dilakukan paling sedikit satu kali dalam setahun.",
        "bukti": "Jadwal pembersihan, checklist atau logbook pelaksanaan, dokumentasi kegiatan.",
        "tipe": "ya_tidak",
        "opsi": OPT_YA_TIDAK,
        "bobot_max": 2
    },
    "A15": {
        "id": "A15",
        "kode": "A15",
        "aspek": "Gedung",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Gedung",
        "kelompok": "gedung",
        "teks": "Apakah lantai terbuat dari bahan yang keras, tahan air, dan tahan terhadap bahan kimia yang dapat merusaknya?",
        "definisi": "Lantai merupakan permukaan dasar ruang yang digunakan untuk aktivitas pekerja. Bahan lantai yang memenuhi persyaratan memiliki karakteristik keras, tahan air, dan tahan terhadap bahan kimia yang dapat merusaknya sesuai kondisi penggunaan.",
        "bukti": "Jenis material lantai, kondisi permukaan, keberadaan retakan atau celah, daya serap air.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "A16": {
        "id": "A16",
        "kode": "A16",
        "aspek": "Gedung",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Gedung",
        "kelompok": "gedung",
        "teks": "Apakah lantai memiliki permukaan yang datar, tidak licin, dan mudah dibersihkan?",
        "definisi": "Permukaan lantai yang memenuhi persyaratan merupakan permukaan yang datar, tidak licin pada penggunaan normal, dan mudah dibersihkan sehingga tidak menyulitkan aktivitas maupun pemeliharaan kebersihan.",
        "bukti": "Kondisi kerataan lantai, keberadaan lubang atau tonjolan, karakteristik antiselip, kondisi sambungan lantai, serta kemudahan membersihkan debu, kotoran, dan cairan.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "A17": {
        "id": "A17",
        "kode": "A17",
        "aspek": "Gedung",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Gedung",
        "kelompok": "gedung",
        "teks": "Apakah lantai dibersihkan secara teratur?",
        "definisi": "Pembersihan lantai secara teratur merupakan kegiatan membersihkan lantai secara berulang sesuai jadwal dan kebutuhan area, sehingga kotoran tidak dibiarkan menumpuk. Ketentuan ini tidak menetapkan frekuensi harian atau mingguan tertentu.",
        "bukti": "Jadwal pembersihan, checklist atau logbook, frekuensi pembersihan, ketersediaan petugas dan peralatan kebersihan.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "A18": {
        "id": "A18",
        "kode": "A18",
        "aspek": "Gedung",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Gedung",
        "kelompok": "gedung",
        "teks": "Apakah atap mampu melindungi bagian dalam gedung dari panas matahari dan air hujan?",
        "definisi": "Atap merupakan bagian teratas gedung yang berfungsi melindungi bagian dalam bangunan dari paparan langsung panas matahari dan air hujan.",
        "bukti": "Kondisi fisik atap, kondisi sambungan atap, tidak ada rembesan atau celah terbuka.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "A19": {
        "id": "A19",
        "kode": "A19",
        "aspek": "Gedung",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Gedung",
        "kelompok": "gedung",
        "teks": "Apakah atap tidak bocor, tidak berlubang, dan bebas dari jamur?",
        "definisi": "Atap yang memenuhi persyaratan merupakan atap yang tidak mengalami kebocoran, tidak memiliki lubang, dan tidak ditumbuhi jamur pada bagian yang dapat diperiksa.",
        "bukti": "Keberadaan lubang atau retakan, tanda kebocoran dan rembesan, pertumbuhan jamur atau lumut.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },

    # Aspek: Ruang Bawah Tanah (Bobot: 5%, Skor Maks: 5)
    "A21": {
        "id": "A21",
        "kode": "A21",
        "aspek": "Ruang Bawah Tanah",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Ruang Bawah Tanah",
        "kelompok": "bawah_tanah",
        "teks": "Apakah bangunan bawah tanah memiliki struktur yang kuat?",
        "definisi": "Bangunan bawah tanah merupakan ruang atau struktur yang berada di bawah permukaan tanah dan menjadi bagian dari Tempat Kerja. Struktur yang kuat tidak menunjukkan kerusakan yang mengindikasikan berkurangnya kekuatan, seperti retak signifikan, deformasi, atau elemen struktur yang rusak.",
        "bukti": "Kondisi dinding penahan tanah, kolom, balok, lantai, fondasi yang dapat diperiksa, plafon, serta indikasi retakan, deformasi, pergeseran, dan kerusakan struktur.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "A22": {
        "id": "A22",
        "kode": "A22",
        "aspek": "Ruang Bawah Tanah",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Ruang Bawah Tanah",
        "kelompok": "bawah_tanah",
        "teks": "Apakah bangunan bawah tanah dilengkapi dengan sistem ventilasi udara yang memadai?",
        "definisi": "Sistem ventilasi udara pada bangunan bawah tanah merupakan sarana ventilasi alami atau mekanis yang memungkinkan pertukaran udara. Sistem dinilai memadai apabila tersedia, dapat berfungsi, dan jalur atau perangkatnya tidak terhalang.",
        "bukti": "Ketersediaan ventilasi alami atau mekanis, kondisi dan fungsi exhaust fan/blower, saluran udara, filter, sirkulasi udara.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "A23": {
        "id": "A23",
        "kode": "A23",
        "aspek": "Ruang Bawah Tanah",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Ruang Bawah Tanah",
        "kelompok": "bawah_tanah",
        "teks": "Apakah bangunan bawah tanah memiliki sumber pencahayaan yang memadai?",
        "definisi": "Sumber pencahayaan pada bangunan bawah tanah merupakan sumber cahaya alami dan/atau buatan yang memungkinkan pekerja melihat jalur, area kerja, serta potensi bahaya saat melakukan aktivitas normal.",
        "bukti": "Ketersediaan sumber pencahayaan alami dan buatan, jumlah serta kondisi lampu, pemerataan cahaya, keberadaan area gelap, dan hasil pengukuran intensitas pencahayaan menggunakan lux meter.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "A24": {
        "id": "A24",
        "kode": "A24",
        "aspek": "Ruang Bawah Tanah",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Ruang Bawah Tanah",
        "kelompok": "bawah_tanah",
        "teks": "Apakah bangunan bawah tanah memiliki saluran pembuangan air yang mengalir dengan baik?",
        "definisi": "Saluran pembuangan air pada bangunan bawah tanah merupakan saluran yang mengalirkan air menuju tempat pembuangan. Saluran berfungsi dengan baik apabila tidak tampak tersumbat dan tidak menimbulkan genangan akibat aliran yang terhambat.",
        "bukti": "Ketersediaan saluran pembuangan, kelancaran aliran air, kondisi fisik saluran, keberadaan genangan, serta fungsi pompa pembuangan apabila digunakan.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "A25": {
        "id": "A25",
        "kode": "A25",
        "aspek": "Ruang Bawah Tanah",
        "kategori": "A. Bangunan Tempat Kerja",
        "topik": "Bangunan Tempat Kerja",
        "sub_bidang": "Ruang Bawah Tanah",
        "kelompok": "bawah_tanah",
        "teks": "Apakah bangunan bawah tanah dalam kondisi bersih dan terawat dengan baik?",
        "definisi": "Bangunan bawah tanah yang bersih dan terawat merupakan ruang dan fasilitas bawah tanah yang bebas dari kotoran atau sampah yang nyata serta dipelihara agar komponen dan fasilitasnya tidak dibiarkan rusak atau tidak berfungsi.",
        "bukti": "Kondisi kebersihan lantai, dinding, dan langit-langit; keberadaan sampah, debu, jamur, rembesan air, dan hama; kondisi fisik bangunan; serta penataan barang dan peralatan.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },

    # --------------------------------------------------------------------------
    # KATEGORI B: FASILITAS KEBERSIHAN (Total Bobot 25%)
    # --------------------------------------------------------------------------
    # Aspek: Toilet (Bobot: 10%, Skor Maks: 10)
    "B1": {
        "id": "B1",
        "kode": "B1",
        "aspek": "Toilet",
        "kategori": "B. Fasilitas Kebersihan",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Toilet",
        "kelompok": "toilet",
        "teks": "Apakah tersedia fasilitas toilet di gedung tempat kerja? (Jika tidak, apakah fasilitas toilet bergabung dengan gedung lain?)",
        "definisi": "Fasilitas toilet yang disediakan untuk pekerja pada gedung tempat kerja, baik berada mandiri di dalam gedung atau bergabung dengan fasilitas terdekat.",
        "bukti": "Keberadaan fisik toilet di gedung atau akses fasilitas toilet bersama.",
        "tipe": "info_toilet",
        "opsi": ["Tersedia mandiri di gedung ini", "Bergabung dengan fasilitas gedung lain"],
        "bobot_max": 0
    },
    "B2": {
        "id": "B2",
        "kode": "B2",
        "aspek": "Toilet",
        "kategori": "B. Fasilitas Kebersihan",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Toilet",
        "kelompok": "toilet",
        "teks": "Apakah jumlah toilet mencukupi kebutuhan pekerja?",
        "definisi": "Jumlah toilet yang mencukupi merupakan ketersediaan fasilitas toilet yang sebanding dengan jumlah pekerja yang menggunakan tempat kerja.",
        "bukti": "Jumlah unit toilet yang tersedia dan berfungsi dibandingkan rasio baku Permenaker No. 5/2018.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "B3": {
        "id": "B3",
        "kode": "B3",
        "aspek": "Toilet",
        "kategori": "B. Fasilitas Kebersihan",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Toilet",
        "kelompok": "toilet",
        "teks": "Apakah toilet bersih dan tidak menimbulkan bau?",
        "definisi": "Toilet yang bersih dan tidak menimbulkan bau merupakan fasilitas sanitasi yang tidak memiliki kotoran, noda, sampah, atau sisa penggunaan yang terlihat serta tidak mengeluarkan bau tidak sedap yang mengganggu. Penilaian dilakukan melalui observasi pada lantai, jamban, dinding, tempat cuci tangan, dan bagian toilet lainnya.",
        "bukti": "Kebersihan lantai, kloset, dinding, dan fasilitas toilet; kondisi saluran pembuangan; ketersediaan air bersih; ventilasi; serta keberadaan bau tidak sedap.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "B4": {
        "id": "B4",
        "kode": "B4",
        "aspek": "Toilet",
        "kategori": "B. Fasilitas Kebersihan",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Toilet",
        "kelompok": "toilet",
        "teks": "Apakah area kerja memiliki toilet khusus penyandang disabilitas?",
        "definisi": "Toilet khusus penyandang disabilitas merupakan fasilitas toilet yang disediakan untuk mendukung akses dan penggunaan oleh penyandang disabilitas. Penilaian awal dilakukan dengan memastikan keberadaan fasilitas; apabila tersedia, kesesuaian ukuran, akses masuk, pintu, ruang manuver, kemiringan lantai, dan pegangan diperiksa pada butir khusus berikutnya.",
        "bukti": "Ketersediaan toilet aksesibel, jalur menuju toilet, lebar pintu, ruang gerak kursi roda, pegangan rambat, kondisi kloset, wastafel, dan fasilitas pendukung lainnya.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },

    # Aspek: Loker (Bobot: 5%, Skor Maks: 5)
    "B5": {
        "id": "B5",
        "kode": "B5",
        "aspek": "Loker",
        "kategori": "B. Fasilitas Kebersihan",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Loker",
        "kelompok": "loker",
        "teks": "Apakah loker tersedia sesuai kebutuhan pekerja?",
        "definisi": "Loker yang tersedia sesuai kebutuhan merupakan tempat penyimpanan barang atau pakaian pekerja dengan jumlah yang memadai bagi pekerja yang membutuhkannya.",
        "bukti": "Jumlah loker yang layak digunakan dengan jumlah pekerja yang memerlukan fasilitas penyimpanan.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "B6": {
        "id": "B6",
        "kode": "B6",
        "aspek": "Loker",
        "kategori": "B. Fasilitas Kebersihan",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Loker",
        "kelompok": "loker",
        "teks": "Apakah area kerja memiliki ruang ganti pakaian?",
        "definisi": "Ruang ganti pakaian merupakan ruang khusus yang disediakan untuk pekerja mengganti pakaian sebelum atau sesudah bekerja. Keberadaannya dinilai berdasarkan tersedianya ruang yang dapat digunakan untuk berganti pakaian secara aman, tertib, dan menjaga privasi pekerja.",
        "bukti": "Ketersediaan ruang ganti pakaian khusus yang aman, tertib, dan menjaga privasi.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },

    # Aspek: Tempat Sampah (Bobot: 5%, Skor Maks: 5)
    "B7": {
        "id": "B7",
        "kode": "B7",
        "aspek": "Tempat Sampah",
        "kategori": "B. Fasilitas Kebersihan",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Tempat Sampah",
        "kelompok": "tempat_sampah",
        "teks": "Apakah area kerja memiliki tempat sampah?",
        "definisi": "Tempat sampah merupakan wadah untuk menampung sampah sementara sebelum dikumpulkan dan dibuang atau diangkut ke tempat pengelolaan sampah.",
        "bukti": "Ketersediaan, jumlah, lokasi penempatan, kondisi fisik, kapasitas, kebersihan tempat sampah.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "B8": {
        "id": "B8",
        "kode": "B8",
        "aspek": "Tempat Sampah",
        "kategori": "B. Fasilitas Kebersihan",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Tempat Sampah",
        "kelompok": "tempat_sampah",
        "teks": "Apakah area kerja menyediakan tempat sampah terpilah untuk sampah organik, nonorganik dan bahan berbahaya?",
        "definisi": "Tempat sampah khusus bahan berbahaya merupakan wadah yang ditetapkan untuk menampung limbah atau sampah yang memiliki sifat berbahaya sesuai jenis kegiatan di tempat kerja. Wadah harus sesuai dengan karakteristik bahan, dalam kondisi baik, tertutup atau diberi penandaan bila diperlukan, dan terpisah dari sampah umum untuk mencegah pencampuran.",
        "bukti": "Ketersediaan wadah sampah organik, nonorganik, dan limbah B3; label atau simbol pada wadah.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },

    # Aspek: Peralatan Kebersihan (Bobot: 5%, Skor Maks: 5)
    "B9": {
        "id": "B9",
        "kode": "B9",
        "aspek": "Peralatan Kebersihan",
        "kategori": "B. Fasilitas Kebersihan",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Peralatan Kebersihan",
        "kelompok": "peralatan_kebersihan",
        "teks": "Apakah peralatan kebersihan dalam kondisi layak dan dapat digunakan?",
        "definisi": "Peralatan kebersihan yang layak merupakan alat yang berada dalam kondisi fisik baik dan dapat menjalankan fungsi normalnya, tidak rusak sehingga menghambat atau membuat kegiatan pembersihan tidak dapat dilakukan.",
        "bukti": "Ketersediaan, kondisi fisik, fungsi, kebersihan, kesesuaian penggunaan, dan tempat penyimpanan peralatan kebersihan.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },

    # --------------------------------------------------------------------------
    # KATEGORI C: KEBUTUHAN UDARA (Total Bobot 25%)
    # --------------------------------------------------------------------------
    # Aspek: KUDR (Bobot: 10%, Skor Maks: 10)
    "C1": {
        "id": "C1",
        "kode": "C1",
        "aspek": "KUDR",
        "kategori": "C. Kebutuhan Udara",
        "topik": "Kebutuhan Udara",
        "sub_bidang": "KUDR",
        "kelompok": "kudr",
        "teks": "Apakah suhu udara di ruang kerja berada dalam rentang 23–26°C?",
        "definisi": "Penilaian terhadap kondisi temperatur udara di dalam ruang kerja untuk mengetahui kesesuaian suhu dengan ketentuan KUDR. Pengukuran dilakukan menggunakan termometer pada area aktivitas pekerja.",
        "bukti": "Hasil pengukuran suhu menggunakan termometer.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "C2": {
        "id": "C2",
        "kode": "C2",
        "aspek": "KUDR",
        "kategori": "C. Kebutuhan Udara",
        "topik": "Kebutuhan Udara",
        "sub_bidang": "KUDR",
        "kelompok": "kudr",
        "teks": "Apakah kelembapan udara di ruang kerja berada dalam rentang 40–60%?",
        "definisi": "Penilaian terhadap tingkat kelembapan relatif udara (Relative Humidity/RH) di dalam ruang kerja untuk mengetahui apakah kondisi kelembapan berada dalam rentang yang dipersyaratkan.",
        "bukti": "Hasil pengukuran menggunakan hygrometer.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },

    # Aspek: Ventilasi (Bobot: 10%, Skor Maks: 10)
    "C3": {
        "id": "C3",
        "kode": "C3",
        "aspek": "Ventilasi",
        "kategori": "C. Kebutuhan Udara",
        "topik": "Kebutuhan Udara",
        "sub_bidang": "Ventilasi",
        "kelompok": "ventilasi",
        "teks": "Apakah ventilasi berfungsi dengan baik?",
        "definisi": "Fungsi ventilasi adalah kondisi ventilasi, baik alami maupun buatan, yang bekerja dengan baik dalam menukar udara ruangan, yang ditandai dengan adanya aliran udara dan peralatan yang beroperasi normal.",
        "bukti": "Ketersediaan ventilasi alami atau mekanis, kondisi dan fungsi kipas atau exhaust fan, kelancaran aliran udara, distribusi udara, kondisi filter dan saluran udara, serta catatan pemeliharaan.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },

    # Aspek: Ruang Udara (Bobot: 5%, Skor Maks: 5)
    "C4": {
        "id": "C4",
        "kode": "C4",
        "aspek": "Ruang Udara",
        "kategori": "C. Kebutuhan Udara",
        "topik": "Kebutuhan Udara",
        "sub_bidang": "Ruang Udara",
        "kelompok": "ruang_udara",
        "teks": "Apakah setiap orang bekerja dalam ruangan mendapat ruang udara (cubic space) paling sedikit 10 m³?",
        "definisi": "Setiap pekerja memperoleh ruang udara paling sedikit 10 m³, dengan memperhitungkan tinggi ruangan sesuai ketentuan Pasal 42 Permenaker No. 5 Tahun 2018.",
        "bukti": "Luas lantai ruangan, tinggi ruangan, volume ruang udara, dan jumlah pekerja yang bekerja secara bersamaan.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },

    # --------------------------------------------------------------------------
    # KATEGORI D: TATA LAKSANA KERUMAHTANGGAAN (HOUSEKEEPING) (Total Bobot 25%)
    # --------------------------------------------------------------------------
    # Aspek: Housekeeping (Bobot: 25%, Skor Maks: 25)
    "D1": {
        "id": "D1",
        "kode": "D1",
        "aspek": "Housekeeping",
        "kategori": "D. Tata Laksana Kerumahtanggaan (Housekeeping)",
        "topik": "Tata Laksana Kerumahtanggaan",
        "sub_bidang": "Tata Laksana Kerumahtanggaan",
        "kelompok": "housekeeping",
        "teks": "Apakah terdapat pemisahan antara alat, perkakas, dan bahan yang diperlukan atau digunakan?",
        "definisi": "Penilaian terhadap kondisi penataan dan pemisahan alat, perkakas, serta bahan yang digunakan dalam kegiatan kerja berdasarkan jenis, fungsi, karakteristik, dan potensi bahayanya. Pemisahan dilakukan untuk mencegah tercampurnya bahan yang tidak kompatibel, menghindari kontaminasi, mengurangi risiko kecelakaan kerja, serta memudahkan penyimpanan, pengambilan, dan penggunaan peralatan maupun bahan.",
        "bukti": "Pengelompokan alat, perkakas, dan bahan; ketersediaan tempat penyimpanan khusus.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "D2": {
        "id": "D2",
        "kode": "D2",
        "aspek": "Housekeeping",
        "kategori": "D. Tata Laksana Kerumahtanggaan (Housekeeping)",
        "topik": "Tata Laksana Kerumahtanggaan",
        "sub_bidang": "Tata Laksana Kerumahtanggaan",
        "kelompok": "housekeeping",
        "teks": "Apakah terdapat penataan antara alat, perkakas, dan bahan yang diperlukan atau digunakan?",
        "definisi": "Penilaian terhadap kondisi penempatan dan pengorganisasian alat, perkakas, serta bahan yang diperlukan atau digunakan dalam kegiatan kerja agar tersusun secara rapi, teratur, mudah dijangkau, dan sesuai dengan fungsi serta kebutuhan pekerjaan.",
        "bukti": "Keteraturan penempatan alat, perkakas, dan bahan.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "D3": {
        "id": "D3",
        "kode": "D3",
        "aspek": "Housekeeping",
        "kategori": "D. Tata Laksana Kerumahtanggaan (Housekeeping)",
        "topik": "Tata Laksana Kerumahtanggaan",
        "sub_bidang": "Tata Laksana Kerumahtanggaan",
        "kelompok": "housekeeping",
        "teks": "Apakah terdapat aktivitas pembersihan antara alat, perkakas, dan bahan yang diperlukan atau digunakan?",
        "definisi": "Penilaian terhadap pelaksanaan kegiatan pembersihan alat, perkakas, dan bahan yang digunakan dalam kegiatan kerja untuk menghilangkan debu, kotoran, sisa bahan, minyak, tumpahan, atau kontaminan lainnya yang dapat memengaruhi kebersihan, fungsi peralatan, kualitas pekerjaan, serta kesehatan dan keselamatan pekerja.",
        "bukti": "Catatan kegiatan pembersihan, checklist rutin, dan keteraturan pembersihan fisik alat.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    },
    "D4": {
        "id": "D4",
        "kode": "D4",
        "aspek": "Housekeeping",
        "kategori": "D. Tata Laksana Kerumahtanggaan (Housekeeping)",
        "topik": "Tata Laksana Kerumahtanggaan",
        "sub_bidang": "Tata Laksana Kerumahtanggaan",
        "kelompok": "housekeeping",
        "teks": "Apakah terdapat prosedur kebersihan, penempatan dan penataan untuk alat, perkakas dan bahan dan secara berkala prosedur dikembangkan?",
        "definisi": "Prosedur mencakup tata cara pembersihan, lokasi penyimpanan, pengelompokan, penempatan berdasarkan jenis dan karakteristik, serta frekuensi pelaksanaan. Pengembangan prosedur dilakukan secara berkala berdasarkan hasil evaluasi, perubahan proses kerja, kondisi lingkungan kerja, dan potensi bahaya yang ditemukan.",
        "bukti": "Dokumen SOP atau instruksi kerja, pengaturan frekuensi dan penanggung jawab pembersihan, ketentuan penempatan dan penataan, bukti sosialisasi, checklist inspeksi, laporan evaluasi, serta riwayat revisi prosedur.",
        "tipe": "radio_3",
        "opsi": OPT_3_TINGKAT,
        "bobot_max": 2
    }
}


# ==============================================================================
# KONFIGURASI BOBOT & SKOR MAKSIMUM PER ASPEK & KATEGORI
# (Sesuai Sheet 'Ringkasan Skor')
# ==============================================================================
BOBOT_RINGKASAN_SKOR = {
    "A. Bangunan Tempat Kerja": {
        "kategori_label": "Kondisi Fisik Bangunan",
        "bobot_kategori_pct": 25,
        "aspek": {
            "halaman": {
                "nama": "Halaman",
                "soal_ids": ["A2", "A3", "A4", "A6", "A7"],
                "screening_id": "A5",
                "bobot_pct": 10,
                "skor_maks": 10,
                "target_indikator": 4
            },
            "gedung": {
                "nama": "Gedung",
                "soal_ids": ["A8", "A9", "A10", "A11", "A12", "A13", "A14", "A15", "A16", "A17", "A18", "A19"],
                "bobot_pct": 10,
                "skor_maks": 10,
                "target_indikator": 12
            },
            "bawah_tanah": {
                "nama": "Ruang Bawah Tanah",
                "soal_ids": ["A21", "A22", "A23", "A24", "A25"],
                "bobot_pct": 5,
                "skor_maks": 5,
                "target_indikator": 5
            }
        }
    },
    "B. Fasilitas Kebersihan": {
        "kategori_label": "Fasilitas Kebersihan & Sanitasi",
        "bobot_kategori_pct": 25,
        "aspek": {
            "toilet": {
                "nama": "Toilet",
                "soal_ids": ["B2", "B3", "B4"],
                "info_id": "B1",
                "bobot_pct": 10,
                "skor_maks": 10,
                "target_indikator": 3
            },
            "loker": {
                "nama": "Loker",
                "soal_ids": ["B5", "B6"],
                "bobot_pct": 5,
                "skor_maks": 5,
                "target_indikator": 2
            },
            "tempat_sampah": {
                "nama": "Tempat Sampah",
                "soal_ids": ["B7", "B8"],
                "bobot_pct": 5,
                "skor_maks": 5,
                "target_indikator": 2
            },
            "peralatan_kebersihan": {
                "nama": "Peralatan Kebersihan",
                "soal_ids": ["B9"],
                "bobot_pct": 5,
                "skor_maks": 5,
                "target_indikator": 1
            }
        }
    },
    "C. Kebutuhan Udara": {
        "kategori_label": "Kebutuhan Kualitas & Ruang Udara",
        "bobot_kategori_pct": 25,
        "aspek": {
            "kudr": {
                "nama": "KUDR",
                "soal_ids": ["C1", "C2"],
                "bobot_pct": 10,
                "skor_maks": 10,
                "target_indikator": 2
            },
            "ventilasi": {
                "nama": "Ventilasi",
                "soal_ids": ["C3"],
                "bobot_pct": 10,
                "skor_maks": 10,
                "target_indikator": 1
            },
            "ruang_udara": {
                "nama": "Ruang Udara",
                "soal_ids": ["C4"],
                "bobot_pct": 5,
                "skor_maks": 5,
                "target_indikator": 1
            }
        }
    },
    "D. Tata Laksana Kerumahtanggaan (Housekeeping)": {
        "kategori_label": "Tata Laksana Kerumahtanggaan (Housekeeping)",
        "bobot_kategori_pct": 25,
        "aspek": {
            "housekeeping": {
                "nama": "Tata Laksana Kerumahtanggaan",
                "soal_ids": ["D1", "D2", "D3", "D4"],
                "bobot_pct": 25,
                "skor_maks": 25,
                "target_indikator": 4
            }
        }
    }
}


# Metadata Istilah / Infografis Regulasi
INFOGRAFIS_DATA = {
    "A10": {
        "istilah": "Kecukupan Ruang Gerak (Minimal 2 m² per orang)",
        "regulasi": "Permenaker No. 5 Tahun 2018 Pasal 9 Ayat (2)",
        "ringkasan": "Setiap pekerja wajib memiliki ruang gerak bebas (free floor space) minimal 2 meter persegi, tidak terhalang mesin, barang, atau perabotan.",
        "poin_kunci": [
            "Mencegah resiko terjepit dan cedera ergonomi",
            "Memastikan kelancaran jalur evakuasi darurat",
            "Dihitung di luar area meja kerja utama dan mesin produksi"
        ],
        "visual_badge": "📐 Min. 2 m² / Orang"
    },
    "B2": {
        "istilah": "Standar Rasio Kebutuhan Toilet K3",
        "regulasi": "Permenaker No. 5 Tahun 2018 Lampiran IV Bidang Kebersihan",
        "ringkasan": "Rasio jumlah jamban/toilet wajib sebanding dengan total jumlah tenaga kerja pada bangunan tempat kerja.",
        "poin_kunci": [
            "1 - 15 pekerja: minimal 1 toilet",
            "16 - 30 pekerja: minimal 2 toilet",
            "31 - 45 pekerja: minimal 3 toilet",
            "46 - 60 pekerja: minimal 4 toilet",
            "61 - 80 pekerja: minimal 5 toilet",
            "81 - 100 pekerja: minimal 6 toilet",
            "> 100 pekerja: +1 toilet setiap kelipatan 40 pekerja tambahan"
        ],
        "visual_badge": "🚻 Rasio Pekerja : Jamban"
    },
    "B4": {
        "istilah": "Akses Toilet Khusus Penyandang Disabilitas",
        "regulasi": "Permenaker No. 5 Tahun 2018 Pasal 33",
        "ringkasan": "Fasilitas toilet aksesibel yang menyediakan kemudahan ruang gerak, pintu lebar, dan pegangan rambat bagi penyandang disabilitas.",
        "poin_kunci": [
            "Lebar pintu masuk memadai untuk kursi roda (min. 85 cm)",
            "Tersedia pegangan rambat (handrail) di dekat kloset dan wastafel",
            "Permukaan lantai tidak licin dan tanpa undakan berbahaya"
        ],
        "visual_badge": "♿ Akses Inklusif"
    },
    "C1": {
        "istilah": "Kenyamanan Suhu Udara Kerja (23°C – 26°C)",
        "regulasi": "Permenaker No. 5 Tahun 2018 Bagian Kedua (Faktor Fisika)",
        "ringkasan": "Suhu ruangan perkantoran dan ruang kerja tertutup disyaratkan berkisar 23°C – 26°C.",
        "poin_kunci": [
            "Mencegah resiko heat stress (kelelahan akibat panas) atau hipotermia",
            "Menjaga konsentrasi kerja dan metabolisme tubuh optimal",
            "Pengukuran dilakukan menggunakan termometer bola basah atau termohigrometer"
        ],
        "visual_badge": "🌡️ 23°C - 26°C Suhu Ideal"
    },
    "C2": {
        "istilah": "Kelembapan Relatif Udara (40% – 60%)",
        "regulasi": "Permenaker No. 5 Tahun 2018 Standar Kualitas Udara Dalam Ruang",
        "ringkasan": "Batas kelembaban udara ideal tempat kerja tertutup guna mencegah gangguan respirasi dan pertumbuhan jamur/patogen.",
        "poin_kunci": [
            "< 40%: Udara terlalu kering, memicu iritasi saluran pernapasan",
            "40% - 60%: Rentang kenyamanan fisiologis manusia optimal",
            "> 60%: Udara terlalu lembap, memicu pertumbuhan spora jamur dan bakteri"
        ],
        "visual_badge": "💧 40% - 60% Kelembapan"
    },
    "C4": {
        "istilah": "Cubic Space (Volume Udara ≥ 10 m³ per Pekerja)",
        "regulasi": "Permenaker No. 5 Tahun 2018 Pasal 10 Ayat (1)",
        "ringkasan": "Setiap ruang kerja harus menyediakan volume udara (ruang kubik) paling sedikit 10 meter kubik per orang yang bekerja di dalamnya.",
        "poin_kunci": [
            "Rumus: (Panjang x Lebar x Tinggi) / Jumlah Pekerja >= 10 m³",
            "Tinggi ruangan yang diperhitungkan maksimal 4 meter",
            "Menjamin sirkulasi udara dan kecukupan pertukaran udara segar"
        ],
        "visual_badge": "📦 Min. 10 m³ / Pekerja"
    },
    "D1": {
        "istilah": "Prinsip 5R / 5S: Pemisahan (Seiri / Ringkas)",
        "regulasi": "Permenaker No. 5 Tahun 2018 Tata Laksana Kerumahtanggaan",
        "ringkasan": "Pemisahan tegas antara barang, alat, dan bahan yang diperlukan dengan yang tidak diperlukan lagi.",
        "poin_kunci": [
            "Membuang atau memindahkan barang yang tidak relevan",
            "Mengurangi tumpukan sampah dan bahaya tersandung/kebakaran",
            "Memaksimalkan efisiensi dan keamanan ruang kerja"
        ],
        "visual_badge": "🧹 5R: Ringkas (Seiri)"
    },
    "D4": {
        "istilah": "SOP & Prosedur Kerumahtanggaan Berkelanjutan",
        "regulasi": "Permenaker No. 5 Tahun 2018 Pasal 45",
        "ringkasan": "Tersedianya Standar Operasional Prosedur tertulis mengenai pembersihan, tata letak bahan, serta peninjauan berkala.",
        "poin_kunci": [
            "Pekerja memiliki panduan baku kebersihan dan penyimpanan alat",
            "Dilakukan evaluasi dan inspeksi kebersihan berkala",
            "Membangun budaya kerja K3 yang tertib dan higienis"
        ],
        "visual_badge": "📋 SOP & Review Rutin"
    }
}


# ==============================================================================
# FUNGSI PERHITUNGAN KEBUTUHAN TOILET (PERMENAKER NO. 5/2018)
# ==============================================================================
def hitung_kebutuhan_toilet(total_pekerja: int) -> int:
    """Menghitung kebutuhan minimal jamban/toilet sesuai rasio Permenaker No. 5/2018."""
    total_pekerja = to_int(total_pekerja)
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
        return 6 + math.ceil((total_pekerja - 100) / 40)


def hitung_evaluasi_toilet_lengkap(daftar_gedung: list) -> dict:
    """Evaluasi pemenuhan standar rasio toilet mandiri per gedung dan kumulatif."""
    if not daftar_gedung:
        return {
            "total_toilet": 0,
            "total_pekerja": 0,
            "syarat_kumulatif": 0,
            "kumulatif_memenuhi": True,
            "selisih_kumulatif": 0,
            "rincian_gedung": []
        }

    total_toilet = sum(to_int(g.get("Jumlah Toilet", 0)) for g in daftar_gedung)
    total_pekerja = sum(to_int(g.get("Total Pekerja", 0)) for g in daftar_gedung)
    syarat_kumulatif = hitung_kebutuhan_toilet(total_pekerja)
    kumulatif_memenuhi = total_toilet >= syarat_kumulatif
    selisih_kumulatif = max(0, syarat_kumulatif - total_toilet)

    rincian_gedung = []
    for idx, g in enumerate(daftar_gedung):
        toilet_g = to_int(g.get("Jumlah Toilet", 0))
        pekerja_g = to_int(g.get("Total Pekerja", 0))
        syarat_m = hitung_kebutuhan_toilet(pekerja_g)
        m_memenuhi = toilet_g >= syarat_m
        selisih_m = max(0, syarat_m - toilet_g)
        rincian_gedung.append({
            "No": g.get("Nomor Gedung", idx + 1),
            "Nama Gedung": g.get("Nama Gedung", f"Gedung {idx+1}"),
            "Jenis Objek": g.get("Jenis Objek", "-"),
            "Total Pekerja": pekerja_g,
            "Pekerja Pria": to_int(g.get("Pekerja Laki-laki", 0)),
            "Pekerja Wanita": to_int(g.get("Pekerja Perempuan", 0)),
            "Toilet Ada": toilet_g,
            "Standar Mandiri": syarat_m,
            "Status Mandiri": "✅ Memenuhi" if m_memenuhi else f"⚠️ Kurang ({selisih_m} unit)",
            "Mandiri Memenuhi": m_memenuhi,
            "Defisit Mandiri": selisih_m
        })

    return {
        "total_toilet": total_toilet,
        "total_pekerja": total_pekerja,
        "syarat_kumulatif": syarat_kumulatif,
        "kumulatif_memenuhi": kumulatif_memenuhi,
        "selisih_kumulatif": selisih_kumulatif,
        "rincian_gedung": rincian_gedung
    }


def evaluasi_toilet_daftar_gedung(daftar_gedung: list) -> list:
    """Memperbarui status Q/B2 evaluasi toilet pada tiap gedung."""
    if not daftar_gedung:
        return daftar_gedung

    eval_info = hitung_evaluasi_toilet_lengkap(daftar_gedung)
    kumulatif_memenuhi = eval_info["kumulatif_memenuhi"]

    for g in daftar_gedung:
        toilet_gedung = to_int(g.get("Jumlah Toilet", 0))
        pekerja_gedung = to_int(g.get("Total Pekerja", 0))
        syarat_mandiri = hitung_kebutuhan_toilet(pekerja_gedung)
        mandiri_memenuhi = toilet_gedung >= syarat_mandiri

        if "B2_Jawaban" not in g or not g.get("B2_Jawaban"):
            if mandiri_memenuhi:
                g["B2_Jawaban"] = "Memenuhi"
                g["B2_Poin"] = 2
            elif toilet_gedung > 0:
                g["B2_Jawaban"] = "Memenuhi Sebagian"
                g["B2_Poin"] = 1
            else:
                g["B2_Jawaban"] = "Tidak Memenuhi"
                g["B2_Poin"] = 0

    return daftar_gedung


# ==============================================================================
# PERHITUNGAN SKOR RINCI PER ASPEK & KATEGORI
# (Mengikuti Struktur Tabel Sheet 'Ringkasan Skor')
# ==============================================================================
def hitung_skor_lengkap_gedung(data_gedung: dict, fasilitas_terpilih: list = None) -> dict:
    """
    Menghitung skor evaluasi K3 gedung secara terstruktur persis sesuai sheet 'Ringkasan Skor':
    - Skor per Aspek (Halaman, Gedung, Ruang Bawah Tanah, Toilet, Loker, dll.)
    - Capaian (%) per Aspek
    - Subtotal Skor per Kategori (A, B, C, D) masing-masing bobot 25%
    - Total Nilai Akhir Tempat Kerja (Maks 100)
    """
    if fasilitas_terpilih is None:
        fasilitas_terpilih = data_gedung.get("Fasilitas Terpilih", [f["id"] for f in KELOMPOK_FASILITAS if f["default_checked"]])

    rincian_tabel = []
    skor_kategori = {
        "A. Bangunan Tempat Kerja": 0.0,
        "B. Fasilitas Kebersihan": 0.0,
        "C. Kebutuhan Udara": 0.0,
        "D. Tata Laksana Kerumahtanggaan (Housekeeping)": 0.0
    }
    skor_maks_tersedia = 0.0

    for kat_nama, kat_info in BOBOT_RINGKASAN_SKOR.items():
        subtotal_kat = 0.0

        for aspek_id, aspek_info in kat_info["aspek"].items():
            aspek_aktif = aspek_id in fasilitas_terpilih
            if not aspek_aktif:
                continue

            soal_ids = aspek_info["soal_ids"]
            screening_id = aspek_info.get("screening_id")

            # Filter soal yang berlaku (contoh jika A5 = Tidak ada saluran air, A6 dan A7 N/A)
            soal_berlaku = []
            ada_saluran = True
            if screening_id and screening_id in data_gedung:
                ans_screening = str(data_gedung.get(f"{screening_id}_Jawaban", "")).lower()
                if "tidak" in ans_screening:
                    ada_saluran = False

            for q_id in soal_ids:
                q_meta = MASTER_PERTANYAAN.get(q_id, {})
                if q_meta.get("depends_on") == screening_id and not ada_saluran:
                    continue
                soal_berlaku.append(q_id)

            jml_indikator = len(soal_berlaku)
            bobot_nilai_max = jml_indikator * 2
            skor_maks_aspek = float(aspek_info["skor_maks"])
            bobot_pct = float(aspek_info["bobot_pct"])

            # Hitung raw score yang diperoleh
            raw_skor = 0
            for q_id in soal_berlaku:
                raw_skor += to_int(data_gedung.get(f"{q_id}_Poin", 0))

            if bobot_nilai_max > 0:
                capaian_pct = (raw_skor / bobot_nilai_max) * 100.0
                skor_didapat = (raw_skor / bobot_nilai_max) * skor_maks_aspek
            else:
                capaian_pct = 100.0
                skor_didapat = skor_maks_aspek

            subtotal_kat += skor_didapat
            skor_maks_tersedia += skor_maks_aspek

            # Interpretasi internal
            if capaian_pct >= 85:
                interpretasi = "Sangat Baik / Terpenuhi"
            elif capaian_pct >= 60:
                interpretasi = "Cukup / Perlu Perbaikan Minor"
            else:
                interpretasi = "Kurang / Prioritas Tindakan Korektif"

            rincian_tabel.append({
                "Kategori": kat_nama,
                "Aspek": aspek_info["nama"],
                "aspek_id": aspek_id,
                "Jumlah Indikator": jml_indikator,
                "Bobot Nilai Max": bobot_nilai_max,
                "Skor Mentah": raw_skor,
                "Bobot Persentase": f"{int(bobot_pct)}%",
                "Capaian (%)": round(capaian_pct, 1),
                "Skor Maksimum": skor_maks_aspek,
                "Skor Tercapai": round(skor_didapat, 2),
                "Interpretasi Internal": interpretasi
            })

        skor_kategori[kat_nama] = round(subtotal_kat, 2)

    total_skor_gedung = round(sum(skor_kategori.values()), 2)
    indeks_pemenuhan = round((total_skor_gedung / skor_maks_tersedia * 100), 1) if skor_maks_tersedia > 0 else 0.0

    return {
        "skor_kategori": skor_kategori,
        "total_skor": total_skor_gedung,
        "skor_maks_tersedia": round(skor_maks_tersedia, 2),
        "indeks_pemenuhan": indeks_pemenuhan,
        "rincian_tabel": rincian_tabel,
        "Skor_Topik_1": skor_kategori["A. Bangunan Tempat Kerja"],
        "Skor_Topik_2": skor_kategori["B. Fasilitas Kebersihan"],
        "Skor_Topik_3": skor_kategori["C. Kebutuhan Udara"],
        "Skor_Topik_4": skor_kategori["D. Tata Laksana Kerumahtanggaan (Housekeeping)"]
    }


# ==============================================================================
# ANALISIS EVALUASI & IDENTIFIKASI BUTIR DEFISIT / KURANG
# ==============================================================================
def analisis_evaluasi_gedung(data_gedung: dict, fasilitas_ids: list = None) -> dict:
    """Menganalisis hasil survei gedung, mencatat poin kurang (< 2) beserta rekomendasinya."""
    if not fasilitas_ids:
        fasilitas_ids = data_gedung.get("Fasilitas Terpilih", [f["id"] for f in KELOMPOK_FASILITAS if f["default_checked"]])

    skor_info = hitung_skor_lengkap_gedung(data_gedung, fasilitas_ids)
    pertanyaan_kurang = []

    for q_id, q_info in MASTER_PERTANYAAN.items():
        if q_info["kelompok"] not in fasilitas_ids:
            continue
        if q_info.get("bobot_max", 2) == 0:
            continue

        poin_raw = data_gedung.get(f"{q_id}_Poin")
        jawaban = str(data_gedung.get(f"{q_id}_Jawaban", ""))

        if poin_raw is not None and str(poin_raw).strip() != "":
            skor_angka = to_int(poin_raw, 0)
            # Kriteria kurang: skor di bawah nilai maksimal 2
            if skor_angka < 2:
                info_reg = INFOGRAFIS_DATA.get(q_id, {})
                regulasi_ref = info_reg.get("regulasi", "Permenaker No. 5 Tahun 2018 tentang K3 Lingkungan Kerja")

                if skor_angka == 1:
                    rekom = f"Tingkatkan pemenuhan aspek '{q_info['aspek']}' agar konsisten di seluruh area/shift dan dilengkapi bukti objektif yang memadai."
                else:
                    rekom = f"Segera sediakan, fungsikan, dan lakukan perbaikan pada aspek '{q_info['aspek']}' sesuai ketentuan baku K3."

                pertanyaan_kurang.append({
                    "id": q_id,
                    "topik": q_info["topik"],
                    "aspek": q_info["aspek"],
                    "sub_bidang": q_info["sub_bidang"],
                    "teks": q_info["teks"],
                    "definisi": q_info["definisi"],
                    "bukti": q_info["bukti"],
                    "jawaban": jawaban,
                    "skor": skor_angka,
                    "regulasi": regulasi_ref,
                    "rekomendasi": rekom
                })

    bidang_perlu_perbaikan = []
    for r in skor_info["rincian_tabel"]:
        if r["Capaian (%)"] < 70:
            bidang_perlu_perbaikan.append(f"{r['Aspek']} ({r['Capaian (%)']}%)")

    status_pemenuhan = "Memenuhi Standar" if skor_info["indeks_pemenuhan"] >= 75 and len(bidang_perlu_perbaikan) == 0 else "Perlu Tindakan Perbaikan"

    return {
        "status_pemenuhan": status_pemenuhan,
        "bidang_perlu_perbaikan": bidang_perlu_perbaikan,
        "indeks_pemenuhan": skor_info["indeks_pemenuhan"],
        "total_skor": skor_info["total_skor"],
        "skor_maks_tersedia": skor_info["skor_maks_tersedia"],
        "skor_info": skor_info,
        "pertanyaan_kurang": pertanyaan_kurang
    }
