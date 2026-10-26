"""Application settings, loaded from environment variables / .env.

Secrets are SecretStr so they never show up in logs or reprs. Everything is
optional at import time so the app (and tests) can start without credentials;
code that needs a secret checks for it where it is used.
"""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Meta Model API (https://dev.meta.ai/docs)
    meta_api_key: SecretStr | None = None
    meta_base_url: str = "https://api.meta.ai/v1"
    meta_model: str = "muse-spark-1.3"

    # Baseten (Muse Spark Open)
    baseten_api_key: SecretStr | None = None

    # Web search
    serper_api_key: SecretStr | None = None

    # WhatsApp Cloud API
    whatsapp_token: SecretStr | None = None
    whatsapp_phone_number_id: str | None = None
    whatsapp_verify_token: SecretStr | None = None
    whatsapp_app_secret: SecretStr | None = None

    # Database
    database_url: SecretStr | None = None

    # Admin page basic auth
    admin_user: str | None = None
    admin_password: SecretStr | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
