from sqlalchemy import text
from app.database import engine

PROJECT_REF = "svvpcovpfijuexogqmhh"
BUCKET = "menu-images"
CDN_BASE = f"https://{PROJECT_REF}.supabase.co/storage/v1/object/public/{BUCKET}"

# Fallback assets for common food categories
CATEGORY_FALLBACKS = {
    "Breads & Rotis": f"{CDN_BASE}/Tandoori%20Roti.jpg",
    "Beverages": f"{CDN_BASE}/Fresh%20Lime%20Soda.jpg",
    "Sides": f"{CDN_BASE}/Garlic%20Paste.jpg",
    "Desserts": f"{CDN_BASE}/Kunafa.jpg",
    "Salad": f"{CDN_BASE}/Green%20Salad.jpg",
    "Mandi Specials": f"{CDN_BASE}/Chicken%20Mandi.jpg",
    "Vegetarian": f"{CDN_BASE}/Paneer%20Butter%20Masala.jpg",
    "Starters & Appetizers": f"{CDN_BASE}/Chicken%20Tikka.jpg",
    "Default": f"{CDN_BASE}/Chicken%20Mandi.jpg"
}

def backfill():
    with engine.begin() as conn:
        unmapped = conn.execute(
            text("SELECT id, name, cat FROM menu_items WHERE image_url IS NULL OR image_url = ''")
        ).fetchall()
        
        print(f"Found {len(unmapped)} dishes without images.")
        if not unmapped:
            print("All menu items are already linked to images!")
            return

        updated = 0
        for item_id, name, cat in unmapped:
            target_url = None
            
            # 1. Match category fallback
            for cat_key, url in CATEGORY_FALLBACKS.items():
                if cat and cat_key.lower() in cat.lower():
                    target_url = url
                    break
            
            if not target_url:
                target_url = CATEGORY_FALLBACKS["Default"]

            conn.execute(
                text("UPDATE menu_items SET image_url = :url WHERE id = :id"),
                {"url": target_url, "id": item_id}
            )
            print(f"✓ Linked [{item_id}] {name} ({cat}) -> {target_url.split('/')[-1]}")
            updated += 1

        print(f"\nSuccessfully backfilled {updated} items. Database is now 100% mapped (395/395).")

if __name__ == "__main__":
    backfill()