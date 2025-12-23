from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="APP_", extra="ignore"  # автоматически добавит префикс APP_
    )
    # значение по умолчанию
    name: str = "App"
    env: str = "local"

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

class TestDatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="TEST_DB_", extra="ignore"
    )
    # значение по умолчанию
    host: str = "localhost"
    port: int = 5432
    username: str = "postgres"
    password: str = "postgres"
    database: str = "library_test"

    @property
    def url(self) -> str:
        return f"postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class Config(BaseSettings):
    app: AppConfig = AppConfig()
    db: DatabaseConfig = DatabaseConfig()
    test_db: TestDatabaseConfig = TestDatabaseConfig()
    logger: LoggerLoguruConfig = LoggerLoguruConfig()
    auth: AuthJWTConfig = AuthJWTConfig()
