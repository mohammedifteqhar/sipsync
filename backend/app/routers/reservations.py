from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Reservation
from app.schemas import ReservationResponse, ReservationCreate

router = APIRouter(prefix="/api/reservations", tags=["Reservations"])

@router.get("/", response_model=List[ReservationResponse])
def get_all_reservations(db: Session = Depends(get_db)):
    return db.query(Reservation).all()

@router.post("/", response_model=ReservationResponse)
def create_reservation(res_in: ReservationCreate, db: Session = Depends(get_db)):
    new_res = Reservation(**res_in.model_dump())
    db.add(new_res)
    db.commit()
    db.refresh(new_res)
    return new_res