import math
import re

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
# PILIHAN JAWABAN: HANYA IYA DAN TIDAK (SKOR 1 DAN 0)
# ==============================================================================
OPT_IYA_TIDAK = ["Iya", "Tidak"]
OPT_YA_TIDAK = OPT_IYA_TIDAK
OPT_3_TINGKAT = OPT_IYA_TIDAK

NILAI_OPSI = {
    "Iya": 1,
    "Ya": 1,
    "Tidak": 0
}

# Daftar pertanyaan khusus jika ada pekerja penyandang disabilitas
PERTANYAAN_DISABILITAS = {"GD2.4", "TL7.14", "TL7.15", "TL7.16"}

# Daftar pertanyaan berkebalikan (skor 1 bila dijawab "Tidak", skor 0 bila "Iya")
PERTANYAAN_TERBALIK = {"AT5.2", "AT5.3", "SP9.5"}


# ==============================================================================
# DAFTAR KELOMPOK FASILITAS (Checklist pada tahap Isi Info Gedung)
# Masih sama seperti sebelumnya
# ==============================================================================
KELOMPOK_FASILITAS = [
    {
        "id": "halaman",
        "kode_kategori": "HL1",
        "aspek": "Halaman",
        "kategori": "Bangunan Tempat Kerja – Halaman",
        "nama": "Area Halaman & Saluran Pembuangan Luar",
        "icon": "🌳",
        "deskripsi": "Kebersihan, kerapian, kerataan, drainase halaman luar, dan penutup saluran air",
        "topik": "Kondisi Fisik",
        "default_checked": True,
        "soal_ids": ["HL1.1", "HL1.2", "HL1.3", "HL1.4", "HL1.5", "HL1.6", "HL1.7", "HL1.8", "HL1.9"]
    },
    {
        "id": "struktur_gedung",
        "kode_kategori": "GD2, DL3, LT4, AT5",
        "aspek": "Struktur Gedung, Dinding, Lantai, Langit-langit & Atap",
        "kategori": "Bangunan Tempat Kerja – Gedung",
        "nama": "Struktur Gedung, Dinding, Lantai, Langit-langit & Atap",
        "icon": "🏢",
        "deskripsi": "Kekokohan struktur gedung, kecukupan ruang gerak (2 m²), cat, kebersihan dinding/lantai/atap, dan ramp disabilitas",
        "topik": "Kondisi Fisik",
        "default_checked": True,
        "soal_ids": [
            "GD2.1", "GD2.2", "GD2.3",
            "DL3.1", "DL3.2", "DL3.3", "DL3.4", "DL3.5", "DL3.6", "DL3.7", "DL3.8",
            "LT4.1", "LT4.2", "LT4.3", "LT4.4", "LT4.5", "LT4.6",
            "AT5.1", "AT5.2", "AT5.3",
            "GD2.4"
        ]
    },
    {
        "id": "bawah_tanah",
        "kode_kategori": "BT6",
        "aspek": "Bangunan Bawah Tanah",
        "kategori": "Bangunan Tempat Kerja – Bangunan Bawah Tanah",
        "nama": "Bangunan Bawah Tanah (Basement / Confined Space)",
        "icon": "⛏️",
        "deskripsi": "Struktur bawah tanah, ventilasi, pencahayaan, saluran air, dan syarat ruang terbatas",
        "topik": "Kondisi Fisik",
        "default_checked": False,
        "soal_ids": ["BT6.1", "BT6.2", "BT6.3", "BT6.4", "BT6.5", "BT6.6"]
    },
    {
        "id": "toilet_sanitasi",
        "kode_kategori": "TL7",
        "aspek": "Toilet & Fasilitas Sanitasi",
        "kategori": "Fasilitas Kebersihan – Toilet",
        "nama": "Toilet & Fasilitas Sanitasi",
        "icon": "🚻",
        "deskripsi": "Kecukupan rasio toilet, kebersihan, air bersih, kelengkapan sabun & wastafel, pemisahan toilet & akses disabilitas",
        "topik": "Fasilitas Kebersihan",
        "default_checked": True,
        "soal_ids": [
            "TL7.1", "TL7.2", "TL7.3", "TL7.4", "TL7.5", "TL7.6", "TL7.7",
            "TL7.8", "TL7.9", "TL7.10", "TL7.11", "TL7.12", "TL7.13",
            "TL7.14", "TL7.15", "TL7.16"
        ]
    },
    {
        "id": "sampah_pakaian",
        "kode_kategori": "FK8, SP9",
        "aspek": "Pakaian Kerja, Loker & Tempat Sampah",
        "kategori": "Fasilitas Kebersihan – Pakaian Kerja, Loker & Tempat Sampah",
        "nama": "Pakaian Kerja, Ruang Ganti & Tempat Sampah",
        "icon": "🗑️",
        "deskripsi": "Penyediaan pakaian kerja, ruang ganti terpisah, loker pekerja, pemilahan tempat sampah & pembalut",
        "topik": "Fasilitas Kebersihan",
        "default_checked": True,
        "soal_ids": ["FK8.1", "FK8.2", "SP9.1", "SP9.2", "SP9.3", "SP9.4", "SP9.5", "SP9.6"]
    },
    {
        "id": "kebutuhan_udara",
        "kode_kategori": "KU10",
        "aspek": "Kebutuhan Udara",
        "kategori": "Kebutuhan Udara",
        "nama": "Kebutuhan Kualitas & Ventilasi Udara Kerja",
        "icon": "💨",
        "deskripsi": "Suhu ruang (23-26°C), kelembaban (40-60%), kadar O2 (19.5-23.5%), ventilasi rutin, cubic space (10 m³)",
        "topik": "Kebutuhan Udara",
        "default_checked": True,
        "soal_ids": ["KU10.1", "KU10.2", "KU10.3", "KU10.4", "KU10.5", "KU10.6"]
    },
    {
        "id": "housekeeping",
        "kode_kategori": "KR11",
        "aspek": "Tata Laksana Kerumahtanggaan",
        "kategori": "Tata Laksana Kerumahtanggaan",
        "nama": "Tata Laksana Kerumahtanggaan (Housekeeping / 5R)",
        "icon": "🧹",
        "deskripsi": "Pemisahan, penataan bahan/alat, jadwal pembersihan teratur, SOP kebersihan, dan pelabelan",
        "topik": "Tata Laksana Kerumahtanggaan",
        "default_checked": True,
        "soal_ids": ["KR11.1", "KR11.2", "KR11.3", "KR11.4", "KR11.5"]
    }
]


def normalize_fasilitas_ids(fasilitas_ids: list) -> list:
    """Menjaga kompatibilitas ID fasilitas lama maupun baru."""
    if not fasilitas_ids:
        return [f["id"] for f in KELOMPOK_FASILITAS if f["default_checked"]]
    alias_map = {
        "gedung": "struktur_gedung",
        "toilet": "toilet_sanitasi",
        "loker": "sampah_pakaian",
        "tempat_sampah": "sampah_pakaian",
        "peralatan_kebersihan": "sampah_pakaian",
        "kudr": "kebutuhan_udara",
        "ventilasi": "kebutuhan_udara",
        "ruang_udara": "kebutuhan_udara"
    }
    valid_ids = {f["id"] for f in KELOMPOK_FASILITAS}
    normalized = []
    for fid in fasilitas_ids:
        mapped = alias_map.get(fid, fid)
        if mapped in valid_ids and mapped not in normalized:
            normalized.append(mapped)
    return normalized if normalized else [f["id"] for f in KELOMPOK_FASILITAS if f["default_checked"]]


