from PIL import Image
import os

# المسار إلى الصورة الأصلية
original_icon = "static/pwa/icon.png"  # الصورة الكبيرة (512x512)

# الأحجام المطلوبة
sizes = [192, 512]

# افتح الصورة وغيّر حجمها
img = Image.open(original_icon)

for size in sizes:
    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    resized.save(f"static/pwa/icon-{size}x{size}.png", "PNG")

print("✅ تم إنشاء الأيقونات بنجاح!")