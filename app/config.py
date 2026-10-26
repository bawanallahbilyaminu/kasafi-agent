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

    # Speech-to-text pipeline (see evals/stt-hausa-2026-10-26.md)
    stt_asr_model: str = "muse-voice-transcribe-1.0"
    stt_audio_model: str = "muse-spark-1.2"
    stt_reconcile_model: str = "muse-spark-1.3"

    # Baseten (Muse Spark Open)
    baseten_api_key: SecretStr | None = None
    baseten_base_url: str = "https://inference.baseten.co/v1"
    # The hackathon key only works with this exact ID (not the docs' "meta-models/muse-spark-open").
    baseten_model: str = "meta-models/muse-spark-open-1026"

    # Web search
    serper_api_key: SecretStr | None = None

    # WhatsApp Cloud API
    whatsapp_token: SecretStr | None = None
    whatsapp_phone_number_id: str | None = None
    whatsapp_verify_token: SecretStr | None = None
    whatsapp_app_secret: SecretStr | None = None
    whatsapp_api_version: str = "v26.0"

    # Database
    database_url: SecretStr | None = None

    # Shown on /privacy and /data-deletion (optional; the WhatsApp command always works)
    privacy_contact_email: str | None = None

    # Admin page basic auth
    admin_user: str | None = None
    admin_password: SecretStr | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
