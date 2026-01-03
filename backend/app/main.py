from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from sqlalchemy import event
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.database import engine, Base
from app.routers import auth, users, admin
from app.routers import appointments

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SPHERE API")

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(appointments.router)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "project": "SPHERE"}

# Serve frontend static files (configure this after building frontend)
# Uncomment after frontend build:
# app.mount("/assets", StaticFiles(directory="../frontend/dist/assets"), name="assets")
# @app.get("/{full_path:path}")
# async def serve_frontend(full_path: str):
#     return FileResponse("../frontend/dist/index.html")