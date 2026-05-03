from dotenv import load_dotenv
from pathlib import Path
import os
import httpx

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")

response = httpx.get(
    f"{url}/auth/v1/admin/users",
    headers={
        "apikey": key,
        "Authorization": f"Bearer {key}"
    }
)

print("Status Code:", response.status_code)
print("Response:", response.text[:500])