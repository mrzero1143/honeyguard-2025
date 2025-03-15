from http.server import BaseHTTPRequestHandler, HTTPServer
from core.security.encryption import encrypt_log
from urllib.parse import urlparse, parse_qs
import threading
import time

class HTTPHoneypot(BaseHTTPRequestHandler):
    def do_GET(self):
        # Simpan log permintaan
        client = self.client_address[0]
        path = self.path
        user_agent = self.headers.get('User-Agent', 'No-UA')
        
        # Parse query string
        parsed_path = urlparse(path)
        query_params = parse_qs(parsed_path.query)
        
        log = f"[HTTP] {client} | Method: GET | Path: {parsed_path.path} | Query: {query_params} | UA: {user_agent}"
        encrypt_log(log.encode())
        
        # Response palsu
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Welcome to the honeypot. Nothing to see here.")

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8', errors='replace')
            
            log = f"[HTTP] {self.client_address[0]} | Method: POST | Data: {post_data}"
            encrypt_log(log.encode())
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Data received. Thank you for your submission.")
        except Exception as e:
            log = f"[ERROR] Failed to process POST request from {self.client_address[0]}: {str(e)}"
            encrypt_log(log.encode())
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Internal server error.")

def run_http_server(server):
    """Jalankan server HTTP dalam thread terpisah"""
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
    except Exception as e:
        log = f"[ERROR] HTTP Honeypot failed: {str(e)}"
        encrypt_log(log.encode())

def start_http_honeypot(port=8080):
    """Jalankan HTTP honeypot pada port tertentu"""
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, HTTPHoneypot)
    
    # Set timeout untuk mencegah koneksi yang menggantung
    httpd.timeout = 60
    
    print(f"HTTP Honeypot berjalan pada port {port}")
    encrypt_log(f"[INFO] HTTP Honeypot started on port {port}".encode())
    
    # Jalankan server dalam thread terpisah
    threading.Thread(target=run_http_server, args=(httpd,), daemon=True).start()