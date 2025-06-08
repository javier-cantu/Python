import os
import html
import re
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path

# === CONFIGURATION ===
input_file = "input.txt"
output_folder = "xhtmls_sequences"
images_folder = "Images"
file_prefix = "HPATOOTP_CH12"
start_index = 1

# === CONFIGURACIÓN DE LA PORTADA (AJUSTADA PARA 1600x2560) ===
COVER_ART_PATH = os.path.join(images_folder, "cover_art.jpg")
COVER_OUTPUT_PATH = os.path.join(images_folder, "cover.jpg")
FONT_PATH = "fonts/roboto-bold-condensed.ttf"

# Dimensiones de la imagen de portada FINAL (el canvas)
# ¡MANTENEMOS LA RESOLUCIÓN SOLICITADA!
IMG_WIDTH, IMG_HEIGHT = 1600, 2560 

# Colores
BACKGROUND_COLOR = "black"
TEXT_COLOR = "white"
BORDER_COLOR = "white"
BORDER_THICKNESS = 10 

# --- Control del tamaño del arte de la portada ---
# Reducimos este porcentaje para dejar más espacio vertical para los textos.
COVER_ART_HEIGHT_PERCENTAGE = 0.45 # <-- Ajustado para dejar más espacio para el texto

# --- Control del tamaño del texto (títulos) ---
# Aumentamos aún más los tamaños iniciales para que el texto sea lo más grande posible.
TITLE_FONT_SIZE = 250 # <-- Aumentado significativamente
SUBTITLE_FONT_SIZE = 120 # <-- Aumentado significativamente
MIN_FONT_SIZE = 50  # <-- Aseguramos que el texto no baje demasiado

# --- Espaciado vertical y márgenes ---
VERTICAL_SPACING = 70 # <-- Ajustado para mayor separación si los textos crecen
TOP_MARGIN = 100 # <-- Margen superior inicial

# =============================================================

# === Read input file ===
with open(input_file, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

# === Get title and subtitle ===
book_title = ""
book_intro = ""
content_start = 0

for i, line in enumerate(lines):
    if line.lower().startswith("title:"):
        book_title = line[6:].strip()
    elif line.lower().startswith("subtitle:"):
        book_intro = line[9:].strip()
    else:
        content_start = i
        break

content_lines = lines[content_start:]

# === Prepare output folders ===
os.makedirs(output_folder, exist_ok=True)
os.makedirs(images_folder, exist_ok=True)

toc_entries = []
missing_images = []

# === Write cover page (XHTML) ===
cover_filename = f"{file_prefix}_{str(start_index).zfill(4)}.xhtml"
with open(os.path.join(output_folder, cover_filename), "w", encoding="utf-8") as f:
    f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <meta charset="UTF-8"/>
    <title>{html.escape(book_title)}</title>
    <link rel="stylesheet" href="../Styles/Style001.css" type="text/css"/>
  </head>
  <body>
    <div class="centered">
      <img src="../Images/{os.path.basename(COVER_OUTPUT_PATH)}" alt="{html.escape(book_title)} Cover" style="max-width:100%; height:auto;"/>
      <h2>{html.escape(book_title)}</h2>
      <p>{html.escape(book_intro)}</p>
      <p><a href="index.xhtml">Go to Index</a></p>
    </div>
  </body>
</html>''')

# === Process content ===
counter = start_index + 1
paragraph_buffer = []

for line in content_lines:
    if line.startswith("[") and line.endswith("]"):
        if paragraph_buffer:
            for i, sentence in enumerate(paragraph_buffer):
                if i == len(paragraph_buffer) - 1:
                    sentence += " ❖"
                filename = f"{file_prefix}_{str(counter).zfill(4)}.xhtml"
                with open(os.path.join(output_folder, filename), "w", encoding="utf-8") as f:
                    f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <meta charset="UTF-8"/>
    <title>Page {counter}</title>
    <link rel="stylesheet" href="../Styles/Style001.css" type="text/css"/>
  </head>
  <body>
    <div class="centered">{html.escape(sentence)}</div>
  </body>
</html>''')
                counter += 1
            paragraph_buffer = []

        section_title = line[1:-1]
        level_titles = section_title.split(" > ")
        current_level = len(level_titles)
        tag = min(current_level, 6)
        current_title = level_titles[-1]
        html_heading = f"<h{tag}>{html.escape(current_title)}</h{tag}>"

        filename = f"{file_prefix}_{str(counter).zfill(4)}.xhtml"
        with open(os.path.join(output_folder, filename), "w", encoding="utf-8") as f:
            f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <meta charset="UTF-8"/>
    <title>{html.escape(current_title)}</title>
    <link rel="stylesheet" href="../Styles/Style001.css" type="text/css"/>
  </head>
  <body>
    <div class="context">
      {html_heading}
    </div>
  </body>
