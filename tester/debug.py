from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

from app.database import get_db
from app.models.users_models import User

db = next(get_db())
users = db.query(User).all()
for u in users:
    print(u.email, "|", u.supabase_uid)