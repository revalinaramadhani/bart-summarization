"""
Nama File: main.py
Deskripsi: Entry point (titik masuk) utama aplikasi.
Sesuai Tabel IV-12, No. 1.
"""
from ui import StreamlitUI

if __name__ == "__main__":
    app = StreamlitUI()
    app.render_halaman_utama()
