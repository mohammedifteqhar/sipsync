import os
from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.models import MenuItem

router = APIRouter()

MANAGER_API_KEY = os.getenv("MANAGER_API_KEY", "sipsync-admin-2026")

def verify_manager_access(x_manager_key: Optional[str] = Header(None)):
    """Guards administrative endpoints against unauthorized public modification."""
    if x_manager_key != MANAGER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Valid manager access key required."
        )
    return True

# ── Pydantic Request Models for Menu Operations ──
class ItemImageUpdate(BaseModel):
    image_url: Optional[str] = None

class ItemDetailsUpdate(BaseModel):
    name: Optional[str] = None
    cat: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None

@router.get("/")
def get_public_menu(db: Session = Depends(get_db)):
    """Public endpoint: Returns all menu items sorted by ID."""
    return db.query(models.MenuItem).order_by(models.MenuItem.id.asc()).all()

@router.patch("/{item_id}/toggle")
def toggle_item_availability(
    item_id: int, 
    db: Session = Depends(get_db),
    _: bool = Depends(verify_manager_access)
):
    """Protected endpoint: Only managers can toggle item 86/in-stock availability."""
    item = db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Menu item with ID {item_id} does not exist."
        )
    
    item.avail = not item.avail
    db.commit()
    db.refresh(item)
    return item

@router.patch("/{item_id}/image")
def update_item_image(
    item_id: int,
    payload: ItemImageUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_manager_access)
):
    """Protected endpoint: Allows floor manager to attach or update a dish photo URL."""
    item = db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu item with ID {item_id} does not exist."
        )

    item.image_url = payload.image_url
    db.commit()
    db.refresh(item)
    return item

@router.put("/{item_id}")
def update_menu_item(
    item_id: int,
    payload: ItemDetailsUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_manager_access)
):
    """Protected endpoint: Allows editing dish name, price, category typos, and image."""
    item = db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu item with ID {item_id} does not exist."
        )

    update_dict = payload.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item