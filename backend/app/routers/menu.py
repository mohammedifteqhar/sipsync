from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import MenuItem
from app.schemas import MenuItemResponse, MenuItemCreate

router = APIRouter(prefix="/api/menu", tags=["Menu"])

@router.get("/", response_model=List[MenuItemResponse])
def get_all_menu_items(db: Session = Depends(get_db)):
    return db.query(MenuItem).all()

@router.put("/{item_id}/toggle")
def toggle_menu_item_availability(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.avail = not item.avail
    db.commit()
    return {"message": "Availability updated", "id": item.id, "avail": item.avail}