import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel
from sqlalchemy import Column, BigInteger, String, Integer, Text
from sqlalchemy.orm import Session
from app.database import Base, get_db

logger = logging.getLogger("sipsync")
router = APIRouter()
MANAGER_KEY = "sipsync-admin-2026"

# ----------------------------------------------------
# SQLAlchemy Database Model
# ----------------------------------------------------
class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = {"schema": "public", "extend_existing": True}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    guests = Column(Integer, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    seating_area = Column(String, default="Ground Floor Dining")
    channel = Column(String, default="Online Customer")
    status = Column(String, default="confirmed")
    notes = Column(Text, nullable=True)

# ----------------------------------------------------
# Pydantic Schemas
# ----------------------------------------------------
class ReservationCreate(BaseModel):
    name: str
    phone: str
    guests: int
    date: str
    time: str
    seating_area: Optional[str] = "Ground Floor Dining"
    channel: Optional[str] = "Online Customer"
    notes: Optional[str] = None

class ReservationStatusUpdate(BaseModel):
    status: str

class ReservationOut(BaseModel):
    id: int
    name: str
    phone: str
    guests: int
    date: str
    time: str
    seating_area: str
    channel: str
    status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# ----------------------------------------------------
# Endpoints (Accepting both with and without trailing slash)
# ----------------------------------------------------
@router.post("/", response_model=ReservationOut, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=ReservationOut, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_reservation(payload: ReservationCreate, db: Session = Depends(get_db)):
    """Public customer and walk-in reservation creation with collision checks."""
    target_spot = (payload.seating_area or "Ground Floor Dining").strip()

    # 1. Query confirmed/seated bookings for the same date
    existing_bookings = db.query(Reservation).filter(
        Reservation.date == payload.date,
        Reservation.status.in_(["confirmed", "seated"])
    ).all()

    # 2. Collision Guard: Check spot match and 90-minute dining block overlap
    try:
        new_time = datetime.strptime(payload.time, "%H:%M")
        for b in existing_bookings:
            b_spot = (b.seating_area or "").strip().lower()
            # Match specific cabin or table designation (e.g., M-01, T-02)
            if target_spot.lower() in b_spot or b_spot in target_spot.lower():
                try:
                    b_time = datetime.strptime(b.time, "%H:%M")
                    # 5400 seconds = 90-minute dining window
                    if abs((new_time - b_time).total_seconds()) < 5400:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail=f"Spot '{target_spot}' is already booked around {b.time} on {payload.date}. Please select another table/cabin or time."
                        )
                except ValueError:
                    continue
    except ValueError:
        pass  # If time format is irregular, proceed to save

    # 3. Create confirmed reservation
    res = Reservation(
        name=payload.name,
        phone=payload.phone,
        guests=payload.guests,
        date=payload.date,
        time=payload.time,
        seating_area=target_spot,
        channel=payload.channel or "Online Customer",
        status="confirmed",
        notes=payload.notes
    )
    try:
        db.add(res)
        db.commit()
        db.refresh(res)
        logger.info(f"New reservation created: #RES-{res.id} for {res.name} at {res.seating_area} ({res.channel})")
        return res
    except Exception as err:
        db.rollback()
        logger.error(f"Failed to commit reservation: {str(err)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database insertion failed: {str(err)}"
        )

@router.get("/", response_model=List[ReservationOut])
@router.get("", response_model=List[ReservationOut], include_in_schema=False)
def get_reservations(db: Session = Depends(get_db)):
    """Fetch all reservations for manager dashboard."""
    try:
        return db.query(Reservation).order_by(Reservation.id.desc()).all()
    except Exception as err:
        db.rollback()
        logger.error(f"Failed to query reservations: {str(err)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failed: {str(err)}"
        )

@router.patch("/{res_id}/status", response_model=ReservationOut)
def update_reservation_status(
    res_id: int,
    payload: ReservationStatusUpdate,
    db: Session = Depends(get_db),
    x_manager_key: Optional[str] = Header(None)
):
    """Floor manager transitions: confirmed -> seated -> cancelled."""
    if x_manager_key != MANAGER_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Manager-Key header."
        )

    res = db.query(Reservation).filter(Reservation.id == res_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found.")

    try:
        res.status = payload.status
        db.commit()
        db.refresh(res)
        logger.info(f"Reservation #RES-{res.id} transitioned to {res.status}")
        return res
    except Exception as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update reservation: {str(err)}"
        )
class CustomerCancelRequest(BaseModel):
    phone: str

@router.post("/{res_id}/cancel", response_model=ReservationOut)
def customer_cancel_reservation(
    res_id: int,
    payload: CustomerCancelRequest,
    db: Session = Depends(get_db)
):
    """Allows a guest to self-cancel by providing their booking ID and matching phone number."""
    res = db.query(Reservation).filter(Reservation.id == res_id).first()
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Reservation not found."
        )

    # Security check: verify phone matches
    cleaned_input_phone = "".join(filter(str.isdigit, payload.phone))
    cleaned_db_phone = "".join(filter(str.isdigit, res.phone))

    if not cleaned_input_phone or cleaned_input_phone != cleaned_db_phone:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="The phone number provided does not match this booking."
        )

    if res.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="This reservation has already been cancelled."
        )

    if res.status == "seated":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cannot cancel a reservation after being seated."
        )

    try:
        res.status = "cancelled"
        db.commit()
        db.refresh(res)
        logger.info(f"Customer self-cancelled reservation #RES-{res.id} ({res.name})")
        return res
    except Exception as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel booking: {str(err)}"
        )