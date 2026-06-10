import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Konfigurasi Halaman
st.set_page_config(page_title="Sistem Dokumentasi Privat Pro", layout="wide")

# File Database (CSV)
DATABASE_FILE = "data_kegiatan_v2.csv"
USER_FILE = "data_users_v2.csv"
FOLDER_FOTO = "saved_images"

# Membuat folder dan file database jika belum ada
if not os.path.exists(FOLDER_FOTO):
    os.makedirs(FOLDER_FOTO)

if not os.path.exists(DATABASE_FILE):
    # Menambahkan kolom 'Waktu_Upload' dan 'Masa_Berlaku_Menit' untuk fitur timer
    df = pd.DataFrame(columns=["ID", "Tanggal", "Nama Kegiatan", "Kategori", "Detail", "File Dokumentasi", "Waktu_Upload", "Masa_Berlaku_Menit"])
    df.to_csv(DATABASE_FILE, index=False)

if not os.path.exists(USER_FILE):
    df_user = pd.DataFrame([{
        "username": "admin",
        "email": "admin@email.com",
        "password": "admin12345",
        "role": "Admin"
    }])
    df_user.to_csv(USER_FILE, index=False)

# --- FUNGSI DATABASE USER ---
def baca_users():
    return pd.read_csv(USER_FILE)

def simpan_users(df):
    df.to_csv(USER_FILE, index=False)

# --- FUNGSI DATABASE KEGIATAN ---
def baca_kegiatan():
    return pd.read_csv(DATABASE_FILE)

def simpan_kegiatan(df):
    df.to_csv(DATABASE_FILE, index=False)

# --- SISTEM LOGIN STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = "Belum Login"

# --- SIDEBAR NAVIGASI ---
st.sidebar.title("🧭 Navigasi")

if st.session_state.logged_in:
    st.sidebar.success(f"Halo, {st.session_state.username} ({st.session_state.role})")
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = "Belum Login"
        st.rerun()
else:
    st.sidebar.info("Status: Belum Login")

pilihan_menu = []
if not st.session_state.logged_in:
    pilihan_menu = ["Log In / Daftar Akun"]
else:
    pilihan_menu.append("Daftar & Dokumentasi Kegiatan")
    if st.session_state.role == "Admin":
        pilihan_menu.append("Menu Admin (Input & Hapus)")
        pilihan_menu.append("Manajemen User & Password")

menu = st.sidebar.selectbox("Pilih Halaman:", pilihan_menu)

# --- HALAMAN 1: LOG IN / DAFTAR AKUN ---
if menu == "Log In / Daftar Akun":
    st.title("🔐 Akses Masuk Sistem")
    st.write("Anda harus masuk atau mendaftar akun terlebih dahulu untuk melihat dokumentasi kegiatan.")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Masuk (Log In)", "Daftar Akun Baru"])
    
    with tab1:
        st.subheader("Silakan Log In")
        input_user = st.text_input("Username:", key="login_user")
        input_pass = st.text_input("Password:", type="password", key="login_pass")
        
        if st.button("Log In"):
            df_users = baca_users()
            user_cocok = df_users[(df_users['username'] == input_user) & (df_users['password'] == input_pass)]
            if not user_cocok.empty:
                st.session_state.logged_in = True
                st.session_state.username = input_user
                st.session_state.role = user_cocok.iloc[0]['role']
                st.success(f"Berhasil Login! Selamat datang {st.session_state.username}.")
                st.rerun()
            else:
                st.error("Username atau Password salah!")
                
    with tab2:
        st.subheader("Form Pendaftaran Akun")
        reg_user = st.text_input("Buat Username (Tanpa Spasi):", key="reg_user")
        reg_gmail = st.text_input("Masukkan Gmail Anda:", key="reg_gmail")
        reg_pass = st.text_input("Buat Password Anda:", type="password", key="reg_pass")
        
        if st.button("Daftar Sekarang"):
            if reg_user and reg_gmail and reg_pass:
                df_users = baca_users()
                if reg_user in df_users['username'].values:
                    st.error("Username sudah terdaftar! Gunakan nama lain.")
                else:
                    new_user = {"username": reg_user, "email": reg_gmail, "password": reg_pass, "role": "User"}
                    df_users = pd.concat([df_users, pd.DataFrame([new_user])], ignore_index=True)
                    simpan_users(df_users)
                    st.success("Pendaftaran Berhasil! Silakan log in di tab 'Masuk'.")
            else:
                st.error("Semua kolom pendaftaran wajib diisi!")

