import os
import logging
from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

# Load environment variables dari .env
load_dotenv()

# Konfigurasi logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_encryption_key():
    """Ambil encryption key dari environment variable"""
    key = os.getenv('LOG_ENCRYPTION_KEY')
    
    if not key:
        logging.error("LOG_ENCRYPTION_KEY tidak ditemukan! Gunakan key default (tidak aman untuk produksi)")
        # Default key untuk development (jangan gunakan di produksi!)
        key = b'YOUR_SECRET_KEY_32BYTE______'  # Ganti dengan key valid 32-byte
    
    # Validasi panjang key (harus 32-byte)
    if len(key) != 32:
        logging.error("Encryption key harus berupa string 32-byte (256-bit).")
        raise ValueError("Panjang encryption key salah")

    try:
        # Validasi format key
        return Fernet(key.encode('utf-8'))
    except Exception as e:
        logging.error(f"Key tidak valid: {str(e)}")
        raise ValueError("Format encryption key salah")

# Inisialisasi Fernet cipher
cipher = get_encryption_key()

def encrypt_log(data: str) -> bytes:
    """Enkripsi log dengan Fernet"""
    try:
        if not isinstance(data, str):
            logging.error("Data untuk dienkripsi harus berupa string.")
            raise ValueError("Input data harus berupa string")
        
        encrypted_data = cipher.encrypt(data.encode('utf-8'))
        logging.debug(f"Log berhasil dienkripsi: {encrypted_data}")
        return encrypted_data
    except Exception as e:
        logging.error(f"Enkripsi gagal: {str(e)}")
        raise

def decrypt_log(encrypted_data: bytes) -> str:
    """Dekripsi log dengan Fernet"""
    try:
        if not isinstance(encrypted_data, bytes):
            logging.error("Data untuk didekripsi harus berupa bytes.")
            raise ValueError("Input data harus berupa bytes")
        
        decrypted_data = cipher.decrypt(encrypted_data).decode('utf-8')
        logging.debug(f"Log berhasil didekripsi: {decrypted_data}")
        return decrypted_data
    except InvalidToken:
        logging.error("Dekripsi gagal: Invalid encryption token")
        raise
    except Exception as e:
        logging.error(f"Dekripsi gagal: {str(e)}")
        raise