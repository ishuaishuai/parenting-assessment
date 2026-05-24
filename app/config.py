from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    MODEL_PROVIDER: str = "kimi"
    MODEL_API_KEY: str = ""
    MODEL_NAME: str = "moonshot-v1-8k"
    MODEL_TEMPERATURE: float = 0.7
    ENABLE_AI_DIAGNOSIS: bool = True
    AI_MAX_TOKENS: int = 2000
    AI_TIMEOUT: int = 30
    
    ADMIN_PASSWORD: str = "admin123"
    DATA_DIR: str = "./data"
    DATABASE_PATH: str = "./data/assessment.db"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
