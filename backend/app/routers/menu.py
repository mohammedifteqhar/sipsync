from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import MenuItem

router = APIRouter(prefix="/menu", tags=["Menu"])

MANAGER_SECRET = "sipsync-admin-2026"

# Pydantic Schemas
class MenuItemOut(BaseModel):
    id: int
    name: str
    cat: str
    price: float
    avail: bool
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

class MenuItemCreate(BaseModel):
    name: str
    cat: str
    price: float
    avail: bool = True
    image_url: Optional[str] = None

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    cat: Optional[str] = None
    price: Optional[float] = None
    avail: Optional[bool] = None
    image_url: Optional[str] = None

# 1. Fetch entire catalog
@router.get("/", response_model=List[MenuItemOut])
def get_all_menu_items(db: Session = Depends(get_db)):
    items = db.query(MenuItem).order_by(MenuItem.cat.asc(), MenuItem.name.asc()).all()
    return items

# 2. Fetch single item
@router.get("/{item_id}", response_model=MenuItemOut)
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# 3. Toggle availability (Manager Action)
@router.patch("/{item_id}/toggle", response_model=MenuItemOut)
def toggle_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    x_manager_key: Optional[str] = Header(None)
):
    if x_manager_key != MANAGER_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing manager key"
        )
    
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    item.avail = not item.avail
    db.commit()
    db.refresh(item)
    return item

# 4. Create new menu item
@router.post("/", response_model=MenuItemOut, status_code=status.HTTP_201_CREATED)
def create_menu_item(
    payload: MenuItemCreate,
    db: Session = Depends(get_db),
    x_manager_key: Optional[str] = Header(None)
):
    if x_manager_key != MANAGER_SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    new_item = MenuItem(
        name=payload.name,
        cat=payload.cat,
        price=payload.price,
        avail=payload.avail,
        image_url=payload.image_url
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

# 5. Update existing menu item
@router.patch("/{item_id}", response_model=MenuItemOut)
def update_menu_item(
    item_id: int,
    payload: MenuItemUpdate,
    db: Session = Depends(get_db),
    x_manager_key: Optional[str] = Header(None)
):
    if x_manager_key != MANAGER_SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item