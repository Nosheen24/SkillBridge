
from supabase import create_client, Client
from app.config import get_settings

settings = get_settings()


def get_supabase_client() -> Client:
    
    return create_client(settings.supabase_url, settings.supabase_key)


# Global Supabase client instance
supabase: Client = get_supabase_client()