# --- HALAMAN 2: DAFTAR KEGIATAN (DENGAN ESTIMASI & AUTO HIDDEN TIMER) ---
elif menu == "Daftar & Dokumentasi Kegiatan":
    st.title("🎬 Galeri & Dokumentasi Kegiatan Internal")
    st.write(f"Logged in sebagai: **{st.session_state.username}** ({st.session_state.role})")
    st.markdown("---")
    
    df_kegiatan = baca_kegiatan()
    
    if df_kegiatan.empty:
        st.info("Belum ada kegiatan yang didokumentasikan saat ini.")
    else:
        waktu_sekarang = datetime.now()
        ada_catatan_aktif = False
        
        for index, row in df_kegiatan.iterrows():
            # Mengubah string waktu upload kembali menjadi objek datetime
            waktu_upload = datetime.strptime(row["Waktu_Upload"], "%Y-%m-%d %H:%M:%S")
            masa_berlaku_menit = int(row["Masa_Berlaku_Menit"])
            waktu_kadaluarsa = waktu_upload + timedelta(minutes=masa_berlaku_menit)
            
            # FITUR FILTER TIMER: Jika waktu sekarang belum melewati batas kadaluarsa, tampilkan!
            if waktu_sekarang < waktu_kadaluarsa:
                ada_catatan_aktif = True
                sisa_waktu = waktu_kadaluarsa - waktu_sekarang
                sisa_jam = sisa_waktu.seconds // 3600
                sisa_menit = (sisa_waktu.seconds % 3600) // 60
                
                with st.container():
                    col1, col2 = st.columns([1, 2])
                    with col1:
                         file_path = row["File Dokumentasi"]
                         if pd.notna(file_path) and os.path.exists(str(file_path)) and str(file_path) != "":
                             if str(file_path).endswith(('.mp4', '.mov', '.avi')):
                                 st.video(str(file_path))
                             else:
                                 st.image(str(file_path), use_container_width=True)
                         else:
                             st.info("📌 Hanya Catatan Teks (Tanpa Media)")
                    with col2:
                        st.subheader(row["Nama Kegiatan"])
                        st.caption(f"📅 Tanggal Kegiatan: {row['Tanggal']} | 🏷️ Kategori: {row['Kategori']}")
                        
                        # Menampilkan estimasi sisa waktu tampil ke publik
                        st.warning(f"⏳ **Estimasi Tampilan Publik:** Catatan ini otomatis hilang dalam **{sisa_jam} Jam {sisa_menit} Menit** lagi. (Akan otomatis hilang pada: {waktu_kadaluarsa.strftime('%H:%M:%S')})")
                        
                        st.write(row["Detail"])
                    st.markdown("---")
        
        if not ada_catatan_aktif:
            st.info("Semua catatan kegiatan sebelumnya telah habis masa berlakunya (kadaluarsa) untuk publik.")

