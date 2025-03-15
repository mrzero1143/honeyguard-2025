import os
import sys
import argparse
import json  # Tambahkan untuk handling file feature names
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, precision_score, confusion_matrix, classification_report
from joblib import dump, load
from datetime import datetime
import time
import matplotlib.pyplot as plt

# Menambahkan root proyek ke PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import konfigurasi global dan utilitas enkripsi
from core.config.config import Config
from core.security.encryption import encrypt_log
from core.utils.logger_config import logger  # Impor logger terpusat

class AnomalyDetector:
    def __init__(self):
        self.model = None
        self.model_path = Path(Config.ML_MODEL_PATH)
        self.feature_names = None
        self.encryption_key = Config.LOG_ENCRYPTION_KEY

        # --- KODE BARU ---
        # Muat feature_names dari file jika model ada
        if self.model_path.exists():
            feature_path = self.model_path.with_suffix('.features')
            if feature_path.exists():
                with open(feature_path, 'r') as f:
                    self.feature_names = json.load(f)
            else:
                logger.warning("File feature names tidak ditemukan. Pastikan model telah dilatih.")
        # ---

    def train(self, dataset_path):
        """Latih model dengan dataset CSV"""
        try:
            start_time = time.time()
            dataset_path = Path(dataset_path)
            if not dataset_path.exists():
                raise FileNotFoundError(f"Dataset tidak ditemukan di {dataset_path}")

            df = pd.read_csv(dataset_path)
            X = df.select_dtypes(include=[np.number])
            
            if X.empty:
                raise ValueError("Dataset tidak mengandung kolom numerik.")

            # Simpan nama fitur
            self.feature_names = X.columns.tolist()

            # --- KODE BARU ---
            # Simpan feature_names ke file
            feature_path = self.model_path.with_suffix('.features')
            with open(feature_path, 'w') as f:
                json.dump(self.feature_names, f)
            logger.info(f"Feature names disimpan ke {feature_path}")
            # ---

            logger.info("Melatih model Isolation Forest...")
            self.model = IsolationForest(
                n_estimators=200,
                max_samples='auto',
                contamination=0.05,
                random_state=42
            )
            self.model.fit(X)

            dump(self.model, self.model_path)
            logger.info(f"Model berhasil disimpan di {self.model_path}")

            # Evaluasi model
            y_pred = self.model.predict(X)
            y_true = np.ones(len(y_pred))  # Asumsi data normal
            accuracy = accuracy_score(y_true, y_pred == 1)
            precision = precision_score(y_true, y_pred == 1, zero_division=0)
            logger.info(f"Evaluasi model - Akurasi: {accuracy:.2f}, Precision: {precision:.2f}")

            elapsed_time = time.time() - start_time
            logger.info(f"Pelatihan selesai dalam {elapsed_time:.2f} detik.")

        except Exception as e:
            logger.error(f"Error pelatihan: {str(e)}", exc_info=True)
            raise

    def detect(self, data, log_result=True, save_to_file=False):
        """Deteksi anomali pada data baru"""
        try:
            start_time = time.time()
            if not self.model:
                if not self.model_path.exists():
                    logger.error("Model tidak ditemukan. Jalankan training terlebih dahulu.")
                    return []
                self.model = load(self.model_path)

            # --- VALIDASI BARU ---
            # Konversi data uji ke DataFrame dengan format yang benar
            if isinstance(data, dict):
                # Pastikan data memiliki semua fitur
                missing_features = set(self.feature_names) - set(data.keys())
                if missing_features:
                    logger.error(f"Data uji kekurangan fitur: {missing_features}")
                    return []
                data = pd.DataFrame([data], columns=self.feature_names)  # Pastikan kolom sesuai
            elif isinstance(data, pd.DataFrame):
                # Validasi bahwa data uji memiliki semua fitur yang dibutuhkan
                missing_features = set(self.feature_names) - set(data.columns)
                if missing_features:
                    logger.error(f"Data kekurangan fitur: {missing_features}")
                    return []

                # Penyesuaian urutan kolom data uji
                data = data[self.feature_names]
                logger.debug(f"Data uji setelah penyesuaian kolom:\n{data}")
            else:
                logger.error("Data harus berupa dictionary atau DataFrame.")
                return []

            # Debugging: Log data uji setelah konversi
            logger.info(f"Data uji setelah konversi:\n{data}")

            # Proses deteksi
            X = data[self.feature_names].select_dtypes(include=[np.number]).values
            predictions = self.model.predict(X)
            result = ["Malicious" if x == -1 else "Benign" for x in predictions]

            if log_result and result:
                log_entry = f"[ML Detection] {datetime.now()} - Result: {result} | Data: {data.to_dict(orient='records')}"
                encrypt_log(log_entry)
                logger.info("Hasil deteksi disimpan ke log terenkripsi.")

            if save_to_file:
                output_path = Path("logs/detection_results.json")
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w") as f:
                    json.dump({"results": result, "data": data.to_dict(orient="records")}, f, indent=4)
                logger.info(f"Hasil deteksi disimpan di {output_path}")

            elapsed_time = time.time() - start_time
            logger.info(f"Deteksi selesai dalam {elapsed_time:.2f} detik.")
            return result

        except Exception as e:
            logger.error(f"Error deteksi: {str(e)}", exc_info=True)
            return []

    def evaluate(self, dataset_path):
        """Evaluasi model pada dataset uji"""
        try:
            dataset_path = Path(dataset_path)
            if not dataset_path.exists():
                raise FileNotFoundError(f"Dataset tidak ditemukan di {dataset_path}")

            df = pd.read_csv(dataset_path)
            X = df.select_dtypes(include=[np.number])
            y_true = np.ones(len(X))  # Asumsi data normal

            if self.model is None:
                self.model = load(self.model_path)

            y_pred = self.model.predict(X)

            accuracy = accuracy_score(y_true, y_pred == 1)
            precision = precision_score(y_true, y_pred == 1, zero_division=0)
            conf_matrix = confusion_matrix(y_true, y_pred == 1)
            report = classification_report(y_true, y_pred == 1, zero_division=0)

            logger.info(f"Evaluasi model pada dataset uji:")
            logger.info(f"Akurasi: {accuracy:.2f}, Precision: {precision:.2f}")
            logger.info(f"Confusion Matrix:\n{conf_matrix}")
            logger.info(f"Classification Report:\n{report}")

            plt.figure(figsize=(6, 4))
            plt.imshow(conf_matrix, cmap=plt.cm.Blues)
            plt.title("Confusion Matrix")
            plt.colorbar()
            plt.xlabel("Predicted")
            plt.ylabel("True")
            plt.xticks([0, 1], ["Benign", "Malicious"])
            plt.yticks([0, 1], ["Benign", "Malicious"])
            plt.show()

        except Exception as e:
            logger.error(f"Error evaluasi: {str(e)}", exc_info=True)

    def get_feature_names(self):
        """Getter untuk nama fitur"""
        return self.feature_names

