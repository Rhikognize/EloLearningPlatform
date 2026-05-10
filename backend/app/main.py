from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth

# Inițializare aplicație
app = FastAPI(
    title="EloLearning Platform API",
    description="Backend-ul pentru platforma de învățare EloLearning",
    version="1.0.0"
)

# Configurare CORS


app.add_middleware(
    CORSMiddleware,
    # Permite request-uri doar de la originile specificate
    allow_origins=[settings.CORS_ORIGIN],
    allow_credentials=True,      # Permite trimiterea de cookies/tokeni de autentificare
    # Permite toate metodele HTTP (GET, POST, PUT, DELETE, etc.)
    allow_methods=["*"],
    allow_headers=["*"],         # Permite toate headerele
)

# Endpoint de test (Health Check)

app.include_router(auth.router)


@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "status": "ok",
        "message": "FastAPI funcționează perfect și CORS este configurat!"
    }
