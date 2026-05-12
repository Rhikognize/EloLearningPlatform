from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth
from app.routers import tasks
from app.routers import auth, tasks, daily_goal

# Inițializare aplicație
app = FastAPI(
    title="EloLearning Platform API",
    description="Backend-ul pentru platforma de învățare EloLearning",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ORIGIN],
    allow_credentials=True,      # Permite trimiterea de cookies/tokeni de autentificare
    # Permite toate metodele HTTP (GET, POST, PUT, DELETE, etc.)
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(daily_goal.router)


@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "status": "ok",
        "message": "FastAPI funcționează perfect și CORS este configurat!"
    }
