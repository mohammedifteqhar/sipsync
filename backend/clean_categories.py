import sys
from sqlalchemy import text
from app.database import engine

CATEGORY_FIXES = {
    "Chinese chi Boneless": "Chinese Chicken (Boneless)",
    "Fried chi an dBurgers": "Fried Chicken & Burgers",
    "DEsert": "Desserts",
    "FResh juices and Milk Shakes": "Fresh Juices & Milkshakes",
    "SAlad": "Salad",
    "soups": "Soups",
    "Fried Rice and Noddles": "Fried Rice & Noodles",
}

def clean_database_categories():
    print("Connecting to Supabase PostgreSQL database...")
    with engine.begin() as conn:
        for old_cat, new_cat in CATEGORY_FIXES.items():
            result = conn.execute(
                text("UPDATE menu SET cat = :new_cat WHERE cat = :old_cat"),
                {"new_cat": new_cat, "old_cat": old_cat}
            )
            print(f"Updated '{old_cat}' -> '{new_cat}': {result.rowcount} items affected")
    print("Database category names successfully normalized!")

if __name__ == "__main__":
    clean_database_categories()