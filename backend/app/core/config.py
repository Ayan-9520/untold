import secrets
from functools import lru_cache

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Blocked secret values — never accept in production
_INSECURE_SECRET_KEYS = frozenset(
    {
        "",
        "dev-only-change-in-production-use-openssl-rand-hex-32",
        "change-this-to-a-long-random-secret-in-production",
        "change-this-in-production",
    }
)

_DEV_SECRET_KEY = "dev-only-" + secrets.token_hex(24)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "UNTOLD API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8000
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql://untold:untold_secret@localhost:5432/untold_db"

    secret_key: str = Field(default=_DEV_SECRET_KEY, min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    cors_origins: str = "http://localhost:5173"

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    enable_websocket: bool = True

    # Rate limiting (Redis-backed via slowapi)
    rate_limit_enabled: bool = True
    rate_limit_default: str = "120/minute"
    rate_limit_auth: str = "10/minute"

    # Database seeding — disabled by default in production
    seed_database: bool = False
    admin_email: str = "admin@untold.com"
    admin_password: str | None = None

    # News engine & AI
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    sportmonks_api_key: str | None = None
    sportradar_api_key: str | None = None
    cricapi_api_key: str | None = None
    news_fetch_interval_minutes: int = 15
    live_sync_interval_seconds: int = 30

    # Payments
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    razorpay_key_id: str | None = None
    razorpay_key_secret: str | None = None
    razorpay_webhook_secret: str | None = None

    # OTT / S3 / Cloudflare R2
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    s3_bucket: str | None = None
    s3_region: str = "auto"
    s3_endpoint_url: str | None = None
    cdn_base_url: str | None = None
    stream_url_expire_seconds: int = 3600

    @model_validator(mode="before")
    @classmethod
    def apply_development_defaults(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data

        env = str(data.get("environment", "development")).strip().lower()
        secret = data.get("secret_key")
        if secret is None or (isinstance(secret, str) and not secret.strip()):
            if env != "production":
                data["secret_key"] = _DEV_SECRET_KEY

        return data

    @field_validator("environment")
    @classmethod
    def normalize_environment(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key_format(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return value

    @model_validator(mode="after")
    def validate_environment_requirements(self) -> "Settings":
        if self.is_production:
            if self.secret_key in _INSECURE_SECRET_KEYS or self.secret_key.startswith("dev-only-"):
                raise ValueError(
                    "SECRET_KEY must be set to a strong random value in production "
                    "(e.g. openssl rand -hex 32)"
                )
            if self.debug:
                raise ValueError("DEBUG must be false in production")
            if not self.cors_origin_list:
                raise ValueError("CORS_ORIGINS must include at least one origin in production")
            if self.seed_database and not self.admin_password:
                raise ValueError(
                    "ADMIN_PASSWORD is required when SEED_DATABASE=true in production"
                )
            if self.admin_password and len(self.admin_password) < 12:
                raise ValueError("ADMIN_PASSWORD must be at least 12 characters in production")
        elif self.seed_database and not self.admin_password:
            raise ValueError("ADMIN_PASSWORD is required when SEED_DATABASE=true")

        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
