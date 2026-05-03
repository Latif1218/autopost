from dotenv import load_dotenv
from pathlib import Path
import os

# Explicit load
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

from app.supabase_client import supabase_admin

def test():
    print("🔍 Debugging...")

    # Check which key is actually being used
    print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
    
    key = os.getenv("SUPABASE_SERVICE_KEY")
    print("SERVICE_KEY starts with:", key[:40] if key else "MISSING")

    try:
        # Direct admin call
        users = supabase_admin.auth.admin.list_users()
        print("✅ Success! Total users:", len(users))
    except Exception as e:
        print("❌ Error:", str(e))
        print("Type:", type(e).__name__)

test()