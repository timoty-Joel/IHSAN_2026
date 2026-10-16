# config_evaluasi.py

SUB_BIDANG_CONFIG = {
    "Kondisi Fisik": {
        "Halaman & Area Terbuka": {
            "Q1": "Kebersihan halaman",
            "Q2": "Kerapian halaman",
            "Q3": "Kondisi permukaan halaman tidak rata/berlubang",
            "Q4": "Drainase halaman becek/tergenang",
            "Q5": "Kecukupan luas halaman untuk lalu lintas orang/barang",
            "Q6": "Kekuatan bahan penutup saluran pembuangan air",
        },
        "Struktur Gedung & Ruang Kerja": {
            "Q7": "Kebersihan dan pemeliharaan gedung",
            "Q8": "Kekokohan struktur bangunan (bebas retak berisiko)",
            "Q9": "Kecukupan ruang gerak minimal 2 m² per pekerja",
        },
        "Dinding & Langit - Langit": {
            "Q10": "Kondisi dinding kering/bebas lembap/bebas korosi",
            "Q11": "Kondisi langit-langit kering/bebas lembap",
            "Q12": "Kondisi dinding dicat dan mudah dibersihkan",
            "Q13": "Langit-langit dicat",
            "Q14": "Kebersihan langit-langit",
            "Q15": "Pengecatan ulang dinding berkala",
            "Q16": "Pembersihan rutin dinding",
            "Q17": "Pembersihan rutin langit-langit",
        },
        "Lantai": {
            "Q18": "Lantai terbuat dari bahan yang keras",
            "Q19": "Lantai tahan air",
            "Q20": "Lantai tahan bahan kimia merusak",
            "Q21": "Lantai datar dan mudah dibersihkan",
            "Q22": "Lantai tidak licin",
            "Q23": "Pembersihan lantai secara teratur",
        },
        "Atap": {
            "Q24": "Perlindungan atap dari panas matahari dan hujan",
            "Q25": "Atap tidak bocor dan tidak berlubang",
            "Q26": "Atap bebas dari jamur",
        },
        "Bangunan Bawah Tanah": {
            "Q27": "Kekuatan struktur bawah tanah",
            "Q28": "Sistem ventilasi udara bawah tanah",
            "Q29": "Sumber pencahayaan bawah tanah",
            "Q30": "Kelancaran saluran pembuangan air bawah tanah",
            "Q31": "Kebersihan dan perawatan ruang bawah tanah",
            "Q32": "Pemenuhan syarat Ruang Terbatas (Confined Space)",
        }
    },
    "Fasilitas Kebersihan": {
        "Toilet & Sanitasi": {
            "Q33": "Kecukupan rasio jumlah toilet terhadap jumlah pekerja",
            "Q34": "Kebersihan toilet dan bebas bau",
            "Q35": "Toilet bebas dari serangga (lalat/nyamuk)",
            "Q36": "Kelancaran saluran pembuangan air toilet",
            "Q37": "Ketersediaan pasokan air bersih",
            "Q38": "Kelengkapan pintu penutup toilet",
            "Q39": "Kecukupan penerangan toilet",
            "Q40": "Kelancaran sirkulasi udara toilet",
            "Q41": "Jadwal pembersihan harian toilet secara periodik",
            "Q42": "Ketersediaan toilet selama jam kerja",
            "Q43": "Pemisahan toilet pria, wanita, dan disabilitas",
            "Q44": "Pemasangan tanda/identitas toilet yang jelas",
            "Q45": "Kelengkapan fasilitas jamban, sabun, dan wastafel",
        },
        "Tempat Penyimpanan & Tempat Sampah": {
            "Q46": "Penyediaan pakaian kerja sesuai aturan K3",
            "Q47": "Penyediaan ruang ganti terpisah pria dan wanita",
            "Q48": "Penyediaan loker penyimpanan aman bagi pekerja",
            "Q49": "Penyediaan tempat sampah terpisah sesuai label",
            "Q50": "Pelabelan tempat sampah terpisah",
            "Q51": "Kondisi tempat sampah dalam keadaan tertutup",
            "Q52": "Tutup tempat sampah berbahan kedap air",
            "Q53": "Tempat sampah tidak menjadi sarang serangga",
            "Q54": "Penyediaan tempat pembuangan pembalut di toilet wanita",
        },
    },
    "Kebutuhan Udara": {
        "Sirkulasi & Kualitas Udara": {
            "Q55": "Kenyamanan suhu ruangan (23 - 26°C)",
            "Q56": "Kadar kelembaban ruangan (40 - 60%)",
            "Q57": "Kadar oksigen dalam ruang (19,5% - 23,5%)",
            "Q58": "Ketersediaan sistem ventilasi memadai",
            "Q59": "Pembersihan rutin ventilasi minimal 3 bulan sekali",
            "Q60": "Kecukupan volume ruang udara minimal 10 m³ per pekerja",
        }
    },
    "Tata Laksana Kerumahtanggaan": {
        "Penataan & Housekeeping": {
            "Q61": "Pemisahan antara alat, perkakas, dan bahan",
            "Q62": "Penataan posisi alat dan material kerja",
            "Q63": "Aktivitas pembersihan berkala teratur",
            "Q64": "Ketersediaan SOP dan pengembangan prosedur kebersihan",
            "Q65": "Pelabelan area dan alat yang jelas",
        }
    }
}

