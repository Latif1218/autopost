from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  

DATABASE_URL = os.getenv("DATABASE_URL")


MAILERLITE_API_KEY = os.getenv("MAILERLITE_API_KEY")


STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_PUBLISHABLE_KEY=os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_SUCCESS_URL = os.getenv("STRIPE_SUCCESS_URL")
STRIPE_CANCEL_URL = os.getenv("STRIPE_CANCEL_URL")


PRICE_IDS = {
    "starter": os.getenv("PRICE_STARTER_MONTHLY"),
    "pro": os.getenv("PRICE_PRO_MONTHLY"),
    "premium": os.getenv("PRICE_PREMIUM_ONETIME"),
}


if not SUPABASE_URL or not SUPABASE_ANON_KEY or not SUPABASE_SERVICE_KEY:
    print("Warning: Some Supabase credentials are missing in .env")

SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY")

UPLOADPOST_API_KEY = os.getenv("UPLOADPOST_API_KEY")
N8N_WEBHOOK_BASE = os.getenv("N8N_WEBHOOK_BASE")

EMAIL_REGEX = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"