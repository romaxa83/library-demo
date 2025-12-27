from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="APP_", extra="ignore"  # автоматически добавит префикс APP_
    )
    # значение по умолчанию
    name: str = "App"
    env: str = "dev"
    url: str = "https://localhost"

class LoggerLoguruConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="LOG_", extra="ignore"
    )
    # значение по умолчанию
    path: str = "logs/app.log" # файл для записей логов
    level: str = "INFO"        # уровень логирования
    rotation: str = "10 MB"    # ротация файла при достижении предела, 10MB
    retention: str = "1 month" # как долго хранятся старые логи
    compression: str = "zip"   # архивирование старых логов
    serialize: bool = True     # форматировать ли в JSON-формат

class AuthJWTConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="AUTH_JWT_", extra="ignore"
    )
    # значение по умолчанию
    private_key_path: Path = BASE_DIR / "jwt-private.pem" # путь к приватному ключу
    public_key_path: Path = BASE_DIR / "jwt-public.pem"   # путь к публичному ключу
    algorithm: str = "RS256"   # алгоритм шифрования
    access_token_expired: int = 10   # время жизни токена
    refresh_token_expired: int = 60*24*7   # время жизни токена
    reset_password_token_expired: int = 60   # время жизни токена

class EmailConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="EMAIL_", extra="ignore"
    )
    # значение по умолчанию
    verify_token_expired: int = 60 # время жизни токена для подтверждения почты

class MailConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="MAIL_", extra="ignore"
    )
    # значение по умолчанию
    host: str = "127.0.0.1"
    port: int = 1025
    username: str | None = None
    password: str | None = None
    from_address: str = "admin@gmail.com"
    from_name: str | None = None

class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="DB_", extra="ignore"
    )
    # значение по умолчанию
    host: str = "localhost"
    port: int = 5432
    username: str = "postgres"
    password: str = "postgres"
    database: str = "library"

    @property
    def url(self) -> str:
        return f"postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

class Config(BaseSettings):
    app: AppConfig = AppConfig()
    db: DatabaseConfig = DatabaseConfig()
    logger: LoggerLoguruConfig = LoggerLoguruConfig()
    auth: AuthJWTConfig = AuthJWTConfig()
    email: EmailConfig = EmailConfig()
    mail: MailConfig = MailConfig()
