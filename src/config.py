from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",  # автоматически добавит префикс APP_
        extra="ignore"
    )
     # значение по умолчанию
    name: str = "App"
    env: str = "local"

class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DB_",  # автоматически добавит префикс APP_
        extra="ignore"
    )
     # значение по умолчанию
    host: str = "localhost"
    port: int = 5432
    username: str
    password: str
    database: str

    @property
    def url(self) -> str:
        return f"postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

class Config(BaseSettings):
    app: AppConfig = AppConfig()
    db: DatabaseConfig = DatabaseConfig()