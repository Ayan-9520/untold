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

_LOCALHOST_MARKERS = ("localhost", "127.0.0.1", "::1")

_DEMO_PROVIDER_IDS = frozenset({"demo", "media_stub"})

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
    # Separate from SECRET_KEY — used only for Fernet field encryption (enterprise secrets vault).
    # If unset, derived from SECRET_KEY for backward compatibility (existing deployments).
    encryption_key: str | None = None
    algorithm: str = "HS256"
    jwt_issuer: str = "untold"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    cors_origins: str = "http://localhost:5173"
    trusted_hosts: str = "*"

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    enable_websocket: bool = True

    # Rate limiting (Redis-backed via slowapi)
    rate_limit_enabled: bool = True
    rate_limit_default: str = "120/minute"
    rate_limit_auth: str = "10/minute"
    rate_limit_ai: str = "30/minute"

    security_csp: str = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
    security_hsts_max_age: int = 31_536_000

    # Observability
    metrics_enabled: bool = True
    otel_enabled: bool = False
    otel_service_name: str = "untold-api"
    otel_exporter_otlp_endpoint: str = "http://localhost:4318"

    # Database seeding — disabled by default in production
    seed_database: bool = False
    admin_email: str = "admin@untold.com"
    admin_password: str | None = None

    # Email (SMTP) — optional; logs only when unset
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_use_tls: bool = True
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    frontend_url: str = "http://localhost:5173"
    password_reset_path: str = "/reset-password"

    # Enterprise compliance (GDPR / SOC2 / ISO27001)
    compliance_access_log_enabled: bool = True
    compliance_privacy_policy_version: str = "1.0"

    # Google OAuth (Studio + public)
    google_client_id: str | None = None
    google_client_secret: str | None = None
    studio_allowed_email_domains: str = ""  # comma-separated, empty = any with studio_role

    # News engine & AI
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_embeddings_model: str = "text-embedding-3-small"
    embeddings_default_provider: str = "demo"
    embeddings_enabled_providers: str = (
        "demo,openai,voyage,cohere,gemini,jina,bge"
    )
    voyage_api_key: str | None = None
    voyage_embeddings_model: str = "voyage-3"
    cohere_api_key: str | None = None
    cohere_embeddings_model: str = "embed-english-v3.0"
    gemini_embeddings_model: str = "text-embedding-004"
    jina_api_key: str | None = None
    jina_embeddings_model: str = "jina-embeddings-v3"
    bge_api_base_url: str | None = None
    bge_api_key: str | None = None
    bge_model: str = "BAAI/bge-small-en-v1.5"
    huggingface_api_token: str | None = None
    vectorstore_default_provider: str = "demo"
    vectorstore_enabled_providers: str = (
        "demo,pgvector,pinecone,weaviate,qdrant,milvus,chroma"
    )
    vectorstore_dimension: int = 384
    vectorstore_collection_prefix: str = "untold"
    pinecone_api_key: str | None = None
    pinecone_index_host: str | None = None
    qdrant_url: str = ""
    qdrant_api_key: str | None = None
    weaviate_url: str = ""
    weaviate_api_key: str | None = None
    milvus_uri: str = ""
    milvus_token: str | None = None
    chroma_url: str = ""
    chroma_api_key: str | None = None
    ai_default_provider: str = "demo"
    research_default_provider: str = "demo"
    script_default_provider: str = "demo"
    image_default_provider: str = "demo"
    image_enabled_providers: str = (
        "demo,openai_images,google_imagen,stability,ideogram,flux,replicate,fal"
    )
    openai_image_model: str = "dall-e-3"
    google_imagen_api_key: str | None = None
    google_imagen_model: str = "imagen-3.0-generate-002"
    stability_api_key: str | None = None
    stability_model: str = "stable-diffusion-xl-1024-v1-0"
    ideogram_api_key: str | None = None
    flux_api_key: str | None = None
    flux_model: str = "flux-pro-1.1"
    replicate_api_token: str | None = None
    replicate_image_model: str = "black-forest-labs/flux-schnell"
    fal_api_key: str | None = None
    fal_image_model: str = "fal-ai/flux/dev"
    video_default_provider: str = "demo"
    video_enabled_providers: str = (
        "demo,runway,google_veo,luma,pika,kling,hailuo,replicate"
    )
    runway_api_key: str | None = None
    runway_model: str = "gen3a_turbo"
    google_veo_api_key: str | None = None
    google_veo_model: str = "veo-2.0-generate-001"
    luma_api_key: str | None = None
    pika_api_key: str | None = None
    kling_api_key: str | None = None
    kling_api_secret: str | None = None
    hailuo_api_key: str | None = None
    hailuo_group_id: str | None = None
    replicate_video_model: str = "minimax/video-01"
    voice_default_provider: str = "demo"
    voice_enabled_providers: str = (
        "demo,elevenlabs,openai_tts,azure_speech,google_tts,cartesia,playht"
    )
    elevenlabs_api_key: str | None = None
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    elevenlabs_model: str = "eleven_multilingual_v2"
    openai_tts_model: str = "tts-1"
    openai_tts_voice: str = "alloy"
    azure_speech_key: str | None = None
    azure_speech_region: str = "eastus"
    azure_speech_voice: str = "en-US-JennyNeural"
    google_tts_api_key: str | None = None
    google_tts_voice: str = "en-US-Neural2-J"
    cartesia_api_key: str | None = None
    cartesia_voice_id: str = "794f9389-aac1-45b6-b726-9d9369183238"
    cartesia_model: str = "sonic-english"
    playht_api_key: str | None = None
    playht_user_id: str | None = None
    playht_voice_id: str = "s3://voice-cloning-zero-shot/d9ff78ba-d016-47f6-b0ef-dd630f59414e/female-cs/manifest.json"
    music_default_provider: str = "demo"
    music_enabled_providers: str = (
        "demo,suno,udio,stable_audio,elevenlabs_music,replicate,fal"
    )
    suno_api_key: str | None = None
    suno_api_base_url: str = "https://api.sunoapi.org/api/v1"
    udio_api_key: str | None = None
    udio_api_base_url: str = "https://api.udio.com/api"
    stable_audio_api_key: str | None = None
    replicate_music_model: str = "meta/musicgen"
    fal_music_model: str = "fal-ai/stable-audio"
    shorts_default_provider: str = "demo"
    seo_default_provider: str = "demo"
    translation_default_provider: str = "demo"
    translation_enabled_providers: str = (
        "demo,google,deepl,openai,gemini,azure,aws_translate"
    )
    google_translate_api_key: str | None = None
    deepl_api_key: str | None = None
    deepl_api_base_url: str = "https://api-free.deepl.com"
    azure_translator_api_key: str | None = None
    azure_translator_region: str = "global"
    aws_translate_region: str = "us-east-1"
    translation_openai_model: str = "gpt-4o-mini"
    translation_gemini_model: str = "gemini-1.5-flash"
    storyboard_default_provider: str = "demo"
    ai_enabled_providers: str = (
        "demo,openai,claude,gemini,openrouter,groq,ollama,azure_openai,bedrock,media_stub"
    )
    # LLM vendor keys
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-flash"
    openrouter_api_key: str | None = None
    openrouter_model: str = "openai/gpt-4o-mini"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_deployment: str | None = None
    azure_openai_api_version: str = "2024-02-15-preview"
    aws_bedrock_region: str = "us-east-1"
    aws_bedrock_model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"
    storage_default_provider: str = "local"
    max_upload_bytes: int = 52_428_800
    ai_allow_demo_in_production: bool = False
    workflow_event_secret: str | None = None
    live_webhook_secret: str | None = None
    sso_allowed_redirect_uris: str = ""
    sportmonks_api_key: str | None = None
    sportradar_api_key: str | None = None
    cricapi_api_key: str | None = None
    news_fetch_interval_minutes: int = 15
    live_sync_interval_seconds: int = 30

    # Payments
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_default_price_id: str | None = None
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
            if self.trusted_host_list == ["*"]:
                raise ValueError("TRUSTED_HOSTS must be set to explicit hostnames in production")
            for label, url in (
                ("DATABASE_URL", self.database_url),
                ("REDIS_URL", self.redis_url),
                ("CELERY_BROKER_URL", self.celery_broker_url),
                ("CELERY_RESULT_BACKEND", self.celery_result_backend),
            ):
                if any(marker in url for marker in _LOCALHOST_MARKERS):
                    raise ValueError(f"{label} must not reference localhost in production")
            demo_providers = [
                self.ai_default_provider,
                self.embeddings_default_provider,
                self.vectorstore_default_provider,
                self.image_default_provider,
                self.video_default_provider,
                self.voice_default_provider,
            ]
            if any(p in _DEMO_PROVIDER_IDS for p in demo_providers):
                raise ValueError(
                    "AI/embeddings/vectorstore default providers must not be 'demo' in production"
                )
            if self.seed_database and not self.admin_password:
                raise ValueError(
                    "ADMIN_PASSWORD is required when SEED_DATABASE=true in production"
                )
            if self.admin_password and len(self.admin_password) < 12:
                raise ValueError("ADMIN_PASSWORD must be at least 12 characters in production")
            if not self.encryption_key:
                raise ValueError(
                    "ENCRYPTION_KEY must be set in production (openssl rand -hex 32) — "
                    "must differ from SECRET_KEY"
                )
            if self.encryption_key == self.secret_key:
                raise ValueError("ENCRYPTION_KEY must differ from SECRET_KEY in production")
            if self.ai_allow_demo_in_production:
                raise ValueError("AI_ALLOW_DEMO_IN_PRODUCTION must be false in production")
            if self.stripe_secret_key and not self.stripe_webhook_secret:
                raise ValueError("STRIPE_WEBHOOK_SECRET is required when STRIPE_SECRET_KEY is set in production")
            if self.razorpay_key_secret and not self.razorpay_webhook_secret:
                raise ValueError("RAZORPAY_WEBHOOK_SECRET is required when Razorpay keys are set in production")
        elif self.seed_database and not self.admin_password:
            raise ValueError("ADMIN_PASSWORD is required when SEED_DATABASE=true")

        return self

    @property
    def trusted_host_list(self) -> list[str]:
        raw = [h.strip() for h in self.trusted_hosts.split(",") if h.strip()]
        return raw or ["*"]

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def sso_redirect_uri_allowlist(self) -> list[str]:
        return [uri.strip() for uri in self.sso_allowed_redirect_uris.split(",") if uri.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def password_reset_url(self) -> str:
        base = self.frontend_url.rstrip("/")
        path = self.password_reset_path if self.password_reset_path.startswith("/") else f"/{self.password_reset_path}"
        return f"{base}{path}"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
