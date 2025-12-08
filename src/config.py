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

class Config(BaseSettings):
    app: AppConfig = AppConfig()