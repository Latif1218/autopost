from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from .config import SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_ANON_KEY

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL missing in .env")
if not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_ANON_KEY missing in .env")
if not SUPABASE_SERVICE_KEY:
    raise ValueError("SUPABASE_SERVICE_KEY missing in .env")

supabase_anon: Client = create_client(
    SUPABASE_URL, 
    SUPABASE_ANON_KEY,
    options=ClientOptions(auto_refresh_token=False, persist_session=False)
)

supabase_admin: Client = create_client(
    SUPABASE_URL, 
    SUPABASE_SERVICE_KEY,
    options=ClientOptions(auto_refresh_token=False, persist_session=False)
)

print("✅ Supabase clients initialized successfully (Service Role + Anon)")