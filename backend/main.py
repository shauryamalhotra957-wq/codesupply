from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.routers import projects


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database schema
    init_db()
    yield


app = FastAPI(
    title="CodeSupply SBOM & Supply Chain API",
    description="Automated multi-ecosystem SBOM generation (CycloneDX v1.5) and anomaly detection platform for SIH1449.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for local React/Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CodeSupply SBOM Engine",
        "version": "1.0.0",
        "supported_ecosystems": ["pypi", "npm"],
    }
