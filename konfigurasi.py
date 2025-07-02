import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NAMA_DB = 'laporan_barang.db'
DB_PATH = os.path.join(BASE_DIR, NAMA_DB)
KATEGORI_KEHILANGAN = ["Hanphone", "Dompet", "SIM", "STNK", "KTP", "Kunci", "Uang", "Lainnya" ]
KATEGORI_DEFAULT = "Lainnya"