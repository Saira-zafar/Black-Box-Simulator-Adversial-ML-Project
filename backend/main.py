"""
Black-Box Attack Simulator Backend Server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.api.routes import router as api_router
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and seed predefined scenarios
    init_db()
    yield


app = FastAPI(
    title="Black-Box Attack Simulator Engine",
    description="Safe, local-only cybersecurity educational testing engine and assessment generator.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for local frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
