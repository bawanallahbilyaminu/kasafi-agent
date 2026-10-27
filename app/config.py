"""Application settings, loaded from environment variables / .env.

Secrets are SecretStr so they never show up in logs or reprs. Everything is
optional at import time so the app (and tests) can start without credentials;
code that needs a secret checks for it where it is used.
"""

from functools import lru_cache

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Meta Model API (https://dev.meta.ai/docs)
    meta_api_key: SecretStr | None = None
    meta_base_url: str = "https://api.meta.ai/v1"
    meta_model: str = "muse-spark-1.3"

    # Pilot gate: comma-separated WhatsApp numbers (digits, country code) whose voice notes may go to
    # model APIs. CLAUDE.md rule 7: no real users' messages to model APIs during the hackathon.
    kasafi_pilot_numbers: str = ""
    voice_max_seconds: int = 180

    # Open access with consent (CLAUDE.md rule 7). When false, only KASAFI_PILOT_NUMBERS are served.
    kasafi_open_access: bool = True
    # Keys the HMAC that turns phone numbers into user IDs. Falls back to WHATSAPP_APP_SECRET.
    kasafi_hash_key: SecretStr | None = None
    kasafi_state_db: str = "data/state.db"
    # Per-number daily limits and a global daily spend cap. The per-call costs are rough estimates;
    # calibrate them against the Meta billing dashboard.
    kasafi_voice_per_day: int = 20
    kasafi_questions_per_day: int = 50
    kasafi_daily_spend_cap_usd: float = 5.0
    kasafi_cost_per_voice_usd: float = 0.02
    kasafi_cost_per_question_usd: float = 0.01

    # Our own test numbers: no per-number daily limits and no global spend cap. They still need
    # consent, and their usage still counts toward the daily spend total.
    kasafi_exempt_numbers: str = ""

    @property
    def pilot_numbers(self) -> set[str]:
        return _parse_numbers(self.kasafi_pilot_numbers)

    @property
    def exempt_numbers(self) -> set[str]:
        return _parse_numbers(self.kasafi_exempt_numbers)

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
    whatsapp_business_account_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("WHATSAPP_BUSINESS_ACCOUNT_ID", "WHATSAPP_WABA_ID", "WABA_ID"),
    )

    # Database
    database_url: SecretStr | None = None

    # Published privacy / data-deletion / terms pages (the URLs registered in the Meta app)
    legal_site_url: str = "https://halalnumeriq.com.ng/kasafi"

    # Admin page basic auth
    admin_user: str | None = None
    admin_password: SecretStr | None = None


def _parse_numbers(value: str) -> set[str]:
    return {"".join(ch for ch in n if ch.isdigit()) for n in value.split(",") if n.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