# ==============================================================================
# MASTER DAFTAR PERTANYAAN — SHEET 'MATRIKS PENILAIAN (2)'
# Kolom A: kode_kategori
# Kolom B: kategori
# Kolom C: id / kode_dimensi
# Kolom D: teks (Aspek Penilaian / pertanyaan)
# Kolom E: panduan (Digunakan untuk infografis pop up ketika dihover)
# ==============================================================================
def _clean_panduan(raw_text: str) -> tuple[str, str]:
    """Memisahkan teks panduan utama dan rujukan regulasi (Dasar: ...) dari Kolom E."""
    lines = [line.strip() for line in raw_text.strip().splitlines() if line.strip()]
    cleaned_lines = []
    regulasi = "Permenaker No. 5 Tahun 2018 tentang K3 Lingkungan Kerja"
    for line in lines:
        if line.lower().startswith("lihat rincian butir pada sheet"):
            continue
        m = re.search(r"\(Dasar:\s*(.+?)\)", line, flags=re.IGNORECASE)
        if m:
            regulasi = m.group(1).strip()
            line_wo_dasar = re.sub(r"\(Dasar:\s*.+?\)", "", line, flags=re.IGNORECASE).strip()
            if line_wo_dasar:
                cleaned_lines.append(line_wo_dasar)
        else:
            cleaned_lines.append(line)
    panduan_bersih = " ".join(cleaned_lines).strip()
    return panduan_bersih, regulasi


