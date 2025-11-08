"""
Nama File: handler.py
Deskripsi: Kelas SistemHandler (Controller).
Menjembatani UI dan backend, mengoordinasi semua alur proses.
Sesuai Tabel IV-12, No. 3.
"""

from model_handler import BartModelHandler
from preprocessor import TextPreprocessor
from pdf_extractor import PDFExtractor

class SistemHandler:
    def __init__(self):
        # Inisialisasi semua kelas pembantu (sesuai Class Diagram)
        self.preprocessor = TextPreprocessor()
        self.extractor = PDFExtractor()
        # Model handler di-load di sini saat startup
        self.model_handler = BartModelHandler()
        
        # Atribut untuk menyimpan teks input saat ini
        self.teks_input_saat_ini = ""

    def proses_upload_pdf(self, file_pdf):
        """
        Mengoordinasi proses upload PDF.
        Memanggil PDFExtractor.
        Sesuai Skenario IV-8, Alternatif 1.
        """
        try:
            teks = self.extractor.ekstrak_teks(file_pdf)
            if not teks:
                # Skenario IV-8, Alternatif 2a (PDF gambar/kosong)
                return "Gagal membaca file PDF. File mungkin tidak mengandung teks.", False
            return teks, True
        except Exception as e:
            # Skenario IV-8, Alternatif 2a (PDF rusak/terenkripsi)
            return f"Gagal memproses file PDF: {str(e)}", False

    def jalankan_peringkasan(self):
        """
        Mengoordinasi alur peringkasan.
        Sesuai Skenario IV-9, Skenario Utama.
        """
        # 1. Pra-pemrosesan (Skenario IV-9, langkah 4a)
        teks_bersih = self.preprocessor.bersihkan_teks(self.teks_input_saat_ini)
        
        # 2. Proses Model (Skenario IV-9, langkah 4b, 4c, 4d)
        # Memanggil model handler untuk tokenisasi, inference, dan decode
        try:
            hasil_ringkasan, info_token = self.model_handler.generate_summary(teks_bersih)
            
            # Skenario IV-9, Alternatif 2a (Input angka/simbol) akan ditangani
            # oleh model dan menghasilkan output (mungkin nonsense)
            # yang tetap kita tampilkan.
            
            return hasil_ringkasan, info_token
            
        except Exception as e:
            # Skenario IV-9, Alternatif 2b (Gagal internal)
            print(f"Error di jalankan_peringkasan: {e}")
            raise e # Lempar error kembali ke UI untuk ditampilkan
