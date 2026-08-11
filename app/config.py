from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_host: str = "127.0.0.1"
    database_port: int = 3306
    database_name: str = "tramites"
    database_user: str = "root"
    database_password: str = ""

    secret_key: str = "cambiar_esta_clave_en_produccion"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 365

    # Secret para el workflow (n8n / agente WhatsApp). Header: X-Webhook-Secret
    webhook_secret: str = "cambiar_webhook_secret"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
