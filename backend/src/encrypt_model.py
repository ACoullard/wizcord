import os
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, x25519
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend

class EncryptModel:
    def __init__(self):
        #TODO: fix this
        self.rsa_private_key = "placeholder" #type: rsa.RSAPrivateKey

    def import_RSA_private_key(self, path, password):
        if not os.path.exists(path):
            raise ValueError(f"Given RSA private key path does not exist: {path}")
        
        with open(path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=password,
            )
            self.rsa_private_key = private_key
        

    def get_RSA_public_key(self):
        
        return self.rsa_private_key.public_key()
        
    def init_x25519_exchange(self):
        """Generates a X225519 key pair to be used for key exchange.
        The public key should be sent to the client and the private key should be kept secret.

        A signature for the X225519 public key is also provided, as it will be sent/published.
        The X225519 public key is signed with this module's internal RSA key - the public key for which may be retrieved with
        the get_RSA_public_key() method.
        Signing is done with PSS padding and SHA256 hashing.

        Returns:
            public key: the public key to be used in X25519
            private key: the private key to be used in X25519
            signature: a signature for the public key's btyes generated using this modules private RSA key.
        """

        private_key = x25519.X25519PrivateKey.generate()
        public_key = private_key.public_key()


        public_key_bytes = public_key.public_bytes_raw()

        signature = self.rsa_private_key.sign(
            data=public_key_bytes,
            padding=padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            algorithm=hashes.SHA256()
        )

        return public_key, private_key, signature