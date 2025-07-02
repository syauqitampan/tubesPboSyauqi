# model.py
import datetime

class Laporan:
    """Merepresentasikan satu entitas laporan barang (Data Class)."""

    def __init__(self,nama: str, deskripsi: str, tempat: str, kategori: str,
                 tanggal: datetime.date | str, jenis_laporan: str = "Kehilangan",
                 id_laporan: int | None = None):
        self.id_laporan = id_laporan
        self.nama = str(nama) if nama else "Tidak Diketahui"
        self.deskripsi = str(deskripsi) if deskripsi else "Tanpa Deskripsi"
        self.tempat = str(tempat) if tempat else "Tidak Diketahui"
        self.kategori = str(kategori) if kategori else "Lainnya"
        self.jenis_laporan = jenis_laporan if jenis_laporan in ["Kehilangan", "Penemuan"] else "Kehilangan"

        if isinstance(tanggal, datetime.date):
            self.tanggal = tanggal
        elif isinstance(tanggal, str):
            try:
                self.tanggal = datetime.datetime.strptime(tanggal, "%Y-%m-%d").date()
            except ValueError:
                self.tanggal = datetime.date.today()
                print(f"Peringatan: Format tanggal '{tanggal}' salah.")
        else:
            self.tanggal = datetime.date.today()
            print(f"Peringatan: Tipe tanggal '{type(tanggal)}' tidak valid.")

    def __repr__(self) -> str:
        return (
            f"Laporan(ID:{self.id_laporan}, Tgl:{self.tanggal.strftime('%Y-%m-%d')}, "
            f"Tempat:{self.tempat}, Kategori:{self.kategori}, Jenis:{self.jenis_laporan})"
        )

    def to_dict(self) -> dict:
        return {
            "id_laporan": self.id_laporan,
            "deskripsi": self.deskripsi,
            "tempat": self.tempat,
            "kategori": self.kategori,
            "tanggal": self.tanggal.strftime("%Y-%m-%d"),
            "jenis_laporan": self.jenis_laporan
        }
