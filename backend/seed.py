from app.database import engine, Base, SessionLocal
from app.models import Reservation, Order, Payment, MenuItem, Customer

def init_and_seed_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Prevent duplicate insertions if run multiple times
    if db.query(MenuItem).first():
        print("Database already contains data. Skipping seeding.")
        db.close()
        return

    print("Inserting initial records...")

    # Menu items
    menu_items = [
        MenuItem(name="Cappuccino", cat="Coffee", price=180, avail=True),
        MenuItem(name="Cold Coffee", cat="Coffee", price=160, avail=True),
        MenuItem(name="Espresso", cat="Coffee", price=120, avail=True),
        MenuItem(name="Cold Brew", cat="Coffee", price=200, avail=True),
        MenuItem(name="Latte", cat="Coffee", price=190, avail=True),
        MenuItem(name="Paneer Sandwich", cat="Food", price=220, avail=True),
        MenuItem(name="Margherita Pizza", cat="Food", price=350, avail=True),
        MenuItem(name="Grilled Sandwich", cat="Food", price=210, avail=False),
        MenuItem(name="Veg Wrap", cat="Food", price=195, avail=True),
        MenuItem(name="Chocolate Cake", cat="Desserts", price=240, avail=True),
        MenuItem(name="Cheesecake", cat="Desserts", price=260, avail=True),
        MenuItem(name="Blueberry Muffin", cat="Desserts", price=130, avail=True),
        MenuItem(name="Masala Chai", cat="Beverages", price=60, avail=True),
        MenuItem(name="Green Tea", cat="Beverages", price=80, avail=True),
        MenuItem(name="Fresh Lime Soda", cat="Beverages", price=90, avail=True),
    ]

    # Reservations
    reservations = [
        Reservation(id="RES-2410", name="Priya Sharma", phone="9876543210", date="2026-08-31", time="12:30", guests=4, status="confirmed", channel="WhatsApp"),
        Reservation(id="RES-2409", name="Arjun Mehta", phone="9812345678", date="2026-08-31", time="13:00", guests=2, status="confirmed", channel="WhatsApp"),
        Reservation(id="RES-2408", name="Sonal Gupta", phone="9098765432", date="2026-08-31", time="19:30", guests=6, status="confirmed", channel="Phone"),
        Reservation(id="RES-2407", name="Rahul Verma", phone="9765432109", date="2026-08-31", time="20:00", guests=2, status="pending", channel="WhatsApp"),
    ]

    # Orders
    orders = [
        Order(id="ORD-5521", customer="Priya Sharma", items="Cappuccino x2, Paneer Sandwich", total=580, type="Dine-in", status="delivered", time="12:45"),
        Order(id="ORD-5520", customer="Arjun Mehta", items="Cold Coffee, Margherita Pizza", total=510, type="Dine-in", status="delivered", time="13:10"),
        Order(id="ORD-5519", customer="Rohan Das", items="Masala Chai x3, Samosa x4", total=340, type="Takeaway", status="paid", time="11:30"),
    ]

    # Customers
    customers = [
        Customer(name="Priya Sharma", phone="9876543210", orders=28, spend=14200, last_visit="31 Aug 2026", status="regular"),
        Customer(name="Arjun Mehta", phone="9812345678", orders=15, spend=7800, last_visit="31 Aug 2026", status="regular"),
        Customer(name="Anjali Kapoor", phone="9654321098", orders=42, spend=22400, last_visit="31 Aug 2026", status="vip"),
    ]

    db.add_all(menu_items + reservations + orders + customers)
    db.commit()
    db.close()
    print("Database initialization and seeding complete.")

if __name__ == "__main__":
    init_and_seed_db()