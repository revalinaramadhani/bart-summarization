"""
Nama File: model_handler.py
Deskripsi: Kelas BartModelHandler (Model).
Disesuaikan dengan struktur repo di mana seluruh file model
(pytorch_model.bin, tokenizer.json, config.json, dst.)
berada di direktori yang sama dengan file ini.
"""

import streamlit as st
from transformers import BartTokenizer, BartForConditionalGeneration
import torch
import os


def load_model_and_tokenizer():
    """
    Load model dan tokenizer langsung dari direktori saat ini (.)
    karena model tidak berada dalam folder khusus.
    """
    try:
        model_path = "."  # Load dari direktori yang sama

        print(f"Mencoba memuat model dari direktori: {os.path.abspath(model_path)}")

        model = BartForConditionalGeneration.from_pretrained(model_path)
        tokenizer = BartTokenizer.from_pretrained(model_path)

        print("Model dan Tokenizer berhasil dimuat.")
        return model, tokenizer

    except Exception as e:
        st.error(
            f"Gagal memuat model. Pastikan seluruh file model "
            f"(pytorch_model.bin, config.json, tokenizer.json, dll.) "
            f"berada di direktori yang sama dengan model_handler.py.\nError: {e}"
        )
        return None, None


class BartModelHandler:
    def __init__(self):
        """
        Inisialisasi handler (model dan tokenizer di-load sekali).
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Menggunakan device: {self.device}")

        self.model, self.tokenizer = load_model_and_tokenizer()

        if self.model:
            self.model.to(self.device)
            self.model.eval()

    def generate_summary(self, teks_bersih):
        """
        Tokenisasi → Inference → Decode → Kembalikan ringkasan + info token
        """
        if not self.model or not self.tokenizer:
            raise Exception("Model atau Tokenizer tidak berhasil dimuat.")

        # Tokenisasi input
        inputs = self.tokenizer(
            teks_bersih,
            max_length=512,
            return_tensors="pt",
            padding="max_length",
            truncation=True
        ).to(self.device)

        input_token_count = inputs.input_ids.shape[1]

        # Proses model
        with torch.no_grad():
            summary_ids = self.model.generate(
                inputs.input_ids,
                num_beams=4,
                max_length=128,
                early_stopping=True
            )

        output_token_count = summary_ids.shape[1]

        # Decode hasil ringkasan
        summary = self.tokenizer.decode(
            summary_ids[0],
            skip_special_tokens=True
        )

        info = (
            f"Panjang artikel: {input_token_count} token. "
            f"Panjang ringkasan: {output_token_count} token."
        )

        return summary, info
