import socket
import paramiko
from threading import Thread
from core.security.encryption import encrypt_log

class SSHHoneypot(paramiko.ServerInterface):
    def __init__(self, client_address):
        self.client_address = client_address
        self.event = paramiko.threading.Event()

    def check_auth_password(self, username, password):
        """Log setiap upaya autentikasi"""
        log = f"[SSH] {self.client_address[0]}:{self.client_address[1]} | Username: {username} | Password: {password}"
        encrypt_log(log.encode())
        return paramiko.AUTH_FAILED  # Selalu tolak autentikasi

    def check_channel_request(self, kind, chanid):
        """Terima permintaan channel"""
        return paramiko.OPEN_SUCCEEDED

def handle_client(client, addr, host_key):
    """Handler untuk setiap koneksi klien"""
    try:
        transport = paramiko.Transport(client)
        transport.add_server_key(host_key)
        server = SSHHoneypot(addr)
        transport.start_server(server=server)

        # Tunggu hingga koneksi ditutup
        while transport.is_active():
            time.sleep(1)
    except Exception as e:
        log = f"[ERROR] SSH connection handler failed for {addr[0]}:{addr[1]}: {str(e)}"
        encrypt_log(log.encode())
    finally:
        client.close()

def start_ssh_honeypot(port=2222):
    """Jalankan SSH honeypot pada port tertentu"""
    host_key = paramiko.RSAKey.generate(2048)  # Buat host key sekali saja
    
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("0.0.0.0", port))
        server_socket.listen(100)
        server_socket.settimeout(60)  # Set timeout untuk mencegah koneksi menggantung
        
        print(f"SSH Honeypot berjalan pada port {port}")
        encrypt_log(f"[INFO] SSH Honeypot started on port {port}".encode())
        
        while True:
            try:
                client, addr = server_socket.accept()
                print(f"Incoming connection from {addr[0]}:{addr[1]}")
                encrypt_log(f"[INFO] Incoming SSH connection from {addr[0]}:{addr[1]}".encode())
                
                # Tangani setiap koneksi dalam thread terpisah
                Thread(target=handle_client, args=(client, addr, host_key)).start()
            except socket.timeout:
                continue  # Lanjutkan jika timeout tercapai
    except Exception as e:
        log = f"[ERROR] SSH Honeypot failed: {str(e)}"
        encrypt_log(log.encode())
        raise