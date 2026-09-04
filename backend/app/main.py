import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.database import engine, Base
from app.routers import menu, reservations, chat

# Configure production-grade structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("sipsync")

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SipSync API",
    description="Production-grade asynchronous hospitality management engine and virtual concierge.",
    version="1.0.0"
)

# Explicit Production CORS Whitelist
ALLOWED_ORIGINS = [
    "https://sipsync-dashboard.onrender.com",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming {request.method} request to {request.url.path}")
    try:
        response = await call_next(request)
        logger.info(f"Completed {request.method} {request.url.path} with status {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Unhandled error processing {request.url.path}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error occurred. Please contact support."}
        )

# Include Modular Routers
app.include_router(menu.router, prefix="/api/menu", tags=["Menu & Inventory"])
app.include_router(reservations.router, prefix="/api/reservations", tags=["Reservations"])
app.include_router(chat.router, prefix="/api/chat", tags=["Virtual Concierge"])

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "SipSync Backend API",
        "environment": "production"
    }