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


# Pilihan jawaban standar skala bertingkat (Skor 0 - 4)
OPT_STANDAR = [
    "Tidak memenuhi / kotor / rusak",
    "1% - 25% dari jumlah keseluruhan objek memenuhi",
    "26% - 50% dari jumlah keseluruhan objek memenuhi",
    "51% - 75% dari jumlah keseluruhan objek memenuhi",
    "76% - 100% dari jumlah keseluruhan objek memenuhi"
]

# Pilihan jawaban toilet / sanitasi (Skor 0 - 4)
OPT_TOILET = [
    "Keseluruhan tidak memenuhi syarat / buruk",
    "0% - 25% keseluruhan memenuhi syarat",
    "26% - 50% keseluruhan memenuhi syarat",
    "51% - 75% keseluruhan memenuhi syarat",
    "76% - 100% keseluruhan memenuhi syarat"
]

# Pilihan jawaban 3 opsi (Skor 0 - 2)
OPT_3_TINGKAT = {
    "pemisahan": ["Tidak ada pemisahan", "Ada tapi tidak signifikan", "Ada pemisahan rapi dan menyeluruh"],
    "penataan": ["Tidak ada penataan", "Ada sebagian kecil penataan", "Ada sebagian besar penataan"],
    "pembersihan": ["Tidak ada jadwal", "Ada pembersihan tapi tidak rutin", "Ada pembersihan rutin dengan jadwal"],
    "sop": ["Tidak terdapat prosedur", "Prosedur terdapat namun belum dikembangkan secara berkala", "Prosedur terdapat dan telah dikembangkan"],
    "pelabelan": ["Tidak ada pelabelan", "Ada tapi tidak merata", "Ada dan diterapkan merata"],
    "ruang_ganti": ["Tidak ada ruang ganti", "Tidak terpisah", "Terpisah"],
    "loker": ["Tidak menyediakan", "Menyediakan tapi tidak terjamin keamanannya", "Menyediakan dan terjamin keamanannya"]
}

