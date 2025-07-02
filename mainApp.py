# mainApp.py

import streamlit as st
import datetime
import pandas as pd


from model import Laporan
from manajerLaporanBarang import LaporanBarang

# --- Fungsi Login Utama ---
def login_page():
    st.title("Login Aplikasi Pelaporan Barang")

    username = st.text_input("Masukkan Username", key="main_username_input_login_page")
    password = st.text_input("Password", type="password", key="main_password_input_login_page")

    if st.button("Login", key="main_login_button_login_page"):
        if username.lower() == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_role = "admin"
            st.success("Login Admin Berhasil!")
            st.rerun()
        elif username:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_role = "user"
            st.success(f"Selamat datang, {username}! Anda login sebagai Pengguna Umum.")
            st.rerun()
        else:
            st.error("Username tidak boleh kosong.")
            st.info("Silakan masukkan nama Anda untuk melanjutkan sebagai pengguna umum, atau 'admin' dengan password yang benar untuk akses admin.")

# --- Fungsi Admin Login Khusus untuk Operasi Sensitif ---
def admin_login_modal():
    st.markdown("---")
    with st.form(key="admin_auth_form_modal_key", clear_on_submit=True):
        st.subheader("Otentikasi Admin untuk Penghapusan")
        admin_username = st.text_input("Username Admin", key="admin_modal_username_input")
        admin_password = st.text_input("Password Admin", type="password", key="admin_modal_password_input")
        
        col_ok, col_cancel = st.columns(2)
        with col_ok:
            # PASTIKAN key ADA DI SINI
            auth_submitted = st.form_submit_button("Lanjutkan sebagai Admin")
        with col_cancel:
            # PASTIKAN key ADA DI SINI
            auth_canceled = st.form_submit_button("Batal")

        if auth_submitted:
            if admin_username == "admin" and admin_password == "admin123":
                st.session_state.is_admin_for_action = True
                st.session_state.show_admin_modal = False 
                st.success("Otentikasi Admin Berhasil!")
                st.rerun()
            else:
                st.error("Username atau password admin salah.")
        
        if auth_canceled:
            st.session_state.show_admin_modal = False
            st.rerun()


