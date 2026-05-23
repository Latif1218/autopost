from fastapi import FastAPI, status
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine, get_db   
from .routers import register_user, login_user, forgot_password, subscription, business_onboarding_router, social_auth
from app.models import *
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .config import SESSION_SECRET_KEY
from sqlalchemy import text


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up application...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables ensured.")
    except Exception as e:
        print(f"Error creating tables: {e}")
    yield
    print("Shutting down...")



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


@app.get("/dashboard")
def dashboard():
    return {"status": "API running"}


limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


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
        "https://www.ottomaxai.com",
        "https://ottomaxai.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
    https_only=False,      
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


app.include_router(register_user.router)
app.include_router(login_user.router)
app.include_router(forgot_password.router)
app.include_router(subscription.router)
app.include_router(business_onboarding_router.router)
app.include_router(social_auth.router)


print("FastAPI app initialized with Supabase")