</html>''')
        toc_entries.append({
            "levels": level_titles,
            "file": filename
        })
        counter += 1

    elif line.startswith("@img:"):
        if paragraph_buffer:
            for i, sentence in enumerate(paragraph_buffer):
                if i == len(paragraph_buffer) - 1:
                    sentence += " ❖"
                filename = f"{file_prefix}_{str(counter).zfill(4)}.xhtml"
                with open(os.path.join(output_folder, filename), "w", encoding="utf-8") as f:
                    f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <meta charset="UTF-8"/>
    <title>Page {counter}</title>
    <link rel="stylesheet" href="../Styles/Style001.css" type="text/css"/>
  </head>
  <body>
    <div class="centered">{html.escape(sentence)}</div>
  </body>
</html>''')
                counter += 1
            paragraph_buffer = []

        try:
            parts = line[5:].split("|", 1)
            img_file = parts[0].strip()
            alt_text = parts[1].strip() if len(parts) > 1 else ""

            image_path = os.path.join(images_folder, img_file)
            if not os.path.isfile(image_path):
                missing_images.append(img_file)

            alt_text_clean = html.escape(alt_text)
            alt_caption = html.escape(alt_text)

            filename = f"{file_prefix}_{str(counter).zfill(4)}.xhtml"
            with open(os.path.join(output_folder, filename), "w", encoding="utf-8") as f:
                f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <meta charset="UTF-8"/>
    <title>Image: {html.escape(img_file)}</title>
    <link rel="stylesheet" href="../Styles/Style001.css" type="text/css"/>
  </head>
  <body>
    <div class="image-page">
      <figure>
        <img src="../Images/{html.escape(img_file)}" alt="{alt_text_clean}" />
        <figcaption>{alt_caption}</figcaption>
      </figure>
    </div>
  </body>
</html>''')
            counter += 1
        except Exception as e:
            print(f"⚠️ Error processing image line: {line}\n{e}")

    elif line == "===":
        for i, sentence in enumerate(paragraph_buffer):
            if i == len(paragraph_buffer) - 1:
                sentence += " ❖"
            filename = f"{file_prefix}_{str(counter).zfill(4)}.xhtml"
            with open(os.path.join(output_folder, filename), "w", encoding="utf-8") as f:
                f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <meta charset="UTF-8"/>
    <title>Page {counter}</title>
    <link rel="stylesheet" href="../Styles/Style001.css" type="text/css"/>
  </head>
  <body>
    <div class="centered">{html.escape(sentence)}</div>
  </body>
</html>''')
            counter += 1
        paragraph_buffer = []

    else:
        paragraph_buffer.append(line)

# Guardar cualquier párrafo restante al final del archivo
if paragraph_buffer:
    for i, sentence in enumerate(paragraph_buffer):
        if i == len(paragraph_buffer) - 1:
            sentence += " ❖"
        filename = f"{file_prefix}_{str(counter).zfill(4)}.xhtml"
        with open(os.path.join(output_folder, filename), "w", encoding="utf-8") as f:
            f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <meta charset="UTF-8"/>
    <title>Page {counter}</title>
    <link rel="stylesheet" href="../Styles/Style001.css" type="text/css"/>
  </head>
  <body>
    <div class="centered">{html.escape(sentence)}</div>
  </body>
