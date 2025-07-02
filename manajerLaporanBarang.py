# manajerLaporanBarang.py

import datetime
import pandas as pd
from model import Laporan
import database


class LaporanBarang:
    """Mengelola logika bisnis laporan barang hilang / ditemukan."""

    _db_setup_done = False

    def __init__(self):
        if not LaporanBarang._db_setup_done:
            print("[LaporanBarang] Melakukan pengecekan/setup database awal...")
            if database.setup_database_initial():
                LaporanBarang._db_setup_done = True
                print("[LaporanBarang] Database siap.")
            else:
                print("[LaporanBarang] KRITICAL: Setup database awal GAGAL!")

    def tambah_laporan(self, laporan: Laporan) -> bool:
        if not isinstance(laporan, Laporan):
            print("Data bukan instance dari kelas Laporan")
            print("[DEBUG] Tipe laporan:", type(laporan))
            return False

        sql = """
        INSERT INTO laporan (nama, deskripsi, tempat, kategori, tanggal, jenis_laporan)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            laporan.nama,
            laporan.deskripsi,
            laporan.tempat,
            laporan.kategori,
            laporan.tanggal.strftime("%Y-%m-%d"),
            laporan.jenis_laporan
        )
        last_id = database.execute_query(sql, params)
        if last_id is not None:
            laporan.id_laporan = last_id
            return True
        return False

    def get_semua_laporan_obj(self) -> list[Laporan]:
        sql = """
        SELECT id, nama, deskripsi, tempat, kategori, tanggal, jenis_laporan
        FROM laporan
        ORDER BY tanggal DESC, id DESC
        """
        rows = database.fetch_query(sql, fetch_all=True)
        laporan_list = []

        if rows:
            for row in rows:
                laporan = Laporan(
                    nama=row['nama'],
                    deskripsi=row['deskripsi'],
                    tempat=row['tempat'],
                    kategori=row['kategori'],
                    tanggal=row['tanggal'],
                    jenis_laporan=row['jenis_laporan'],
                    id_laporan=row['id']
                )
                laporan_list.append(laporan)
        return laporan_list

    def get_laporan_by_id(self, laporan_id: int) -> Laporan | None:
        """Mengambil satu laporan berdasarkan ID-nya."""
        sql = """
        SELECT id, nama, deskripsi, tempat, kategori, tanggal, jenis_laporan
        FROM laporan
        WHERE id = ?
        """
        row = database.fetch_query(sql, params=(laporan_id,), fetch_all=False)
        if row:
            return Laporan(
                nama=row['nama'],
                deskripsi=row['deskripsi'],
                tempat=row['tempat'],
                kategori=row['kategori'],
                tanggal=row['tanggal'],
                jenis_laporan=row['jenis_laporan'],
                id_laporan=row['id']
            )
        return None


    def get_dataframe_laporan(self, filter_jenis: str | None = None, filter_kategori: str | None = None) -> pd.DataFrame:
        query = "SELECT id, nama, tanggal, kategori, deskripsi, tempat, jenis_laporan FROM laporan WHERE 1=1" # Tambahkan 'id' di sini
        params = []

        if filter_jenis and filter_jenis != "Semua":
            query += " AND jenis_laporan = ?"
            params.append(filter_jenis)
        
        if filter_kategori and filter_kategori != "Semua":
            query += " AND kategori = ?"
            params.append(filter_kategori)

        query += " ORDER BY tanggal DESC, id DESC"
        df = database.get_dataframe(query, params=tuple(params))

        # Jika ingin menampilkan kolom tertentu, sesuaikan di sini
        # Contoh: df = df[['id', 'nama', 'tanggal', 'kategori', 'deskripsi', 'tempat', 'jenis_laporan']]
        return df

    def cari_laporan_berdasarkan_tempat(self, tempat: str) -> list[Laporan]:
        sql = """
        SELECT id,nama, deskripsi, tempat, kategori, tanggal, jenis_laporan
        FROM laporan
        WHERE tempat LIKE ?
        ORDER BY tanggal DESC
        """
        rows = database.fetch_query(sql, params=(f"%{tempat}%",), fetch_all=True)
        laporan_list = []

        if rows:
            for row in rows:
                laporan = Laporan(
                    nama=row['nama'],
                    deskripsi=row['deskripsi'],
                    tempat=row['tempat'],
                    kategori=row['kategori'],
                    tanggal=row['tanggal'],
                    jenis_laporan=row['jenis_laporan'],
                    id_laporan=row['id']
                )
                laporan_list.append(laporan)
        return laporan_list

    def get_laporan_count_by_jenis(self) -> dict:
        sql = "SELECT jenis_laporan, COUNT(*) as count FROM laporan GROUP BY jenis_laporan"
        rows = database.fetch_query(sql)
        return {row['jenis_laporan']: row['count'] for row in rows} if rows else {}

    def get_laporan_count_by_kategori(self) -> dict:
        sql = "SELECT kategori, COUNT(*) as count FROM laporan GROUP BY kategori"
        rows = database.fetch_query(sql)
        return {row['kategori']: row['count'] for row in rows} if rows else {}

    def get_laporan_trend_by_month(self) -> pd.DataFrame:
        sql = "SELECT strftime('%Y-%m', tanggal) as bulan, COUNT(*) as count FROM laporan GROUP BY bulan ORDER BY bulan"
        df = database.get_dataframe(sql)
        return df

    # --- KODE BARU UNTUK EDIT DAN HAPUS ---
    def update_laporan(self, laporan: Laporan) -> bool:
        """Memperbarui laporan yang sudah ada di database."""
        if not isinstance(laporan, Laporan) or laporan.id_laporan is None:
            print("Objek Laporan tidak valid atau ID tidak ada untuk update.")
            return False

        sql = """
        UPDATE laporan
        SET nama = ?, deskripsi = ?, tempat = ?, kategori = ?, tanggal = ?, jenis_laporan = ?
        WHERE id = ?
        """
        params = (
            laporan.nama,
            laporan.deskripsi,
            laporan.tempat,
            laporan.kategori,
            laporan.tanggal.strftime("%Y-%m-%d"),
            laporan.jenis_laporan,
            laporan.id_laporan 
        )
        print("[DEBUG] Data untuk update:")
        print("ID:", laporan.id_laporan)
        print("Nama:", laporan.nama)
        print("Deskripsi:", laporan.deskripsi)
        print("Tempat:", laporan.tempat)
        print("Kategori:", laporan.kategori)
        print("Tanggal:", laporan.tanggal)
        print("Jenis:", laporan.jenis_laporan)

        return database.execute_query(sql, params) is not None
    def hapus_laporan(self, id_laporan: int) -> bool:
        try:
            self.kursor.execute("DELETE FROM laporan WHERE id_laporan = ?", (id_laporan,))
            self.koneksi.commit()
            return self.kursor.rowcount > 0
        except Exception as e:
            print("[ERROR] Gagal menghapus laporan:", e)
            return False