# ==============================================================================
# METADATA INFOGRAFIS (Dapat di-hover saat pengisian kuesioner)
# ==============================================================================
INFOGRAFIS_DATA = {
    "Q9": {
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
    "Q32": {
        "istilah": "Ruang Terbatas (Confined Space)",
        "regulasi": "Permenaker No. 5/2018 & Kepdirjen Binwasnaker No. KEP.113/DJPPK/IX/2006",
        "ringkasan": "Ruangan dengan akses masuk/keluar terbatas, ventilasi tidak memadai, serta potensi gas berbahaya, kekurangan oksigen, atau terperangkap.",
        "poin_kunci": [
            "Contoh: Basement tertutup, tangki, bunker, silo, saluran limbah",
            "Wajib memiliki Surat Izin Masuk Ruang Terbatas (Entry Permit)",
            "Pengukuran gas atmosfer berkala (O2, LEL, H2S, CO)"
        ],
        "visual_badge": "⚠️ Izin Masuk & Ventilasi Khusus"
    },
    "Q33": {
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
    "Q43": {
        "istilah": "Pemisahan Toilet Pria, Wanita & Disabilitas",
        "regulasi": "Permenaker No. 5 Tahun 2018 Pasal 33",
        "ringkasan": "Toilet harus terpisah tegas antara tenaga kerja laki-laki, perempuan, serta aksesibel ramah bagi penyandang disabilitas.",
        "poin_kunci": [
            "Memberikan privasi dan kenyamanan higienitas",
            "Dilengkapi pintu yang dapat dikunci dari dalam",
            "Tanda/simbol toilet yang jelas dan tidak membingungkan"
        ],
        "visual_badge": "♿ Akses Inklusif & Terpisah"
    },
    "Q45": {
        "istilah": "5 Fasilitas Sanitasi Esensial Toilet K3",
        "regulasi": "Permenaker No. 5 Tahun 2018 Pasal 34",
        "ringkasan": "Kelengkapan standar higienitas jamban yang wajib tersedia di lingkungan tempat kerja.",
        "poin_kunci": [
            "1. Jamban leher angsa / kloset duduk/jongkok bersih",
            "2. Alat pembilas (flush valve / gayung & kran air bersih)",
            "3. Tempat cuci tangan (wastafel) air mengalir",
            "4. Sabun pembersih tangan cair / dispenser",
            "5. Tempat sampah tertutup kedap air"
        ],
        "visual_badge": "🧼 Standar Higiene Sanitasi"
    },
    "Q54": {
        "istilah": "Tempat Pembuangan Khusus Pembalut Wanita",
        "regulasi": "Permenaker No. 5 Tahun 2018 Pasal 34 Ayat (3)",
        "ringkasan": "Penyediaan wadah sampah khusus sanitasi wanita di dalam bilik toilet perempuan guna menjaga kesehatan reproduksi & higienitas lingkungan.",
        "poin_kunci": [
            "Bahan wajib kedap air dan tidak berkarat",
            "Dilengkapi tutup rapat (pedal injak disarankan)",
            "Diberikan label jelas dan dikosongkan/dibersihkan setiap hari"
        ],
        "visual_badge": "🔴 Wadah Higiene Tertutup"
    },
    "Q55": {
        "istilah": "Iklim Kerja & Kenyamanan Termal (23°C – 26°C)",
        "regulasi": "Permenaker No. 5 Tahun 2018 Bagian Kedua (Faktor Fisika)",
        "ringkasan": "Suhu ruangan perkantoran dan ruang kerja tertutup disyaratkan berkisar 23°C – 26°C dengan selisih antar ruangan maksimal 5°C.",
        "poin_kunci": [
            "Mencegah resiko heat stress (kelelahan akibat panas) atau hipotermia",
            "Menjaga konsentrasi kerja dan metabolisme tubuh optimal",
            "Pengukuran dilakukan menggunakan termometer bola basah atau termohigrometer"
        ],
        "visual_badge": "🌡️ 23°C - 26°C Suhu Ideal"
    },
    "Q56": {
        "istilah": "Kelembaban Relatif Udara (40% – 60%)",
        "regulasi": "Permenaker No. 5 Tahun 2018 Standar Udara Dalam Ruang",
        "ringkasan": "Batas kelembaban udara ideal tempat kerja tertutup guna mencegah gangguan respirasi dan pertumbuhan mikroorganisme patogen.",
        "poin_kunci": [
            "< 40%: Udara terlalu kering, memicu iritasi tenggorokan & mata kering",
            "40% - 60%: Rentang kenyamanan fisiologis manusia optimal",
            "> 60%: Udara terlalu lembap, pemicu jamur (mold), tungau, dan spora alergen"
        ],
        "visual_badge": "💧 40% - 60% Kelembaban Relatif"
    },
    "Q57": {
        "istilah": "Kadar Oksigen Udara Kerja Aman (19,5% – 23,5%)",
        "regulasi": "Standar Ambang Batas Oksigen Lingkungan Kerja & Confined Space",
        "ringkasan": "Kadar konsentrasi gas oksigen (O2) di udara atmosfer tempat kerja wajib berada pada batas aman.",
        "poin_kunci": [
            "< 19.5%: Oksigen Kurang (Hipoksia/Asfiksia, lemas, hilang kesadaran)",
            "19.5% - 23.5%: Oksigen Aman dan Layak untuk bernapas",
            "> 23.5%: Oksigen Diperkaya (Sangat mudah terbakar & meledak secara spontan)"
        ],
        "visual_badge": "🫁 19.5% - 23.5% O₂ Normal"
    },
    "Q60": {
        "istilah": "Cubic Space (Volume Udara ≥ 10 m³ per Pekerja)",
        "regulasi": "Permenaker No. 5 Tahun 2018 Pasal 10 Ayat (1)",
        "ringkasan": "Setiap ruang kerja harus menyediakan volume udara (ruang kubik) paling sedikit 10 meter kubik per orang yang bekerja di dalamnya.",
        "poin_kunci": [
            "Rumus: (Panjang x Lebar x Tinggi) / Jumlah Pekerja >= 10 m³",
            "Tinggi ruangan yang diperhitungkan maksimal 4 meter",
            "Menjamin sirkulasi udara dan kecukupan pertukaran udara segar (ACH)"
        ],
        "visual_badge": "📦 Min. 10 m³ / Pekerja"
    },
    "Q61": {
        "istilah": "Prinsip 5R / 5S (Ringkas / Seiri)",
        "regulasi": "Permenaker No. 5 Tahun 2018 Tata Laksana Kerumahtanggaan",
        "ringkasan": "Pemisahan tegas antara barang yang diperlukan dan barang yang tidak diperlukan lagi di area kerja.",
        "poin_kunci": [
            "Membuang atau memindahkan barang yang tidak relevan",
            "Mengurangi tumpukan sampah dan bahaya tersandung/kebakaran",
            "Memaksimalkan efisiensi ruang kerja"
        ],
        "visual_badge": "🧹 5R: Ringkas (Seiri)"
    },
    "Q64": {
        "istilah": "SOP & Prosedur Kerumahtanggaan Berkelanjutan",
        "regulasi": "Permenaker No. 5 Tahun 2018 Pasal 45",
        "ringkasan": "Tersedianya Standar Operasional Prosedur tertulis mengenai pembersihan, tata letak bahan, serta peninjauan berkala.",
        "poin_kunci": [
            "Pekerja memiliki panduan baku kebersihan dan penyimpanan alat",
            "Dilakukan evaluasi dan audit kebersihan berkala",
            "Membangun budaya kerja K3 yang tertib dan higienis"
        ],
        "visual_badge": "📋 SOP & Review Rutin"
    }
}

# ==============================================================================
# DAFTAR KELOMPOK FASILITAS (Checklist pada tahap Isi Info Gedung)
# ==============================================================================
KELOMPOK_FASILITAS = [
    {
        "id": "halaman",
        "nama": "Area Halaman & Saluran Pembuangan Luar",
        "icon": "🌳",
        "deskripsi": "Kebersihan, kerapian, kerataan, drainase halaman luar, dan penutup saluran air",
        "topik": "Kondisi Fisik",
        "default_checked": True,
        "soal_ids": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]
    },
    {
        "id": "struktur_gedung",
        "nama": "Struktur Gedung, Dinding, Lantai, Langit-langit & Atap",
        "icon": "🏢",
        "deskripsi": "Kekokohan struktur gedung, kecukupan ruang gerak (2 m²), cat, kebersihan dinding/lantai/atap",
        "topik": "Kondisi Fisik",
        "default_checked": True,
        "soal_ids": ["Q7", "Q8", "Q9", "Q10", "Q11", "Q12", "Q13", "Q14", "Q15", "Q16", "Q17", "Q18", "Q19", "Q20", "Q21", "Q22", "Q23", "Q24", "Q25", "Q26"]
    },
    {
        "id": "bawah_tanah",
        "nama": "Bangunan Bawah Tanah (Basement / Confined Space)",
        "icon": "⛏️",
        "deskripsi": "Struktur bawah tanah, ventilasi, pencahayaan, saluran air, dan syarat ruang terbatas",
        "topik": "Kondisi Fisik",
        "default_checked": False,
        "soal_ids": ["Q27", "Q28", "Q29", "Q30", "Q31", "Q32"]
    },
    {
        "id": "toilet_sanitasi",
        "nama": "Toilet & Fasilitas Sanitasi",
        "icon": "🚻",
        "deskripsi": "Kecukupan rasio toilet, kebersihan, air bersih, kelengkapan sabun & wastafel, pemisahan toilet",
        "topik": "Fasilitas Kebersihan",
        "default_checked": True,
        "soal_ids": ["Q33", "Q34", "Q35", "Q36", "Q37", "Q38", "Q39", "Q40", "Q41", "Q42", "Q43", "Q44", "Q45"]
    },
    {
        "id": "sampah_pakaian",
        "nama": "Pakaian Kerja, Ruang Ganti & Tempat Sampah",
        "icon": "🗑️",
        "deskripsi": "Penyediaan pakaian kerja, ruang ganti terpisah, loker pekerja, pemilahan tempat sampah & pembalut",
        "topik": "Fasilitas Kebersihan",
        "default_checked": True,
        "soal_ids": ["Q46", "Q47", "Q48", "Q49", "Q50", "Q51", "Q52", "Q53", "Q54"]
    },
    {
        "id": "kebutuhan_udara",
        "nama": "Kebutuhan Kualitas & Ventilasi Udara Kerja",
        "icon": "💨",
        "deskripsi": "Suhu ruang (23-26°C), kelembaban (40-60%), kadar O2 (19.5-23.5%), ventilasi rutin, cubic space (10 m³)",
        "topik": "Kebutuhan Udara",
        "default_checked": True,
        "soal_ids": ["Q55", "Q56", "Q57", "Q58", "Q59", "Q60"]
    },
    {
        "id": "housekeeping",
        "nama": "Tata Laksana Kerumahtanggaan (Housekeeping / 5R)",
        "icon": "🧹",
        "deskripsi": "Pemisahan, penataan bahan/alat, jadwal pembersihan teratur, SOP kebersihan, dan pelabelan",
        "topik": "Tata Laksana Kerumahtanggaan",
        "default_checked": True,
        "soal_ids": ["Q61", "Q62", "Q63", "Q64", "Q65"]
    }
]

# ==============================================================================
# MASTER DAFTAR PERTANYAAN (Q1 - Q65)
# ==============================================================================
MASTER_PERTANYAAN = {
    # --- Topik 1: Kondisi Fisik (Halaman) ---
    "Q1": {
        "id": "Q1",
        "teks": "Apakah halaman bersih?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "halaman",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Halaman & Area Terbuka"
    },
    "Q2": {
        "id": "Q2",
        "teks": "Apakah halaman tertata rapi?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "halaman",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Halaman & Area Terbuka"
    },
    "Q3": {
        "id": "Q3",
        "teks": "Apakah halaman rata atau tidak berlubang-lubang?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "halaman",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Halaman & Area Terbuka"
    },
    "Q4": {
        "id": "Q4",
        "teks": "Apakah halaman tidak becek / tidak ada genangan air?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "halaman",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Halaman & Area Terbuka"
    },
    "Q5": {
        "id": "Q5",
        "teks": "Apakah halaman cukup luas untuk lalu lintas orang dan barang?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "halaman",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Halaman & Area Terbuka"
    },
    "Q6": {
        "id": "Q6",
        "teks": "Apakah saluran air pembuangan tertutup dengan bahan yang kuat?",
        "tipe": "radio",
        "opsi": [
            "Tidak ada saluran air pembuangan",
            "Ada, 0% - 25% saluran tertutup bahan kuat",
            "Ada, 26% - 50% saluran tertutup bahan kuat",
            "Ada, 51% - 75% saluran tertutup bahan kuat",
            "Ada, 76% - 100% saluran tertutup bahan kuat"
        ],
        "bobot_max": 4,
        "kelompok": "halaman",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Halaman & Area Terbuka"
    },

    # --- Topik 1: Kondisi Fisik Gedung ---
    "Q7": {
        "id": "Q7",
        "teks": "Apakah gedung terpelihara sehingga selalu bersih?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "struktur_gedung",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Struktur Gedung & Ruang Kerja"
    },
    "Q8": {
        "id": "Q8",
        "teks": "Apakah struktur gedung kuat dan kokoh (tidak retak/rusak berisiko)?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "struktur_gedung",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Struktur Gedung & Ruang Kerja"
    },
    "Q9": {
        "id": "Q9",
        "teks": "Apakah gedung cukup luas sehingga memberikan ruang gerak paling sedikit 2 m² per orang?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "struktur_gedung",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Struktur Gedung & Ruang Kerja",
        "has_infografis": True
    },
    "Q10": {
        "id": "Q10",
        "teks": "Apakah dinding kering / tidak lembap / tidak korosi?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "struktur_gedung",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Dinding & Langit - Langit"
    },
    "Q11": {
        "id": "Q11",
        "teks": "Apakah langit-langit kering atau tidak lembab?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "struktur_gedung",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Dinding & Langit - Langit"
    },
    "Q12": {
        "id": "Q12",
        "teks": "Apakah dinding dicat, bersih dan mudah dibersihkan?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "struktur_gedung",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Dinding & Langit - Langit"
    },
    "Q13": {
        "id": "Q13",
        "teks": "Apakah langit-langit dicat?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "struktur_gedung",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Dinding & Langit - Langit"
    },
    "Q14": {
        "id": "Q14",
        "teks": "Apakah langit-langit bersih dan mudah dibersihkan?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "struktur_gedung",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Dinding & Langit - Langit"
    },
    "Q15": {
        "id": "Q15",
        "teks": "Apakah dinding dilakukan pengecatan ulang berkala?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "struktur_gedung",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Dinding & Langit - Langit"
    },
    "Q16": {
        "id": "Q16",
        "teks": "Apakah dinding dibersihkan secara rutin?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "struktur_gedung",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Dinding & Langit - Langit"
    },
    "Q17": {
        "id": "Q17",
        "teks": "Apakah langit-langit dibersihkan secara rutin?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "struktur_gedung",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Dinding & Langit - Langit"
    },
    "Q18": {
        "id": "Q18",
        "teks": "Apakah lantai terbuat dari bahan yang keras?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "struktur_gedung",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Lantai"
    },
    "Q19": {
        "id": "Q19",
        "teks": "Apakah lantai terbuat dari bahan yang tahan air?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "struktur_gedung",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Lantai"
    },
    "Q20": {
        "id": "Q20",
        "teks": "Apakah lantai terbuat dari bahan yang tahan terhadap bahan kimia yang merusak?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "struktur_gedung",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Lantai"
    },
    "Q21": {
        "id": "Q21",
        "teks": "Apakah lantai datar dan mudah dibersihkan?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "struktur_gedung",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Lantai"
    },
    "Q22": {
        "id": "Q22",
        "teks": "Apakah lantai tidak licin?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "struktur_gedung",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Lantai"
    },
    "Q23": {
        "id": "Q23",
        "teks": "Apakah lantai dibersihkan secara teratur?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "struktur_gedung",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Lantai"
    },
    "Q24": {
        "id": "Q24",
        "teks": "Apakah keseluruhan atap mampu memberi perlindungan dari panas matahari dan hujan?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "struktur_gedung",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Atap"
    },
    "Q25": {
        "id": "Q25",
        "teks": "Apakah keseluruhan atap tidak bocor dan tidak berlubang?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "struktur_gedung",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Atap"
    },
    "Q26": {
        "id": "Q26",
        "teks": "Apakah keseluruhan atap tidak berjamur?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "struktur_gedung",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Atap"
    },

    # --- Topik 1: Bangunan Bawah Tanah ---
    "Q27": {
        "id": "Q27",
        "teks": "Apakah bangunan bawah tanah memiliki struktur yang kuat?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "bawah_tanah",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Bangunan Bawah Tanah"
    },
    "Q28": {
        "id": "Q28",
        "teks": "Apakah bangunan bawah tanah memiliki sistem ventilasi udara?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "bawah_tanah",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Bangunan Bawah Tanah"
    },
    "Q29": {
        "id": "Q29",
        "teks": "Apakah bangunan bawah tanah memiliki sumber pencahayaan yang memadai?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "bawah_tanah",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Bangunan Bawah Tanah"
    },
    "Q30": {
        "id": "Q30",
        "teks": "Apakah saluran pembuangan air bawah tanah mengalir dengan baik?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "bawah_tanah",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Bangunan Bawah Tanah"
    },
    "Q31": {
        "id": "Q31",
        "teks": "Apakah bangunan bawah tanah bersih dan terawat?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "bawah_tanah",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Bangunan Bawah Tanah"
    },
    "Q32": {
        "id": "Q32",
        "teks": "Apakah bangunan bawah tanah mengikuti syarat Ruang Terbatas (Confined Space)?",
        "tipe": "radio",
        "opsi": ["Tidak", "Ya"],
        "bobot_max": 2,
        "kelompok": "bawah_tanah",
        "topik": "Kondisi Fisik",
        "sub_bidang": "Bangunan Bawah Tanah",
        "has_infografis": True
    },

    # --- Topik 2: Fasilitas Kebersihan (Toilet & Sanitasi) ---
    "Q33": {
        "id": "Q33",
        "teks": "Kecukupan rasio jumlah toilet terhadap jumlah pekerja (dihitung otomatis)",
        "tipe": "auto_toilet",
        "bobot_max": 1,
        "kelompok": "toilet_sanitasi",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Toilet & Sanitasi",
        "has_infografis": True
    },
    "Q34": {
        "id": "Q34",
        "teks": "Apakah toilet bersih dan tidak menimbulkan bau?",
        "tipe": "radio",
        "opsi": OPT_TOILET,
        "bobot_max": 4,
        "kelompok": "toilet_sanitasi",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Toilet & Sanitasi"
    },
    "Q35": {
        "id": "Q35",
        "teks": "Apakah toilet bebas dari lalat, nyamuk, atau serangga lainnya?",
        "tipe": "radio",
        "opsi": OPT_TOILET,
        "bobot_max": 4,
        "kelompok": "toilet_sanitasi",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Toilet & Sanitasi"
    },
    "Q36": {
        "id": "Q36",
        "teks": "Apakah toilet tersedia saluran pembuangan air yang mengalir dengan lancar?",
        "tipe": "radio",
        "opsi": OPT_TOILET,
        "bobot_max": 4,
        "kelompok": "toilet_sanitasi",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Toilet & Sanitasi"
    },
    "Q37": {
        "id": "Q37",
        "teks": "Apakah toilet selalu tersedia pasokan air bersih yang cukup?",
        "tipe": "radio",
        "opsi": OPT_TOILET,
        "bobot_max": 4,
        "kelompok": "toilet_sanitasi",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Toilet & Sanitasi"
    },
    "Q38": {
        "id": "Q38",
        "teks": "Apakah bilik toilet dilengkapi pintu penutup yang dapat dikunci?",
        "tipe": "radio",
        "opsi": OPT_TOILET,
        "bobot_max": 4,
        "kelompok": "toilet_sanitasi",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Toilet & Sanitasi"
    },
    "Q39": {
        "id": "Q39",
        "teks": "Apakah toilet memiliki penerangan yang cukup?",
        "tipe": "radio",
        "opsi": OPT_TOILET,
        "bobot_max": 4,
        "kelompok": "toilet_sanitasi",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Toilet & Sanitasi"
    },
    "Q40": {
        "id": "Q40",
        "teks": "Apakah toilet memiliki sirkulasi udara / ventilasi yang baik?",
        "tipe": "radio",
        "opsi": OPT_TOILET,
        "bobot_max": 4,
        "kelompok": "toilet_sanitasi",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Toilet & Sanitasi"
    },
    "Q41": {
        "id": "Q41",
        "teks": "Apakah toilet dibersihkan setiap hari secara periodik dan tercatat?",
        "tipe": "radio",
        "opsi": OPT_TOILET,
        "bobot_max": 4,
        "kelompok": "toilet_sanitasi",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Toilet & Sanitasi"
    },
    "Q42": {
        "id": "Q42",
        "teks": "Apakah toilet dapat digunakan tanpa hambatan selama jam kerja?",
        "tipe": "radio",
        "opsi": OPT_TOILET,
        "bobot_max": 4,
        "kelompok": "toilet_sanitasi",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Toilet & Sanitasi"
    },
    "Q43": {
        "id": "Q43",
        "teks": "Apakah toilet terpisah antara laki-laki, perempuan, dan aksesibel bagi disabilitas?",
        "tipe": "radio",
        "opsi": ["Tidak terpisah", "Terpisah"],
        "bobot_max": 2,
        "kelompok": "toilet_sanitasi",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Toilet & Sanitasi",
        "has_infografis": True
    },
    "Q44": {
        "id": "Q44",
        "teks": "Apakah toilet diberikan tanda/identitas petunjuk yang jelas?",
        "tipe": "radio",
        "opsi": OPT_TOILET,
        "bobot_max": 4,
        "kelompok": "toilet_sanitasi",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Toilet & Sanitasi"
    },
    "Q45": {
        "id": "Q45",
        "teks": "Kelengkapan fasilitas sanitasi toilet meliputi:",
        "tipe": "checkbox",
        "opsi": [
            "Jamban leher angsa / kloset duduk/jongkok bersih",
            "Alat pembilas (flush valve / gayung & kran)",
            "Tempat sampah bertutup",
            "Tempat cuci tangan (wastafel) dengan air mengalir",
            "Sabun pembersih tangan"
        ],
        "bobot_max": 5,
        "kelompok": "toilet_sanitasi",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Toilet & Sanitasi",
        "has_infografis": True
    },

    # --- Topik 2: Fasilitas Kebersihan (Tempat Sampah & Pakaian) ---
    "Q46": {
        "id": "Q46",
        "teks": "Apakah Perusahaan menyediakan pakaian kerja bagi tenaga kerja?",
        "tipe": "radio",
        "opsi": ["Tidak Menyediakan", "Menyediakan sesuai aturan K3"],
        "bobot_max": 2,
        "kelompok": "sampah_pakaian",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Tempat Penyimpanan & Tempat Sampah"
    },
    "Q47": {
        "id": "Q47",
        "teks": "Apakah Perusahaan menyediakan ruang ganti yang terpisah antara laki-laki dan perempuan?",
        "tipe": "radio",
        "opsi": OPT_3_TINGKAT["ruang_ganti"],
        "bobot_max": 3,
        "kelompok": "sampah_pakaian",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Tempat Penyimpanan & Tempat Sampah"
    },
    "Q48": {
        "id": "Q48",
        "teks": "Apakah Perusahaan menyediakan tempat penyimpanan atau loker aman bagi setiap pekerja?",
        "tipe": "radio",
        "opsi": OPT_3_TINGKAT["loker"],
        "bobot_max": 3,
        "kelompok": "sampah_pakaian",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Tempat Penyimpanan & Tempat Sampah"
    },
    "Q49": {
        "id": "Q49",
        "teks": "Apakah Perusahaan menyediakan tempat sampah terpisah yang diberikan label sesuai jenis limbah?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "sampah_pakaian",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Tempat Penyimpanan & Tempat Sampah"
    },
    "Q50": {
        "id": "Q50",
        "teks": "Apakah tempat sampah terpisah diberikan pelabelan yang jelas dan mudah dipahami?",
        "tipe": "radio",
        "opsi": OPT_TOILET,
        "bobot_max": 4,
        "kelompok": "sampah_pakaian",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Tempat Penyimpanan & Tempat Sampah"
    },
    "Q51": {
        "id": "Q51",
        "teks": "Apakah tempat sampah selalu dalam keadaan tertutup rapat?",
        "tipe": "radio",
        "opsi": OPT_TOILET,
        "bobot_max": 4,
        "kelompok": "sampah_pakaian",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Tempat Penyimpanan & Tempat Sampah"
    },
    "Q52": {
        "id": "Q52",
        "teks": "Apakah tutup dan badan tempat sampah terbuat dari bahan kedap air?",
        "tipe": "radio",
        "opsi": OPT_TOILET,
        "bobot_max": 4,
        "kelompok": "sampah_pakaian",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Tempat Penyimpanan & Tempat Sampah"
    },
    "Q53": {
        "id": "Q53",
        "teks": "Apakah tempat sampah tidak menjadi sarang lalat atau binatang serangga lain?",
        "tipe": "radio",
        "opsi": [
            "Keseluruhan menjadi sarang serangga",
            "0% - 25% bebas serangga",
            "26% - 50% bebas serangga",
            "51% - 75% bebas serangga",
            "76% - 100% bebas serangga"
        ],
        "bobot_max": 4,
        "kelompok": "sampah_pakaian",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Tempat Penyimpanan & Tempat Sampah"
    },
    "Q54": {
        "id": "Q54",
        "teks": "Kelengkapan tempat pembuangan pembalut wanita di toilet perempuan meliputi:",
        "tipe": "checkbox",
        "opsi": [
            "Disediakan di dalam ruang/bilik toilet perempuan",
            "Terbuat dari bahan yang kedap air",
            "Dilengkapi dengan penutup rapat",
            "Diberikan label penanda yang jelas",
            "Dibersihkan dan dikosongkan setiap hari"
        ],
        "bobot_max": 5,
        "kelompok": "sampah_pakaian",
        "topik": "Fasilitas Kebersihan",
        "sub_bidang": "Tempat Penyimpanan & Tempat Sampah",
        "has_infografis": True
    },

    # --- Topik 3: Kebutuhan Udara ---
    "Q55": {
        "id": "Q55",
        "teks": "Apakah suhu ruangan nyaman antara 23 – 26 °C dengan selisih antar ruangan tidak melebihi 5 °C?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "kebutuhan_udara",
        "topik": "Kebutuhan Udara",
        "sub_bidang": "Sirkulasi & Kualitas Udara",
        "has_infografis": True
    },
    "Q56": {
        "id": "Q56",
        "teks": "Apakah kadar kelembaban udara ruangan berada pada rentang 40% – 60%?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "kebutuhan_udara",
        "topik": "Kebutuhan Udara",
        "sub_bidang": "Sirkulasi & Kualitas Udara",
        "has_infografis": True
    },
    "Q57": {
        "id": "Q57",
        "teks": "Apakah kadar gas oksigen dalam ruangan berada pada rentang aman 19,5% – 23,5%?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "kebutuhan_udara",
        "topik": "Kebutuhan Udara",
        "sub_bidang": "Sirkulasi & Kualitas Udara",
        "has_infografis": True
    },
    "Q58": {
        "id": "Q58",
        "teks": "Apakah terdapat sistem ventilasi udara (alami, buatan, atau kombinasi) yang memadai?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "kebutuhan_udara",
        "topik": "Kebutuhan Udara",
        "sub_bidang": "Sirkulasi & Kualitas Udara"
    },
    "Q59": {
        "id": "Q59",
        "teks": "Apakah sistem ventilasi dibersihkan secara berkala minimal 3 bulan sekali?",
        "tipe": "radio",
        "opsi": [
            "Ventilasi tidak pernah dibersihkan",
            "Ventilasi dibersihkan secara berkala min. 1 tahun sekali",
            "Ventilasi dibersihkan secara berkala min. 6 bulan sekali",
            "Ventilasi dibersihkan secara berkala min. 3 bulan sekali",
            "Ventilasi dibersihkan secara berkala min. 1 bulan sekali"
        ],
        "bobot_max": 4,
        "kelompok": "kebutuhan_udara",
        "topik": "Kebutuhan Udara",
        "sub_bidang": "Sirkulasi & Kualitas Udara"
    },
    "Q60": {
        "id": "Q60",
        "teks": "Apakah setiap pekerja dalam ruangan mendapat volume ruang udara (cubic space) minimal 10 m³?",
        "tipe": "radio",
        "opsi": OPT_STANDAR,
        "bobot_max": 4,
        "kelompok": "kebutuhan_udara",
        "topik": "Kebutuhan Udara",
        "sub_bidang": "Sirkulasi & Kualitas Udara",
        "has_infografis": True
    },

    # --- Topik 4: Tata Laksana Kerumahtanggaan (Housekeeping 5R) ---
    "Q61": {
        "id": "Q61",
        "teks": "Apakah terdapat pemisahan antara alat, perkakas, dan bahan yang diperlukan atau digunakan?",
        "tipe": "radio",
        "opsi": OPT_3_TINGKAT["pemisahan"],
        "bobot_max": 3,
        "kelompok": "housekeeping",
        "topik": "Tata Laksana Kerumahtanggaan",
        "sub_bidang": "Penataan & Housekeeping",
        "has_infografis": True
    },
    "Q62": {
        "id": "Q62",
        "teks": "Apakah terdapat penataan teratur antara alat, perkakas, dan material kerja?",
        "tipe": "radio",
        "opsi": OPT_3_TINGKAT["penataan"],
        "bobot_max": 3,
        "kelompok": "housekeeping",
        "topik": "Tata Laksana Kerumahtanggaan",
        "sub_bidang": "Penataan & Housekeeping"
    },
    "Q63": {
        "id": "Q63",
        "teks": "Apakah terdapat aktivitas pembersihan berkala teratur dengan jadwal tertulis?",
        "tipe": "radio",
        "opsi": OPT_3_TINGKAT["pembersihan"],
        "bobot_max": 3,
        "kelompok": "housekeeping",
        "topik": "Tata Laksana Kerumahtanggaan",
        "sub_bidang": "Penataan & Housekeeping"
    },
    "Q64": {
        "id": "Q64",
        "teks": "Apakah terdapat SOP kebersihan, penataan alat/bahan, dan berkala dievaluasi serta dikembangkan?",
        "tipe": "radio",
        "opsi": OPT_3_TINGKAT["sop"],
        "bobot_max": 3,
        "kelompok": "housekeeping",
        "topik": "Tata Laksana Kerumahtanggaan",
        "sub_bidang": "Penataan & Housekeeping",
        "has_infografis": True
    },
    "Q65": {
        "id": "Q65",
        "teks": "Apakah terdapat pelabelan dan marka area kerja serta penempatan alat yang jelas?",
        "tipe": "radio",
        "opsi": OPT_3_TINGKAT["pelabelan"],
        "bobot_max": 3,
        "kelompok": "housekeeping",
        "topik": "Tata Laksana Kerumahtanggaan",
        "sub_bidang": "Penataan & Housekeeping"
    }
}


# ==============================================================================
# FUNGSI UTILITAS PENILAIAN & RASIO K3
# ==============================================================================
def hitung_kebutuhan_toilet(total_pekerja: int) -> int:
    """Menghitung standar jumlah jamban/toilet berdasarkan Permenaker No. 5 Tahun 2018."""
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

def evaluasi_toilet_daftar_gedung(daftar_gedung: list) -> list:
    """Mengevaluasi kecukupan toilet per gedung dan secara kumulatif."""
    if not daftar_gedung:
        return daftar_gedung

    total_toilet = sum(to_int(g.get("Jumlah Toilet", 0)) for g in daftar_gedung)
    total_pekerja = sum(to_int(g.get("Total Pekerja", 0)) for g in daftar_gedung)
    syarat_total = hitung_kebutuhan_toilet(total_pekerja)
    kumulatif_memenuhi = total_toilet >= syarat_total

    rincian = ", ".join([
        f"{g.get('Nama Gedung', f'Gedung {idx+1}')}: {g.get('Jumlah Toilet', 0)}/{hitung_kebutuhan_toilet(to_int(g.get('Total Pekerja', 0)))}"
        for idx, g in enumerate(daftar_gedung)
    ])

    for g in daftar_gedung:
        toilet_gedung = to_int(g.get("Jumlah Toilet", 0))
        pekerja_gedung = to_int(g.get("Total Pekerja", 0))
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
            g["Q33_Jawaban"] = (
                f"{status_mandiri} mandiri ({toilet_gedung}/{syarat_mandiri}) | "
                f"Kumulatif {status_kumulatif} ({total_toilet}/{syarat_total}) | "
                f"Rincian ({rincian})"
            )
            g["Q33_Poin"] = 1 if kumulatif_memenuhi else 0

    return daftar_gedung

def hitung_evaluasi_toilet_lengkap(daftar_gedung: list) -> dict:
    """
    Menghitung evaluasi pemenuhan standar toilet K3 Permenaker No. 5/2018
    secara komprehensif: pemenuhan mandiri per gedung dan kumulatif seluruh fasilitas.
    """
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

def get_standar_target_bidang(fasilitas_ids: list) -> dict:
    """
    Menghitung target ambang batas skor minimal pemenuhan standar K3
    secara dinamis berdasarkan kelompok fasilitas yang ada/dipilih.
    """
    punya_halaman = "halaman" in fasilitas_ids
    punya_bawah_tanah = "bawah_tanah" in fasilitas_ids
    punya_toilet = "toilet_sanitasi" in fasilitas_ids
    punya_sampah = "sampah_pakaian" in fasilitas_ids
    punya_udara = "kebutuhan_udara" in fasilitas_ids
    punya_housekeeping = "housekeeping" in fasilitas_ids

    # Hitung target Kondisi Fisik
    skor_fisik = 0
    if punya_halaman:
        skor_fisik += 20  # Q1 - Q6
    skor_fisik += 70      # Struktur umum Q7 - Q26
    if punya_bawah_tanah:
        skor_fisik += 20  # Q27 - Q32

    # Target Fasilitas Kebersihan
    skor_kebersihan = 0
    if punya_toilet:
        skor_kebersihan += 35
    if punya_sampah:
        skor_kebersihan += 20

    targets = {}
    if punya_halaman or punya_bawah_tanah or "struktur_gedung" in fasilitas_ids:
        targets["Kondisi Fisik"] = int(skor_fisik * 0.70)  # Ambang batas 70% standar
    if punya_toilet or punya_sampah:
        targets["Fasilitas Kebersihan"] = int(skor_kebersihan * 0.70)
    if punya_udara:
        targets["Kebutuhan Udara"] = 14  # dari total 20 poin
    if punya_housekeeping:
        targets["Tata Laksana Kerumahtanggaan"] = 10  # dari total 15 poin

    return targets

def analisis_evaluasi_gedung(data_gedung: dict, fasilitas_ids: list = None) -> dict:
    """
    Menganalisis skor aktual gedung, membandingkan dengan standar,
    dan mengidentifikasi butir pertanyaan yang bernilai di bawah standar.
    """
    if not fasilitas_ids:
        fasilitas_ids = data_gedung.get("Fasilitas Terpilih", [])
    if not fasilitas_ids:
        # Default fasilitas inti dan deteksi dari data pertanyaan yang ada
        fasilitas_ids = ["struktur_gedung", "toilet_sanitasi", "sampah_pakaian", "kebutuhan_udara", "housekeeping"]
        if any(f"Q{i}_Poin" in data_gedung for i in range(1, 7)):
            fasilitas_ids.append("halaman")
        if any(f"Q{i}_Poin" in data_gedung for i in range(27, 33)):
            fasilitas_ids.append("bawah_tanah")

    skor_aktual = {
        "Kondisi Fisik": to_int(data_gedung.get("Skor_Topik_1", 0)),
        "Fasilitas Kebersihan": to_int(data_gedung.get("Skor_Topik_2", 0)),
        "Kebutuhan Udara": to_int(data_gedung.get("Skor_Topik_3", 0)),
        "Tata Laksana Kerumahtanggaan": to_int(data_gedung.get("Skor_Topik_4", 0))
    }

    target_standar = get_standar_target_bidang(fasilitas_ids)
    bidang_perlu_perbaikan = []

    for bidang, target in target_standar.items():
        aktual = skor_aktual.get(bidang, 0)
        if aktual < target:
            bidang_perlu_perbaikan.append(f"{bidang} ({aktual}/{target} Poin)")

    # Analisis detail butir pertanyaan kurang
    pertanyaan_kurang = []
    SOALAN_3_PILIHAN = {"Q47", "Q48", "Q61", "Q62", "Q63", "Q64", "Q65"}
    SOALAN_2_PILIHAN = {"Q32", "Q43", "Q46"}
    SOALAN_CHECKBOX = {"Q45", "Q54"}

    for q_id, q_info in MASTER_PERTANYAAN.items():
        if q_info["kelompok"] not in fasilitas_ids:
            continue

        poin = data_gedung.get(f"{q_id}_Poin")
        jawaban = str(data_gedung.get(f"{q_id}_Jawaban", ""))

        if "N/A" in jawaban or "Tidak ada" in jawaban:
            continue

        if poin is not None and str(poin).strip() != "":
            try:
                skor_angka = int(float(str(poin).strip()))
            except Exception:
                continue

            kurang = False

            if q_id == "Q33":
                if skor_angka == 0:
                    kurang = True
            elif q_id in SOALAN_3_PILIHAN:
                if skor_angka < 2:
                    kurang = True
            elif q_id in SOALAN_2_PILIHAN:
                if skor_angka < 1:
                    kurang = True
            elif q_id in SOALAN_CHECKBOX:
                if skor_angka < 4:
                    kurang = True
            else:
                if skor_angka <= 2:
                    kurang = True

            if kurang:
                info_reg = INFOGRAFIS_DATA.get(q_id, {})
                regulasi_ref = info_reg.get("regulasi", "Permenaker No. 5 Tahun 2018 tentang K3 Lingkungan Kerja")
                istilah_kunci = info_reg.get("istilah", q_info["sub_bidang"])
                poin_standar = info_reg.get("poin_kunci", [])

                rekomendasi_teks = f"Perlu peningkatan pada aspek '{q_info['sub_bidang']}' agar memenuhi standar K3."
                if poin_standar:
                    rekomendasi_teks += f" Rekomendasi: {poin_standar[0]}."

                pertanyaan_kurang.append({
                    "id": q_id,
                    "topik": q_info["topik"],
                    "sub_bidang": q_info["sub_bidang"],
                    "istilah": istilah_kunci,
                    "regulasi": regulasi_ref,
                    "teks": q_info["teks"],
                    "jawaban": jawaban,
                    "skor": skor_angka,
                    "rekomendasi": rekomendasi_teks
                })

    status_pemenuhan = "Memenuhi Standar" if not bidang_perlu_perbaikan else "Perlu Tindakan Perbaikan"

    return {
        "status_pemenuhan": status_pemenuhan,
        "bidang_perlu_perbaikan": bidang_perlu_perbaikan,
        "skor_aktual": skor_aktual,
        "target_standar": target_standar,
        "pertanyaan_kurang": pertanyaan_kurang
    }
