from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from app.database import Base

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    cat = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    avail = Column(Boolean, default=True)
    image_url = Column(String, nullable=True)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer = Column(String, nullable=False)
    items = Column(String, nullable=False)
    total = Column(Float, nullable=False)
    type = Column(String, default="Dine-in")
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    guests = Column(Integer, default=2)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    seating_area = Column(String, default="Ground Floor Dining")
    channel = Column(String, default="Walk-in Desk")
    status = Column(String, default="confirmed")