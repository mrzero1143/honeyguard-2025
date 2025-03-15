# Memungkinkan import modul dengan:
# from core.service_emu import SSHHoneypot, HTTPHoneypot

from .ssh_honeypot import SSHHoneypot, start_ssh_honeypot
from .http_honeypot import HTTPHoneypot, start_http_honeypot