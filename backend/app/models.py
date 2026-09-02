from sqlalchemy import Column, Integer, String, Float, Boolean
from app.database import Base

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    guests = Column(Integer, default=2)
    status = Column(String, default="confirmed")
    channel = Column(String, default="WhatsApp")

class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)
    customer = Column(String, nullable=False)
    items = Column(String, nullable=False)
    total = Column(Float, nullable=False)
    type = Column(String, default="Dine-in")
    status = Column(String, default="pending")
    time = Column(String, nullable=False)

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, index=True)
    order_id = Column(String, nullable=False)
    customer = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    method = Column(String, default="UPI")
    status = Column(String, default="success")
    dt = Column(String, nullable=False)

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    cat = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    avail = Column(Boolean, default=True)

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False, unique=True)
    orders = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    last_visit = Column(String, nullable=False)
    status = Column(String, default="new")