import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(page_title="Sistem Dokumentasi Kegiatan", layout="wide")

# File Database (CSV)
DATABASE_FILE = "data_kegiatan.csv"
USER_FILE = "data_users.csv"
FOLDER_FOTO = "saved_images"

# Membuat folder dan file database jika belum ada
if not os.path.exists(FOLDER_FOTO):
    os.makedirs(FOLDER_FOTO)

if not os.path.exists(DATABASE_FILE):
    df = pd.DataFrame(columns=["Tanggal", "Nama Kegiatan", "Kategori", "Detail", "File Dokumentasi"])
    df.to_csv(DATABASE_FILE, index=False)

if not os.path.exists(USER_FILE):
    # Membuat user admin default pertama kali dengan password baru: admin12345
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

# --- SISTEM LOGIN STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = "Publik Belum Login"

# --- SIDEBAR NAVIGASI ---
st.sidebar.title("🧭 Navigasi")

if st.session_state.logged_in:
    st.sidebar.success(f"Halo, {st.session_state.username} ({st.session_state.role})")
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = "Publik Belum Login"
        st.rerun()
else:
    st.sidebar.info("Status: Belum Login (Publik)")

pilihan_menu = ["Tampilan Publik", "Log In / Daftar Akun"]
if st.session_state.logged_in and st.session_state.role == "Admin":
    pilihan_menu.append("Menu Admin (Input Kegiatan)")
    pilihan_menu.append("Manajemen User (Ubah Role)")
elif st.session_state.logged_in and st.session_state.role == "User":
    pilihan_menu.append("Menu User (Akses Khusus)")

menu = st.sidebar.selectbox("Pilih Halaman:", pilihan_menu)

# --- HALAMAN 1: TAMPILAN PUBLIK ---
if menu == "Tampilan Publik":
    st.title("🎬 Galeri & Dokumentasi Kegiatan")
    st.write("Semua orang (Publik & Terdaftar) bisa melihat dokumentasi di bawah ini.")
    st.markdown("---")
    
    df_kegiatan = pd.read_csv(DATABASE_FILE)
    if df_kegiatan.empty:
        st.info("Belum ada kegiatan yang didokumentasikan.")
    else:
        for index, row in df_kegiatan.iterrows():
            with st.container():
                col1, col2 = st.columns([1, 2])
                with col1:
                     file_path = row["File Dokumentasi"]
                     # Cek apakah ada file dokumentasi yang tersimpan
                     if pd.notna(file_path) and os.path.exists(str(file_path)):
                         if str(file_path).endswith(('.mp4', '.mov', '.avi')):
                             st.video(str(file_path))
                         else:
                             st.image(str(file_path), use_container_width=True)
                     else:
                         # Tampilan jika admin memilih tidak mengupload foto/video
                         st.info("📌 Hanya Catatan Teks (Tanpa Media)")
                with col2:
                    st.subheader(row["Nama Kegiatan"])
                    st.caption(f"📅 Tanggal: {row['Tanggal']} | 🏷️ Kategori: {row['Kategori']}")
                    st.write(row["Detail"])
                st.markdown("---")

# --- HALAMAN 2: LOG IN / DAFTAR AKUN ---
elif menu == "Log In / Daftar Akun":
    st.title("🔐 Akses Akun Pengguna")
    tab1, tab2 = st.tabs(["Masuk (Log In)", "Daftar Akun Baru (Publik)"])
    
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
                st.success(f"Berhasil Login sebagai {st.session_state.username}!")
                st.rerun()
            else:
                st.error("Username atau Password salah!")
                
    with tab2:
        st.subheader("Form Pendaftaran User Publik")
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

# --- HALAMAN 3: MENU ADMIN (INPUT KEGIATAN) ---
elif menu == "Menu Admin (Input Kegiatan)":
    st.title("➕ Tambah Dokumentasi Kegiatan Baru (Akses Admin)")
    
    with st.form("form_admin", clear_on_submit=True):
        nama = st.text_input("Nama Kegiatan/Catatan:")
        kategori = st.selectbox("Kategori:", ["Kegiatan Utama", "Catatan Harian", "Dokumentasi Project"])
        tanggal = st.date_input("Tanggal Kegiatan:", datetime.now())
        detail = st.text_area("Detail Keterangan Kegiatan:")
        
        # Sifatnya opsional sekarang
        uploaded_file = st.file_uploader("Upload Foto/Video Dokumentasi (Boleh Dikosongkan):", type=["png", "jpg", "jpeg", "mp4"])
        
        if st.form_submit_button("Simpan & Publikasikan"):
            if nama: # Sekarang hanya nama kegiatan yang wajib diisi
                file_path = "" # Default kosong jika tidak upload file
                
                if uploaded_file is not None:
                    file_path = os.path.join(FOLDER_FOTO, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                new_data = {
                    "Tanggal": [tanggal.strftime("%Y-%m-%d")], "Nama Kegiatan": [nama],
                    "Kategori": [kategori], "Detail": [detail], "File Dokumentasi": [file_path]
                }
                pd.DataFrame(new_data).to_csv(DATABASE_FILE, mode='a', header=False, index=False)
                st.success(f"Sukses mempublikasikan kegiatan!")
            else:
                st.error("Nama kegiatan wajib diisi.")

# --- HALAMAN 4: MANAJEMEN USER ---
elif menu == "Manajemen User (Ubah Role)":
    st.title("👥 Halaman Manajemen Pengguna (Akses Admin)")
    df_users = baca_users()
    st.dataframe(df_users[["username", "email", "role"]])
    
    st.markdown("---")
    st.subheader("Ubah Role Pengguna")
    list_username = df_users["username"].tolist()
    if "admin" in list_username: list_username.remove("admin") 
    
    if len(list_username) == 0:
        st.info("Belum ada user publik lain yang mendaftar.")
    else:
        pilih_user = st.selectbox("Pilih Username yang ingin diubah rolenya:", list_username)
        role_baru = st.radio("Pilih Role Akses Baru:", ["User", "Admin"])
        
        if st.button("Terapkan Perubahan Role"):
            df_users.loc[df_users['username'] == pilih_user, 'role'] = role_baru
            simpan_users(df_users)
            st.success(f"Berhasil! Akun '{pilih_user}' sekarang menjadi **{role_baru}**.")
            st.rerun()