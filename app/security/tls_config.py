"""
TLS/HTTPS configuration utilities.
"""

import ssl
import os
from typing import Optional, Tuple


class TLSConfig:
    """
    TLS/HTTPS configuration for production deployment.
    """
    
    def __init__(self):
        self.cert_file = os.getenv("TLS_CERT_FILE")
        self.key_file = os.getenv("TLS_KEY_FILE")
        self.ca_file = os.getenv("TLS_CA_FILE")
    
    def is_tls_configured(self) -> bool:
        """Check if TLS is properly configured."""
        return bool(self.cert_file and self.key_file and 
                   os.path.exists(self.cert_file) and 
                   os.path.exists(self.key_file))
    
    def get_ssl_context(self) -> Optional[ssl.SSLContext]:
        """
        Create SSL context for HTTPS server.
        
        Returns:
            SSL context if TLS is configured, None otherwise
        """
        if not self.is_tls_configured():
            return None
        
        try:
            # Create SSL context
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            
            # Load certificate and private key
            context.load_cert_chain(self.cert_file, self.key_file)
            
            # Load CA certificates if provided
            if self.ca_file and os.path.exists(self.ca_file):
                context.load_verify_locations(self.ca_file)
            
            # Security settings
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
            
            return context
            
        except Exception as e:
            print(f"Error creating SSL context: {e}")
            return None
    
    def get_uvicorn_ssl_config(self) -> dict:
        """
        Get SSL configuration for uvicorn server.
        
        Returns:
            Dictionary with SSL configuration for uvicorn
        """
        if not self.is_tls_configured():
            return {}
        
        return {
            "ssl_keyfile": self.key_file,
            "ssl_certfile": self.cert_file,
            "ssl_ca_certs": self.ca_file if self.ca_file else None,
            "ssl_version": ssl.PROTOCOL_TLS_SERVER,
            "ssl_cert_reqs": ssl.CERT_NONE,  # Adjust based on requirements
            "ssl_ciphers": "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS"
        }
    
    def generate_self_signed_cert(self, 
                                 cert_file: str = "cert.pem", 
                                 key_file: str = "key.pem",
                                 days: int = 365) -> bool:
        """
        Generate self-signed certificate for development.
        
        Args:
            cert_file: Path to certificate file
            key_file: Path to private key file
            days: Certificate validity in days
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            import datetime
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Code Review Assistant"),
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=days)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.DNSName("127.0.0.1"),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())
            
            # Write private key
            with open(key_file, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # Write certificate
            with open(cert_file, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            print(f"Self-signed certificate generated: {cert_file}, {key_file}")
            return True
            
        except ImportError:
            print("cryptography package required for certificate generation")
            return False
        except Exception as e:
            print(f"Error generating certificate: {e}")
            return False


# Global TLS config instance
tls_config = TLSConfig()