import os
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas

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

@router.get("/")
def get_public_menu(db: Session = Depends(get_db)):
    """Public endpoint: Returns all menu items."""
    return db.query(models.MenuItem).all()

@router.patch("/{item_id}/toggle")
def toggle_item_availability(
    item_id: int, 
    db: Session = Depends(get_db),
    _: bool = Depends(verify_manager_access)
):
    """Protected endpoint: Only managers can toggle item stock."""
    item = db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Menu item with ID {item_id} does not exist."
        )
    
    # Correct column name: 'avail'
    item.avail = not item.avail
    db.commit()
    db.refresh(item)
    return item