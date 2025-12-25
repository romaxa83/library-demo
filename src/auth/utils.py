from datetime import datetime, timezone, timedelta

import bcrypt
import jwt
from src.config import Config

config = Config()

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

def create_access_token(payload: dict)->str:
    payload.update({TOKEN_TYPE_FIELD: ACCESS_TOKEN_TYPE})
    return encode_jwt(payload)

def create_refresh_token(payload: dict)->str:
    payload.update({TOKEN_TYPE_FIELD: REFRESH_TOKEN_TYPE})
    return encode_jwt(payload=payload, expired=config.auth.refresh_token_expired)

def encode_jwt(
        payload: dict,
        private_key: str = config.auth.private_key_path.read_text(),
        algorithm: str = config.auth.algorithm,
        expired: int = config.auth.access_token_expired
):
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    expired_at = now + timedelta(minutes=expired)
    to_encode.update({
        "exp": expired_at,
        "iat": now,
    })

    encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)
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