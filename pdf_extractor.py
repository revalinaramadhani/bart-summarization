"""
Nama File: pdf_extractor.py
Deskripsi: Kelas PDFExtractor.
Bertanggung jawab untuk ekstrak teks dari file PDF.
Sesuai Tabel IV-12, No. 5.
"""
import pypdf
import io

class PDFExtractor:
    def ekstrak_teks(self, file_pdf) -> str:
        """
        Membaca file PDF dan mengekstrak semua teks di dalamnya.
        Sesuai Skenario IV-8, Alternatif 1.
        """
        try:
            # file_pdf adalah objek UploadedFile dari Streamlit
            # Kita baca sebagai bytes
            pdf_bytes = io.BytesIO(file_pdf.getvalue())
            reader = pypdf.PdfReader(pdf_bytes)
            
            teks_hasil = ""
            for page in reader.pages:
                teks_hasil += page.extract_text() + " "
            
            if not teks_hasil.strip():
                # Skenario IV-8, Alternatif 2a (PDF gambar/kosong)
                raise Exception("File PDF ini tidak mengandung teks (kemungkinan adalah PDF gambar).")
                
            return teks_hasil
            
        except Exception as e:
            # Skenario IV-8, Alternatif 2a (PDF rusak/terenkripsi)
            print(f"Error di PDFExtractor: {e}")
            # Lempar kembali error-nya agar bisa ditangkap handler
            raise e
