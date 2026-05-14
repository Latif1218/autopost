from app.database import engine
from sqlalchemy import text

def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Database connected successfully!")
            print("Result:", result.scalar())
    except Exception as e:
        print("Database connection failed:")
        print(e)

test_connection()