# Gunakan image Python resmi
FROM python:3.11-slim

# Metadata container
LABEL maintainer="HoneyGuard Team <team@honeyguard.com>" \
      description="Containerized HoneyGuard 2025 application" \
      version="1.0"

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip  # Pastikan cache pip dihapus sepenuhnya

# Copy semua kode
COPY . .

# Buat pengguna non-root untuk menjalankan aplikasi
RUN adduser --disabled-password --gecos "" honeyguard
RUN chown -R honeyguard:honeyguard /app

# Expose port untuk layanan
EXPOSE 2222  # SSH honeypot
EXPOSE 5000  # Web dashboard
EXPOSE 8080  # HTTP honeypot

# Switch ke pengguna non-root
USER honeyguard

# Command untuk menjalankan honeypot + web
CMD ["sh", "-c", "python core/service_emu/ssh_honeypot.py & python web_ui/app.py & wait"]