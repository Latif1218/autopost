from fastapi import FastAPI, status
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine, get_db   # check_database_health সরানো হয়েছে
from .routers import register_user, login_user, forgot_password
# অন্য routers যোগ করো (পরে)
# from .routers import business_onboarding_router, subscription ইত্যাদি

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .config import SESSION_SECRET_KEY
from sqlalchemy import text


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up application...")
    try:
        # Tables create (development এর জন্য)
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables ensured.")
    except Exception as e:
        print(f"⚠️ Error creating tables: {e}")
    yield
    print("👋 Shutting down...")


# Database Health Check Function
def check_database_health():
    """Simple database health check"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False


app = FastAPI(lifespan=lifespan, title="Ottomax API")

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:8000",
        "https://fafaseleto-frontend.vercel.app",
        "http://192.168.7.56:3000",
        "https://nonprinting-featherlight-leatrice.ngrok-free.dev",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session Middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
    https_only=False,      # Development এ False রাখো, Production এ True করো
    same_site="lax"
)

@app.get('/health', status_code=status.HTTP_200_OK)
def health():
    is_db_ok = check_database_health()
    return {
        "status": "healthy" if is_db_ok else "degraded",
        "database": "connected" if is_db_ok else "disconnected",
        "detail": "API is running"
    }


# Routers
app.include_router(register_user.router)
app.include_router(login_user.router)
app.include_router(forgot_password.router)
# app.include_router(business_onboarding_router.router)   # পরে uncomment করো
# app.include_router(subscription.router)  # পরে

print("✅ FastAPI app initialized with Supabase")