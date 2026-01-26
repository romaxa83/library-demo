from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_" ,# автоматически добавит префикс APP_
        extra="ignore",
        frozen = True  # Объект станет неизменяемым (hashable)
    )
    # значение по умолчанию
    name: str = "App"
    env: str = "dev"
    url: str = "https://localhost"
    port: str = "80"
    superadmin_email: str = "admin@gmail.com"
    superadmin_password: str = "password12"

    @property
    def is_testing_env(self) -> bool:
        return self.env == "testing"

class LoggerLoguruConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="LOG_", extra="ignore", frozen = True
    )
    # значение по умолчанию
    path: str = "logs/app/app.log" # файл для записей логов
    level: str = "INFO"            # уровень логирования
    rotation: str = "10 MB"        # ротация файла при достижении предела, 10MB
    retention: str = "1 month"     # как долго хранятся старые логи
    compression: str = "zip"       # архивирование старых логов
    serialize: bool = True         # форматировать ли в JSON-формат

class AuthJWTConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="AUTH_JWT_", extra="ignore", frozen = True
    )
    # значение по умолчанию
    private_key_path: Path = BASE_DIR / "jwt-private.pem" # путь к приватному ключу
    public_key_path: Path = BASE_DIR / "jwt-public.pem"   # путь к публичному ключу
    algorithm: str = "RS256"                 # алгоритм шифрования
    access_token_expired: int = 10           # время жизни токена
    refresh_token_expired: int = 60*24*7     # время жизни токена
    reset_password_token_expired: int = 60   # время жизни токена

class EmailConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="EMAIL_", extra="ignore", frozen = True
    )
    # значение по умолчанию
    verify_token_expired: int = 60 # время жизни токена для подтверждения почты

class MailConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="MAIL_", extra="ignore", frozen = True
    )
    # значение по умолчанию
    host: str = "127.0.0.1"
    port: int = 1025
    username: str | None = None
    password: str | None = None
    from_address: str = "admin@gmail.com"
    from_name: str | None = None

class CORSConfig(BaseSettings):
    """Конфигурация CORS"""
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="CORS_", extra="ignore", frozen = True
    )
    # значение по умолчанию
    allow_origins: list[str] = [
        "http://localhost",
        "http://localhost:8000",
    ]
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]
    allow_credentials: bool = False
    max_age: int = 600  # max age in seconds

class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="DB_", extra="ignore", frozen = True
    )
    # значение по умолчанию
    host: str = "localhost"
    port: int = 5432
    username: str = "postgres"
    password: str = "postgres"
    database: str = "library"

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

class RedisDB(BaseSettings):
    cache: int = 0

class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="REDIS_", extra="ignore", frozen = True
    )
    # значение по умолчанию
    host: str = "localhost"
    port: int = 6379
    password: str = ""
    username: str = "root"
    db: RedisDB = RedisDB()

    @property
    def url(self) -> str:
        return f"redis://{self.username}:{self.password}@{self.host}:{self.port}/{self.db.cache}"

class CacheNamespace(BaseSettings):
    permissions: str = "permissions"

class CacheConfig(BaseSettings):
    prefix: str = "app-cache"
    namespace: CacheNamespace = CacheNamespace()


class MediaConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="MEDIA_", extra="ignore", frozen = True
    )
    storage_type: str = "local"  # 'local' or 's3'
    root_path: Path = BASE_DIR / "storage" / "media"

    # Публичный путь (откуда будем раздавать статику)
    public_path: Path = BASE_DIR / "public"

    url_prefix: str = "/media"

    # Конфигурация превью: имя: (ширина, высота)
    thumbnails: dict[str, tuple[int, int]] = {
        "small": (150, 150),
        "medium": (600, 600)
    }

class RabbitMQConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="RABBITMQ_", extra="ignore", frozen=True
    )
    # значение по умолчанию
    host: str = "localhost"
    port: int = 5672
    password: str = "password"
    user: str = "root"

    # "amqp://guest:guest@localhost:5672/"
    @property
    def url(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"


class Config(BaseSettings):
    app: AppConfig = AppConfig()
    db: DatabaseConfig = DatabaseConfig()
    logger: LoggerLoguruConfig = LoggerLoguruConfig()
    auth: AuthJWTConfig = AuthJWTConfig()
    email: EmailConfig = EmailConfig()
    mail: MailConfig = MailConfig()
    cors: CORSConfig = CORSConfig()
    redis: RedisConfig = RedisConfig()
    cache: CacheConfig = CacheConfig()
    media: MediaConfig = MediaConfig()
    rabbitmq: RabbitMQConfig = RabbitMQConfig()

@lru_cache
def get_config() -> Config:
    return Config()

config = get_config()
