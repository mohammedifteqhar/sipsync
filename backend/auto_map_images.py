import os
import re
from pathlib import Path
from urllib.parse import quote
from rapidfuzz import process, fuzz
from sqlalchemy import text
from app.database import engine

PROJECT_REF = "svvpcovpfijuexogqmhh"
BUCKET_NAME = "menu-images"
BASE_URL = f"https://{PROJECT_REF}.supabase.co/storage/v1/object/public/{BUCKET_NAME}"
IMAGES_FOLDER = r"D:\sipsync\menu-images"

def clean_name(val: str) -> str:
    """Normalize file and dish names for accurate fuzzy matching."""
    name = Path(val).stem
    name = re.sub(r"[_\-\d]+", " ", name)
    return name.strip().lower()

def auto_assign():
    valid_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    image_files = [
        f for f in os.listdir(IMAGES_FOLDER) 
        if Path(f).suffix.lower() in valid_extensions
    ]
    print(f"Found {len(image_files)} images in local directory.")

    cleaned_file_map = {clean_name(f): f for f in image_files}
    clean_choices = list(cleaned_file_map.keys())

    with engine.begin() as conn:
        items = conn.execute(text("SELECT id, name FROM menu_items")).fetchall()
        print(f"Loaded {len(items)} menu items from database.\n")

        matched_count = 0
        for item_id, dish_name in items:
            cleaned_dish = clean_name(dish_name)

            best_match, score, _ = process.extractOne(
                cleaned_dish, 
                clean_choices, 
                scorer=fuzz.token_sort_ratio
            )

            if score >= 60:
                actual_filename = cleaned_file_map[best_match]
                safe_filename = quote(actual_filename)
                public_url = f"{BASE_URL}/{safe_filename}"

                conn.execute(
                    text("UPDATE menu_items SET image_url = :url WHERE id = :id"),
                    {"url": public_url, "id": item_id}
                )
                print(f"[{score:.0f}%] '{dish_name}' -> {actual_filename}")
                matched_count += 1
            else:
                print(f"[NO MATCH] '{dish_name}' (Closest: '{best_match}' with {score:.0f}%)")

        print(f"\nCompleted: Assigned {matched_count}/{len(items)} images.")

if __name__ == "__main__":
    auto_assign()