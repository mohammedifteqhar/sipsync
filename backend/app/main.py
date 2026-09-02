from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import menu, reservations, chat

app = FastAPI(
    title="SipSync API",
    description="Asynchronous Backend for Cafe Operations and CRM Management",
    version="1.0.0"
)

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all modular routers
app.include_router(menu.router)
app.include_router(reservations.router)
app.include_router(chat.router)

@app.get("/")
def health_check():
    return {"status": "online", "system": "SipSync Engine"}
