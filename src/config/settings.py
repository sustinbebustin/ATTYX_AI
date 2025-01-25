from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "ATTYX AI"
    API_VERSION: str = "v1"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    
    # API Keys
    OPENAI_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SLACK_BOT_TOKEN: Optional[str] = None
    SLACK_SIGNING_SECRET: Optional[str] = None
    SENDGRID_API_KEY: Optional[str] = None
    
    # Models
    MODEL_NAME: str = "gpt-4-turbo-preview"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Database
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379"
    
    # Queue Settings
    QUEUE_TIMEOUT: int = 300
    MAX_RETRIES: int = 3
    
    # Business Hours
    BUSINESS_START_HOUR: int = 9
    BUSINESS_END_HOUR: int = 17
    WEEKEND_EXCLUDED: bool = True
    
    # Lead Management
    MAX_CALL_ATTEMPTS: int = 6
    INITIAL_CALL_DELAY: int = 10  # minutes
    
    # Rate Limits
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # seconds
    
    # Services
    NOTIFICATION_ENABLED: bool = True
    ANALYTICS_ENABLED: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings"""
    return Settings()