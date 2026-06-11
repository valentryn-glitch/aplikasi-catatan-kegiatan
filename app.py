import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Konfigurasi Halaman
st.set_page_config(page_title="Sistem Dokumentasi Privat Pro v2", layout="wide")

# File Database (CSV) - Menggunakan V2 agar terhindar dari error bentrok kolom sebelumnya
DATABASE_FILE = "data_kegiatan_v2.csv"
USER_FILE = "data_users_v2.csv"
FOLDER_FOTO = "saved_images"

# Membuat folder dan file database jika belum ada
if not os.path.exists(FOLDER_FOTO):
    os.makedirs(FOLDER_FOTO)

if not os.path.exists(DATABASE_FILE):
    df = pd.DataFrame(columns=["ID", "Tanggal", "Nama Kegiatan", "Kategori", "Detail", "File Dokumentasi", "Waktu_Upload", "Masa_Berlaku_Menit", "Oleh_Admin"])
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
    # Siapa pun yang sudah login (User baru maupun Admin) BISA melihat menu utama ini
    pilihan_menu.append("🎬 Catatan & Dokumentasi Aktif")
    
    # Menu khusus ADMIN saja
    if st.session_state.role == "Admin":
        pilihan_menu.append("➕ Input & Hapus Catatan")
        pilihan_menu.append("📜 History Semua Catatan")
        pilihan_menu.append("👥 Manajemen User & Password")

menu = st.sidebar.selectbox("Pilih Halaman:", pilihan_menu)

# --- HALAMAN 1: LOG IN / DAFTAR AKUN ---
if menu == "Log In / Daftar Akun":
    st.title("🔐 Akses Masuk Sistem")
    st.write("Silakan masuk atau daftar akun baru untuk melihat dokumentasi kegiatan.")
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
        st.subheader("Form Pendaftaran Akun (Publik)")
        reg_user = st.text_input("Buat Username (Tanpa Spasi):", key="reg_user")
        reg_gmail = st.text_input("Masukkan Gmail Anda:", key="reg_gmail")
        reg_pass = st.text_input("Buat Password Anda:", type="password", key="reg_pass")
        
        if st.button("Daftar Sekarang"):
            if reg_user and reg_gmail and reg_pass:
                df_users = baca_users()
                if reg_user in df_users['username'].values:
                    st.error("Username sudah terdaftar! Gunakan nama lain.")
                else:
                    # Setiap orang mendaftar otomatis mendapat role 'User' dan BISA langsung melihat catatan aktif setelah login
                    new_user = {"username": reg_user, "email": reg_gmail, "password": reg_pass, "role": "User"}
                    df_users = pd.concat([df_users, pd.DataFrame([new_user])], ignore_index=True)
                    simpan_users(df_users)
                    st.success("Pendaftaran Berhasil! Silakan masuk menggunakan tab 'Masuk (Log In)'.")
            else:
                st.error("Semua kolom pendaftaran wajib diisi!")

# --- HALAMAN 2: CATATAN AKTIF (Bisa dilihat oleh User baru & Admin selama Timer masih ada) ---
elif menu == "🎬 Catatan & Dokumentasi Aktif":
    st.title("🎬 Galeri Kegiatan & Catatan Aktif")
    st.write(f"Halo **{st.session_state.username}**, berikut adalah catatan kegiatan internal saat ini:")
    st.markdown("---")
    
    df_kegiatan = baca_kegiatan()
    
    if df_kegiatan.empty:
        st.info("Belum ada catatan kegiatan saat ini.")
    else:
        waktu_sekarang = datetime.now()
        ada_catatan_aktif = False
        
        for index, row in df_kegiatan.iterrows():
            waktu_upload = datetime.strptime(row["Waktu_Upload"], "%Y-%m-%d %H:%M:%S")
            masa_berlaku_menit = int(row["Masa_Berlaku_Menit"])
            waktu_kadaluarsa = waktu_upload + timedelta(minutes=masa_berlaku_menit)
            
            # Tampilkan hanya yang BELUM kadaluarsa
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
                        st.caption(f"📅 Tanggal: {row['Tanggal']} | 🏷️ Kategori: {row['Kategori']}")
                        st.warning(f"⏳ **Sisa Waktu Tampil:** {sisa_jam} Jam {sisa_menit} Menit lagi (Hingga: {waktu_kadaluarsa.strftime('%H:%M:%S')})")
                        st.write(row["Detail"])
                    st.markdown("---")
        
        if not ada_catatan_aktif:
            st.info("Saat ini tidak ada catatan aktif yang bisa dilihat. Semua catatan sebelumnya telah melewati batas durasi tampil publik.")

