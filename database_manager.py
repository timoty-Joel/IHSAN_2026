
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1RTlhOLxdXShS2UAdp2JFgUQyXe2ufEJ8xgGOgCnRdsk/edit"
LOCAL_STORAGE_PATH = os.path.join(os.path.dirname(__file__), "survei_data_local.json")


def _get_gsheets_conn():
    """Mengambil koneksi Google Sheets jika tersedia."""
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception:
        return None


def _load_local_data() -> dict:
    """Membaca basis data lokal JSON."""
    if not os.path.exists(LOCAL_STORAGE_PATH):
        # Inisialisasi basis data awal dengan beberapa sampel representatif
        initial_data = {
            "perusahaan": [
                {
                    "Company Key": "HIBB-DEMO-01",
                    "Waktu Pengisian": (datetime.now() - timedelta(days=25)).strftime("%Y-%m-%d %H:%M:%S"),
                    "Nama Perusahaan": "PT Nusantara Chemindo",
                    "No Induk Perusahaan": "912000345678",
                    "No Telp Perusahaan": "021-89765432",
                    "Legalitas": "PT",
                    "Lokasi Pengujian": "Kawasan Industri MM2100, Cikarang",
                    "Nama Responden": "Ahmad Fauzi",
                    "Email Responden": "fauzi@nusantarachem.com",
                    "Jabatan": "HSE Officer",
                    "Jenis Usaha (KBLI)": "Industri Pengolahan",
                    "Kategori Pekerja": "Industri Besar (≥ 100 orang)",
                    "Nama Lembaga K3": "PT Mitra K3 Prima",
                    "Nama Ahli K3": "Ir. Hendra Gunawan, S.T., M.KKK",
                    "Nomor SKP Ahli": "KEP.123/BINWASK3/2023",
                    "Status Verifikasi": "Terverifikasi Memenuhi Standar",
                    "Catatan Verifikator": "Fasilitas sanitasi dan ventilasi sangat baik. Dilengkapi APD lengkap.",
                    "Waktu Verifikasi": (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                    "Company Key": "HIBB-DEMO-02",
                    "Waktu Pengisian": (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S"),
                    "Nama Perusahaan": "PT Sentosa Logistik Indonesia",
                    "No Induk Perusahaan": "812009876543",
                    "No Telp Perusahaan": "021-55667788",
                    "Legalitas": "PT",
                    "Lokasi Pengujian": "Jl. Marunda Makmur No. 12, Jakarta Utara",
                    "Nama Responden": "Siti Rahmawati",
                    "Email Responden": "siti.rahma@sentosalog.co.id",
                    "Jabatan": "Koordinator K3",
                    "Jenis Usaha (KBLI)": "Pengangkutan dan Pergudangan",
                    "Kategori Pekerja": "Industri Sedang (20 - 99 orang)",
                    "Nama Lembaga K3": "Balai K3 Jakarta",
                    "Nama Ahli K3": "Dr. Dian Pratama",
                    "Nomor SKP Ahli": "KEP.456/BINWASK3/2024",
                    "Status Verifikasi": "Perlu Tindakan Perbaikan",
                    "Catatan Verifikator": "Perlu penambahan ventilasi pada gudang penyimpanan bagian barat dan pelabelan tempat sampah 3 warna.",
                    "Waktu Verifikasi": (datetime.now() - timedelta(days=12)).strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                    "Company Key": "HIBB-DEMO-03",
                    "Waktu Pengisian": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"),
                    "Nama Perusahaan": "CV Karya Mandiri Konstruksi",
                    "No Induk Perusahaan": "712003344556",
                    "No Telp Perusahaan": "022-77889900",
                    "Legalitas": "CV",
                    "Lokasi Pengujian": "Proyek Gedung Perkantoran Sudirman Central",
                    "Nama Responden": "Bambang Wijaya",
                    "Email Responden": "bambang@karyamandiri.com",
                    "Jabatan": "Site Safety Inspector",
                    "Jenis Usaha (KBLI)": "Konstruksi",
                    "Kategori Pekerja": "Industri Besar (≥ 100 orang)",
                    "Nama Lembaga K3": "PJK3 Multi Prima Solusi",
                    "Nama Ahli K3": "Budi Hartanto, S.T.",
                    "Nomor SKP Ahli": "KEP.789/BINWASK3/2023",
                    "Status Verifikasi": "Menunggu Verifikasi",
                    "Catatan Verifikator": "",
                    "Waktu Verifikasi": ""
                }
            ],
            "hasil_survei": [
                {
                    "Company Key": "HIBB-DEMO-01",
                    "Nomor Gedung": 1,
                    "Nama Gedung": "Gedung Kantor Utama",
                    "Jenis Objek": "1. Perkantoran",
                    "Waktu Penilaian Gedung": (datetime.now() - timedelta(days=25)).strftime("%Y-%m-%d %H:%M:%S"),
                    "Total Pekerja": 85,
                    "Pekerja Laki-laki": 50,
                    "Pekerja Perempuan": 35,
                    "Pekerja Disabilitas": 0,
                    "Jumlah Toilet": 6,
                    "Skor_Topik_1": 68,
                    "Skor_Topik_2": 52,
                    "Skor_Topik_3": 18,
                    "Skor_Topik_4": 10,
                    "Total Poin Gedung": 148,
                    "Status Pemenuhan": "Memenuhi Standar",
                    "Bidang perlu diperbaiki": "Tidak ada"
                },
                {
                    "Company Key": "HIBB-DEMO-01",
                    "Nomor Gedung": 2,
                    "Nama Gedung": "Pabrik Produksi Utama",
                    "Jenis Objek": "2. Pabrik / Area Produksi",
                    "Waktu Penilaian Gedung": (datetime.now() - timedelta(days=25)).strftime("%Y-%m-%d %H:%M:%S"),
                    "Total Pekerja": 120,
                    "Pekerja Laki-laki": 90,
                    "Pekerja Perempuan": 30,
                    "Pekerja Disabilitas": 1,
                    "Jumlah Toilet": 7,
                    "Skor_Topik_1": 64,
                    "Skor_Topik_2": 48,
                    "Skor_Topik_3": 17,
                    "Skor_Topik_4": 9,
                    "Total Poin Gedung": 138,
                    "Status Pemenuhan": "Memenuhi Standar",
                    "Bidang perlu diperbaiki": "Tidak ada"
                },
                {
                    "Company Key": "HIBB-DEMO-02",
                    "Nomor Gedung": 1,
                    "Nama Gedung": "Warehouse Logistik A",
                    "Jenis Objek": "5. Pergudangan / Warehouse",
                    "Waktu Penilaian Gedung": (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S"),
                    "Total Pekerja": 45,
                    "Pekerja Laki-laki": 40,
                    "Pekerja Perempuan": 5,
                    "Pekerja Disabilitas": 0,
                    "Jumlah Toilet": 2,
                    "Skor_Topik_1": 50,
                    "Skor_Topik_2": 32,
                    "Skor_Topik_3": 10,
                    "Skor_Topik_4": 6,
                    "Total Poin Gedung": 98,
                    "Status Pemenuhan": "Perlu Tindakan Perbaikan",
                    "Bidang perlu diperbaiki": "Fasilitas Kebersihan (32/38), Kebutuhan Udara (10/14)"
                },
                {
                    "Company Key": "HIBB-DEMO-03",
                    "Nomor Gedung": 1,
                    "Nama Gedung": "Site Office & Workshop",
                    "Jenis Objek": "3. Workshop",
                    "Waktu Penilaian Gedung": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"),
                    "Total Pekerja": 110,
                    "Pekerja Laki-laki": 105,
                    "Pekerja Perempuan": 5,
                    "Pekerja Disabilitas": 0,
                    "Jumlah Toilet": 6,
                    "Skor_Topik_1": 65,
                    "Skor_Topik_2": 45,
                    "Skor_Topik_3": 16,
                    "Skor_Topik_4": 9,
                    "Total Poin Gedung": 135,
                    "Status Pemenuhan": "Memenuhi Standar",
                    "Bidang perlu diperbaiki": "Tidak ada"
                }
            ]
        }
        _save_local_data(initial_data)
        return initial_data

    try:
        with open(LOCAL_STORAGE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"perusahaan": [], "hasil_survei": []}


def _save_local_data(data: dict):
    """Menyimpan data ke berkas JSON lokal."""
    try:
        with open(LOCAL_STORAGE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.warning(f"Gagal menulis cache lokal: {e}")


def load_all_surveys() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Mengambil data perusahaan dan survei gedung.
    Memprioritaskan sinkronisasi Google Sheets, fallback otomatis ke cache lokal.
    """
    conn = _get_gsheets_conn()
    df_perusahaan = None
    df_survei = None

    if conn is not None:
        try:
            raw_p = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Data_Perusahaan", ttl="5s")
            if raw_p is not None and not raw_p.empty:
                df_perusahaan = raw_p.fillna("").astype(str)
        except Exception:
            pass

        try:
            raw_s = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Hasil_Survei", ttl="5s")
            if raw_s is not None and not raw_s.empty:
                df_survei = raw_s.fillna("").astype(str)
        except Exception:
            pass

    # Jika Google Sheets gagal atau kosong, gunakan database lokal
    local_data = _load_local_data()

    if df_perusahaan is None or df_perusahaan.empty:
        df_perusahaan = pd.DataFrame(local_data.get("perusahaan", []))

    if df_survei is None or df_survei.empty:
        df_survei = pd.DataFrame(local_data.get("hasil_survei", []))

    # Pastikan kolom-kolom penting ada
    if not df_perusahaan.empty and "Status Verifikasi" not in df_perusahaan.columns:
        df_perusahaan["Status Verifikasi"] = "Menunggu Verifikasi"
    if not df_perusahaan.empty and "Catatan Verifikator" not in df_perusahaan.columns:
        df_perusahaan["Catatan Verifikator"] = ""

    return df_perusahaan, df_survei


def save_survey_submission(company_data: dict, list_gedung: list) -> bool:
    """Menyimpan hasil survei baru ke Google Sheets dan penyimpanan lokal."""
    # 1. Simpan ke lokal
    local_data = _load_local_data()

    # Cek apakah Company Key sudah ada di lokal
    existing_keys = [c.get("Company Key") for c in local_data.get("perusahaan", [])]
    if company_data.get("Company Key") in existing_keys:
        # Update
        local_data["perusahaan"] = [
            c if c.get("Company Key") != company_data.get("Company Key") else company_data
            for c in local_data["perusahaan"]
        ]
        # Hapus gedung lama
        local_data["hasil_survei"] = [
            g for g in local_data.get("hasil_survei", [])
            if g.get("Company Key") != company_data.get("Company Key")
        ]
        local_data["hasil_survei"].extend(list_gedung)
    else:
        local_data.setdefault("perusahaan", []).append(company_data)
        local_data.setdefault("hasil_survei", []).extend(list_gedung)

    _save_local_data(local_data)

    # 2. Sinkronkan ke Google Sheets
    conn = _get_gsheets_conn()
    if conn is not None:
        try:
            # Update Data_Perusahaan
            try:
                curr_p = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Data_Perusahaan", ttl="0s")
            except Exception:
                curr_p = pd.DataFrame()

            new_df_p = pd.DataFrame([company_data]).fillna("").astype(str)
            if curr_p is not None and not curr_p.empty and len(curr_p.columns) > 0:
                clean_curr_p = curr_p.fillna("").astype(str)
                updated_p = pd.concat([clean_curr_p, new_df_p], ignore_index=True)
            else:
                updated_p = new_df_p

            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Data_Perusahaan", data=updated_p)

            # Update Hasil_Survei
            try:
                curr_s = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Hasil_Survei", ttl="0s")
            except Exception:
                curr_s = pd.DataFrame()

            new_df_s = pd.DataFrame(list_gedung).fillna("").astype(str)
            if curr_s is not None and not curr_s.empty and len(curr_s.columns) > 0:
                clean_curr_s = curr_s.fillna("").astype(str)
                updated_s = pd.concat([clean_curr_s, new_df_s], ignore_index=True)
            else:
                updated_s = new_df_s

            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Hasil_Survei", data=updated_s)
            return True
        except Exception as e:
            st.warning(f"Sinkronisasi GSheets tertunda ({e}). Data aman tersimpan di cache lokal.")
            return True

    return True


def update_verification_status(company_key: str, status_verifikasi: str, catatan: str, nama_verifikator: str) -> bool:
    """Mengupdate status verifikasi survei oleh Penguji K3 (PJK3/Balai K3)."""
    return update_verification_comprehensive(
        company_key,
        {
            "Status Verifikasi": status_verifikasi,
            "Catatan Verifikator": catatan,
            "Nama Verifikator": nama_verifikator,
            "Nama Ahli K3": nama_verifikator
        }
    )

def update_verification_comprehensive(
    company_key: str,
    verif_details: dict,
    list_gedung_verified: list = None
) -> bool:
    """
    Menyimpan hasil verifikasi lengkap oleh Penguji K3 (PJK3 / Balai K3),
    mencakup data lembaga K3, nama penguji, SKP, status, rekomendasi teknis,
    serta rekaman kuesioner gedung yang telah diverifikasi.
    """
    local_data = _load_local_data()
    updated = False
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Update data perusahaan lokal
    for p in local_data.get("perusahaan", []):
        if str(p.get("Company Key", "")).strip().upper() == str(company_key).strip().upper():
            p.update(verif_details)
            p["Waktu Verifikasi"] = now_str
            updated = True
            break

    # 2. Update data gedung lokal jika diverifikasi ulang
    if list_gedung_verified:
        other_gedung = [
            g for g in local_data.get("hasil_survei", [])
            if str(g.get("Company Key", "")).strip().upper() != str(company_key).strip().upper()
        ]
        other_gedung.extend(list_gedung_verified)
        local_data["hasil_survei"] = other_gedung
        updated = True

    if updated:
        _save_local_data(local_data)

    # 3. Sinkronkan ke Google Sheets jika koneksi tersedia
    conn = _get_gsheets_conn()
    if conn is not None:
        try:
            curr_p = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Data_Perusahaan", ttl="0s")
            if curr_p is not None and not curr_p.empty and "Company Key" in curr_p.columns:
                mask_p = curr_p["Company Key"].astype(str).str.strip().str.upper() == str(company_key).strip().upper()
                if mask_p.any():
                    for k, v in verif_details.items():
                        curr_p.loc[mask_p, k] = v
                    curr_p.loc[mask_p, "Waktu Verifikasi"] = now_str
                    conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Data_Perusahaan", data=curr_p.fillna("").astype(str))

            if list_gedung_verified:
                curr_s = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Hasil_Survei", ttl="0s")
                if curr_s is not None and not curr_s.empty and "Company Key" in curr_s.columns:
                    # Hapus baris lama untuk company key ini lalu gabungkan yang baru diverifikasi
                    other_s = curr_s[curr_s["Company Key"].astype(str).str.strip().str.upper() != str(company_key).strip().upper()]
                    new_s_df = pd.DataFrame(list_gedung_verified).fillna("").astype(str)
                    merged_s = pd.concat([other_s.fillna("").astype(str), new_s_df], ignore_index=True)
                    conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Hasil_Survei", data=merged_s)
        except Exception:
            pass

    return updated


def filter_surveys_by_time(
    df_perusahaan: pd.DataFrame,
    df_survei: pd.DataFrame,
    start_date: datetime.date,
    end_date: datetime.date
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Menyaring dataframe perusahaan dan survei gedung berdasarkan rentang waktu pengisian.
    """
    if df_perusahaan.empty:
        return df_perusahaan, df_survei

    df_p = df_perusahaan.copy()
    if "Waktu Pengisian" in df_p.columns:
        # Parsing tanggal secara fleksibel
        df_p["_parsed_datetime"] = pd.to_datetime(df_p["Waktu Pengisian"], errors="coerce")
        df_p["_parsed_date"] = df_p["_parsed_datetime"].dt.date

        # Filter rentang tanggal
        mask = (df_p["_parsed_date"] >= start_date) & (df_p["_parsed_date"] <= end_date)
        filtered_p = df_p[mask].drop(columns=["_parsed_datetime", "_parsed_date"], errors="ignore")
    else:
        filtered_p = df_p

    # Filter survei berdasarkan Company Key yang lolos
    if not filtered_p.empty and not df_survei.empty and "Company Key" in df_survei.columns:
        valid_keys = set(filtered_p["Company Key"].astype(str).str.strip().str.upper())
        mask_s = df_survei["Company Key"].astype(str).str.strip().str.upper().isin(valid_keys)
        filtered_s = df_survei[mask_s].copy()
    else:
        filtered_s = pd.DataFrame(columns=df_survei.columns) if not df_survei.empty else df_survei

    return filtered_p, filtered_s
