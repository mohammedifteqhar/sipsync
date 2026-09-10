import logging
import traceback
from typing import List, Optional
from fastapi import FastAPI, Request, Depends, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import Column, BigInteger, String, Float
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.routers import menu, reservations, chat

# Configure production-grade structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("sipsync")

# ----------------------------------------------------
# Database Model & Pydantic Schemas for Orders
# ----------------------------------------------------
class Order(Base):
    __tablename__ = "orders"
    __table_args__ = {"schema": "public", "extend_existing": True}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    customer = Column(String, nullable=False)
    items = Column(String, nullable=False)
    total = Column(Float, nullable=False)
    type = Column(String, default="Dine-in")
    status = Column(String, default="pending")

# Initialize schema metadata
Base.metadata.create_all(bind=engine)

class OrderCreate(BaseModel):
    customer: str
    items: str
    total: float
    type: Optional[str] = "Dine-in"
    status: Optional[str] = "pending"

class OrderStatusUpdate(BaseModel):
    status: str

class OrderResponse(BaseModel):
    id: int
    customer: str
    items: str
    total: float
    type: str
    status: str

    class Config:
        from_attributes = True

# ----------------------------------------------------
# App Initialization & Production Middleware
# ----------------------------------------------------
app = FastAPI(
    title="Raidan RMS API",
    description="Production-grade asynchronous hospitality management engine and digital ordering pipeline.",
    version="1.0.0"
)

ALLOWED_ORIGINS = [
    "https://sipsync-dashboard.onrender.com",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming {request.method} request to {request.url.path}")
    try:
        response = await call_next(request)
        logger.info(f"Completed {request.method} {request.url.path} with status {response.status_code}")
        return response
    except Exception as e:
        err_tb = traceback.format_exc()
        logger.error(f"Unhandled error processing {request.url.path}:\n{err_tb}")
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "detail": "Internal server error occurred.",
                "traceback": err_tb
            }
        )

# ----------------------------------------------------
# Modular Routers
# ----------------------------------------------------
app.include_router(menu.router, prefix="/api/menu", tags=["Menu & Inventory"])
app.include_router(reservations.router, prefix="/api/reservations", tags=["Reservations"])
app.include_router(chat.router, prefix="/api/chat", tags=["Virtual Concierge"])

# ----------------------------------------------------
# Live Kitchen Orders Endpoints
# ----------------------------------------------------
MANAGER_KEY = "sipsync-admin-2026"

@app.post("/api/orders/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, tags=["Orders"])
def place_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """Public customer-facing endpoint called by order.html when scanning table QR codes."""
    new_order = Order(
        customer=order_data.customer,
        items=order_data.items,
        total=order_data.total,
        type=order_data.type or "Dine-in",
        status=order_data.status or "pending"
    )
    try:
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        logger.info(f"New QR order created: #{new_order.id} for {new_order.customer} (Total: ₹{new_order.total})")
        return new_order
    except Exception as err:
        db.rollback()
        logger.error(f"Failed to commit order to database: {str(err)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database insertion failed: {str(err)}"
        )

@app.get("/api/orders/", response_model=List[OrderResponse], tags=["Orders"])
def get_live_orders(db: Session = Depends(get_db)):
    """Called by manager dashboard to poll incoming kitchen orders."""
    try:
        return db.query(Order).order_by(Order.id.desc()).all()
    except Exception as err:
        db.rollback()
        logger.error(f"Failed to query orders: {str(err)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failed: {str(err)}"
        )

@app.patch("/api/orders/{order_id}/status", response_model=OrderResponse, tags=["Orders"])
def update_order_status(
    order_id: int, 
    update_data: OrderStatusUpdate, 
    db: Session = Depends(get_db),
    x_manager_key: Optional[str] = Header(None)
):
    """Allows floor manager to transition orders from pending -> served -> paid."""
    if x_manager_key != MANAGER_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or missing X-Manager-Key header."
        )

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    try:
        order.status = update_data.status
        db.commit()
        db.refresh(order)
        logger.info(f"Order #{order.id} transitioned to {order.status}")
        return order
    except Exception as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update order status: {str(err)}"
        
        )
        
from app.models import CustomerReview, ServiceRequest

class ReviewCreate(BaseModel):
    table_number: str
    order_id: Optional[int] = None
    food_rating: int
    service_rating: int
    ambiance_rating: int
    tags: List[str] = []

class ServiceRequestCreate(BaseModel):
    table_number: str
    request_type: str

# ── 1. Reviews Endpoint ──
@app.post("/api/reviews/", status_code=status.HTTP_201_CREATED, tags=["Feedback"])
def submit_review(data: ReviewCreate, db: Session = Depends(get_db)):
    review = CustomerReview(
        table_number=data.table_number,
        order_id=data.order_id,
        food_rating=data.food_rating,
        service_rating=data.service_rating,
        ambiance_rating=data.ambiance_rating,
        tags=data.tags
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return {"status": "success", "review_id": review.id}

# ── 2. Silent Waiter Call Endpoints ──
@app.post("/api/service-requests/", status_code=status.HTTP_201_CREATED, tags=["Assistance"])
def create_service_request(data: ServiceRequestCreate, db: Session = Depends(get_db)):
    req = ServiceRequest(
        table_number=data.table_number,
        request_type=data.request_type,
        status="pending"
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req

@app.get("/api/service-requests/active", tags=["Assistance"])
def get_active_service_requests(db: Session = Depends(get_db)):
    """Polled by manager dashboard to show active calls."""
    return db.query(ServiceRequest).filter(ServiceRequest.status == "pending").all()

@app.patch("/api/service-requests/{req_id}/attend", tags=["Assistance"])
def attend_service_request(req_id: int, db: Session = Depends(get_db)):
    req = db.query(ServiceRequest).filter(ServiceRequest.id == req_id).first()
    if req:
        req.status = "attended"
        db.commit()
    return {"status": "attended"}

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "Raidan RMS API",
        "environment": "production"
    }