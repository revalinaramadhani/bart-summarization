"""
Nama File: model_handler.py
Deskripsi: Kelas BartModelHandler (Model).
Membungkus model BART dan tokenizer, bertanggung jawab untuk
memuat model dan menjalankan inference. Sesuai Tabel IV-12, No. 6.
"""

import streamlit as st
from transformers import BartTokenizer, BartForConditionalGeneration
import torch

# Menggunakan cache_resource agar model hanya di-load SEKALI saat aplikasi start
# Ini SANGAT PENTING untuk performa Streamlit
@st.cache_resource
def load_model_and_tokenizer(model_path):
    """
    Fungsi terpisah untuk me-load model dan tokenizer.
    Fungsi ini di-cache oleh Streamlit.
    """
    try:
        print(f"Mencoba memuat model dari: {model_path}")
        model = BartForConditionalGeneration.from_pretrained(model_path)
        tokenizer = BartTokenizer.from_pretrained(model_path)
        print("Model dan Tokenizer berhasil dimuat.")
        return model, tokenizer
    except Exception as e:
        print(f"Error saat memuat model: {e}")
        # Jika gagal, tampilkan error di UI Streamlit
        st.error(f"Gagal memuat model dari folder '{model_path}'. Pastikan folder model ada di direktori yang sama dengan main.py. Error: {e}")
        return None, None

class BartModelHandler:
    def __init__(self, model_path="bart-base-cnn-dailymail-finetuned"):
        """
        Inisialisasi handler dan memuat model/tokenizer dari cache.
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Menggunakan device: {self.device}")
        
        self.model, self.tokenizer = load_model_and_tokenizer(model_path)
        if self.model:
            self.model.to(self.device)
            self.model.eval() # Set model ke mode evaluasi

    def generate_summary(self, teks_bersih):
        """
        Menjalankan proses tokenisasi, inference, dan decode.
        Sesuai Skenario IV-9, langkah 4b, 4c, 4d.
        """
        if not self.model or not self.tokenizer:
            raise Exception("Model atau Tokenizer tidak berhasil dimuat.")

        # Skenario IV-9, langkah 4b (Tokenisasi)
        inputs = self.tokenizer(
            teks_bersih,
            max_length=512,  # Sesuai Skenario IV-8 (512 token)
            return_tensors="pt",
            padding="max_length",
            truncation=True
        ).to(self.device)
        
        input_token_count = inputs.input_ids.shape[1]

        # Skenario IV-9, langkah 4c (Proses Model)
        # Nonaktifkan perhitungan gradien untuk menghemat memori
        with torch.no_grad():
            summary_ids = self.model.generate(
                inputs.input_ids,
                num_beams=4,
                max_length=128, # Sesuai notebook
                early_stopping=True
            )
            
        output_token_count = summary_ids.shape[1]

        # Skenario IV-9, langkah 4d (Dekode)
        summary = self.tokenizer.decode(
            summary_ids[0], 
            skip_special_tokens=True
        )
        
        # Info tambahan (Skenario IV-9, langkah 7)
        info = f"Panjang artikel: {input_token_count} token. Panjang ringkasan: {output_token_count} token."
        
        return summary, info
