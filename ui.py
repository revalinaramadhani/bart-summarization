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

        # Inisialisasi semua state UI
        if "teks_input" not in st.session_state:
            st.session_state.teks_input = ""

        if "textarea_input" not in st.session_state:
            st.session_state.textarea_input = ""

        if "teks_output" not in st.session_state:
            st.session_state.teks_output = ""

        if "info_proses" not in st.session_state:
            st.session_state.info_proses = ""

        if "error" not in st.session_state:
            st.session_state.error = ""

        if "pdf_file_uploader" not in st.session_state:
            st.session_state.pdf_file_uploader = None

        self.handler = st.session_state.handler


    # -------------------------
    #    TOMBOL SUMMARIZE
    # -------------------------
    def _handle_tombol_summarize(self):

        # Kirim teks ke handler
        st.session_state.handler.teks_input_saat_ini = st.session_state.teks_input

        # Reset output/error
        st.session_state.teks_output = ""
        st.session_state.info_proses = ""
        st.session_state.error = ""

        loading = st.empty()

        try:
            loading.info("⏳ Sedang meringkas... Silakan tunggu.")
            start = time.time()

            hasil, info = self.handler.jalankan_peringkasan()

            waktu = time.time() - start
            loading.empty()

            st.session_state.teks_output = hasil
            st.session_state.info_proses = f"Ringkasan dihasilkan dalam {waktu:.2f} detik. {info}"

        except Exception as e:
            loading.empty()
            st.session_state.error = f"Terjadi kesalahan: {str(e)}"
            st.error(st.session_state.error)


    # -------------------------
    #       UPLOAD PDF
    # -------------------------
    def _handle_upload_pdf(self):
        file_pdf = st.session_state.pdf_file_uploader

        if file_pdf is None:
            # Jika user menghapus file → kosongkan input
            st.session_state.teks_input = ""
            st.session_state.textarea_input = ""
            return

        st.session_state.error = ""
        st.session_state.teks_output = ""
        st.session_state.info_proses = ""

        with st.spinner("Mengekstrak teks dari PDF..."):
            try:
                teks, sukses = self.handler.proses_upload_pdf(file_pdf)

                if sukses:
                    st.session_state.teks_input = teks
                    st.session_state.textarea_input = teks   # sinkron ke textarea
                else:
                    st.session_state.error = teks
                    st.session_state.teks_input = ""
                    st.session_state.textarea_input = ""
            except Exception as e:
                st.session_state.error = f"Gagal memproses PDF: {str(e)}"
                st.session_state.teks_input = ""
                st.session_state.textarea_input = ""


    # -------------------------
    #         CLEAR
    # -------------------------
    def _handle_tombol_clear(self):
        st.session_state.teks_input = ""
        st.session_state.textarea_input = ""
        st.session_state.teks_output = ""
        st.session_state.info_proses = ""
        st.session_state.error = ""
        st.session_state.pdf_file_uploader = None


    # -------------------------
    #      RENDER UI
    # -------------------------
    def render_halaman_utama(self):
        st.set_page_config(page_title="Aplikasi Peringkasan Teks Berita", layout="wide")

        st.title("Aplikasi Peringkasan Teks Berita")
        st.markdown("Silakan masukkan teks berita dalam bahasa Inggris untuk diringkas.")
        st.divider()

        # ==========================
        #    INPUT TEKS LANGSUNG
        # ==========================
        st.subheader("Metode Input 1 : Input Teks Langsung")

        st.text_area(
            "Ketik atau paste teks berita...",
            height=300,
            value=st.session_state.textarea_input,   # nilai ditampilkan dari state
            key="textarea_input",
            on_change=lambda: st.session_state.update({
                "teks_input": st.session_state.textarea_input
            })
        )

        panjang_teks = len(st.session_state.teks_input.split())
        st.caption(f"Estimasi: {panjang_teks} kata. (Maksimal ~512 token, otomatis dipotong)")


        # ==========================
        #      INPUT PDF
        # ==========================
        st.subheader("Metode Input 2 : Upload File PDF")

        st.file_uploader(
            "Upload File PDF",
            type=["pdf"],
            key="pdf_file_uploader",
            on_change=self._handle_upload_pdf
        )

        st.divider()


        # ==========================
        #   TOMBOL AKSI
        # ==========================
        col1, col2, col_spacer = st.columns([1, 1, 5])

        with col1:
            st.button(
                "Summarize",
                on_click=self._handle_tombol_summarize,
                disabled=(st.session_state.teks_input.strip() == ""),
                type="primary"
            )

        with col2:
            st.button("Clear", on_click=self._handle_tombol_clear)

        if st.session_state.error:
            st.error(st.session_state.error)


        # ==========================
        #     HASIL RINGKASAN
        # ==========================
        if st.session_state.teks_output:
            st.subheader("Hasil Ringkasan")
            st.markdown(
                f"""
                <div style="background-color:#f0f2f6;padding:15px;border-radius:5px;">
                {st.session_state.teks_output}
                </div>
                """,
                unsafe_allow_html=True
            )
            st.caption(st.session_state.info_proses)