def analisis_sub_bidang_kurang(data_gedung: dict, bidang_nama: str):
    """
    Mengidentifikasi sub bidang dan butir pertanyaan yang nilainya tidak memenuhi standar.
    Kriteria kurang:
    - Q34 bernilai 0
    - Pertanyaan skala nilai (1-5) bernilai <= 3
    - Pertanyaan biner/opsi lain bernilai poin 1 padahal maksimal 2, dsb.
    """
    hasil_sub_bidang = {}
    daftar_sub = SUB_BIDANG_CONFIG.get(bidang_nama, {})

    # Kumpulan soalan mengikut jenis pilihan jawapan
    SOALAN_3_PILIHAN = {"Q47", "Q48", "Q61", "Q62", "Q63", "Q64", "Q65"}
    SOALAN_2_PILIHAN = {"Q32", "Q43", "Q46"}
    SOALAN_CHECKBOX = {"Q45", "Q54"}

    for nama_sub, daftar_q in daftar_sub.items():
        soal_tidak_terpenuhi = []

        for q_id, deskripsi in daftar_q.items():
            poin = data_gedung.get(f"{q_id}_Poin")
            jawaban = str(data_gedung.get(f"{q_id}_Jawaban", ""))

            # Abaikan soalan yang dilangkau atau N/A
            if "N/A" in jawaban or "Tidak ada" in jawaban or "Tidak terpenuhi" in jawaban and poin == 0:
                pass

            if "N/A" in jawaban or "Tidak ada" in jawaban:
                continue

            if poin is not None and str(poin).isdigit():
                skor_angka = int(poin)
                kurang = False

                # 1. Logik khusus untuk nisbah tandas (Q34)
                if q_id == "Q34":
                    if skor_angka == 0:
                        kurang = True

                # 2. Logik untuk soalan 3 pilihan (Markah maksimum = 3)
                elif q_id in SOALAN_3_PILIHAN:
                    if skor_angka < 3:
                        kurang = True

                # 3. Logik untuk soalan 2 pilihan / Ya-Tidak (Markah maksimum = 2)
                elif q_id in SOALAN_2_PILIHAN:
                    if skor_angka < 2:
                        kurang = True

                # 4. Logik untuk soalan kotak semak (Kelengkapan kemudahan tandas / pembalut, maks = 5)
                elif q_id in SOALAN_CHECKBOX:
                    if skor_angka < 5:
                        kurang = True

                # 5. Logik untuk soalan skala standard 5 pilihan (Default)
                else:
                    if skor_angka <= 3:
                        kurang = True

                # Masukkan ke dalam senarai jika kriteria tidak dipenuhi
                if kurang:
                    soal_tidak_terpenuhi.append({
                        "id": q_id,
                        "deskripsi": deskripsi,
                        "jawaban_user": jawaban,
                        "skor": skor_angka
                    })

        if soal_tidak_terpenuhi:
            hasil_sub_bidang[nama_sub] = soal_tidak_terpenuhi

    return hasil_sub_bidang