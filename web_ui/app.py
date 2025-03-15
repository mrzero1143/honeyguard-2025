from flask import render_template, current_app
from . import create_app
import os
from pathlib import Path
from core.security.encryption import decrypt_log  # Pastikan fungsi decrypt_log tersedia

app = create_app()

@app.route('/')
def dashboard():
    logs = []
    log_file = Path(current_app.root_path) / '../logs/encrypted_logs.txt'

    try:
        if log_file.exists():
            with open(log_file, 'rb') as f:
                encrypted_logs = f.readlines()
            
            logs = []
            for line in encrypted_logs:
                try:
                    decrypted_log = decrypt_log(line.strip()).decode()
                    logs.append(decrypted_log)
                except Exception as e:
                    current_app.logger.error(f"Gagal mendekripsi log: {e}")
                    continue  # Lewati log yang gagal didekripsi
        
        else:
            current_app.logger.warning("File log tidak ditemukan.")
    
    except Exception as e:
        current_app.logger.error(f"Error saat membaca log: {e}")

    return render_template(
        'dashboard.html',
        logs=logs,
        title="HoneyGuard 2025 Dashboard"
    )

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    # Validasi environment variable untuk key enkripsi
    encryption_key = os.getenv("LOG_ENCRYPTION_KEY")
    if not encryption_key:
        raise ValueError("LOG_ENCRYPTION_KEY tidak ditemukan. Pastikan variabel lingkungan telah diatur.")

    # Jalankan aplikasi Flask
    app.run(host='0.0.0.0', port=5000, debug=False)