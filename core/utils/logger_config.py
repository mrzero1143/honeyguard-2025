# core/utils/logger_config.py
import os
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Pastikan folder logs ada
try:
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
except Exception as e:
    # Jika gagal membuat folder logs, gunakan folder default (current directory)
    log_dir = Path(".")
    print(f"Warning: Gagal membuat folder logs. Menggunakan folder default. Error: {e}")

# Konfigurasi logging (hanya diinisialisasi sekali)
def setup_logger():
    try:
        # Tentukan level logging secara dinamis (default INFO, bisa diubah ke DEBUG jika perlu)
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        numeric_log_level = getattr(logging, log_level, logging.INFO)

        # Buat logger
        logger = logging.getLogger(__name__)
        logger.setLevel(numeric_log_level)

        # Format log
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Hindari duplikasi handler
        if not logger.handlers:
            # Handler untuk output ke terminal
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

            # Handler untuk output ke file (dengan RotatingFileHandler)
            log_file_name = os.getenv("LOG_FILE_NAME", "ml_training.log")  # Nama file log dapat dikonfigurasi
            log_file_path = log_dir / log_file_name
            file_handler = RotatingFileHandler(
                log_file_path,
                maxBytes=5 * 1024 * 1024,  # Batasi ukuran file log menjadi 5MB
                backupCount=3              # Simpan maksimal 3 backup log lama
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            # Log awal untuk memastikan logger telah diinisialisasi
            logger.info(f"Logger berhasil diinisialisasi dengan level: {log_level}")
            logger.debug(f"Log file disimpan di: {log_file_path}")

        return logger

    except Exception as e:
        print(f"Error saat menginisialisasi logger: {e}")
        raise

# Inisialisasi logger
logger = setup_logger()