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
        # Inisialisasi handler
        if "handler" not in st.session_state:
            st.session_state.handler = SistemHandler()
            print("SistemHandler diinisialisasi")

        # Inisialisasi SEMUA state di sini
        if "teks_input" not in st.session_state:
            st.session_state.teks_input = ""
        if "teks_output" not in st.session_state:
            st.session_state.teks_output = ""
        if "info_proses" not in st.session_state:
            st.session_state.info_proses = ""
        if "error" not in st.session_state:
            st.session_state.error = ""
        
        # Ambil handler
        self.handler = st.session_state.handler

    def _handle_tombol_summarize(self):
        # Set input untuk handler
        self.handler.teks_input_saat_ini = st.session_state.teks_input
        
        # Reset output/error
        st.session_state.teks_output = ""
        st.session_state.info_proses = ""
        st.session_state.error = ""
        
        # Gunakan st.empty() untuk loading yang handal
        loading_placeholder = st.empty()
        
        try:
            loading_placeholder.info("⏳ Sedang meringkas... Silakan tunggu.")
            
            start_time = time.time()
            hasil, info = self.handler.jalankan_peringkasan()
            end_time = time.time()
            
            loading_placeholder.empty() # Hapus pesan loading
            
            waktu_proses = end_time - start_time
            st.session_state.teks_output = hasil
            st.session_state.info_proses = f"Ringkasan dihasilkan dalam {waktu_proses:.2f} detik. {info}"
        
        except Exception as e:
            loading_placeholder.empty() # Hapus pesan loading jika error
            st.session_state.error = f"Terjadi kesalahan saat memproses ringkasan: {str(e)}"
            st.error(st.session_state.error)

    def _handle_upload_pdf(self):
        # Ambil file dari session state
        file_pdf = st.session_state.pdf_file_uploader
        
        # [PERBAIKAN PENTING] Penjaga jika file dihapus (None)
        if file_pdf is None:
            # Saat user menekan 'x' untuk hapus file, set teks_input jadi kosong
            st.session_state.teks_input = ""
            return

        # Jika file ADA, baru proses
        st.session_state.error = ""
        st.session_state.teks_output = ""
        st.session_state.info_proses = ""
        
        with st.spinner("Mengekstrak teks dari PDF..."):
            try:
                teks_dari_pdf, sukses = self.handler.proses_upload_pdf(file_pdf)
                if sukses:
                    st.session_state.teks_input = teks_dari_pdf # Ini akan update text_area
                else:
                    st.session_state.error = teks_dari_pdf
                    st.session_state.teks_input = ""
            
            except Exception as e:
                st.session_state.error = f"Gagal memproses file PDF: {str(e)}"
                st.session_state.teks_input = ""

    def _handle_tombol_clear(self):
        st.session_state.teks_input = ""
        st.session_state.teks_output = ""
        st.session_state.info_proses = ""
        st.session_state.error = ""
        # [TAMBAHAN] Kita juga harus mengosongkan widget file_uploader
        st.session_state.pdf_file_uploader = None 

    def render_halaman_utama(self):
        st.set_page_config(page_title="Aplikasi Peringkasan Teks Berita", layout="wide")
        st.title("Aplikasi Peringkasan Teks Berita")
        st.markdown("Selamat datang! Silahkan masukkan teks berita berbahasa Inggris di bawah ini untuk diringkas")
        st.divider()

        st.subheader("Metode Input 1 : Input Teks Langsung")
        
        st.text_area(
            "Ketik atau tempel (paste) teks berita Anda di sini...",
            height=300,
            key="teks_input" # Ini adalah satu-satunya 'key' yang benar
        )
        
        panjang_teks = len(st.session_state.teks_input.split())
        st.caption(f"Estimasi: {panjang_teks} kata. (Maksimal ~512 token, teks akan dipotong otomatis)")

        st.subheader("Metode Input 2 : Upload File PDF")
        
        st.file_uploader(
            "Upload PDF", 
            type=["pdf"], 
            on_change=self._handle_upload_pdf, 
            key="pdf_file_uploader" # Gunakan key yang berbeda
        )

        st.divider()

        # --- [ BARIS DEBUG DITAMBAHKAN DI SINI ] ---
        # Baris ini akan memberitahu kita APA SEBENARNYA isi state 'teks_input'
        st.write(f"DEBUG: Isi 'teks_input' saat ini adalah: '{st.session_state.teks_input}'")
        # --- [ AKHIR BARIS DEBUG ] ---


        # --- Bagian 3: Tombol Aksi ---
        col1, col2, col_spacer = st.columns([1, 1, 5])

        with col1:
            is_disabled = st.session_state.teks_input == ""
            st.button(
                "Summarize", 
                on_click=self._handle_tombol_summarize,
                disabled=is_disabled,
                type="primary"
            )

        with col2:
            st.button("Clear", on_click=self._handle_tombol_clear)
        
        if st.session_state.error:
            st.error(st.session_state.error)

        # --- Bagian 4: Hasil Ringkasan ---
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
            st.caption(st.session_state.info_proses)
