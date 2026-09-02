from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import MenuItem, Order

router = APIRouter(prefix="/api/chat", tags=["AI Chat"])

class ChatRequest(BaseModel):
    message: str

@router.post("/")
def handle_chat_message(req: ChatRequest, db: Session = Depends(get_db)):
    msg = req.message.lower().strip()

    # Dynamic Menu Check
    if any(k in msg for k in ["menu", "coffee", "food", "drink", "price", "bestseller"]):
        items = db.query(MenuItem).filter(MenuItem.avail == True).limit(4).all()
        if items:
            item_list = ", ".join([f"{i.name} (₹{int(i.price)})" for i in items])
            return {
                "intent": "MENU_INQUIRY",
                "reply": f"Our top available items right now: {item_list}! Would you like to reserve a table or order for takeaway? ☕"
            }
        return {
            "intent": "MENU_INQUIRY",
            "reply": "We offer artisanal coffees, pizzas, wraps, and fresh desserts. Let me know what you crave!"
        }

    # Reservation Intent
    if any(k in msg for k in ["book", "table", "reserve", "seat", "reservation"]):
        return {
            "intent": "BOOKING",
            "reply": "I can arrange a table for you! Please tell me your preferred time, date, and how many guests are joining. 📅"
        }

    # Order Status Intent
    if any(k in msg for k in ["order", "status", "ord-"]):
        # Extract potential order ID token
        tokens = [t.upper() for t in msg.split() if "ORD-" in t.upper()]
        if tokens:
            order_id = tokens[0]
            existing_order = db.query(Order).filter(Order.id == order_id).first()
            if existing_order:
                return {
                    "intent": "STATUS",
                    "reply": f"Order {existing_order.id} for {existing_order.customer} ({existing_order.items}) is currently marked as '{existing_order.status.upper()}'. ✅"
                }
            return {
                "intent": "STATUS",
                "reply": f"I couldn't find an active order matching {order_id}. Please re-check the ID or ask the cashier counter."
            }
        return {
            "intent": "STATUS",
            "reply": "To check your order's live status, please provide your Order ID (for example, ORD-5521). 🔍"
        }

    # Review / Feedback Intent
    if any(k in msg for k in ["feedback", "good", "great", "review", "loved"]):
        return {
            "intent": "FEEDBACK",
            "reply": "Thank you so much for your kind words! We would love it if you shared your experience on Google Reviews: g.page/brewandco ⭐"
        }

    # General Fallback
    return {
        "intent": "GENERAL",
        "reply": "Hello! I am Brew & Co's virtual concierge. Ask me about available menu items, book a table, or ask for your order status! ☕"
    }