# config_evaluasi.py
from daftar_pertanyaan import MASTER_PERTANYAAN, to_int

SUB_BIDANG_CONFIG = {
    "Kondisi Fisik": {},
    "Fasilitas Kebersihan": {},
    "Kebutuhan Udara": {},
    "Tata Laksana Kerumahtanggaan": {}
}

for q_id, q_info in MASTER_PERTANYAAN.items():
    topik = q_info["topik"]
    kat = f"[{q_info['kode_kategori']}] {q_info['kategori']}"
    SUB_BIDANG_CONFIG.setdefault(topik, {}).setdefault(kat, {})[q_id] = q_info["teks"]


def analisis_sub_bidang_kurang(data_gedung: dict, bidang_nama: str):
    """
    Mengidentifikasi sub bidang dan butir pertanyaan yang nilainya tidak memenuhi standar (Skor = 0).
    """
    hasil_sub_bidang = {}
    daftar_sub = SUB_BIDANG_CONFIG.get(bidang_nama, {})

    for nama_sub, daftar_q in daftar_sub.items():
        soal_tidak_terpenuhi = []

        for q_id, deskripsi in daftar_q.items():
            poin = data_gedung.get(f"{q_id}_Poin")
            jawaban = str(data_gedung.get(f"{q_id}_Jawaban", ""))

            if "N/A" in jawaban or "Tidak berlaku" in jawaban:
                continue

            if poin is not None and str(poin).strip() != "":
                skor_angka = to_int(poin, 0)
                if skor_angka < 1:
                    soal_tidak_terpenuhi.append({
                        "id": q_id,
                        "deskripsi": deskripsi,
                        "jawaban_user": jawaban,
                        "skor": skor_angka
                    })

        if soal_tidak_terpenuhi:
            hasil_sub_bidang[nama_sub] = soal_tidak_terpenuhi

    return hasil_sub_bidang
