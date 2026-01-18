"""Main FastAPI application for Timetable Management System."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Timetable Management System API",
    description="Backend API for Codora.ai Timetable Management System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Timetable Management System API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Database health check."""
    return {"status": "healthy", "database": "connected"}


# Import routers here
# from app.routes import upload, schedule, conflicts, admin
# app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
# app.include_router(schedule.router, prefix="/api/schedule", tags=["Schedule"])
# app.include_router(conflicts.router, prefix="/api/conflicts", tags=["Conflicts"])
# app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
