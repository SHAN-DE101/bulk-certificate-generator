import os
from PIL import Image, ImageDraw, ImageFont

STORAGE_DIR = "certificates"
os.makedirs(STORAGE_DIR, exist_ok=True)


def generate_certificate_image(item_id: str, recipient_name: str, event_name: str, issue_date: str) -> str:
    """Generates a clean certificate image using Pillow."""
    width, height = 1200, 800
    image = Image.new("RGB", (width, height), color=(250, 250, 252))
    draw = ImageDraw.Draw(image)

    # Decorative Border
    draw.rectangle([30, 30, width - 30, height - 30], outline=(30, 41, 59), width=8)
    draw.rectangle([45, 45, width - 45, height - 45], outline=(203, 213, 225), width=2)

    # Standard default font
    font = ImageFont.load_default()

    draw.text((width // 2, 160), "CERTIFICATE OF PARTICIPATION", fill=(30, 41, 59), anchor="mm")
    draw.text((width // 2, 240), "This is proudly presented to", fill=(100, 116, 139), anchor="mm")
    draw.text((width // 2, 340), recipient_name.upper(), fill=(15, 23, 42), anchor="mm")
    draw.text((width // 2, 440), f"for completing/attending: {event_name}", fill=(51, 65, 85), anchor="mm")
    draw.text((width // 2, 540), f"Date of Issue: {issue_date}", fill=(100, 116, 139), anchor="mm")
    draw.text((width // 2, 700), f"Certificate ID: {item_id}", fill=(148, 163, 184), anchor="mm")

    file_path = os.path.join(STORAGE_DIR, f"{item_id}.png")
    image.save(file_path, "PNG")
    return file_path
