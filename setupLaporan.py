# setup_laporan_db.py

import sqlite3
import os
from konfigurasi import DB_PATH

def setup_database():
    print(f"Memeriksa/membuat database di {DB_PATH}")
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        sql_create_table = """
        CREATE TABLE IF NOT EXISTS laporan (
            id_laporan INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            deskripsi TEXT NOT NULL,
            tempat TEXT NOT NULL,
            kategori TEXT,
            tanggal DATE NOT NULL,
            jenis_laporan TEXT NOT NULL CHECK (jenis_laporan IN ('Kehilangan', 'Penemuan'))
        );
        """

        print("Membuat tabel 'laporan' (jika belum ada)...")
        cursor.execute(sql_create_table)
        conn.commit()
        print(" -> Tabel 'laporan' siap.")
        return True
    except sqlite3.Error as e:
        print(f" -> Error: SQLite saat setup: {e}")
        return False
    finally:
        if conn:
            conn.close()
            print(" -> Koneksi ke DB setup ditutup.")

if __name__ == "__main__":
    print("--- Memulai Setup Database Laporan Barang Hilang ---")
    if setup_database():
        print(f"\nSetup database '{os.path.basename(DB_PATH)}' selesai.")
    else:
        print("\nSetup database gagal.")
    print("--- Selesai Setup Database ---")