st.set_page_config(
    page_title="Pelaporan Barang Hilang / Ditemukan",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_manajer_laporan():
    return LaporanBarang()

manajer = get_manajer_laporan()

def halaman_tambah_laporan(manajer: LaporanBarang):
    st.header("Tambah Laporan Barang")

    button = st.button("Buka Form Tambah Laporan")
    if not button:
        st.info("Klik tombol di atas untuk membuka form tambah laporan.")
        return
    
    with st.form(key="tambah_laporan_form_main", clear_on_submit=True):
        nama = st.text_input("Nama Pelapor*", placeholder="Contoh: Syauqi", key="tambah_laporan_nama_input")
        deskripsi = st.text_area("Deskripsi*", placeholder="Contoh: Dompet warna hitam berisi KTP dan ATM", key="tambah_laporan_deskripsi_input")
        tempat = st.text_input("Tempat Kejadian*", placeholder="Contoh: Perpustakaan", key="tambah_laporan_tempat_input")
        kategori = st.selectbox("Kategori Barang", ["Dompet", "Kartu Identitas", "Elektronik", "Buku", "Pakaian", "Lainnya"], key="tambah_laporan_kategori_select")
        tanggal = st.date_input("Tanggal Kejadian", value=datetime.date.today(), key="tambah_laporan_tanggal_input")
        jenis_laporan = st.radio("Jenis Laporan", ["Kehilangan", "Penemuan"], key="tambah_laporan_jenis_radio")

        # PASTIKAN key ADA DI SINI
        submitted = st.form_submit_button("Laporkan")
        if submitted:
            if not deskripsi or not tempat:
                st.warning("Deskripsi dan tempat tidak boleh kosong!")
            else:
                laporan = Laporan(
                    nama=nama,
                    deskripsi=deskripsi,
                    tempat=tempat,
                    kategori=kategori,
                    tanggal=tanggal,
                    jenis_laporan=jenis_laporan
                )
                
                print("[DEBUG] Jenis objek laporan:", type(laporan))
                print("[DEBUG] Isi objek laporan:", laporan.to_dict())


                if manajer.tambah_laporan(laporan):
                    st.success("Laporan berhasil ditambahkan.")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Gagal menambahkan laporan.")

def halaman_daftar_laporan(manajer: LaporanBarang):
    st.header(" 📋 Daftar Laporan Barang")
    
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
        st.session_state.laporan_to_edit_id = None
    if 'show_admin_modal' not in st.session_state:
        st.session_state.show_admin_modal = False
    if 'is_admin_for_action' not in st.session_state:
        st.session_state.is_admin_for_action = False
    if 'laporan_to_delete_id' not in st.session_state:
        st.session_state.laporan_to_delete_id = None


    if st.session_state.edit_mode:
        halaman_edit_laporan(manajer, st.session_state.laporan_to_edit_id)
        return

    with st.spinner("Memuat data..."):
        df = manajer.get_dataframe_laporan() # df ini akan punya kolom 'id'
    
    if df.empty:
        st.info("Belum ada laporan yang tercatat.")
    else:
        df_display = df.copy()
        df_display['tanggal'] = pd.to_datetime(df_display['tanggal']).dt.strftime('%d-%m-%Y')
        
        report_options_dict = {
            f"{row['jenis_laporan']} - {row['nama']} - {row['deskripsi']} ({row['tanggal']})": row['id'] 
            for index, row in df_display.iterrows()
        }
        
        display_options = ["Pilih Laporan untuk Detail/Edit/Hapus"] + list(report_options_dict.keys())
        selected_report_display_text = st.selectbox(
            "Pilih Laporan:", 
            options=display_options,
            index=0,
            key="select_report_for_detail_halaman_daftar"
        )
        
        selected_laporan_id = None
        if selected_report_display_text != "Pilih Laporan untuk Detail/Edit/Hapus":
            selected_laporan_id = report_options_dict[selected_report_display_text]
            laporan_detail = manajer.get_laporan_by_id(selected_laporan_id)
            
            if laporan_detail:
                st.subheader(f"Detail Laporan #{laporan_detail.id_laporan}") 
                st.write(f"**Jenis Laporan:** {laporan_detail.jenis_laporan}")
                st.write(f"**Nama Pelapor:** {laporan_detail.nama}")
                st.write(f"**Tanggal Kejadian:** {laporan_detail.tanggal.strftime('%d-%m-%Y')}")
                st.write(f"**Tempat Kejadian:** {laporan_detail.tempat}")
                st.write(f"**Kategori:** {laporan_detail.kategori}")
                st.write(f"**Deskripsi:** {laporan_detail.deskripsi}")
                
                col_edit, col_delete = st.columns(2)
                with col_edit:
                    if st.button("Edit Laporan", key=f"edit_btn_laporan_{selected_laporan_id}"):
                        st.session_state.edit_mode = True
                        st.session_state.laporan_to_edit_id = selected_laporan_id
                        st.rerun()
                
                with col_delete:
                    if st.session_state.get('user_role') == 'admin':
                        if st.button("Hapus Laporan", key=f"delete_btn_laporan_{selected_laporan_id}"):
                            st.session_state.show_admin_modal = True
                            st.session_state.laporan_to_delete_id = selected_laporan_id
                            st.rerun()
                    else:
                        st.info("Hanya Admin yang dapat menghapus laporan.")
                        
                if st.session_state.is_admin_for_action and st.session_state.laporan_to_delete_id == selected_laporan_id:
                    st.session_state.is_admin_for_action = False 
                    st.session_state.show_admin_modal = False
                    
                    if manajer.hapus_laporan(selected_laporan_id): 
                        st.success("Laporan berhasil dihapus oleh Admin.")
                        st.cache_data.clear()
                        del st.session_state.laporan_to_delete_id 
                        st.rerun()
                    else:
                        st.error("Gagal menghapus laporan.")

            else:
                st.error("Laporan tidak ditemukan.")

        st.markdown("---")
        st.subheader("📌 Ringkasan Semua Laporan")
        st.dataframe(df_display.drop(columns=['id']).rename(columns={
            'nama': 'Nama Pelapor',
            'deskripsi': 'Deskripsi',
            'tempat': 'Tempat',
            'kategori': 'Kategori',
            'tanggal': 'Tanggal',
            'jenis_laporan': 'Jenis Laporan'
        }), use_container_width=True)


def halaman_edit_laporan(manajer: LaporanBarang, laporan_id: int):
    laporan_saat_ini = manajer.get_laporan_by_id(laporan_id)
    if not laporan_saat_ini:
        st.error("Laporan tidak ditemukan untuk diedit.")
        st.session_state.edit_mode = False
        st.session_state.laporan_to_edit_id = None
        st.rerun()
        return

    st.header(f"Edit Laporan Barang #{laporan_id}")
    
    kategori_options = ["Dompet", "Kartu Identitas", "Elektronik", "Buku", "Pakaian", "Lainnya"]
    try:
        current_kategori_index = kategori_options.index(laporan_saat_ini.kategori)
    except ValueError:
        current_kategori_index = kategori_options.index("Lainnya")

    with st.form(key=f"edit_laporan_form_id_{laporan_id}", clear_on_submit=False):
        nama = st.text_input("Nama Pelapor*", value=laporan_saat_ini.nama, key=f"edit_laporan_nama_input_{laporan_id}")
        deskripsi = st.text_area("Deskripsi*", value=laporan_saat_ini.deskripsi, key=f"edit_laporan_deskripsi_input_{laporan_id}")
        tempat = st.text_input("Tempat Kejadian*", value=laporan_saat_ini.tempat, key=f"edit_laporan_tempat_input_{laporan_id}")
        kategori = st.selectbox("Kategori Barang", options=kategori_options, index=current_kategori_index, key=f"edit_laporan_kategori_select_{laporan_id}")
        tanggal = st.date_input("Tanggal Kejadian", value=laporan_saat_ini.tanggal, key=f"edit_laporan_tanggal_input_{laporan_id}")
        jenis_laporan = st.radio("Jenis Laporan", ["Kehilangan", "Penemuan"], 
                                 index=0 if laporan_saat_ini.jenis_laporan == "Kehilangan" else 1, key=f"edit_laporan_jenis_radio_{laporan_id}")

        col_submit, col_cancel = st.columns(2)
        with col_submit:
            # PASTIKAN key ADA DI SINI
            submitted = st.form_submit_button("Simpan Perubahan")
        with col_cancel:
            # PASTIKAN key ADA DI SINI
            canceled = st.form_submit_button("Batal")
        if submitted:
            if not deskripsi or not tempat:
                st.warning("Deskripsi dan tempat tidak boleh kosong!")
            else:
                laporan_terupdate = Laporan(
                    id_laporan=laporan_id,
                    nama=nama,
                    deskripsi=deskripsi,
                    tempat=tempat,
                    kategori=kategori,
                    tanggal=tanggal,
                    jenis_laporan=jenis_laporan
                )
                if manajer.update_laporan(laporan_terupdate):
                    st.success("Laporan berhasil diperbarui.")
                    st.session_state.edit_mode = False
                    st.session_state.laporan_to_edit_id = None
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Gagal memperbarui laporan.")
        
        if canceled:
            st.session_state.edit_mode = False
            st.session_state.laporan_to_edit_id = None
            st.rerun()


def halaman_cari_laporan(manajer: LaporanBarang):
    st.header("🔍 Cari Laporan Berdasarkan Tempat 🔍 ")
    tempat_dicari = st.text_input("Masukkan kata kunci tempat:", key="cari_laporan_tempat_input")
    if tempat_dicari:
        hasil = manajer.cari_laporan_berdasarkan_tempat(tempat_dicari)
        if hasil:
            df = pd.DataFrame([lap.to_dict() for lap in hasil]) 
            df['tanggal'] = pd.to_datetime(df['tanggal']).dt.strftime('%d-%m-%Y')
            st.dataframe(df.rename(columns={
                'id_laporan': 'ID Laporan', 
                'nama': 'Nama Pelapor',
                'deskripsi': 'Deskripsi',
                'tempat': 'Tempat',
                'kategori': 'Kategori',
                'tanggal': 'Tanggal',
                'jenis_laporan': 'Jenis Laporan'
            }), use_container_width=True)
        else:
            st.warning("Tidak ditemukan laporan dengan tempat tersebut.")

def halaman_dashboard(manajer: LaporanBarang):
    st.header("📊 Dashboard Statistik Laporan")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Jumlah Laporan per Jenis")
        data_jenis = manajer.get_laporan_count_by_jenis()
        df_jenis = pd.DataFrame(list(data_jenis.items()), columns=['Jenis', 'Jumlah'])
        if not df_jenis.empty:
            st.bar_chart(df_jenis.set_index('Jenis'))
        else:
            st.info("Belum ada data laporan untuk jenis.")

    with col2:
        st.subheader("Jumlah Laporan per Kategori")
        data_kategori = manajer.get_laporan_count_by_kategori()
        df_kategori = pd.DataFrame(list(data_kategori.items()), columns=['Kategori', 'Jumlah'])
        if not df_kategori.empty:
            st.bar_chart(df_kategori.set_index('Kategori'))
        else:
            st.info("Belum ada data laporan untuk kategori.")

    st.subheader("Tren Laporan per Bulan")
    df_trend = manajer.get_laporan_trend_by_month()
    if not df_trend.empty:
        df_trend['bulan'] = pd.to_datetime(df_trend['bulan'])
        df_trend = df_trend.sort_values('bulan')
        df_trend = df_trend.set_index('bulan')
        st.line_chart(df_trend)
    else:
        st.info("Belum ada data untuk tren bulanan.")

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "user_role" not in st.session_state:
        st.session_state.user_role = None

    if not st.session_state.logged_in:
        login_page()
    else:
        st.sidebar.title(f"Selamat datang, {st.session_state.username} ({st.session_state.user_role})!")
        st.sidebar.title("Menu Pelaporan Barang")
        menu = st.sidebar.radio("Pilih Halaman", [
            "Tambah Laporan",
            "Daftar Laporan",
            "Cari Laporan",
            "Dashboard Statistik"
        ], key="sidebar_menu_main")
        st.sidebar.markdown("---")
        st.sidebar.caption("Aplikasi Pelaporan Barang Hilang / Ditemukan")

        if st.session_state.get('show_admin_modal', False):
            admin_login_modal()
        # Perhatikan urutan ini: jika edit_mode aktif, panggil halaman_edit_laporan
        # Ini mencegah menu utama menggambar ulang form edit.
        elif st.session_state.get('edit_mode', False) and st.session_state.get('laporan_to_edit_id') is not None:
            halaman_edit_laporan(manajer, st.session_state.laporan_to_edit_id)
        elif menu == "Tambah Laporan":
            halaman_tambah_laporan(manajer)
        elif menu == "Daftar Laporan":
            halaman_daftar_laporan(manajer)
        elif menu == "Cari Laporan":
            halaman_cari_laporan(manajer)
        elif menu == "Dashboard Statistik":
            halaman_dashboard(manajer)

        st.sidebar.markdown("---")
        if st.sidebar.button("Logout", key="main_logout_button_main"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_role = None
            # Hapus semua state terkait editing/deleting agar bersih saat logout
            if 'edit_mode' in st.session_state:
                del st.session_state.edit_mode
            if 'laporan_to_edit_id' in st.session_state:
                del st.session_state.laporan_to_edit_id
            if 'show_admin_modal' in st.session_state:
                del st.session_state.show_admin_modal
            if 'is_admin_for_action' in st.session_state:
                del st.session_state.is_admin_for_action
            if 'laporan_to_delete_id' in st.session_state:
                del st.session_state.laporan_to_delete_id
            st.success("Anda telah logout.")
            st.rerun()


if __name__ == "__main__":
    main()