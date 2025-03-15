# core/config/config.py
import os
from pathlib import Path
from core.utils.logger_config import logger  # Import logger terpusat

class Config:
    # Default paths
    ML_MODEL_PATH = Path(os.getenv("ML_MODEL_PATH", "core/ml_models/anomaly_model.joblib"))
    DATASET_PATH = Path(os.getenv("DATASET_PATH", "data/network_data.csv"))
    LOG_FILE_PATH = Path(os.getenv("LOG_FILE_PATH", "logs/ml_training.log"))
    LOG_ENCRYPTION_KEY = os.getenv("LOG_ENCRYPTION_KEY", "default_encryption_key")

    @staticmethod
    def validate_paths():
        try:
            # Pastikan folder untuk model, logs, dan dataset ada
            for path in [Config.ML_MODEL_PATH, Config.LOG_FILE_PATH, Config.DATASET_PATH]:
                if not path.parent.exists():
                    logger.info(f"Membuat folder: {path.parent}")
                    path.parent.mkdir(parents=True, exist_ok=True)

            # Logging validasi path
            logger.info(f"Path validated: Model={Config.ML_MODEL_PATH}, Log={Config.LOG_FILE_PATH}")

            # Validasi keberadaan file dataset
            if not Config.DATASET_PATH.exists():
                logger.warning(f"Dataset tidak ditemukan di {Config.DATASET_PATH}. Pastikan file dataset tersedia.")
            else:
                logger.info(f"Dataset ditemukan di {Config.DATASET_PATH}")

        except Exception as e:
            logger.error(f"Path validation error: {str(e)}")
            raise