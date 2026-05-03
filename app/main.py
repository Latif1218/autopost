from fastapi import FastAPI, status
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine, check_database_health
from .routers import register_user, login_user, forgot_password, business_onboarding_router, subscriptiion
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .config import SESSION_SECRET_KEY

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up: Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
    yield
    print("Shutting down...")

Base.metadata.create_all(bind=engine)

app = FastAPI(lifespan=lifespan)

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
        "http://localhost:5501",
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(
    SessionMiddleware,
    secret_key = SESSION_SECRET_KEY,
    https_only = True,
    same_site="lax"
)


@app.get('/health', status_code=status.HTTP_200_OK)
def health():
    is_db_ok = check_database_health()
    return {
        "status": "healthy" if is_db_ok else "degraded",
        "detail": "API is healthy and running."
    }


app.include_router(register_user.router)
app.include_router(login_user.router)
app.include_router(forgot_password.router)
app.include_router(business_onboarding_router.router)
app.include_router(subscriptiion.router)