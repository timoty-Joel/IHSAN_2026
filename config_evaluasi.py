# config_evaluasi.py

SUB_BIDANG_CONFIG = {
    "Bangunan Tempat Kerja": {
        "Halaman": {
            "A2": "Kebersihan dan kerapian halaman",
            "A3": "Kerataan permukaan halaman",
            "A4": "Halaman tidak becek dan bebas genangan air",
            "A6": "Kekuatan penutup saluran air pembuangan halaman",
            "A7": "Kelancaran aliran saluran air pembuangan halaman",
        },
        "Gedung": {
            "A8": "Kondisi kebersihan dan pemeliharaan gedung",
            "A9": "Kekuatan dan kekokohan struktur gedung",
            "A10": "Kecukupan ruang gerak minimal 2 m² per orang",
            "A11": "Dinding dan langit-langit kering dan tidak lembap",
            "A12": "Dinding dan langit-langit dicat / mudah dibersihkan",
            "A13": "Pengecatan ulang dinding dan langit-langit min. 5 tahun sekali",
            "A14": "Pembersihan dinding dan langit-langit min. 1 tahun sekali",
            "A15": "Lantai keras, tahan air, dan tahan bahan kimia",
            "A16": "Permukaan lantai datar, tidak licin, dan mudah dibersihkan",
            "A17": "Pembersihan lantai secara teratur",
            "A18": "Perlindungan atap dari panas matahari dan air hujan",
            "A19": "Atap tidak bocor, tidak berlubang, dan bebas jamur",
        },
        "Ruang Bawah Tanah": {
            "A21": "Kekuatan struktur bangunan bawah tanah",
            "A22": "Sistem ventilasi udara bangunan bawah tanah",
            "A23": "Sumber pencahayaan bangunan bawah tanah",
            "A24": "Saluran pembuangan air bangunan bawah tanah",
            "A25": "Kebersihan dan perawatan bangunan bawah tanah",
        }
    },
    "Fasilitas Kebersihan": {
        "Toilet": {
            "B2": "Kecukupan jumlah toilet terhadap jumlah pekerja",
            "B3": "Kebersihan toilet dan bebas bau",
            "B4": "Ketersediaan toilet khusus penyandang disabilitas",
        },
        "Loker": {
            "B5": "Ketersediaan loker penyimpanan sesuai kebutuhan pekerja",
            "B6": "Ketersediaan ruang ganti pakaian pekerja",
        },
        "Tempat Sampah": {
            "B7": "Ketersediaan tempat sampah di area kerja",
            "B8": "Tempat sampah terpilah organik, anorganik, dan limbah B3",
        },
        "Peralatan Kebersihan": {
            "B9": "Kelayakan dan fungsi peralatan kebersihan",
        }
    },
    "Kebutuhan Udara": {
        "KUDR": {
            "C1": "Suhu udara ruang kerja dalam rentang 23–26°C",
            "C2": "Kelembapan relatif udara dalam rentang 40–60%",
        },
        "Ventilasi": {
            "C3": "Fungsi ventilasi udara alami maupun mekanis",
        },
        "Ruang Udara": {
            "C4": "Kecukupan ruang udara (cubic space) minimal 10 m³ per pekerja",
        }
    },
    "Tata Laksana Kerumahtanggaan": {
        "Housekeeping": {
            "D1": "Pemisahan antara alat, perkakas, dan bahan",
            "D2": "Penataan posisi alat, perkakas, dan bahan",
            "D3": "Aktivitas pembersihan berkala teratur",
            "D4": "SOP kebersihan, penataan bahan dan pengembangan berkala",
        }
    }
}

def analisis_sub_bidang_kurang(data_gedung: dict, bidang_nama: str):
    """
    Mengidentifikasi sub bidang dan butir pertanyaan yang nilainya tidak memenuhi standar.
    Kriteria kurang:
    - Poin < 2 (atau skor < 2 untuk pertanyaan 3 opsi / biner)
    """
    hasil_sub_bidang = {}
    
    # Normalisasi nama bidang
    lookup_nama = bidang_nama
    if "Bangunan" in bidang_nama or "Fisik" in bidang_nama:
        lookup_nama = "Bangunan Tempat Kerja"
    elif "Fasilitas" in bidang_nama or "Kebersihan" in bidang_nama and "Tata" not in bidang_nama:
        lookup_nama = "Fasilitas Kebersihan"
    elif "Udara" in bidang_nama:
        lookup_nama = "Kebutuhan Udara"
    elif "Tata Laksana" in bidang_nama or "Housekeeping" in bidang_nama:
        lookup_nama = "Tata Laksana Kerumahtanggaan"

    daftar_sub = SUB_BIDANG_CONFIG.get(lookup_nama, {})

    for nama_sub, daftar_q in daftar_sub.items():
        soal_tidak_terpenuhi = []

        for q_id, deskripsi in daftar_q.items():
            poin = data_gedung.get(f"{q_id}_Poin")
            jawaban = str(data_gedung.get(f"{q_id}_Jawaban", ""))

            if "N/A" in jawaban or "Tidak ada" in jawaban:
                continue

            if poin is not None and str(poin).strip() != "":
                try:
                    skor_angka = int(float(str(poin).strip()))
                except Exception:
                    continue

                if skor_angka < 2:
                    soal_tidak_terpenuhi.append({
                        "id": q_id,
                        "deskripsi": deskripsi,
                        "jawaban_user": jawaban,
                        "skor": skor_angka
                    })

        if soal_tidak_terpenuhi:
            hasil_sub_bidang[nama_sub] = soal_tidak_terpenuhi

    return hasil_sub_bidang