# --- HALAMAN 3: MENU ADMIN (INPUT & HAPUS KEGIATAN) ---
elif menu == "Menu Admin (Input & Hapus)":
    st.title("🛠️ Menu Kontrol Catatan & Kegiatan (Akses Admin)")
    
    tab_input, tab_hapus = st.tabs(["➕ Input Catatan Baru", "🗑️ Hapus Catatan"])
    
    with tab_input:
        with st.form("form_admin", clear_on_submit=True):
            nama = st.text_input("Nama Kegiatan/Catatan:")
            kategori = st.selectbox("Kategori:", ["Kegiatan Utama", "Catatan Harian", "Dokumentasi Project"])
            tanggal = st.date_input("Tanggal Kegiatan:", datetime.now())
            detail = st.text_area("Detail Keterangan Kegiatan:")
            uploaded_file = st.file_uploader("Upload Foto/Video Dokumentasi (Boleh Dikosongkan):", type=["png", "jpg", "jpeg", "mp4"])
            
            st.markdown("### ⏱️ Pengaturan Durasi Tampilan Publik")
            st.write("Atur berapa lama catatan ini boleh dilihat oleh publik/user setelah di-upload:")
            col_jam, col_menit = st.columns(2)
            with col_jam:
                durasi_jam = st.number_input("Durasi (Jam):", min_value=0, max_value=72, value=1, step=1)
            with col_menit:
                durasi_menit = st.number_input("Durasi (Menit):", min_value=0, max_value=59, value=0, step=1)
            
            if st.form_submit_button("Simpan & Publikasikan"):
                if nama:
                    # Hitung total durasi dalam menit
                    total_menit = (durasi_jam * 60) + durasi_menit
                    if total_menit == 0:
                        st.error("Durasi tampilan tidak boleh 0 jam 0 menit!")
                    else:
                        file_path = ""
                        if uploaded_file is not None:
                            file_path = os.path.join(FOLDER_FOTO, uploaded_file.name)
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                        
                        waktu_sekarang_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        id_unik = str(int(datetime.now().timestamp()))
                        
                        new_data = {
                            "ID": [id_unik],
                            "Tanggal": [tanggal.strftime("%Y-%m-%d")],
                            "Nama Kegiatan": [nama],
                            "Kategori": [kategori],
                            "Detail": [detail],
                            "File Dokumentasi": [file_path],
                            "Waktu_Upload": [waktu_sekarang_str],
                            "Masa_Berlaku_Menit": [total_menit]
                        }
                        
                        df_kegiatan = baca_kegiatan()
                        df_kegiatan = pd.concat([df_kegiatan, pd.DataFrame(new_data)], ignore_index=True)
                        simpan_kegiatan(df_kegiatan)
                        st.success(f"Sukses mempublikasikan catatan kegiatan dengan durasi tampil {durasi_jam} jam {durasi_menit} menit!")
                        st.rerun()
                else:
                    st.error("Nama kegiatan wajib diisi.")
                    
    with tab_hapus:
        st.subheader("Hapus Catatan Secara Manual")
        df_kegiatan = baca_kegiatan()
        
        if df_kegiatan.empty:
            st.info("Tidak ada catatan untuk dihapus.")
        else:
            # Membuat list pilihan untuk drop-down hapus data
            pilihan_hapus = {}
            for idx, r in df_kegiatan.iterrows():
                pilihan_hapus[f"{r['Tanggal']} - {r['Nama Kegiatan']} (ID: {r['ID']})"] = r['ID']
                
            catatan_dipilih = st.selectbox("Pilih catatan yang ingin dihapus Permanen:", list(pilihan_hapus.keys()))
            id_hapus = pilihan_hapus[catatan_dipilih]
            
            if st.button("Hapus Catatan Sekarang", type="primary"):
                # Menghapus baris berdasarkan ID yang dipilih
                df_kegiatan_baru = df_kegiatan[df_kegiatan['ID'].astype(str) != str(id_hapus)]
                simpan_kegiatan(df_kegiatan_baru)
                st.success("Catatan tersebut berhasil dihapus dari database!")
                st.rerun()

# --- HALAMAN 4: MANAJEMEN USER & PASSWORD (PASSWORD TERLIHAT OLEH ADMIN) ---
elif menu == "Manajemen User & Password":
    st.title("👥 Halaman Manajemen Pengguna (Akses Admin)")
    st.write("Di halaman ini Admin dapat mengubah peran akun serta melihat Password pengguna yang terdaftar.")
    
    df_users = baca_users()
    
    st.subheader("Daftar User Terdaftar & Password")
    # Menampilkan tabel lengkap termasuk kolom password asli
    st.dataframe(df_users[["username", "email", "password", "role"]], use_container_width=True)
    
    st.markdown("---")
    st.subheader("Ubah Peran / Role Akses Pengguna")
    list_username = df_users["username"].tolist()
    if "admin" in list_username: 
        list_username.remove("admin") 
    
    if len(list_username) == 0:
        st.info("Belum ada user lain yang mendaftar.")
    else:
        pilih_user = st.selectbox("Pilih Username yang ingin diubah rolenya:", list_username)
        role_baru = st.radio("Pilih Role Akses Baru:", ["User", "Admin"])
        
        if st.button("Terapkan Perubahan Role"):
            df_users.loc[df_users['username'] == pilih_user, 'role'] = role_baru
            simpan_users(df_users)
            st.success(f"Berhasil! Akun '{pilih_user}' sekarang memiliki hak akses sebagai **{role_baru}**.")
            st.rerun()