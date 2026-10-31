"""Application settings, loaded from environment variables / .env.

Secrets are SecretStr so they never show up in logs or reprs. Everything is
optional at import time so the app (and tests) can start without credentials;
code that needs a secret checks for it where it is used.
"""

from functools import lru_cache
from urllib.parse import quote

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
    # CLAUDE.md rule 5 excludes security content. False (strict) also refuses security-budget questions;
    # set true to treat security-agency budget lines as ordinary budget facts.
    kasafi_allow_security_budget: bool = False
    # Reasoning effort for the answer planner (speed vs accuracy; see evals/run_answer_eval.py)
    kasafi_plan_reasoning: str = "minimal"   # same eval score as "low", median 7.9 s vs 9.9 s (Oct 27)
    # ... and for Muse Spark's budget-line readings (Open always reasons): "minimal" is ~3 s faster (Oct 30)
    kasafi_read_reasoning: str = "minimal"
    # Model prices in USD per 1M tokens, for the eval runs' cost line (app/usage.py). Meta: Muse Spark launch post;
    # Baseten (Muse Spark Open): price trackers' copy of Baseten's page, Oct 23 2026. Cached reads not confirmed by
    # Meta: its cached price is assumed equal to Baseten's. Reasoning tokens are billed as output.
    # Fetching new documents (and the web searches that find them) and the open-web fallback. The eval runners
    # turn both off except for the cases that need a fetch, so a run doesn't spend searches and downloads.
    kasafi_fetch_enabled: bool = True
    kasafi_open_web: bool = True
    kasafi_price_meta_in: float = 1.25
    kasafi_price_meta_cached: float = 0.15
    kasafi_price_meta_out: float = 4.25
    kasafi_price_baseten_in: float = 1.25
    kasafi_price_baseten_cached: float = 0.15
    kasafi_price_baseten_out: float = 4.25
    kasafi_price_fireworks_in: float = 1.25          # Fireworks' model page, Oct 30 2026
    kasafi_price_fireworks_cached: float = 0.15
    kasafi_price_fireworks_out: float = 4.25
    # Eval runs stop when the day's eval spend (all runs, both providers) reaches this (evals/runtime.DailyBudget)
    eval_daily_usd: float = 5.0
    # How long a read-back question waits for Eh / A'a / a correction
    kasafi_pending_ttl_minutes: int = 15

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
    # Hazard information (docs/hazard-and-services.md), both optional: OpenRouteService directions (without it,
    # straight-line distance) and NASA FIRMS fire detections (without it, no fires layer)
    ors_api_key: SecretStr | None = None
    firms_map_key: SecretStr | None = None
    # the hazard fetchers' schedule (app/hazards/fetch.py) runs in the app only when this is on
    kasafi_hazard_fetch: bool = False
    # the hazard fetchers stop for the day (UTC) at this many Open-Meteo calls, well under the free 10,000
    kasafi_openmeteo_daily_cap: int = 5000
    # the official advisories crawl and NCDC reports (app/hazards/advisories.py; they use Muse Spark), off by default
    kasafi_advisories_fetch: bool = False
    # what the advisories crawl's model calls (NCDC: document check, OCR, Sokoto's row) may cost a month, in USD
    kasafi_advisories_monthly_usd: float = 2.0
    # hazard alerts people sign up for (app/alerts): the triggers are checked after each hazard fetch round only
    # when this is on; in the dry run (the default) alerts go to /admin/alerts, never to users
    kasafi_alerts: bool = False
    kasafi_alerts_dry_run: bool = True
    # the most kasafi_hazard_alert messages sent in a Lagos day, all users together (each delivered one is charged);
    # 0 (unset) sends none live; the dry run applies it only when it is set
    kasafi_alerts_daily_cap: int = 0
    # the template languages Meta has approved (comma-separated); a send in any other language is skipped and logged
    kasafi_alert_template_langs: str = "ha"
    # Fireworks serves Muse Spark Open too: the fallback host when Baseten fails (app/providers/fireworks.py)
    fireworks_api_key: SecretStr | None = None
    fireworks_base_url: str = "https://api.fireworks.ai/inference/v1"
    fireworks_model: str = "accounts/fireworks/models/muse-spark-open"
    # The second of the two independent row readings runs on Muse Spark Open (app/agent/line_answer.py); slower
    # than this, or failing, and Muse Spark reads instead
    kasafi_open_reader: bool = True
    kasafi_open_read_timeout_s: float = 20.0
    # Other stages run on Muse Spark Open too, to spend Baseten's credits rather than Meta's (comma list of plan,
    # compose; app/agent/answer.stage_json). Slower than the timeout, or failing, and Muse Spark answers instead.
    # Oct 30, the 39: compose on Open 0 wrong, median 2.9 s vs 6.2 s; the planner on Open missed m21's rank
    # query 2 of 3 times (Muse Spark ~1 of 5), so it stays on Muse Spark
    kasafi_open_stages: str = "compose"
    kasafi_open_stage_timeout_s: float = 15.0

    # Web search
    serper_api_key: SecretStr | None = None
    # ReliefWeb API v2 needs a pre-approved appname (apidoc.reliefweb.int); its search is skipped without one
    reliefweb_appname: str = ""
    # IOM DTM API keys (dtm-apim-portal.iom.int): the Baseline (displacement, v3) and Humanitarian Needs
    # Assessment (HNA, v1) products; each lookup is skipped while its key is empty
    dtmapi_subscription_key: SecretStr | None = None
    dtmhna_subscription_key: SecretStr | None = None
    # Multi-source topic answers: the whole look-up-and-fetch budget, in seconds
    kasafi_topic_budget_s: float = 90.0
    # Self-growing library: live document fetches per day (all users), and where fetched PDFs are kept
    kasafi_fetches_per_day: int = 20
    kasafi_fetch_dir: str = "data/fetched"
    # Evidence images: a SAM 3.1 crop of the cited table row, sent after the text answer (users can turn them off)
    kasafi_evidence_images: bool = True
    kasafi_max_images: int = 2
    kasafi_crop_timeout_s: float = 25.0     # for all of an answer's images; the text has already been sent
    kasafi_pdf_dir: str = "data/pdfs"       # seed PDFs on the server (deploy/deploy.sh --sync-pdfs); dev uses data/
    sam_model: str = "sam-3.1"
    # dev.meta.ai/docs/pricing-rate-limits (Oct 29): SAM 3.1 image segmentation $2.50 per 1,000 images
    kasafi_cost_per_sam_usd: float = 0.0025

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

    # Database. DATABASE_URL wins if set. Otherwise it's built from POSTGRES_PASSWORD and
    # POSTGRES_HOST: the docker-compose dev DB on 127.0.0.1, or the "db" container on the VPS.
    database_url: SecretStr | None = None
    postgres_password: SecretStr | None = None
    # 127.0.0.1, not localhost: on Windows localhost tries IPv6 first and the connect hangs.
    postgres_host: str = "127.0.0.1"

    def db_url(self, driver: str = "") -> str:
        """Connection URL. driver="" for psycopg (postgresql://), "psycopg" for SQLAlchemy/Alembic."""
        url = self.database_url.get_secret_value() if self.database_url else ""
        if not url and self.postgres_password and self.postgres_password.get_secret_value():
            pw = quote(self.postgres_password.get_secret_value(), safe="")
            url = f"postgresql://kasafi:{pw}@{self.postgres_host}:5432/kasafi"
        if not url:
            raise RuntimeError("DATABASE_URL (or POSTGRES_PASSWORD for the dev database) is not set")
        scheme, rest = url.split("://", 1)
        base = scheme.split("+", 1)[0]
        return f"{base}+{driver}://{rest}" if driver else f"{base}://{rest}"

    @property
    def has_database(self) -> bool:
        try:
            self.db_url()
        except RuntimeError:
            return False
        return True

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
