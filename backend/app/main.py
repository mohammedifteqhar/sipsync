import os
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.database import engine, Base, get_db
from app.models import Order, Reservation, MenuItem
from app.routers import menu

# Create database tables if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SipSync & Raidan Restaurant API",
    version="2.0.0",
    description="Live Kitchen Display, Table QR Ordering, and POS API"
)

# Allow requests from Render dashboard, local testing, and customer devices
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MANAGER_SECRET = "sipsync-admin-2026"

# Include Menu Router
app.include_router(menu.router, prefix="/api")

# --- Pydantic Schemas ---

class OrderCreate(BaseModel):
    customer: str
    items: str
    total: float
    type: Optional[str] = "Dine-in"
    status: Optional[str] = "pending"

class OrderOut(BaseModel):
    id: int
    customer: str
    items: str
    total: float
    type: Optional[str]
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: str

class ReservationCreate(BaseModel):
    name: str
    phone: str
    guests: int
    date: str
    time: str
    seating_area: Optional[str] = "Ground Floor Dining"
    channel: Optional[str] = "Walk-in Desk"
    status: Optional[str] = "confirmed"

class ReservationOut(BaseModel):
    id: int
    name: str
    phone: str
    guests: int
    date: str
    time: str
    seating_area: Optional[str]
    channel: Optional[str]
    status: str

    class Config:
        from_attributes = True

class ReservationStatusUpdate(BaseModel):
    status: str

class ServiceRequest(BaseModel):
    table_number: str
    request_type: str

class ReviewCreate(BaseModel):
    table_number: str
    food_rating: int
    service_rating: int
    ambiance_rating: int
    tags: Optional[List[str]] = []

# --- System Health & Root ---

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "SipSync Restaurant Management API",
        "docs": "/docs"
    }

# --- Orders Endpoints ---

@app.get("/api/orders/", response_model=List[OrderOut])
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).order_by(Order.id.desc()).all()

@app.post("/api/orders/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    new_order = Order(
        customer=payload.customer,
        items=payload.items,
        total=payload.total,
        type=payload.type,
        status=payload.status or "pending"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@app.patch("/api/orders/{order_id}/status", response_model=OrderOut)
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    x_manager_key: Optional[str] = Header(None)
):
    if x_manager_key != MANAGER_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: invalid or missing manager key"
        )
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = payload.status
    db.commit()
    db.refresh(order)
    return order

# --- Reservations Endpoints ---

@app.get("/api/reservations/", response_model=List[ReservationOut])
def get_reservations(db: Session = Depends(get_db)):
    return db.query(Reservation).order_by(Reservation.id.desc()).all()

@app.post("/api/reservations/", response_model=ReservationOut, status_code=status.HTTP_201_CREATED)
def create_reservation(payload: ReservationCreate, db: Session = Depends(get_db)):
    new_res = Reservation(
        name=payload.name,
        phone=payload.phone,
        guests=payload.guests,
        date=payload.date,
        time=payload.time,
        seating_area=payload.seating_area,
        channel=payload.channel,
        status=payload.status or "confirmed"
    )
    db.add(new_res)
    db.commit()
    db.refresh(new_res)
    return new_res

@app.patch("/api/reservations/{reservation_id}/status", response_model=ReservationOut)
def update_reservation_status(
    reservation_id: int,
    payload: ReservationStatusUpdate,
    db: Session = Depends(get_db),
    x_manager_key: Optional[str] = Header(None)
):
    if x_manager_key != MANAGER_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: invalid or missing manager key"
        )

    res = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")

    res.status = payload.status
    db.commit()
    db.refresh(res)
    return res

# --- Waiter Call & Micro-Feedback Endpoints ---

@app.post("/api/service-requests/", status_code=status.HTTP_200_OK)
def log_service_request(req: ServiceRequest):
    # Logs service requests silently for floor attendants
    print(f"[SERVICE ALERT] Table: {req.table_number} -> {req.request_type}")
    return {"status": "success", "message": "Floor captain paged"}

@app.post("/api/reviews/", status_code=status.HTTP_200_OK)
def log_customer_review(review: ReviewCreate):
    # Logs review ratings for quality control and analytics
    print(f"[CUSTOMER REVIEW] Table: {review.table_number} | Food: {review.food_rating}★ | Service: {review.service_rating}★ | Tags: {review.tags}")
    return {"status": "success", "message": "Feedback recorded"}