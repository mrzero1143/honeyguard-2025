# File: core/__init__.py
"""
Core module HoneyGuard 2025
Menyediakan integrasi antara emulasi layanan, model ML, dan keamanan
"""

# Import komponen utama
from .service_emu.ssh_honeypot import SSHHoneypot
from .service_emu.http_honeypot import HTTPHoneypot
from .ml_models.anomaly_detector import AnomalyDetector
from .security.encryption import encrypt_log, decrypt_log

# Inisialisasi default
def initialize():
    """Inisialisasi komponen core"""
    print("[+] Initializing HoneyGuard Core...")
    # Contoh inisialisasi (bisa dikembangkan)
    anomaly_detector = AnomalyDetector()
    return {
        "services": [SSHHoneypot, HTTPHoneypot],
        "detector": anomaly_detector
    }

# Metadata versi
__version__ = "2025.1.0"