from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SipSync Backend"
    # Default to local SQLite file for development; override with Postgres in .env for production
    DATABASE_URL: str = "sqlite:///./sipsync.db"

    class Config:
        env_file = ".env"

settings = Settings()
