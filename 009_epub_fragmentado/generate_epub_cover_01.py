from PIL import Image, ImageDraw, ImageFont
import os

# === CONFIGURATION ===
input_file = "input.txt"
output_image = "cover.jpg"
font_path = "fonts/roboto-bold-condensed.ttf"
width, height = 1600, 2560
background_color = "black"
text_color = "white"
border_color = "white"
border_thickness = 10

# === Read title and subtitle from input.txt ===
title = "Untitled"
subtitle = ""

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        if line.lower().startswith("title:"):
            title = line[6:].strip()
        elif line.lower().startswith("subtitle:"):
            subtitle = line[9:].strip()
        if title and subtitle:
            break

title = title.upper()
subtitle = subtitle.upper()

# === Create image ===
img = Image.new("RGB", (width, height), background_color)
draw = ImageDraw.Draw(img)

# === Function to auto-fit font ===
def fit_text(draw, text, font_path, max_width, max_font_size):
    size = max_font_size
    while size > 10:
        font = ImageFont.truetype(font_path, size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        if text_width <= max_width:
            return font
        size -= 2
    return ImageFont.truetype(font_path, 10)

# === Fit fonts ===
font_title = fit_text(draw, title, font_path, width - 100, 240)
font_sub = fit_text(draw, subtitle, font_path, width - 100, 120)

# === Measure positions ===
def get_text_size(text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

title_w, title_h = get_text_size(title, font_title)
sub_w, sub_h = get_text_size(subtitle, font_sub)

spacing = 80
total_height = title_h + spacing + sub_h

title_x = (width - title_w) // 2
title_y = (height - total_height) // 2

sub_x = (width - sub_w) // 2
sub_y = title_y + title_h + spacing

# === Draw text ===
draw.text((title_x, title_y), title, font=font_title, fill=text_color)
draw.text((sub_x, sub_y), subtitle, font=font_sub, fill=text_color)

# === Draw border ===
for i in range(border_thickness):
    draw.rectangle([i, i, width - 1 - i, height - 1 - i], outline=border_color)

# === Save ===
img.save(output_image, quality=95)
print(f"✅ Cover image saved as {output_image}")
