import bcrypt
import jwt
from src.config import Config

config = Config()

def encode_jwt(
        payload: dict,
        private_key: str = config.auth.private_key_path.read_text(),
        algorithm: str = config.auth.algorithm
):
    encoded = jwt.encode(payload, private_key, algorithm=algorithm)
    return encoded

def decode_jwt(
        token: str | bytes,
        public_key: str = config.auth.public_key_path.read_text(),
        algorithm: str = config.auth.algorithm
):
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded

def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()

    return bcrypt.hashpw(pwd_bytes, salt)

def check_password(
        password: str,
        hashed_password: bytes
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password
    )