# --- FITUR BARU ---
def parse_arguments():
    parser = argparse.ArgumentParser(description="HoneyGuard ML Anomaly Detector")
    parser.add_argument("--train", action="store_true", help="Latih model dengan dataset")
    parser.add_argument("--detect", action="store_true", help="Jalankan deteksi anomali")
    parser.add_argument("--evaluate", action="store_true", help="Evaluasi model pada dataset uji")
    parser.add_argument("--dataset", type=str, default="data/network_data.csv", help="Path dataset pelatihan")
    parser.add_argument("--testdata", type=str, help="Path data uji (JSON/CSV)")
    parser.add_argument("--save-log", action="store_true", help="Simpan hasil deteksi ke file JSON")
    return parser.parse_args()

def load_test_data(filepath):
    filepath = Path(filepath)
    if filepath.suffix == ".json":
        return pd.read_json(filepath)
    elif filepath.suffix == ".csv":
        return pd.read_csv(filepath)
    else:
        raise ValueError("Format file tidak didukung. Gunakan JSON atau CSV.")

# --- BLOK UTAMA ---
if __name__ == "__main__":
    # Validasi path sebelum eksekusi
    Config.validate_paths()

    args = parse_arguments()
    detector = AnomalyDetector()

    if args.train:
        logger.info("Memulai proses pelatihan...")
        detector.train(args.dataset)
        logger.info(f"Fitur yang digunakan: {detector.get_feature_names()}")

    if args.detect:
        logger.info("Memulai deteksi anomali...")
        if args.testdata:
            test_data = load_test_data(args.testdata)
        else:
            test_data = {
                "duration": 0,
                "src_bytes": 1000,
                "dst_bytes": 5000,
                "land": 0,
                "wrong_fragment": 0
            }

        predictions = detector.detect(
            test_data,
            log_result=True,
            save_to_file=args.save_log
        )
        logger.info(f"Hasil deteksi: {predictions}")

    if args.evaluate:
        logger.info("Memulai evaluasi model...")
        detector.evaluate(args.dataset)