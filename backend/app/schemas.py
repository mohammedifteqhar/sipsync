from pydantic import BaseModel
from typing import Optional

# Menu Schemas
class MenuItemBase(BaseModel):
    name: str
    cat: str
    price: float
    avail: bool = True

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemResponse(MenuItemBase):
    id: int
    class Config:
        from_attributes = True

# Reservation Schemas
class ReservationBase(BaseModel):
    id: str
    name: str
    phone: str
    date: str
    time: str
    guests: int = 2
    status: str = "confirmed"
    channel: str = "WhatsApp"

class ReservationCreate(ReservationBase):
    pass

class ReservationResponse(ReservationBase):
    class Config:
        from_attributes = True

# Order Schemas
class OrderBase(BaseModel):
    id: str
    customer: str
    items: str
    total: float
    type: str = "Dine-in"
    status: str = "pending"
    time: str

class OrderResponse(OrderBase):
    class Config:
        from_attributes = True

# Customer Schemas
class CustomerResponse(BaseModel):
    id: int
    name: str
    phone: str
    orders: int
    spend: float
    last_visit: str
    status: str

    class Config:
        from_attributes = True