</html>''')
        counter += 1
    paragraph_buffer = []


# === Write index.xhtml ===
index_file = os.path.join(output_folder, "index.xhtml")
with open(index_file, "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">\n')
    f.write('    <head>\n')
    f.write('        <meta charset="UTF-8"/>\n')
    f.write('        <title>Index</title>\n')
    f.write('        <link rel="stylesheet" href="../Styles/Style001.css" type="text/css"/>\n')
    f.write('    </head>\n')
    f.write('    <body>\n')
    f.write('        <div class="centered">\n')
    f.write('            <h2>Index</h2>\n')

    def write_toc(entries, depth=0):
        current_level = {}
        for entry in entries:
            if len(entry["levels"]) > depth:
                key = entry["levels"][depth]
                if key not in current_level:
                    current_level[key] = []
                current_level[key].append(entry)

        if not current_level:
            return

        f.write("            " + "    " * depth + "<ul>\n")
        for key, subentries in current_level.items():
            item = subentries[0]
            link = item["file"] if depth + 1 == len(item["levels"]) else None

            f.write("            " + "    " * (depth + 1) + "<li>")
            if link:
                f.write(f'<a href="{link}">{html.escape(key)}</a>')
            else:
                f.write(f"{html.escape(key)}")

            deeper = [e for e in subentries if len(e["levels"]) > depth + 1]
            if deeper:
                write_toc(deeper, depth + 1)
            f.write("</li>\n")
        f.write("            " + "    " * depth + "</ul>\n")

    write_toc(toc_entries)

    f.write('        </div>\n')
    f.write('    </body>\n')
    f.write('</html>\n')

if missing_images:
    print("\n❌ Missing image files:")
    for img in missing_images:
        print(f" - {img}")
else:
    print("✅ All image references verified.")

# === PARTE DE CREACIÓN DE PORTADA (AÑADIDA Y MEJORADA) ===
# --------------------------------------------------------
# Esta es la sección donde se aplican los nuevos controles.
# --------------------------------------------------------
img = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), BACKGROUND_COLOR)
draw = ImageDraw.Draw(img)

# --- Función para ajustar el tamaño de texto (mejorada) ---
def fit_text(draw_obj, text, font_path, max_width, initial_font_size, min_font_size):
    size = initial_font_size
    while size >= min_font_size:
        try:
            font = ImageFont.truetype(font_path, size)
            bbox = draw_obj.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            if text_width <= max_width:
                return font
            size -= 1
        except IOError:
            print(f"⚠️ Warning: Font not found at {font_path}. Using default.")
            return ImageFont.load_default()
    
    print(f"⚠️ Warning: Text '{text}' could not fit within max_width {max_width} even at min_font_size {min_font_size}. Using min font size.")
    try:
        return ImageFont.truetype(font_path, min_font_size)
    except IOError:
        return ImageFont.load_default()


# Cargar y posicionar imagen central
current_y_position = TOP_MARGIN # Inicia el posicionamiento vertical desde el margen superior

if os.path.exists(COVER_ART_PATH):
    cover_art = Image.open(COVER_ART_PATH).convert("RGB")
    
    original_width, original_height = cover_art.size
    
    # Calcula la altura máxima deseada para la imagen de arte basada en el porcentaje
    cover_art_height_limit = int(IMG_HEIGHT * COVER_ART_HEIGHT_PERCENTAGE)
    
    # --- LÓGICA DE ESCALADO DE IMAGEN ARTE (PRIORIZA ALTURA, RESPETA ANCHO) ---
    scale_factor_by_height = cover_art_height_limit / original_height
    new_height = cover_art_height_limit
    new_width = int(original_width * scale_factor_by_height)
    
    max_allowed_width = IMG_WIDTH - BORDER_THICKNESS * 2 
    if new_width > max_allowed_width:
        scale_factor_by_width = max_allowed_width / original_width
        new_width = max_allowed_width
        new_height = int(original_height * scale_factor_by_width)
    
    cover_art = cover_art.resize((new_width, new_height), Image.Resampling.LANCZOS)
    # --- FIN LÓGICA DE ESCALADO ---
    
    art_x = (IMG_WIDTH - cover_art.width) // 2
    img.paste(cover_art, (art_x, current_y_position))
    current_y_position += cover_art.height + VERTICAL_SPACING
else:
    print(f"⚠️ Warning: Cover art not found at {COVER_ART_PATH}. Generating cover without central image.")


# Fuentes para título y subtítulo
font_title = fit_text(draw, book_title.upper(), FONT_PATH, IMG_WIDTH - BORDER_THICKNESS * 2, TITLE_FONT_SIZE, MIN_FONT_SIZE)
font_sub = fit_text(draw, book_intro.upper(), FONT_PATH, IMG_WIDTH - BORDER_THICKNESS * 2, SUBTITLE_FONT_SIZE, MIN_FONT_SIZE)

# Función para dibujar texto centrado y actualizar la posición Y
def draw_centered_text_and_update_y(text, y_start, font, draw_obj):
    bbox = draw_obj.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (IMG_WIDTH - text_width) // 2
    draw_obj.text((x, y_start), text, font=font, fill=TEXT_COLOR)
    return y_start + text_height + VERTICAL_SPACING

# Dibujar títulos
current_y_position = draw_centered_text_and_update_y(book_title.upper(), current_y_position, font_title, draw)
current_y_position = draw_centered_text_and_update_y(book_intro.upper(), current_y_position, font_sub, draw)

# Borde
for i in range(BORDER_THICKNESS):
    draw.rectangle([i, i, IMG_WIDTH - 1 - i, IMG_HEIGHT - 1 - i], outline=BORDER_COLOR)

# Guardar imagen
img.save(COVER_OUTPUT_PATH, quality=95)
print(f"✅ Portada generada como {COVER_OUTPUT_PATH}")
# =============================================================

print("\n✅ XHTML files generated successfully, with EPUB 3-compatible headers and full alt attributes.")