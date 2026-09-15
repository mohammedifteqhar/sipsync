import os
import qrcode
from PIL import Image, ImageDraw, ImageFont

# Base production URL where customer menu is hosted
BASE_ORDER_URL = "https://sipsync-dashboard.onrender.com/order.html"

# Output directory for generated assets
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "qr_codes"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 22 Dining Units
SPOTS = [
    # Ground Floor
    ("T-01", "Ground Floor Table"),
    ("T-02", "Ground Floor Table"),
    ("T-03", "Ground Floor Table"),
    ("T-04", "Ground Floor Table"),
    ("T-05", "Ground Floor Table"),
    ("T-06", "Ground Floor Table"),
    ("T-07", "Ground Floor Table"),
    ("T-08", "Ground Floor Table"),
    ("T-09", "Ground Floor Table"),
    ("T-10", "Ground Floor Table"),
    ("T-11", "Ground Floor Table"),
    ("T-12", "Ground Floor Table"),
    ("T-13", "Ground Floor Table"),
    ("T-14", "Ground Floor Table"),
    # First Floor Majlis Cabins
    ("M-01", "Majlis Cabin (Floor Seating)"),
    ("M-02", "Majlis Cabin (Floor Seating)"),
    ("M-03", "Majlis Cabin (Floor Seating)"),
    ("M-04", "Majlis Cabin (Floor Seating)"),
    ("M-05", "Majlis Cabin (Floor Seating)"),
    ("M-06", "Majlis Cabin (Floor Seating)"),
    ("M-07", "Majlis Cabin (Floor Seating)"),
    # VIP Dining
    ("VIP-01", "Private VIP Hall")
]

# Color Palette
CLR_BG = (247, 246, 243)       # Warm soft background
CLR_PRIMARY = (11, 32, 24)      # Deep Forest Black
CLR_ACCENT = (184, 115, 51)     # Arabian Copper / Gold
CLR_WHITE = (255, 255, 255)
CLR_MUTED = (115, 113, 109)
CLR_BORDER = (232, 230, 225)

def get_font(size: int, bold: bool = False):
    """Load default truetype or standard fallback."""
    font_names = ["arialbd.ttf" if bold else "arial.ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except IOError:
            continue
    return ImageFont.load_default()

def generate_qr_card(spot_id: str, label: str) -> Image.Image:
    card_w, card_h = 800, 1060
    card = Image.new("RGB", (card_w, card_h), CLR_BG)
    draw = ImageDraw.Draw(card)

    # 1. Outer Frame / Border
    draw.rectangle([(20, 20), (card_w - 20, card_h - 20)], fill=CLR_WHITE, outline=CLR_BORDER, width=3)

    # 2. Header Brand Banner
    draw.rectangle([(20, 20), (card_w - 20, 140)], fill=CLR_PRIMARY)
    f_brand = get_font(38, bold=True)
    f_sub = get_font(18, bold=False)
    
    draw.text((card_w // 2, 60), "RAIDAN RESTAURANT", font=f_brand, fill=CLR_WHITE, anchor="mm")
    draw.text((card_w // 2, 104), "The Authentic Taste of Arabia · Frazer Town", font=f_sub, fill=CLR_ACCENT, anchor="mm")

    # 3. QR Code Generation
    target_url = f"{BASE_ORDER_URL}?table={spot_id}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=11,
        border=2
    )
    qr.add_data(target_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=CLR_PRIMARY, back_color=CLR_WHITE).convert("RGB")

    qr_size = 460
    qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
    
    # QR Container Box with border
    qr_x = (card_w - qr_size) // 2
    qr_y = 190
    draw.rectangle(
        [(qr_x - 14, qr_y - 14), (qr_x + qr_size + 14, qr_y + qr_size + 14)],
        fill=CLR_WHITE,
        outline=CLR_BORDER,
        width=2
    )
    card.paste(qr_img, (qr_x, qr_y))

    # 4. Spot Identifier Badge
    badge_w, badge_h = 360, 68
    badge_x = (card_w - badge_w) // 2
    badge_y = 700
    draw.rounded_rectangle([(badge_x, badge_y), (badge_x + badge_w, badge_y + badge_h)], radius=18, fill=CLR_PRIMARY)
    
    f_spot = get_font(32, bold=True)
    display_title = f"Majlis {spot_id}" if spot_id.startswith("M") else (f"Table {spot_id}" if spot_id.startswith("T") else spot_id)
    draw.text((card_w // 2, badge_y + badge_h // 2), display_title, font=f_spot, fill=CLR_WHITE, anchor="mm")

    # 5. Label Description
    f_desc = get_font(20, bold=False)
    draw.text((card_w // 2, 796), label, font=f_desc, fill=CLR_MUTED, anchor="mm")

    # 6. Action Callout
    f_callout = get_font(26, bold=True)
    f_help = get_font(17, bold=False)
    draw.text((card_w // 2, 850), "📱 SCAN TO ORDER DIRECTLY", font=f_callout, fill=CLR_ACCENT, anchor="mm")
    draw.text((card_w // 2, 896), "View live menu · Call waiter · Request instant bill", font=f_help, fill=CLR_MUTED, anchor="mm")

    # 7. Bottom Accent Bar
    draw.rectangle([(20, card_h - 32), (card_w - 20, card_h - 20)], fill=CLR_ACCENT)

    return card

def main():
    print(f"Generating QR Codes for {len(SPOTS)} seating spots...\n")
    generated_images = []

    for spot_id, label in SPOTS:
        card = generate_qr_card(spot_id, label)
        out_path = os.path.join(OUTPUT_DIR, f"{spot_id}_qr.png")
        card.save(out_path, "PNG", quality=95)
        generated_images.append(card.convert("RGB"))
        print(f"  ✓ Created: {spot_id} ({label}) -> {out_path}")

    # Compile all cards into a single printable PDF
    if generated_images:
        pdf_path = os.path.join(OUTPUT_DIR, "all_table_qrs.pdf")
        generated_images[0].save(
            pdf_path,
            "PDF",
            resolution=150.0,
            save_all=True,
            append_images=generated_images[1:]
        )
        print(f"\nSuccessfully compiled all 22 cards into: {pdf_path}")

if __name__ == "__main__":
    main()