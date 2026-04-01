from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv
 
load_dotenv()
 
class Settings(BaseSettings):
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: str = ""
    app_name: str = "SkillBridge API"
    app_version: str = "1.0.0"
    debug: bool = True
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"
 
    class Config:
        env_file = ".env"
        extra = "ignore"
 
@lru_cache()
def get_settings():
    return Settings()