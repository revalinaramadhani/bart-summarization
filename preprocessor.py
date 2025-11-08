"""
Nama File: preprocessor.py
Deskripsi: Kelas TextPreprocessor.
Bertanggung jawab untuk membersihkan teks. Sesuai Tabel IV-12, No. 4.
"""
import re

class TextPreprocessor:
    def bersihkan_teks(self, teks_mentah: str) -> str:
        """
        Membersihkan teks mentah dari karakter tidak perlu.
        Sesuai Skenario IV-9, langkah 4a.
        """
        # Ganti newline dan tab dengan spasi
        teks = re.sub(r'[\n\t]+', ' ', teks_mentah)
        # Hapus spasi berlebih
        teks = re.sub(r'\s+', ' ', teks).strip()
        # (Anda bisa tambahkan regex lain di sini jika perlu)
        
        # Skenario IV-9, Alternatif 2a (input angka/simbol)
        # Kita tidak memblokirnya, kita hanya membersihkannya.
        # Model yang akan menanganinya.
        
        return teks
