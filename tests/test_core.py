import unittest
from unittest.mock import patch, MagicMock
import paramiko
import pandas as pd
from io import StringIO
from core.service_emu.ssh_honeypot import SSHHoneypot
from core.ml_models.anomaly_detector import AnomalyDetector
from core.security.encryption import encrypt_log, decrypt_log

class TestSSHFunctionality(unittest.TestCase):
    def test_authentication_failure(self):
        """Pastikan autentikasi selalu gagal"""
        honeypot = SSHHoneypot(("192.168.1.100", 12345))
        result = honeypot.check_auth_password("admin", "password123")
        self.assertEqual(result, paramiko.AUTH_FAILED)

    @patch('core.security.encryption.encrypt_log')
    def test_log_format(self, mock_encrypt):
        """Pastikan format log sesuai yang diharapkan"""
        honeypot = SSHHoneypot(("192.168.1.100", 2222))
        honeypot.check_auth_password("user", "pass123")
        
        expected_log = "[SSH] ('192.168.1.100', 2222) attempted login: user:pass123"
        mock_encrypt.assert_called_once_with(expected_log)

    @patch('core.security.encryption.encrypt_log')
    def test_invalid_login_details(self, mock_encrypt):
        """Pastikan log tercatat bahkan jika detail login tidak valid"""
        honeypot = SSHHoneypot(("192.168.1.100", 2222))
        honeypot.check_auth_password("", "")  # Login kosong
        
        expected_log = "[SSH] ('192.168.1.100', 2222) attempted login: :"
        mock_encrypt.assert_called_once_with(expected_log)


class TestAnomalyDetection(unittest.TestCase):
    @patch('core.ml_models.anomaly_detector.dump')  # Mock dump untuk simpan model
    def test_model_training(self, mock_dump):
        """Pastikan model bisa dilatih dengan data dummy"""
        # Buat data dummy
        data = """duration,protocol_type,service
        0,tcp,http
        1,udp,dns
        2,tcp,ftp"""
        
        df = pd.read_csv(StringIO(data))
        detector = AnomalyDetector()
        detector.train(df)
        
        # Pastikan model tersimpan
        self.assertTrue(hasattr(detector, 'model'))
        mock_dump.assert_called_once()  # Pastikan model disimpan

    def test_anomaly_detection_positive(self):
        """Test deteksi anomali (kasus positif)"""
        detector = AnomalyDetector()
        test_data = pd.DataFrame({
            'duration': [10],
            'protocol_type': ['icmp'],
            'service': ['unknown']
        })
        
        result = detector.detect(test_data)
        self.assertIn("Malicious", result)

    def test_anomaly_detection_negative(self):
        """Test deteksi anomali (kasus negatif)"""
        detector = AnomalyDetector()
        test_data = pd.DataFrame({
            'duration': [0],
            'protocol_type': ['tcp'],
            'service': ['http']
        })
        
        result = detector.detect(test_data)
        self.assertIn("Benign", result)

    @patch('core.ml_models.anomaly_detector.load')  # Mock load untuk muat model
    def test_model_not_found(self, mock_load):
        """Pastikan exception ditangani jika model tidak ditemukan"""
        mock_load.side_effect = FileNotFoundError("Model not found")
        detector = AnomalyDetector()
        
        with self.assertRaises(FileNotFoundError):
            detector.detect({"duration": 10, "protocol_type": "icmp", "service": "unknown"})

class TestEncryption(unittest.TestCase):
    def test_encryption_cycle(self):
        """Pastikan enkripsi-dekripsi berfungsi"""
        original_data = "Sensitive log entry"
        encrypted = encrypt_log(original_data)
        decrypted = decrypt_log(encrypted).decode()
        self.assertEqual(original_data, decrypted)

    def test_empty_encryption(self):
        """Pastikan enkripsi-dekripsi berfungsi untuk string kosong"""
        original_data = ""
        encrypted = encrypt_log(original_data)
        decrypted = decrypt_log(encrypted).decode()
        self.assertEqual(original_data, decrypted)

if __name__ == '__main__':
    unittest.main()