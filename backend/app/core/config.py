
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Automated Timetable Scheduling System"
    DATABASE_URL: str = "sqlite:///./timetable.db"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SECRET_KEY: str = "FIXME_PRODUCTION_SECRET_KEY"

    class Config:
        env_file = ".env"

settings = Settings()
