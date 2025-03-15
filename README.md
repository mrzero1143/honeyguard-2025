# -HoneyGuard 2025  By_MRzero1143
**Next-gen honeypot system with advanced threat detection and deception technology**

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## -Fitur Utama

HoneyGuard 2025 adalah sistem honeypot modern yang dirancang untuk mendeteksi ancaman siber secara proaktif. Berikut adalah fitur utamanya:

- **Emulasi Layanan**: Simulasi layanan SSH, HTTP, dan FTP untuk menarik aktivitas mencurigakan.
- **Deteksi Anomali**: Menggunakan Machine Learning (Isolation Forest) untuk mendeteksi aktivitas tidak normal.
- **Enkripsi Log**: Enkripsi end-to-end untuk melindungi log dari akses tidak sah.
- **Dashboard Real-Time**: Antarmuka web interaktif untuk memantau aktivitas serangan secara real-time.
- **Siap Deploy dengan Docker**: Mudah di-deploy menggunakan Docker Compose untuk lingkungan produksi.

---

## -Instalasi

Ikuti langkah-langkah berikut untuk menjalankan HoneyGuard 2025 di sistem Anda:

### Prasyarat
- Python 3.11
- Docker & Docker Compose
- Git

### Langkah-Langkah

```bash
# Clone repositori
git clone https://github.com/mrzero1143/honeyguard-2025.git
cd honeyguard-2025

# Salin file .env contoh
cp .env.example .env

# Edit file .env sesuai kebutuhan
# Contoh:
# SECRET_KEY=your_secure_secret_key_here
# LOG_ENCRYPTION_KEY=your_secure_encryption_key_here

# Build dan jalankan dengan Docker Compose
docker-compose up --build -d

# Akses dashboard di browser:
http://localhost:5000