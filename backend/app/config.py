from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/toxscore"

    # Upstash Redis
    UPSTASH_REDIS_REST_URL: str = ""
    UPSTASH_REDIS_REST_TOKEN: str = ""

    # Anthropic
    ANTHROPIC_API_KEY: str = ""

    # Application
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    AI_RATE_LIMIT_PER_HOUR: int = 20
    AI_RATE_LIMIT_AUTHENTICATED_PER_HOUR: int = 50

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
