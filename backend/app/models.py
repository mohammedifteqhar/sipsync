from sqlalchemy import Column, Integer, BigInteger, String, Float, Boolean, Text
from app.database import Base

class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = {"schema": "public", "extend_existing": True}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    guests = Column(Integer, default=2)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    seating_area = Column(String, default="Ground Floor Dining")
    status = Column(String, default="confirmed")
    channel = Column(String, default="Online Customer")
    notes = Column(Text, nullable=True)

class Order(Base):
    __tablename__ = "orders"
    __table_args__ = {"schema": "public", "extend_existing": True}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    customer = Column(String, nullable=False)
    items = Column(String, nullable=False)
    total = Column(Float, nullable=False)
    type = Column(String, default="Dine-in")
    status = Column(String, default="pending")
    time = Column(String, nullable=True)

class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = {"schema": "public", "extend_existing": True}

    id = Column(String, primary_key=True, index=True)
    order_id = Column(String, nullable=False)
    customer = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    method = Column(String, default="UPI")
    status = Column(String, default="paid")
    dt = Column(String, nullable=False)

class MenuItem(Base):
    __tablename__ = "menu"
    __table_args__ = {"schema": "public", "extend_existing": True}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    cat = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    avail = Column(Boolean, default=True)
    image_url = Column(String, nullable=True)

class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = {"schema": "public", "extend_existing": True}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False, unique=True)
    orders = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    last_visit = Column(String, nullable=False)
    status = Column(String, default="new")
    
from sqlalchemy import ARRAY

class CustomerReview(Base):
    __tablename__ = "customer_reviews"
    __table_args__ = {"schema": "public", "extend_existing": True}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    table_number = Column(String, nullable=False)
    order_id = Column(BigInteger, nullable=True)
    food_rating = Column(Integer, nullable=False)
    service_rating = Column(Integer, nullable=False)
    ambiance_rating = Column(Integer, nullable=False)
    tags = Column(ARRAY(String), nullable=True)
    created_at = Column(String, nullable=True)

class ServiceRequest(Base):
    __tablename__ = "service_requests"
    __table_args__ = {"schema": "public", "extend_existing": True}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    table_number = Column(String, nullable=False)
    request_type = Column(String, nullable=False)
    status = Column(String, default="pending")