_RAW_MATRIKS_2 = [
    # --- HL1: Bangunan Tempat Kerja – Halaman ---
    ("HL1", "Bangunan Tempat Kerja – Halaman", "HL1.1", "Apakah di tempat kerja ada halaman?",
     "Termasuk halaman adalah area untuk lahan parkir, taman, lapangan, jalan akses.",
     "halaman", "Kondisi Fisik"),
    ("HL1", "Bangunan Tempat Kerja – Halaman", "HL1.2", "Apakah halaman bersih?",
     "Halaman bersih yaitu halaman yang tidak terdapat sampah, kotoran, atau barang/material berserakan.",
     "halaman", "Kondisi Fisik"),
    ("HL1", "Bangunan Tempat Kerja – Halaman", "HL1.3", "Apakah halaman tertata rapi?",
     "Halaman tertata rapi yaitu barang, material, kendaraan, dan peralatan di halaman diletakkan pada tempat/area yang telah ditentukan, tidak menghalangi jalur orang maupun kendaraan, serta taman/tanaman (jika ada) terpelihara.\n(Dasar: Permenaker 5/2018 Pasal 27 ayat (1) huruf a)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "halaman", "Kondisi Fisik"),
    ("HL1", "Bangunan Tempat Kerja – Halaman", "HL1.4", "Apakah halaman rata?",
     "Halaman rata yaitu permukaan halaman (area parkir, lapangan, jalan akses) tidak bergelombang, tidak berlubang, tidak retak atau amblas, dan tidak terdapat perbedaan ketinggian yang dapat membuat orang tersandung atau kendaraan terguncang.\n(Dasar: Permenaker 5/2018 Pasal 27 ayat (1) huruf a)",
     "halaman", "Kondisi Fisik"),
    ("HL1", "Bangunan Tempat Kerja – Halaman", "HL1.5", "Apakah halaman tidak becek?",
     "Halaman tidak becek yaitu permukaan halaman tidak berlumpur dan tidak terdapat genangan air atau tanah basah yang menetap, termasuk setelah hujan reda.\n(Dasar: Permenaker 5/2018 Pasal 27 ayat (1) huruf a)",
     "halaman", "Kondisi Fisik"),
    ("HL1", "Bangunan Tempat Kerja – Halaman", "HL1.6", "Apakah cukup luas untuk akses lalu lintas orang dan barang?",
     "Halaman cukup luas untuk lalu lintas orang dan barang yaitu jalur pejalan kaki dan jalur kendaraan/pengangkut barang memiliki lebar yang memadai sehingga orang dan barang dapat bergerak tanpa saling mengganggu, bersinggungan, atau terhambat.\n(Dasar: Permenaker 5/2018 Pasal 27 ayat (1) huruf b)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "halaman", "Kondisi Fisik"),
    ("HL1", "Bangunan Tempat Kerja – Halaman", "HL1.7", "Apakah terdapat saluran air pembuangan?",
     "Saluran air pembuangan yaitu parit/drainase/selokan di halaman yang berfungsi mengalirkan air hujan dan air buangan ke luar area kerja. Bila halaman tidak memiliki saluran sama sekali, beri N/A pada dimensi HL1.8 dan HL1.9 dan jelaskan di kolom komentar.\n(Dasar: Permenaker 5/2018 Pasal 27 ayat (2))",
     "halaman", "Kondisi Fisik"),
    ("HL1", "Bangunan Tempat Kerja – Halaman", "HL1.8", "Apakah saluran air tertutup dengan bahan yang kuat?",
     "Saluran air tertutup dengan bahan yang kuat yaitu seluruh ruas saluran air di halaman ditutup (plat beton, grill/besi, atau penutup sejenis) dengan bahan yang mampu menahan beban orang dan kendaraan yang melintas. Beri N/A bila tidak ada saluran.\n(Dasar: Permenaker 5/2018 Pasal 27 ayat (2))\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "halaman", "Kondisi Fisik"),
    ("HL1", "Bangunan Tempat Kerja – Halaman", "HL1.9", "Apakah saluran air tidak tergenang?",
     "Saluran air tidak tergenang yaitu air buangan mengalir lancar menuju pembuangan akhir dan tidak ada air yang tertahan di dalam saluran maupun meluap ke halaman. Beri N/A bila tidak ada saluran.\n(Dasar: Permenaker 5/2018 Pasal 27 ayat (2))\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "halaman", "Kondisi Fisik"),

    # --- GD2: Bangunan Tempat Kerja – Gedung ---
    ("GD2", "Bangunan Tempat Kerja – Gedung", "GD2.1", "Apakah Gedung terpelihara dan bersih?",
     "Gedung terpelihara dan bersih yaitu bangunan dirawat secara berkala dengan tersedianya jadwal pemeliharaan sehingga tidak ada kerusakan yang dibiarkan, serta bagian dalam dan luar gedung bebas dari sampah, debu, kotoran, dan hama.\n(Dasar: Permenaker 5/2018 Pasal 28 ayat (2) huruf a)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "struktur_gedung", "Kondisi Fisik"),
    ("GD2", "Bangunan Tempat Kerja – Gedung", "GD2.2", "Apakah struktur Gedung kuat dan kokoh?",
     "Struktur gedung kuat dan kokoh yaitu elemen struktur (fondasi, kolom, balok, pelat lantai, dan rangka atap) tidak menunjukkan retak struktural, deformasi, atau ketidakstabilan yang membahayakan pekerja. Bahan bangunan bisa berupa beton, kayu, besi atau bahan lain yang lazim digunakan untuk struktur bangunan.\n(Dasar: Permenaker 5/2018 Pasal 28 ayat (2) huruf b)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "struktur_gedung", "Kondisi Fisik"),
    ("GD2", "Bangunan Tempat Kerja – Gedung", "GD2.3", "Apakah Gedung cukup luas sehingga memberikan ruang Gerak paling sedikit 2 m2 per orang?",
     "Gedung cukup luas (area kerja) yaitu ruang gerak setiap pekerja paling sedikit 2 m². Cara menilai: luas lantai kerja yang dapat digunakan untuk bergerak (m²) dibagi jumlah pekerja terbanyak di ruang/gedung tersebut pada satu waktu kerja; hasil ≥ 2 m² per orang berarti memenuhi. Perlu dihitung luas lantai dibagi jumlah orang atau pekerja.\n(Dasar: Permenaker 5/2018 Pasal 28 ayat (2) huruf c)",
     "struktur_gedung", "Kondisi Fisik"),

    # --- DL3: Bangunan Tempat Kerja – Gedung: Dinding dan Langit-langit ---
    ("DL3", "Bangunan Tempat Kerja – Gedung: Dinding dan Langit-langit", "DL3.1", "Apakah dinding kering/tidak lembab/tidak korosi/keropos/berayap?",
     "Dinding kering/tidak lembab/tidak korosi yaitu permukaan dinding tidak basah, tidak merembes, tidak berjamur atau berlumut, dan bagian logamnya tidak berkarat.\n(Dasar: Permenaker 5/2018 Pasal 29 huruf a)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "struktur_gedung", "Kondisi Fisik"),
    ("DL3", "Bangunan Tempat Kerja – Gedung: Dinding dan Langit-langit", "DL3.2", "Apakah langit-langit kering atau tidak lembab?",
     "Langit-langit kering atau tidak lembab yaitu plafon/langit-langit tidak basah, tidak merembes, dan tidak berjamur.\n(Dasar: Permenaker 5/2018 Pasal 29 huruf a)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "struktur_gedung", "Kondisi Fisik"),
    ("DL3", "Bangunan Tempat Kerja – Gedung: Dinding dan Langit-langit", "DL3.3", "Apakah dinding dicat, dan atau mudah dibersihkan?",
     "Dinding dicat, dan atau mudah dibersihkan yaitu dinding dilapisi cat (atau lapisan lain seperti keramik) pada permukaan yang halus dan tidak berpori sehingga mudah dilap atau dicuci, serta dalam keadaan bersih.\n(Dasar: Permenaker 5/2018 Pasal 29 huruf b)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "struktur_gedung", "Kondisi Fisik"),
    ("DL3", "Bangunan Tempat Kerja – Gedung: Dinding dan Langit-langit", "DL3.4", "Apakah langit-langit dicat dan atau mudah dibersihkan?",
     "Langit-langit dicat dan atau mudah dibersihkan yaitu langit-langit dilapisi cat (atau lapisan lain) pada permukaan yang halus dan tidak berpori sehingga mudah dibersihkan, serta dalam keadaan bersih.\n(Dasar: Permenaker 5/2018 Pasal 29 huruf b)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "struktur_gedung", "Kondisi Fisik"),
    ("DL3", "Bangunan Tempat Kerja – Gedung: Dinding dan Langit-langit", "DL3.5", "Apakah dinding dilakukan pengecatan ulang?",
     "Dinding dilakukan pengecatan ulang yaitu dinding dicat ulang paling sedikit 5 (lima) tahun sekali. Bukti: catatan/dokumen pemeliharaan atau keterangan penanggung jawab gedung tentang tahun pengecatan terakhir, serta kondisi cat saat survei.\n(Dasar: Permenaker 5/2018 Pasal 29 huruf c)",
     "struktur_gedung", "Kondisi Fisik"),
    ("DL3", "Bangunan Tempat Kerja – Gedung: Dinding dan Langit-langit", "DL3.6", "Apakah langit-langit dilakukan pengecatan ulang?",
     "Langit-langit dilakukan pengecatan ulang yaitu langit-langit dicat ulang paling sedikit 5 (lima) tahun sekali. Bukti: catatan/dokumen pemeliharaan atau keterangan penanggung jawab gedung tentang tahun pengecatan terakhir, serta kondisi cat saat survei.\n(Dasar: Permenaker 5/2018 Pasal 29 huruf c)",
     "struktur_gedung", "Kondisi Fisik"),
    ("DL3", "Bangunan Tempat Kerja – Gedung: Dinding dan Langit-langit", "DL3.7", "Apakah dinding dibersihkan secara rutin dan terjadwal?",
     "Dinding dibersihkan secara rutin yaitu dinding dibersihkan paling sedikit 1 (satu) kali setahun.\n(Dasar: Permenaker 5/2018 Pasal 29 huruf d)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "struktur_gedung", "Kondisi Fisik"),
    ("DL3", "Bangunan Tempat Kerja – Gedung: Dinding dan Langit-langit", "DL3.8", "Apakah langit-langit dibersihkan secara rutin dan terjadwal?",
     "Langit-langit dibersihkan secara rutin yaitu langit-langit dibersihkan paling sedikit 1 (satu) kali setahun.\n(Dasar: Permenaker 5/2018 Pasal 29 huruf d)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "struktur_gedung", "Kondisi Fisik"),

    # --- LT4: Bangunan Tempat Kerja – Gedung: Lantai ---
    ("LT4", "Bangunan Tempat Kerja – Gedung: Lantai", "LT4.1", "Apakah lantai terbuat dari bahan yang keras?",
     "Lantai terbuat dari bahan yang keras yaitu lantai berbahan padat dan kuat seperti beton, keramik, granit, epoksi, vinil atau paving, bukan tanah, pasir, atau papan lapuk, serta tidak retak, pecah, atau aus hingga lapisan dasar terlihat.\n(Dasar: Permenaker 5/2018 Pasal 30 huruf a)",
     "struktur_gedung", "Kondisi Fisik"),
    ("LT4", "Bangunan Tempat Kerja – Gedung: Lantai", "LT4.2", "Apakah lantai terbuat dari bahan yang tahan air?",
     "Lantai terbuat dari bahan yang tahan air yaitu bahan lantai tidak menyerap air dan tidak rusak (menggelembung, melapuk, mengelupas) bila terkena air atau dibersihkan dengan air.\n(Dasar: Permenaker 5/2018 Pasal 30 huruf a)",
     "struktur_gedung", "Kondisi Fisik"),
    ("LT4", "Bangunan Tempat Kerja – Gedung: Lantai", "LT4.3", "Apakah lantai terbuat dari bahan yang tahan dari bahan kimia yang merusak?",
     "Lantai tahan dari bahan kimia yang merusak yaitu lantai area kerja tidak rusak, berlubang, korosi, atau mengelupas apabila terkena tumpahan atau paparan bahan kimia.\n(Dasar: Permenaker 5/2018 Pasal 30 huruf a)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "struktur_gedung", "Kondisi Fisik"),
    ("LT4", "Bangunan Tempat Kerja – Gedung: Lantai", "LT4.4", "Apakah lantai datar dan mudah dibersihkan?",
     "Lantai datar dan mudah dibersihkan yaitu permukaan lantai rata (tidak bergelombang atau berlubang) dan halus sehingga mudah disapu atau dipel.\n(Dasar: Permenaker 5/2018 Pasal 30 huruf b)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "struktur_gedung", "Kondisi Fisik"),
    ("LT4", "Bangunan Tempat Kerja – Gedung: Lantai", "LT4.5", "Apakah lantai tidak licin?",
     "Lantai tidak licin yaitu permukaan lantai tidak menyebabkan orang tergelincir, baik karena bahan/teksturnya maupun karena air, minyak, atau tumpahan di atasnya.\n(Dasar: Permenaker 5/2018 Pasal 30 huruf b)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "struktur_gedung", "Kondisi Fisik"),
    ("LT4", "Bangunan Tempat Kerja – Gedung: Lantai", "LT4.6", "Apakah lantai dibersihkan secara teratur?",
     "Lantai dibersihkan secara teratur yaitu lantai dibersihkan sesuai jadwal yang ditetapkan (disapu/dipel/divakum) dan tumpahan atau kotoran segera dibersihkan, termasuk karpet yang digunakan untuk melapisi lantai apabila ada.\n(Dasar: Permenaker 5/2018 Pasal 30 huruf c)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "struktur_gedung", "Kondisi Fisik"),

    # --- AT5: Bangunan Tempat Kerja – Gedung: Atap ---
    ("AT5", "Bangunan Tempat Kerja – Gedung: Atap", "AT5.1", "Apakah keseluruhan atap mampu memberi perlindungan dari panas matahari dan hujan?",
     "Atap berupa beton, genteng, logam, PVC atau material lain yang dapat memberikan perlindungan dari panas matahari dan hujan pada seluruh area kerja dan jalur yang digunakan pekerja.\n(Dasar: Permenaker 5/2018 Pasal 31 huruf a)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "struktur_gedung", "Kondisi Fisik"),
    ("AT5", "Bangunan Tempat Kerja – Gedung: Atap", "AT5.2", "Apakah terdapat atap yang bocor?",
     "Atap bocor yaitu atap yang meneteskan atau merembeskan air dan terdapat lubang, retak, atau bagian yang patah/bergeser. (Catatan: Pilih 'Tidak' jika atap tidak bocor/memenuhi syarat).\n(Dasar: Permenaker 5/2018 Pasal 31 huruf b)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "struktur_gedung", "Kondisi Fisik"),
    ("AT5", "Bangunan Tempat Kerja – Gedung: Atap", "AT5.3", "Apakah terdapat atap yang berjamur?",
     "Atap berjamur yaitu bagian atap/langit-langit yang ditumbuhi jamur atau lumut. (Catatan: Pilih 'Tidak' jika atap bebas jamur/memenuhi syarat).\n(Dasar: Permenaker 5/2018 Pasal 31 huruf b)",
     "struktur_gedung", "Kondisi Fisik"),

    # --- GD2.4: Khusus Disabilitas pada Gedung ---
    ("GD2", "Bangunan Tempat Kerja – Gedung", "GD2.4", "Apakah tersedia jalur landai (ramp) pada area yang memiliki perbedaan ketinggian untuk memudahkan akses pengguna kursi roda?",
     "Jalur landai (ramp) tersedia yaitu pada setiap perbedaan ketinggian lantai/permukaan yang dilalui pekerja dan tamu (tangga masuk gedung, teras, selasar, undakan antarruang, jalur dari area parkir ke gedung) terdapat jalur miring yang dapat dilalui pengguna kursi roda secara mandiri, aman, dan nyaman, atau tersedia alternatif setara (mis. lift). Isi N/A bila tidak ada perbedaan ketinggian pada jalur pekerja.\n(Dasar: Permen PUPR No. 14/PRT/M/2017 tentang Persyaratan Kemudahan Bangunan Gedung; Permenaker 5/2018 Pasal 35 ayat (2) huruf d dan e tentang akses mudah dilalui bagi pengguna kursi roda)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "struktur_gedung", "Kondisi Fisik"),

    # --- BT6: Bangunan Tempat Kerja – Bangunan Bawah Tanah ---
    ("BT6", "Bangunan Tempat Kerja – Bangunan Bawah Tanah", "BT6.1", "Apakah bangunan bawah tanah memiliki struktur yang kuat?",
     "Bangunan bawah tanah memiliki struktur yang kuat yaitu dapat dilihat dari kondisi dinding, lantai, kolom, dan langit-langit bangunan bawah tanah tidak retak struktural, tidak merembes, tidak berdeformasi, serta tidak ada bagian yang runtuh atau beton terkelupas dengan tulangan terbuka.\n(Dasar: Permenaker 5/2018 Pasal 32 ayat (1) huruf a)",
     "bawah_tanah", "Kondisi Fisik"),
    ("BT6", "Bangunan Tempat Kerja – Bangunan Bawah Tanah", "BT6.2", "Apakah bangunan bawah tanah memiliki sistem ventilasi udara?",
     "Bangunan bawah tanah memiliki sistem ventilasi udara yaitu tersedia ventilasi alami atau mekanis yang menjamin pergantian udara sehingga udara tidak pengap dan kadar oksigen yang cukup untuk beraktivitas.\n(Dasar: Permenaker 5/2018 Pasal 32 ayat (1) huruf b)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "bawah_tanah", "Kondisi Fisik"),
    ("BT6", "Bangunan Tempat Kerja – Bangunan Bawah Tanah", "BT6.3", "Apakah bangunan bawah tanah memiliki sumber pencahayaan yang memadai?",
     "Bangunan bawah tanah memiliki sumber pencahayaan yaitu terdapat lampu (atau cahaya alami) yang berfungsi dan menerangi seluruh area, termasuk tangga, lorong, dan jalur keluar. Tingkat pencahayaan dibawah tanah memadai untuk aktivitas pekerja.\n(Dasar: Permenaker 5/2018 Pasal 32 ayat (1) huruf c)",
     "bawah_tanah", "Kondisi Fisik"),
    ("BT6", "Bangunan Tempat Kerja – Bangunan Bawah Tanah", "BT6.4", "Apakah saluran pembuangan air mengalir dengan baik?",
     "Saluran pembuangan air mengalir dengan baik yaitu saluran/penampung pembuangan air di bangunan bawah tanah berfungsi, air mengalir lancar, tidak tersumbat, dan tidak ada genangan.\n(Dasar: Permenaker 5/2018 Pasal 32 ayat (1) huruf d)",
     "bawah_tanah", "Kondisi Fisik"),
    ("BT6", "Bangunan Tempat Kerja – Bangunan Bawah Tanah", "BT6.5", "Apakah bangunan bawah tanah bersih dan terawat?",
     "Bangunan bawah tanah bersih dan terawat yaitu bebas sampah, kotoran, genangan, dan barang berserakan, serta lantai, dinding, dan peralatannya dalam kondisi baik, dipelihara berkala dan terjadwal.\n(Dasar: Permenaker 5/2018 Pasal 32 ayat (1) huruf e)",
     "bawah_tanah", "Kondisi Fisik"),
    ("BT6", "Bangunan Tempat Kerja – Bangunan Bawah Tanah", "BT6.6", "Apakah bangunan bawah tanah mengikuti syarat Ruang Terbatas?",
     "Bangunan bawah tanah mengikuti syarat Ruang Terbatas yaitu bila bangunan bawah tanah termasuk ruang terbatas (ruang yang cukup besar untuk dimasuki pekerja, memiliki akses masuk/keluar terbatas, dan tidak dirancang untuk ditempati terus-menerus), penerapan higiene dan sanitasinya mengikuti ketentuan peraturan perundang-undangan tentang ruang terbatas.\n(Dasar: Permenaker 5/2018 Pasal 32 ayat (2))\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "bawah_tanah", "Kondisi Fisik"),

    # --- TL7: Fasilitas Kebersihan – Toilet ---
    ("TL7", "Fasilitas Kebersihan – Toilet", "TL7.1", "Apakah toilet bersih dan tidak menimbulkan bau?",
     "Toilet bersih dan tidak menimbulkan bau yaitu seluruh bagian toilet bebas kotoran, noda, dan sampah, serta tidak tercium bau tidak sedap.\n(Dasar: Permenaker 5/2018 Pasal 34 ayat (1) huruf a)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "toilet_sanitasi", "Fasilitas Kebersihan"),
    ("TL7", "Fasilitas Kebersihan – Toilet", "TL7.2", "Apakah toilet tidak terdapat lalat, nyamuk, atau serangga lainnya?",
     "Toilet tidak terdapat lalat, nyamuk, atau serangga lainnya yaitu tidak ditemukan serangga (lalat, nyamuk, kecoa, dan sejenisnya) maupun jentik di dalam toilet dan pada tempat penampungan airnya (bak/ember) saat survei.\n(Dasar: Permenaker 5/2018 Pasal 34 ayat (1) huruf b)",
     "toilet_sanitasi", "Fasilitas Kebersihan"),
    ("TL7", "Fasilitas Kebersihan – Toilet", "TL7.3", "Apakah toilet tersedia saluran pembuangan air yang mengalir dengan baik?",
     "Toilet tersedia saluran pembuangan air yang mengalir dengan baik yaitu lantai miring ke arah saluran, saluran pembuangan berfungsi, air buangan mengalir lancar, tidak tersumbat, dan tidak ada genangan di lantai.\n(Dasar: Permenaker 5/2018 Pasal 34 ayat (1) huruf c)",
     "toilet_sanitasi", "Fasilitas Kebersihan"),
    ("TL7", "Fasilitas Kebersihan – Toilet", "TL7.4", "Apakah toilet tersedia air bersih?",
     "Toilet tersedia air bersih yaitu air tersedia pada keran, bak, atau penampung selama jam kerja, tampak jernih, tidak berbau, dan tidak berwarna.\n(Dasar: Permenaker 5/2018 Pasal 34 ayat (1) huruf d)",
     "toilet_sanitasi", "Fasilitas Kebersihan"),
    ("TL7", "Fasilitas Kebersihan – Toilet", "TL7.5", "Apakah toilet dilengkapi dengan pintu?",
     "Toilet dilengkapi dengan pintu yaitu setiap bilik/ruang toilet memiliki pintu yang berfungsi dan menjaga privasi pengguna.\n(Dasar: Permenaker 5/2018 Pasal 34 ayat (1) huruf e dan Pasal 35 ayat (1))\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "toilet_sanitasi", "Fasilitas Kebersihan"),
    ("TL7", "Fasilitas Kebersihan – Toilet", "TL7.6", "Apakah toilet memiliki penerangan yang cukup?",
     "Toilet memiliki penerangan yang cukup yaitu ruang toilet cukup terang untuk digunakan dan dibersihkan dengan aman, baik dari lampu maupun cahaya alami.\n(Dasar: Permenaker 5/2018 Pasal 34 ayat (1) huruf f)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "toilet_sanitasi", "Fasilitas Kebersihan"),
    ("TL7", "Fasilitas Kebersihan – Toilet", "TL7.7", "Apakah toilet memiliki sirkulasi udara yang baik?",
     "Toilet memiliki sirkulasi udara yang baik yaitu terdapat ventilasi alami atau buatan yang berfungsi sehingga udara tidak pengap dan tidak lembab.\n(Dasar: Permenaker 5/2018 Pasal 34 ayat (1) huruf g)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "toilet_sanitasi", "Fasilitas Kebersihan"),
    ("TL7", "Fasilitas Kebersihan – Toilet", "TL7.8", "Apakah toilet dibersihkan setiap hari secara periodik?",
     "Toilet dibersihkan setiap hari secara periodik yaitu toilet dibersihkan paling sedikit sekali setiap hari kerja sesuai jadwal yang ditetapkan.\n(Dasar: Permenaker 5/2018 Pasal 34 ayat (1) huruf h)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "toilet_sanitasi", "Fasilitas Kebersihan"),
    ("TL7", "Fasilitas Kebersihan – Toilet", "TL7.9", "Apakah toilet dapat digunakan selama jam kerja?",
     "Toilet dapat digunakan selama jam kerja yaitu toilet tidak terkunci, rusak, atau tidak dapat dipakai karena sedang dibersihkan pada seluruh jam kerja, termasuk setiap shift, dan pekerja dapat menggunakannya bila diperlukan.\n(Dasar: Permenaker 5/2018 Pasal 34 ayat (1) huruf i)",
     "toilet_sanitasi", "Fasilitas Kebersihan"),
    ("TL7", "Fasilitas Kebersihan – Toilet", "TL7.10", "Apakah toilet terpisah antara laki-laki dan perempuan, serta penyandang cacat?",
     "Toilet terpisah antara laki-laki, perempuan, dan penyandang cacat yaitu tersedia toilet tersendiri (ruang/bilik berbeda) untuk pekerja laki-laki, pekerja perempuan, dan pekerja penyandang disabilitas, dengan toilet disabilitas yang memenuhi persyaratan ukuran dan aksesibilitas.\n(Dasar: Permenaker 5/2018 Pasal 34 ayat (3) dan Pasal 35 ayat (2))\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "toilet_sanitasi", "Fasilitas Kebersihan"),
    ("TL7", "Fasilitas Kebersihan – Toilet", "TL7.11", "Apakah toilet diberikan tanda yang jelas?",
     "Toilet diberikan tanda yang jelas yaitu setiap toilet laki-laki, perempuan, dan disabilitas diberi rambu (simbol dan/atau tulisan) yang mudah terlihat dan terbaca.\n(Dasar: Permenaker 5/2018 Pasal 34 ayat (3))",
     "toilet_sanitasi", "Fasilitas Kebersihan"),
    ("TL7", "Fasilitas Kebersihan – Toilet", "TL7.12", "Apakah jumlah jamban telah sesuai dengan jumlah pekerja dalam 1 waktu kerja?",
     "Jumlah jamban sesuai dengan jumlah pekerja dalam satu waktu kerja yaitu jumlah jamban memenuhi ketentuan: 1–15 orang = 1 jamban; 16–30 orang = 2; 31–45 orang = 3; 46–60 orang = 4; 61–80 orang = 5; 81–100 orang = 6; setiap penambahan 40 orang ditambah 1 jamban.\n(Dasar: Permenaker 5/2018 Pasal 34 ayat (5) sampai (8))\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "toilet_sanitasi", "Fasilitas Kebersihan"),
    ("TL7", "Fasilitas Kebersihan – Toilet", "TL7.13", "Apakah Kelengkapan fasilitas toilet memadai?",
     "Kelengkapan fasilitas toilet meliputi paling sedikit jamban, air bersih yang cukup, alat pembilas, tempat sampah, tempat cuci tangan, dan sabun.\n(Dasar: Permenaker 5/2018 Pasal 34 ayat (2))\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "toilet_sanitasi", "Fasilitas Kebersihan"),
    ("TL7", "Fasilitas Kebersihan – Toilet", "TL7.14", "Apakah ruang toilet memungkinkan pengguna kursi roda melakukan manuver atau berputar 180 derajat?",
     "Ruang toilet memungkinkan pengguna kursi roda berputar 180° yaitu di dalam ruang toilet disabilitas tersedia ruang bebas yang cukup sehingga pengguna kursi roda dapat masuk, berputar 180 derajat, dan keluar tanpa bantuan serta tanpa terhalang jamban, tempat sampah, ember, atau benda lain. Ruang toilet disabilitas paling sedikit berukuran panjang 152,5 cm, lebar 227,5 cm, dan tinggi 240 cm. Bila toilet disabilitas tidak tersedia, beri skor 0.\n(Dasar: Permenaker 5/2018 Pasal 35 ayat (2) huruf a, b, c, d, dan e)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "toilet_sanitasi", "Fasilitas Kebersihan"),
    ("TL7", "Fasilitas Kebersihan – Toilet", "TL7.15", "Apakah toilet dilengkapi pegangan rambat (handrail) untuk membantu penyandang disabilitas berpindah dari kursi roda ke jamban dan sebaliknya?",
     "Pegangan rambat (handrail) yaitu batang pegangan yang terpasang tetap pada dinding di samping dan/atau belakang jamban pada toilet disabilitas sehingga pengguna kursi roda dapat berpindah dari kursi roda ke jamban dan sebaliknya secara mandiri dan aman. Bila toilet disabilitas tidak tersedia, beri skor 0.\n(Dasar: Permenaker 5/2018 Pasal 35 ayat (2) huruf i)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "toilet_sanitasi", "Fasilitas Kebersihan"),
    ("TL7", "Fasilitas Kebersihan – Toilet", "TL7.16", "Apakah tempat cuci tangan dapat dijangkau dan digunakan oleh pekerja pengguna kursi roda?",
     "Tempat cuci tangan dapat dijangkau dan digunakan pengguna kursi roda yaitu wastafel/keran di toilet disabilitas berada pada ketinggian dan posisi yang terjangkau, tersedia ruang kosong di bawahnya untuk lutut dan ruang bebas di depannya, sehingga pengguna kursi roda dapat mendekat, mengoperasikan keran, dan mencuci tangan tanpa bantuan. Bila toilet disabilitas tidak tersedia, beri skor 0.\n(Dasar: Permenaker 5/2018 Pasal 34 ayat (2) huruf e dan f serta Pasal 35 ayat (2) huruf e; standar teknis: Permen PUPR No. 14/PRT/M/2017)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "toilet_sanitasi", "Fasilitas Kebersihan"),

    # --- FK8: Fasilitas Kebersihan – Pakaian Kerja dan Loker ---
    ("FK8", "Fasilitas Kebersihan – Pakaian Kerja dan Loker", "FK8.1", "Apakah Perusahaan menyediakan pakaian kerja?",
     "Perusahaan menyediakan pakaian kerja yaitu bagi pekerja yang diwajibkan memakai pakaian kerja sesuai syarat K3, pakaian kerja disediakan oleh pengurus/perusahaan. Isi N/A bila perusahaan tidak mewajibkan pakaian kerja.\n(Dasar: Permenaker 5/2018 Pasal 36 ayat (1) dan (2))\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "sampah_pakaian", "Fasilitas Kebersihan"),
    ("FK8", "Fasilitas Kebersihan – Pakaian Kerja dan Loker", "FK8.2", "Apakah Perusahaan menyediakan tempat penyimpanan atau loker untuk setiap pekerja yang terjamin keamanannya?",
     "Perusahaan menyediakan tempat penyimpanan/loker yaitu setiap pekerja memiliki loker yang terjamin keamanannya, dan bila pekerja berganti pakaian di tempat kerja tersedia ruang ganti yang bersih, terpisah antara laki-laki dan perempuan.\n(Dasar: Permenaker 5/2018 Pasal 36 ayat (3) dan (4))\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "sampah_pakaian", "Fasilitas Kebersihan"),

    # --- SP9: Fasilitas Kebersihan – Tempat Sampah dan Pembuangan Pembalut ---
    ("SP9", "Fasilitas Kebersihan – Tempat Sampah dan Pembuangan Pembalut", "SP9.1", "Apakah Perusahaan menyediakan tempat sampah terpisah?",
     "Perusahaan menyediakan tempat sampah terpisah yaitu tempat sampah dipisahkan menurut jenis sampah (organik, non organik, dan bahan berbahaya) dan tersedia pada setiap tempat kerja.\n(Dasar: Permenaker 5/2018 Pasal 37 ayat (1) dan (2) huruf a)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "sampah_pakaian", "Fasilitas Kebersihan"),
    ("SP9", "Fasilitas Kebersihan – Tempat Sampah dan Pembuangan Pembalut", "SP9.2", "Apakah Perusahaan menyediakan tempat sampah terpisah yang diberikan label sesuai ketentuan?",
     "Tempat sampah terpisah diberikan label sesuai ketentuan yaitu setiap tempat sampah diberi label yang jelas untuk jenis sampah organik, non organik, dan bahan berbahaya sesuai ketentuan peraturan perundang-undangan.\n(Dasar: Permenaker 5/2018 Pasal 37 ayat (2) huruf a)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "sampah_pakaian", "Fasilitas Kebersihan"),
    ("SP9", "Fasilitas Kebersihan – Tempat Sampah dan Pembuangan Pembalut", "SP9.3", "Apakah tempat sampah terpisah tertutup?",
     "Tempat sampah terpisah tertutup yaitu setiap tempat sampah dilengkapi penutup yang berfungsi dan ditutup saat tidak digunakan, serta sampah tidak menyembul atau tumpah keluar.\n(Dasar: Permenaker 5/2018 Pasal 37 ayat (2) huruf b)",
     "sampah_pakaian", "Fasilitas Kebersihan"),
    ("SP9", "Fasilitas Kebersihan – Tempat Sampah dan Pembuangan Pembalut", "SP9.4", "Apakah tutup tempat sampah terpisah terbuat dari bahan yang kedap air?",
     "Tutup tempat sampah terbuat dari bahan yang kedap air yaitu penutup (dan badan) tempat sampah terbuat dari bahan yang tidak menyerap dan tidak bocor, misalnya plastik atau logam, bukan kardus atau anyaman.\n(Dasar: Permenaker 5/2018 Pasal 37 ayat (2) huruf b)",
     "sampah_pakaian", "Fasilitas Kebersihan"),
    ("SP9", "Fasilitas Kebersihan – Tempat Sampah dan Pembuangan Pembalut", "SP9.5", "Apakah tempat sampah terpisah menjadi sarang lalat atau binatang serangga lain?",
     "PERHATIAN, butir ini berkebalikan: terpenuhi (pilih 'Tidak', skor 1) bila tempat sampah terpisah TIDAK menjadi sarang lalat atau binatang serangga lain, yaitu tidak ada lalat, belatung, kecoa, atau semut yang berkerumun serta tidak berbau busuk menyengat; tidak terpenuhi (pilih 'Iya', skor 0) bila ditemukan.\n(Dasar: Permenaker 5/2018 Pasal 37 ayat (2))",
     "sampah_pakaian", "Fasilitas Kebersihan"),
    ("SP9", "Fasilitas Kebersihan – Tempat Sampah dan Pembuangan Pembalut", "SP9.6", "Apakah tersedia Tempat Pembuangan Pembalut di ruang toilet perempuan?",
     "Tempat pembuangan pembalut yaitu wadah khusus di ruang toilet perempuan untuk membuang pembalut yang kedap cairan, bertutup, berlabel jelas, dan dibersihkan setiap hari.\n(Dasar: Permenaker 5/2018 Pasal 38)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "sampah_pakaian", "Fasilitas Kebersihan"),

    # --- KU10: Kebutuhan Udara ---
    ("KU10", "Kebutuhan Udara", "KU10.1", "Apakah suhu ruangan nyaman antara 23 – 26 derajat Celcius dengan perbedaan suhu antar ruangan tidak boleh melebihi 5 derajat Celcius?",
     "Suhu ruangan nyaman yaitu suhu kering ruangan antara 23–26 °C dengan perbedaan suhu antar ruangan tidak melebihi 5 °C (ukur dengan termometer). Berlaku untuk tempat kerja pekerjaan administratif, pelayanan umum, dan fungsi manajerial; N/A untuk area lain.\n(Dasar: Permenaker 5/2018 Pasal 40 ayat (1) dan (3))\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "kebutuhan_udara", "Kebutuhan Udara"),
    ("KU10", "Kebutuhan Udara", "KU10.2", "Apakah kelembaban ruangan antara 40-60%?",
     "Kelembaban ruangan antara 40–60% (ukur dengan higrometer). Berlaku untuk tempat kerja pekerjaan administratif, pelayanan umum, dan fungsi manajerial; N/A untuk area lain.\n(Dasar: Permenaker 5/2018 Pasal 40 ayat (3) huruf a)",
     "kebutuhan_udara", "Kebutuhan Udara"),
    ("KU10", "Kebutuhan Udara", "KU10.3", "Apakah kadar oksigen dalam ruang antara 19,5% - 23,5%?",
     "Kadar oksigen dalam ruang antara 19,5% sampai 23,5% dari volume udara (ukur dengan alat ukur oksigen). Berlaku untuk tempat kerja pekerjaan administratif, pelayanan umum, dan fungsi manajerial; N/A untuk area lain.\n(Dasar: Permenaker 5/2018 Pasal 40 ayat (4))",
     "kebutuhan_udara", "Kebutuhan Udara"),
    ("KU10", "Kebutuhan Udara", "KU10.4", "Apakah terdapat sistem ventilasi (alami, buatan, atau kombinasi) dalam ruang?",
     "Sistem ventilasi dalam ruang yaitu tersedia ventilasi alami (jendela/lubang angin), buatan (exhaust, blower, AC), atau kombinasi keduanya yang menjamin kebutuhan udara pekerja dan mengurangi kadar kontaminan.\n(Dasar: Permenaker 5/2018 Pasal 41 ayat (1) dan (2))\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "kebutuhan_udara", "Kebutuhan Udara"),
    ("KU10", "Kebutuhan Udara", "KU10.5", "Apakah sistem ventilasi dibersihkan secara berkala minimal 3 bulan sekali?",
     "Sistem ventilasi dibersihkan berkala yaitu ventilasi buatan (filter AC, kipas, exhaust, saluran udara) dibersihkan paling sedikit 3 (tiga) bulan sekali. Isi N/A bila hanya menggunakan ventilasi alami.\n(Dasar: Permenaker 5/2018 Pasal 41 ayat (3))\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "kebutuhan_udara", "Kebutuhan Udara"),
    ("KU10", "Kebutuhan Udara", "KU10.6", "Apakah setiap orang bekerja dalam ruangan mendapat ruang udara (cubic space) paling sedikit 10 m3?",
     "Ruang udara (cubic space) yaitu setiap orang yang bekerja dalam ruangan mendapat ruang udara paling sedikit 10 m³. Hitung: (panjang × lebar × tinggi) dibagi jumlah pekerja di ruangan, dengan tinggi ruangan di atas 4 m dihitung maksimal 4 m.\n(Dasar: Permenaker 5/2018 Pasal 42)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "kebutuhan_udara", "Kebutuhan Udara"),

    # --- KR11: Tata Laksana Kerumahtanggaan ---
    ("KR11", "Tata Laksana Kerumahtanggaan", "KR11.1", "Apakah terdapat pemisahan antara alat, perkakas, dan bahan yang diperlukan atau digunakan?",
     "Memisahkan alat, perkakas, dan bahan yaitu alat, perkakas, dan bahan yang diperlukan atau digunakan dalam pekerjaan dipilah dan dipisahkan dari yang tidak diperlukan (rusak, tidak terpakai, atau kedaluwarsa), serta dikelompokkan terpisah menurut jenis dan fungsinya.\n(Dasar: Permenaker 5/2018 Pasal 43 ayat (2) huruf a)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "housekeeping", "Tata Laksana Kerumahtanggaan"),
    ("KR11", "Tata Laksana Kerumahtanggaan", "KR11.2", "Apakah terdapat penataan antara alat, perkakas, dan bahan yang diperlukan atau digunakan?",
     "Menata alat, perkakas, dan bahan yaitu alat, perkakas, dan bahan diletakkan pada posisi yang telah ditetapkan, tertata rapi dan tertib, mudah dijangkau, serta aman sehingga tidak menghalangi jalur kerja maupun menimbulkan bahaya kecelakaan.\n(Dasar: Permenaker 5/2018 Pasal 43 ayat (2) huruf b dan Pasal 44 ayat (1))\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "housekeeping", "Tata Laksana Kerumahtanggaan"),
    ("KR11", "Tata Laksana Kerumahtanggaan", "KR11.3", "Apakah terdapat aktivitas pembersihan antara alat, perkakas, dan bahan yang diperlukan atau digunakan?",
     "Aktivitas pembersihan alat, perkakas, dan bahan yaitu alat, perkakas, dan bahan dibersihkan secara rutin sesuai jadwal yang ditetapkan sehingga bebas dari debu tebal, kotoran, oli/minyak, dan tumpahan.\n(Dasar: Permenaker 5/2018 Pasal 43 ayat (2) huruf c)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "housekeeping", "Tata Laksana Kerumahtanggaan"),
    ("KR11", "Tata Laksana Kerumahtanggaan", "KR11.4", "Apakah terdapat prosedur kebersihan, penempatan dan penataan untuk alat, perkakas dan bahan dan secara berkala prosedur dikembangkan?",
     "Prosedur kebersihan, penempatan, dan penataan yaitu terdapat prosedur tertulis untuk kebersihan, penempatan, dan penataan alat, perkakas, dan bahan yang ditetapkan secara resmi, dilaksanakan oleh pekerja, serta dikembangkan (ditinjau dan diperbarui) secara berkala.\n(Dasar: Permenaker 5/2018 Pasal 43 ayat (2) huruf d dan e)\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "housekeeping", "Tata Laksana Kerumahtanggaan"),
    ("KR11", "Tata Laksana Kerumahtanggaan", "KR11.5", "Apakah terdapat pelabelan yang jelas?",
     "Pelabelan yang jelas yaitu bahan disimpan di gudang atau area penyimpanan khusus dan setiap jenis bahan diberi label yang jelas, terbaca, dan tidak tertukar sehingga barang-barang tersebut dapat dibedakan.\n(Dasar: Permenaker 5/2018 Pasal 44 ayat (2))\nLihat rincian butir pada sheet Rincian Kriteria (2).",
     "housekeeping", "Tata Laksana Kerumahtanggaan"),
]


MASTER_PERTANYAAN = {}
INFOGRAFIS_DATA = {}

for kode_kat, kat, kode_dim, teks_q, panduan_raw, kelompok_id, topik_nama in _RAW_MATRIKS_2:
    panduan_bersih, regulasi_str = _clean_panduan(panduan_raw)
    is_disabilitas = kode_dim in PERTANYAAN_DISABILITAS
    is_terbalik = kode_dim in PERTANYAAN_TERBALIK
    depends_on = "HL1.7" if kode_dim in {"HL1.8", "HL1.9"} else None

    MASTER_PERTANYAAN[kode_dim] = {
        "id": kode_dim,
        "kode": kode_dim,
        "kode_kategori": kode_kat,
        "kategori": kat,
        "aspek": kat,
        "sub_bidang": kat,
        "topik": topik_nama,
        "kelompok": kelompok_id,
        "teks": teks_q,
        "panduan": panduan_bersih,
        "definisi": panduan_bersih,
        "regulasi": regulasi_str,
        "tipe": "ya_tidak",
        "opsi": OPT_IYA_TIDAK,
        "bobot_max": 1,
        "khusus_disabilitas": is_disabilitas,
        "reverse_score": is_terbalik,
        "depends_on": depends_on,
        "has_infografis": True
    }

    badge_label = f"♿ Disabilitas • {kode_kat}" if is_disabilitas else f"📋 {kode_kat} • {kode_dim}"
    INFOGRAFIS_DATA[kode_dim] = {
        "istilah": f"[{kode_dim}] {kat}",
        "regulasi": regulasi_str,
        "ringkasan": panduan_bersih,
        "poin_kunci": [],
        "visual_badge": badge_label
    }


PANDUAN_PENGISIAN = {
    "Iya": {
        "skor": 1,
        "makna": "Memenuhi / Iya",
        "kriteria": "Kondisi aktual sesuai dengan panduan penilaian dan persyaratan K3."
    },
    "Tidak": {
        "skor": 0,
        "makna": "Tidak Memenuhi / Tidak",
        "kriteria": "Kondisi aktual belum memenuhi panduan penilaian yang diharapkan."
    }
}


def hitung_skor_opsi(q_id: str, jawaban: str) -> int:
    """Menghitung skor (1 atau 0) berdasarkan pilihan Iya/Tidak (memperhitungkan butir terbalik)."""
    ans_norm = str(jawaban).strip().lower()
    is_yes = ans_norm in {"iya", "ya"}
    is_no = ans_norm == "tidak"
    if q_id in PERTANYAAN_TERBALIK:
        return 1 if is_no else 0
    return 1 if is_yes else 0


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
    """Memperbarui status TL7.12 evaluasi rasio toilet pada tiap gedung."""
    if not daftar_gedung:
        return daftar_gedung

    for g in daftar_gedung:
        toilet_gedung = to_int(g.get("Jumlah Toilet", 0))
        pekerja_gedung = to_int(g.get("Total Pekerja", 0))
        syarat_mandiri = hitung_kebutuhan_toilet(pekerja_gedung)
        mandiri_memenuhi = toilet_gedung >= syarat_mandiri

        if "TL7.12_Jawaban" not in g or not g.get("TL7.12_Jawaban"):
            g["TL7.12_Jawaban"] = "Iya" if mandiri_memenuhi else "Tidak"
            g["TL7.12_Poin"] = 1 if mandiri_memenuhi else 0

    return daftar_gedung


# ==============================================================================
# PERHITUNGAN SKOR RINCI PER KATEGORI & TOPIK ('MATRIKS PENILAIAN (2)')
# ==============================================================================
def is_soal_applicable(q_id: str, data_gedung: dict, fasilitas_terpilih: list) -> bool:
    """Menentukan apakah butir pertanyaan berlaku untuk gedung ini."""
    q_info = MASTER_PERTANYAAN.get(q_id)
    if not q_info:
        return False
    if q_info["kelompok"] not in fasilitas_terpilih:
        return False

    # Cek apakah pertanyaan khusus disabilitas
    jml_disabilitas = to_int(data_gedung.get("Pekerja Disabilitas", 0))
    if q_info.get("khusus_disabilitas") and jml_disabilitas <= 0:
        return False

    # Cek jika HL1.1 dijawab Tidak, maka HL1.2 - HL1.9 tidak berlaku
    if q_id != "HL1.1" and q_info["kelompok"] == "halaman":
        ans_hl1_1 = str(data_gedung.get("HL1.1_Jawaban", "Iya")).strip().lower()
        if ans_hl1_1 == "tidak":
            return False

    # Cek dependensi saluran pembuangan air halaman (HL1.8 & HL1.9 bergantung pada HL1.7)
    dep = q_info.get("depends_on")
    if dep:
        ans_dep = str(data_gedung.get(f"{dep}_Jawaban", "Iya")).strip().lower()
        if ans_dep == "tidak":
            return False

    return True


def hitung_skor_lengkap_gedung(data_gedung: dict, fasilitas_terpilih: list = None) -> dict:
    """
    Menghitung skor evaluasi K3 gedung berdasarkan sheet 'Matriks Penilaian (2)':
    - Setiap butir bernilai 1 (Memenuhi) atau 0 (Tidak Memenuhi)
    - Pertanyaan disabilitas (GD2.4, TL7.14, TL7.15, TL7.16) hanya dihitung jika Pekerja Disabilitas > 0
    """
    fasilitas_norm = normalize_fasilitas_ids(fasilitas_terpilih or data_gedung.get("Fasilitas Terpilih", []))

    skor_topik = {
        "Kondisi Fisik": 0,
        "Fasilitas Kebersihan": 0,
        "Kebutuhan Udara": 0,
        "Tata Laksana Kerumahtanggaan": 0
    }
    maks_topik = {
        "Kondisi Fisik": 0,
        "Fasilitas Kebersihan": 0,
        "Kebutuhan Udara": 0,
        "Tata Laksana Kerumahtanggaan": 0
    }

    # Kelompokkan per kode_kategori (HL1 .. KR11)
    urutan_kat = ["HL1", "GD2", "DL3", "LT4", "AT5", "BT6", "TL7", "FK8", "SP9", "KU10", "KR11"]
    kat_stats = {}

    for q_id, q_info in MASTER_PERTANYAAN.items():
        if not is_soal_applicable(q_id, data_gedung, fasilitas_norm):
            continue

        k_kat = q_info["kode_kategori"]
        if k_kat not in kat_stats:
            kat_stats[k_kat] = {
                "Kode Kategori": k_kat,
                "Kategori": q_info["kategori"],
                "Topik": q_info["topik"],
                "Jumlah Indikator": 0,
                "Skor Tercapai": 0,
                "Skor Maksimum": 0
            }

        poin = to_int(data_gedung.get(f"{q_id}_Poin", 0))
        kat_stats[k_kat]["Jumlah Indikator"] += 1
        kat_stats[k_kat]["Skor Maksimum"] += 1
        kat_stats[k_kat]["Skor Tercapai"] += poin

        topik = q_info["topik"]
        skor_topik[topik] = skor_topik.get(topik, 0) + poin
        maks_topik[topik] = maks_topik.get(topik, 0) + 1

    rincian_tabel = []
    for k_kat in urutan_kat:
        if k_kat not in kat_stats:
            continue
        st_item = kat_stats[k_kat]
        jml = st_item["Jumlah Indikator"]
        tercapai = st_item["Skor Tercapai"]
        capaian_pct = round((tercapai / jml * 100.0), 1) if jml > 0 else 100.0

        if capaian_pct >= 85:
            interp = "Memenuhi Standar"
        elif capaian_pct >= 65:
            interp = "Cukup / Perlu Perbaikan Minor"
        else:
            interp = "Kurang / Prioritas Tindakan Korektif"

        rincian_tabel.append({
            "Kode Kategori": k_kat,
            "Kategori": st_item["Kategori"],
            "Aspek": f"[{k_kat}] {st_item['Kategori']}",
            "Jumlah Indikator": jml,
            "Bobot Nilai Max": jml,
            "Bobot Persentase": f"{jml} Butir",
            "Capaian (%)": capaian_pct,
            "Skor Maksimum": jml,
            "Skor Tercapai": tercapai,
            "Interpretasi Internal": interp
        })

    total_skor = sum(skor_topik.values())
    skor_maks_tersedia = sum(maks_topik.values())
    indeks_pemenuhan = round((total_skor / skor_maks_tersedia * 100.0), 1) if skor_maks_tersedia > 0 else 0.0

    return {
        "skor_kategori": skor_topik,
        "maks_kategori": maks_topik,
        "total_skor": total_skor,
        "skor_maks_tersedia": skor_maks_tersedia,
        "indeks_pemenuhan": indeks_pemenuhan,
        "rincian_tabel": rincian_tabel,
        "Skor_Topik_1": skor_topik["Kondisi Fisik"],
        "Skor_Topik_2": skor_topik["Fasilitas Kebersihan"],
        "Skor_Topik_3": skor_topik["Kebutuhan Udara"],
        "Skor_Topik_4": skor_topik["Tata Laksana Kerumahtanggaan"]
    }


def analisis_evaluasi_gedung(data_gedung: dict, fasilitas_ids: list = None) -> dict:
    """Menganalisis hasil survei gedung, mencatat butir yang bernilai 0 beserta rekomendasinya."""
    fasilitas_norm = normalize_fasilitas_ids(fasilitas_ids or data_gedung.get("Fasilitas Terpilih", []))
    skor_info = hitung_skor_lengkap_gedung(data_gedung, fasilitas_norm)
    pertanyaan_kurang = []

    for q_id, q_info in MASTER_PERTANYAAN.items():
        if not is_soal_applicable(q_id, data_gedung, fasilitas_norm):
            continue

        poin_raw = data_gedung.get(f"{q_id}_Poin")
        jawaban = str(data_gedung.get(f"{q_id}_Jawaban", ""))

        if "N/A" in jawaban:
            continue

        if poin_raw is not None and str(poin_raw).strip() != "":
            skor_angka = to_int(poin_raw, 0)
            if skor_angka < 1:
                pertanyaan_kurang.append({
                    "id": q_id,
                    "kode_kategori": q_info["kode_kategori"],
                    "topik": q_info["topik"],
                    "aspek": q_info["kategori"],
                    "sub_bidang": q_info["kategori"],
                    "teks": q_info["teks"],
                    "definisi": q_info["panduan"],
                    "bukti": q_info["panduan"],
                    "jawaban": jawaban,
                    "skor": skor_angka,
                    "regulasi": q_info["regulasi"],
                    "rekomendasi": f"Tindak lanjuti pemenuhan [{q_id}]: {q_info['panduan']}"
                })

    bidang_perlu_perbaikan = []
    for r in skor_info["rincian_tabel"]:
        if r["Capaian (%)"] < 75:
            bidang_perlu_perbaikan.append(f"{r['Kode Kategori']} - {r['Kategori']} ({r['Skor Tercapai']}/{r['Skor Maksimum']})")

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
