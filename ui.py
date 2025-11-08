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
        # Inisialisasi SistemHandler (controller)
        if "handler" not in st.session_state:
            st.session_state.handler = SistemHandler()
            print("SistemHandler diinisialisasi")

        # Inisialisasi seluruh state global UI
        for key in ["teks_input", "textarea_input", "teks_output", "info_proses", "error"]:
            if key not in st.session_state:
                st.session_state[key] = ""

        self.handler = st.session_state.handler


    # -------------------------------------------------------------
    # FUNGSI: Menangani Upload File PDF
    # -------------------------------------------------------------
    def _handle_upload_pdf(self):
        file_pdf = st.session_state.get("pdf_file_uploader")

        # Jika user menghapus file melalui tombol X
        if file_pdf is None:
            st.session_state.teks_input = ""
            st.session_state.textarea_input = ""
            return

        # Reset error & output
        st.session_state.error = ""
        st.session_state.teks_output = ""
        st.session_state.info_proses = ""

        # Ekstraksi PDF
        with st.spinner("Mengekstrak teks dari PDF..."):
            try:
                teks, sukses = self.handler.proses_upload_pdf(file_pdf)

                if sukses:
                    st.session_state.teks_input = teks
                    st.session_state.textarea_input = teks
                else:
                    st.session_state.error = teks
                    st.session_state.teks_input = ""
                    st.session_state.textarea_input = ""

            except Exception as e:
                st.session_state.error = f"Gagal memproses PDF: {str(e)}"
                st.session_state.teks_input = ""
                st.session_state.textarea_input = ""


    # -------------------------------------------------------------
    # FUNGSI: Menjalankan proses summarize
    # -------------------------------------------------------------
    def _handle_tombol_summarize(self):
        self.handler.teks_input_saat_ini = st.session_state.teks_input

        st.session_state.teks_output = ""
        st.session_state.info_proses = ""
        st.session_state.error = ""

        loading = st.empty()
        loading.info("⏳ Sedang meringkas...")

        try:
            start = time.time()
            hasil, info = self.handler.jalankan_peringkasan()
            end = time.time()

            loading.empty()

            st.session_state.teks_output = hasil
            st.session_state.info_proses = f"Ringkasan dihasilkan dalam {end - start:.2f} detik. {info}"

        except Exception as e:
            loading.empty()
            st.session_state.error = f"Terjadi kesalahan saat memproses ringkasan: {str(e)}"
            st.error(st.session_state.error)


    # -------------------------------------------------------------
    # FUNGSI: Clear input + output
    # -------------------------------------------------------------
    def _handle_tombol_clear(self):
        st.session_state.teks_input = ""
        st.session_state.textarea_input = ""
        st.session_state.teks_output = ""
        st.session_state.info_proses = ""
        st.session_state.error = ""

        # Hapus file uploader dengan cara aman
        st.session_state.pop("pdf_file_uploader", None)


    # -------------------------------------------------------------
    # RENDER HALAMAN UTAMA
    # -------------------------------------------------------------
    def render_halaman_utama(self):
        st.set_page_config(
            page_title="Aplikasi Peringkasan Teks Berita",
            layout="wide"
        )

        st.title("Aplikasi Peringkasan Teks Berita")
        st.markdown(
            "Masukkan teks berita berbahasa Inggris atau upload file PDF untuk diringkas."
        )

        st.divider()
        st.subheader("Metode Input 1 : Input Teks Langsung")

        st.text_area(
            "Ketik atau paste teks berita di sini...",
            height=300,
            key="textarea_input",
            on_change=lambda: st.session_state.update({
                "teks_input": st.session_state.textarea_input
            })
        )

        # Informasi jumlah kata
        panjang_teks = len(st.session_state.teks_input.split())
        st.caption(f"Estimasi: {panjang_teks} kata. (Model memproses hingga ~512 token)")

        st.divider()
        st.subheader("Metode Input 2 : Upload File PDF")

        st.file_uploader(
            "Upload File PDF",
            type=["pdf"],
            key="pdf_file_uploader",
            on_change=self._handle_upload_pdf
        )

        st.divider()

        # Tombol aksi
        col1, col2, col3 = st.columns([1, 1, 5])

        with col1:
            disabled = (st.session_state.teks_input == "")
            st.button(
                "Summarize",
                on_click=self._handle_tombol_summarize,
                disabled=disabled,
                type="primary"
            )

        with col2:
            st.button("Clear", on_click=self._handle_tombol_clear)

        # Error message
        if st.session_state.error:
            st.error(st.session_state.error)

        # Hasil ringkasan
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