# --- HALAMAN 3: INPUT & HAPUS CATATAN (KHUSUS ADMIN) ---
elif menu == "➕ Input & Hapus Catatan":
    st.title("🛠️ Pusat Kontrol Catatan (Akses Admin)")
    tab_input, tab_hapus = st.tabs(["➕ Tambah Catatan Baru", "🗑️ Hapus Catatan Permanen"])
    
    with tab_input:
        with st.form("form_admin", clear_on_submit=True):
            nama = st.text_input("Nama Kegiatan/Catatan:")
            kategori = st.selectbox("Kategori:", ["Kegiatan Utama", "Catatan Harian", "Dokumentasi Project"])
            tanggal = st.date_input("Tanggal Kegiatan:", datetime.now())
            detail = st.text_area("Detail Keterangan:")
            uploaded_file = st.file_uploader("Upload Media (Opsional):", type=["png", "jpg", "jpeg", "mp4"])
            
            st.markdown("### ⏱️ Durasi Tampilan Publik")
            col_j, col_m = st.columns(2)
            with col_j: durasi_jam = st.number_input("Jam:", min_value=0, max_value=72, value=1)
            with col_m: durasi_menit = st.number_input("Menit:", min_value=0, max_value=59, value=0)
            
            if st.form_submit_button("Publikasikan"):
                if nama:
                    total_menit = (durasi_jam * 60) + durasi_menit
                    if total_menit == 0:
                        st.error("Durasi tidak boleh 0 menit!")
                    else:
                        file_path = ""
                        if uploaded_file is not None:
                            file_path = os.path.join(FOLDER_FOTO, uploaded_file.name)
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                        
                        waktu_sekarang_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        id_unik = str(int(datetime.now().timestamp()))
                        
                        new_data = {
                            "ID": [id_unik], "Tanggal": [tanggal.strftime("%Y-%m-%d")],
                            "Nama Kegiatan": [nama], "Kategori": [kategori], "Detail": [detail],
                            "File Dokumentasi": [file_path], "Waktu_Upload": [waktu_sekarang_str],
                            "Masa_Berlaku_Menit": [total_menit], "Oleh_Admin": [st.session_state.username]
                        }
                        df_keg = baca_kegiatan()
                        df_keg = pd.concat([df_keg, pd.DataFrame(new_data)], ignore_index=True)
                        simpan_kegiatan(df_keg)
                        st.success("Catatan berhasil disimpan dan dipublikasikan!")
                        st.rerun()
                else:
                    st.error("Nama catatan wajib diisi!")
                    
    with tab_hapus:
        st.subheader("Hapus dari Database")
        df_keg = baca_kegiatan()
        if df_keg.empty:
            st.info("Database kosong.")
        else:
            pilihan_hapus = {f"{r['Tanggal']} - {r['Nama Kegiatan']} (ID: {r['ID']})": r['ID'] for idx, r in df_keg.iterrows()}
            catatan_dipilih = st.selectbox("Pilih catatan untuk dihapus total:", list(pilihan_hapus.keys()))
            if st.button("Hapus Permanen", type="primary"):
                df_keg_baru = df_keg[df_keg['ID'].astype(str) != str(pilihan_hapus[catatan_dipilih])]
                simpan_kegiatan(df_keg_baru)
                st.success("Berhasil dihapus dari database!")
                st.rerun()

# --- HALAMAN 4: HISTORY CATATAN (KHUSUS ADMIN - MELIHAT SEMUA DATA TERMASUK YANG KADALUARSA) ---
elif menu == "📜 History Semua Catatan":
    st.title("📜 Riwayat Seluruh Catatan Kegiatan (Akses Admin)")
    st.write("Halaman ini menampilkan seluruh catatan yang pernah dibuat, termasuk catatan yang timernya sudah habis di halaman user/publik.")
    st.markdown("---")
    
    df_kegiatan = baca_kegiatan()
    
    if df_kegiatan.empty:
        st.info("Belum ada riwayat catatan di database.")
    else:
        # Menampilkan tabel ringkasan data mentah agar admin mudah memantau
        st.subheader("📊 Tabel Data Riwayat")
        st.dataframe(df_kegiatan[["ID", "Tanggal", "Nama Kegiatan", "Kategori", "Waktu_Upload", "Masa_Berlaku_Menit", "Oleh_Admin"]], use_container_width=True)
        st.markdown("---")
        
        # Menampilkan bentuk visual list ke bawah
        st.subheader("📂 Detail Tampilan Riwayat")
        waktu_sekarang = datetime.now()
        
        for index, row in df_kegiatan.iterrows():
            waktu_upload = datetime.strptime(row["Waktu_Upload"], "%Y-%m-%d %H:%M:%S")
            masa_berlaku_menit = int(row["Masa_Berlaku_Menit"])
            waktu_kadaluarsa = waktu_upload + timedelta(minutes=masa_berlaku_menit)
            
            # Cek status untuk label
            if waktu_sekarang >= waktu_kadaluarsa:
                status_label = "🔴 KADALUARSA (User biasa tidak bisa lihat lagi)"
            else:
                status_label = "🟢 AKTIF (Masih tayang di halaman user)"
                
            with st.container():
                st.markdown(f"### **{row['Nama Kegiatan']}**")
                st.caption(f"🆔 ID: {row['ID']} | 📅 Tanggal: {row['Tanggal']} | 👤 Diinput Oleh: {row['Oleh_Admin']}")
                st.info(f"📊 **Status:** {status_label} | 🕒 Di-upload pada: {row['Waktu_Upload']} (Masa Tayang: {row['Masa_Berlaku_Menit']} Menit)")
                st.write(f"**Isi Catatan:** {row['Detail']}")
                st.markdown("---")

# --- HALAMAN 5: MANAJEMEN USER & PASSWORD ---
elif menu == "👥 Manajemen User & Password":
    st.title("👥 Manajemen Pengguna & Intip Password")
    df_users = baca_users()
    st.dataframe(df_users[["username", "email", "password", "role"]], use_container_width=True)
    
    st.markdown("---")
    st.subheader("Ubah Role Akses")
    list_username = df_users["username"].tolist()
    if "admin" in list_username: list_username.remove("admin") 
    
    if len(list_username) == 0:
        st.info("Belum ada user lain yang mendaftar.")
    else:
        pilih_user = st.selectbox("Pilih Username:", list_username)
        role_baru = st.radio("Pilih Role Baru:", ["User", "Admin"])
        if st.button("Terapkan Perubahan"):
            df_users.loc[df_users['username'] == pilih_user, 'role'] = role_baru
            simpan_users(df_users)
            st.success(f"Akun '{pilih_user}' sekarang sukses menjadi **{role_baru}**.")
            st.rerun()