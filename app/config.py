

from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache
from typing import Union

#change
class Settings(BaseSettings):

    # Supabase Configuration
    supabase_url: str
    supabase_key: str  # This should be the anon/public key
    supabase_service_key: str = ""  # Optional: for admin operations

    # Application Configuration
    app_name: str = "SkillBridge API"
    app_version: str = "1.0.0"
    debug: bool = True

    # CORS Configuration
    allowed_origins: Union[str, list[str]] = "http://localhost:3000,http://localhost:5173"

    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:

    return Settings()
