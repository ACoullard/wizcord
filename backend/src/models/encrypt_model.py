import os
import dotenv
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# TODO: Add timestamp to x25519 exchange to prevent replay attacks

dotenv.load_dotenv()

class EncryptModel:
    def __init__(self):
        #TODO: fix this
        # self.rsa_private_key = "placeholder" #type: rsa.RSAPrivateKey
        # self.rsa_private_key = self.import_RSA_private_key("../keys/RSA_private_key.ppk", os.getenv("RSA_PASSPHRASE").encode("utf-8"))
        self.hkdf_salt = os.urandom(16)


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
            tuple:
            - public key: the public key to be used in X25519
            - private key: the private key to be used in X25519
            - signature: a signature for the public key's btyes generated using this modules private RSA key.
        """

        private_key = x25519.X25519PrivateKey.generate()
        public_key = private_key.public_key()


        # public_key_bytes = public_key.public_bytes_raw()

        # signature = self.rsa_private_key.sign(
        #     data=public_key_bytes,
        #     padding=padding.PSS(
        #         mgf=padding.MGF1(hashes.SHA256()),
        #         salt_length=padding.PSS.MAX_LENGTH
        #     ),
        #     algorithm=hashes.SHA256()
        # )

        return public_key, private_key
    
    def complete_x25519_exchange(self, private_key_bytes: bytes, peer_public_key_bytes: bytes):
        private_key = x25519.X25519PrivateKey.from_private_bytes(private_key_bytes)
        peer_public_key = x25519.X25519PublicKey.from_public_bytes(peer_public_key_bytes)

        shared_secret = private_key.exchange(peer_public_key)
        
        symmetric_key = shared_secret
        # symetric_key = HKDF(
        #     algorithm=hashes.SHA256(),
        #     length=64,
        #     salt=self.hkdf_salt,
        #     info=b'symmetric-key',
        # ).derive(shared_secret)

        del private_key

        return symmetric_key
    
    def encrypt(self, symmetric_key: bytes, content: bytes) -> bytes:
        """Encrypt using Fernet and a given symmetric key.
        See python encryption.fernet docs for more info on Fernet.

        Args:
            symmetric_key (bytes): a 32 byte long key to use for encryption
            content (bytes): the content to be encrypted

        Raises:
            ValueError: if the key is not of the proper type or length
            ValueError: if the content is not in bytes form

        Returns:
            bytes: the resulting encrypted bytes
        """
        if not isinstance(symmetric_key, bytes) or len(symmetric_key) != 32:
            raise ValueError("Invalid symmetric key")
        if not isinstance(content, bytes):
            raise ValueError("Content must be in bytes form")
        
        f = Fernet(symmetric_key)
        result = f.encrypt(content)
        return result
    
    def decrypt(self, symmetric_key: bytes, cyphertext: bytes) -> bytes:
        """Decrypt Fernet bytes into the plaintext bytes.

        Args:
            symmetric_key (bytes): a 32 byte long key to use for encryption
            cyphertext (bytes): the cyphertext bytes to be decrypted

        Raises:
            ValueError: if the symmetric key is not of the proper length
            ValueError: if the cyphertext is not in byte form
            ValueError: if the decry

        Returns:
            bytes: _description_
        """
        if not isinstance(symmetric_key, bytes):
            raise TypeError("Symmetric key must be bytes")
        elif len(symmetric_key) != 32:
            raise ValueError("Invalid symmetric key")
        if not isinstance(cyphertext, bytes):
            raise ValueError("Cyphertext must be in bytes form")
    
        f = Fernet(symmetric_key)
        try: 
            result = f.decrypt(cyphertext)
        except InvalidToken as e:
            raise ValueError("Decryption failed. Invalid cyphertext or key")

        return result


    def public_key_to_string(self, public_key: x25519.X25519PublicKey):
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public_key_bytes.decode("utf-8")
    
    def private_key_to_string(self, private_key: x25519.X25519PrivateKey):
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return private_key_bytes.decode("utf-8")
    