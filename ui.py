"""
Nama File: ui.py
Deskripsi: Kelas StreamlitUI (View).
Bertanggung jawab untuk merender semua komponen antarmuka (UI) 
dan menangkap interaksi pengguna. Sesuai Tabel IV-12, No. 2.
"""

import streamlit as st
from handler import SistemHandler
import time

class StreamlitUI:
    def __init__(self):
        # Inisialisasi handler sebagai atribut, sesuai Class Diagram
        # Ini akan otomatis menginisialisasi semua kelas lain di backend
        if "handler" not in st.session_state:
            st.session_state.handler = SistemHandler()
            print("SistemHandler diinisialisasi")

        # Inisialisasi session state untuk menyimpan input dan output
        if "teks_input" not in st.session_state:
            st.session_state.teks_input = ""
        if "teks_output" not in st.session_state:
            st.session_state.teks_output = ""
        if "info_proses" not in st.session_state:
            st.session_state.info_proses = ""
        if "error" not in st.session_state:
            st.session_state.error = ""
        
        # Ambil handler dari session state
        self.handler = st.session_state.handler

    def _handle_tombol_summarize(self):
        # Method ini dipanggil saat tombol 'Summarize' ditekan
        self.handler.teks_input_saat_ini = st.session_state.teks_input
        st.session_state.teks_output = ""
        st.session_state.info_proses = ""
        st.session_state.error = ""
        
        # Menggunakan st.empty() untuk loading yang lebih handal
        loading_placeholder = st.empty()
        
        try:
            loading_placeholder.info("⏳ Sedang meringkas... Silakan tunggu.")
            
            start_time = time.time()
            # Panggil handler untuk menjalankan peringkasan
            hasil, info = self.handler.jalankan_peringkasan()
            end_time = time.time()
            
            loading_placeholder.empty() # Hapus pesan loading
            
            waktu_proses = end_time - start_time
            
            st.session_state.teks_output = hasil
            st.session_state.info_proses = f"Ringkasan dihasilkan dalam {waktu_proses:.2f} detik. {info}"
        
        except Exception as e:
            loading_placeholder.empty() # Hapus pesan loading jika error
            # Menampilkan pesan error (sesuai Skenario IV-9, Alternatif 2b)
            st.session_state.error = f"Terjadi kesalahan saat memproses ringkasan: {str(e)}"
            st.error(st.session_state.error)

    # --- PERBAIKAN 1: FUNGSI _handle_upload_pdf ---
    def _handle_upload_pdf(self):
        # AMBIL FILE DARI SESSION STATE MENGGUNAKAN KEY
        file_pdf = st.session_state.pdf_file_uploader
        
        # INI ADALAH PENJAGA (GUARD) YANG PALING PENTING
        # Jika fungsi ini terpicu karena file dihapus (menjadi None),
        # kita langsung berhenti di sini.
        if file_pdf is None:
            return

        # Jika file ADA, baru kita proses
        st.session_state.error = ""
        st.session_state.teks_output = ""
        st.session_state.info_proses = ""
        
        # Menampilkan indikator loading (sesuai Skenario IV-8, Alternatif)
        with st.spinner("Mengekstrak teks dari PDF..."):
            try:
                # Panggil handler untuk memproses PDF
                teks_dari_pdf, sukses = self.handler.proses_upload_pdf(file_pdf)
                if sukses:
                    st.session_state.teks_input = teks_dari_pdf
                else:
                    # Menampilkan pesan error (sesuai Skenario IV-8, Alternatif 2a)
                    st.session_state.error = teks_dari_pdf
                    st.session_state.teks_input = "" # Kosongkan text area jika gagal
            
            except Exception as e:
                st.session_state.error = f"Gagal memproses file PDF: {str(e)}"
                st.session_state.teks_input = ""
    # --- AKHIR PERBAIKAN 1 ---

    def _handle_tombol_clear(self):
        # Method ini mengosongkan semua state
        st.session_state.teks_input = ""
        st.session_state.teks_output = ""
        st.session_state.info_proses = ""
        st.session_state.error = ""

    def render_halaman_utama(self):
        # --- Bagian 1: Judul dan Petunjuk ---
        st.set_page_config(page_title="Aplikasi Peringkasan Teks Berita", layout="wide")
        st.title("Aplikasi Peringkasan Teks Berita")
        st.markdown("Selamat datang! Silahkan masukkan teks berita berbahasa Inggris di bawah ini untuk diringkas")
        st.divider()

        # --- Bagian 2: Metode Input (Sesuai Gambar IV-6) ---
        
        # Metode Input 1: Teks Langsung
        st.subheader("Metode Input 1 : Input Teks Langsung")
        
        # Gunakan st.session_state.teks_input sebagai value dari text_area
        # Ini penting agar text_area bisa di-update oleh proses upload PDF
        teks_area = st.text_area(
            "Ketik atau tempel (paste) teks berita Anda di sini...",
            value=st.session_state.teks_input,
            height=300,
            # Kita beri 'key' agar bisa diakses, tapi callback 'on_change' lebih baik
        )
        
        # Update session state setiap kali user mengetik
        st.session_state.teks_input = teks_area
        
        # Hitung token/karakter (Sesuai Skenario IV-8, langkah 4)
        # Ini hanya estimasi kasar, tokenizer asli ada di backend
        panjang_teks = len(st.session_state.teks_input.split())
        st.caption(f"Estimasi: {panjang_teks} kata. (Maksimal ~512 token, teks akan dipotong otomatis)")

        # --- PERBAIKAN 2: PEMANGGILAN st.file_uploader ---
        st.subheader("Metode Input 2 : Upload File PDF")
        st.file_uploader(
            "Upload PDF", 
            type=["pdf"], 
            on_change=self._handle_upload_pdf, 
            key="pdf_file_uploader" # HARUS PAKAI KEY, HAPUS ARGS
        )
        # --- AKHIR PERBAIKAN 2 ---

        st.divider()

        # --- Bagian 3: Tombol Aksi ---
        col1, col2, col_spacer = st.columns([1, 1, 5])

        with col1:
            # Tombol 'Summarize' di-disable jika teks_input kosong
            # Ini 100% sesuai Skenario IV-8, Kondisi Awal
            is_disabled = st.session_state.teks_input == ""
            st.button(
                "Summarize", 
                on_click=self._handle_tombol_summarize,
                disabled=is_disabled,
                type="primary"
            )

        with col2:
            st.button("Clear", on_click=self._handle_tombol_clear)
        
        # Tampilkan pesan error jika ada (dari PDF rusak, dll)
        if st.session_state.error:
            st.error(st.session_state.error)

        # --- Bagian 4: Hasil Ringkasan (Sesuai Gambar IV-7) ---
        if st.session_state.teks_output:
            st.subheader("Hasil Ringkasan")
            st.markdown(
                f"""
                <div style="background-color: #f0f2f6; padding: 15px; border-radius: 5px;">
                {st.session_state.teks_output}
                </div>
                """, 
                unsafe_allow_html=True
            )
            # Tampilkan info tambahan (Sesuai Skenario IV-9, langkah 7)
            st.caption(st.session_state.info_proses)
