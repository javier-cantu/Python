import os
import html
import re
from PIL import Image, ImageDraw, ImageFont # <--- Nueva importación para la portada
from pathlib import Path # <--- Nueva importación para la portada (aunque PIL ya la tiene, es buena práctica)

# === CONFIGURATION ===
input_file = "input.txt"
output_folder = "xhtmls_sequences"
images_folder = "Images"
file_prefix = "HPATOOTP_CH02"
start_index = 1

# === CONFIGURACIÓN DE LA PORTADA (AÑADIDO DEL NUEVO SCRIPT) ===
# Se asume que 'images_folder' ya existe o se creará.
COVER_ART_PATH = os.path.join(images_folder, "cover_art.jpg") # Tu imagen artística para la portada
COVER_OUTPUT_PATH = os.path.join(images_folder, "cover.jpg") # La portada final que generará
FONT_PATH = "fonts/roboto-bold-condensed.ttf" # Asegúrate de tener esta fuente o cambia la ruta
IMG_WIDTH, IMG_HEIGHT = 1600, 2560 # Dimensiones de la imagen de portada
BACKGROUND_COLOR = "black"
TEXT_COLOR = "white"
BORDER_COLOR = "white"
BORDER_THICKNESS = 10
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
os.makedirs(images_folder, exist_ok=True) # Asegurarse de que la carpeta de imágenes exista

toc_entries = []
missing_images = []

# === Write cover page (XHTML) ===
# Esta página es una cubierta "lógica" que puede apuntar a la imagen de portada
# o ser una página introductoria. Se mantiene de tu script original.
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
# Nota: He añadido una etiqueta <img> aquí para que el XHTML de portada
# pueda mostrar la imagen generada. Ajusta el estilo CSS si es necesario.

# === Process content ===
counter = start_index + 1
paragraph_buffer = []

for line in content_lines:
    if line.startswith("[") and line.endswith("]"):
        # Guardar cualquier párrafo pendiente antes de un nuevo título
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
        tag = min(current_level, 6) # Asegura que el tag no exceda h6
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
        # Guardar cualquier párrafo pendiente antes de una imagen
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
        # Guardar cualquier párrafo pendiente (maneja el caso de triple === al final)
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
    f.write('   <head>\n')
    f.write('     <meta charset="UTF-8"/>\n')
    f.write('     <title>Index</title>\n')
    f.write('     <link rel="stylesheet" href="../Styles/Style001.css" type="text/css"/>\n')
    f.write('   </head>\n')
    f.write('   <body>\n')
    f.write('     <div class="centered">\n')
    f.write('       <h2>Index</h2>\n')

    def write_toc(entries, depth=0):
        current_level = {}
        for entry in entries:
            if len(entry["levels"]) > depth: # Solo procesa entradas con suficiente profundidad
                key = entry["levels"][depth]
                if key not in current_level:
                    current_level[key] = []
                current_level[key].append(entry)

        if not current_level: # Si no hay entradas para este nivel, no escribir ul
            return

        f.write("       " + "   " * depth + "<ul>\n")
        for key, subentries in current_level.items():
            item = subentries[0]
            # Un enlace solo si es el último nivel o si el elemento tiene un archivo asociado a este nivel
            link = item["file"] if depth + 1 == len(item["levels"]) else None

            f.write("       " + "   " * (depth + 1) + "<li>")
            if link:
                f.write(f'<a href="{link}">{html.escape(key)}</a>')
            else:
                f.write(f"{html.escape(key)}") # Si no es un enlace final, solo el texto

            deeper = [e for e in subentries if len(e["levels"]) > depth + 1]
            if deeper:
                write_toc(deeper, depth + 1)
            f.write("</li>\n")
        f.write("       " + "   " * depth + "</ul>\n")

    write_toc(toc_entries)

    f.write('     </div>\n')
    f.write('   </body>\n')
    f.write('</html>\n')

if missing_images:
    print("\n❌ Missing image files:")
    for img in missing_images:
        print(f" - {img}")
else:
    print("✅ All image references verified.")

# === PARTE DE CREACIÓN DE PORTADA (AÑADIDO DEL NUEVO SCRIPT) ===
# Asegúrate de que book_title y book_intro ya estén definidos desde la lectura inicial
img = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), BACKGROUND_COLOR)
draw = ImageDraw.Draw(img)

# Función para ajustar el tamaño de texto
def fit_text(draw_obj, text, font_path, max_width, max_font_size):
    size = max_font_size
    while size > 10:
        try:
            font = ImageFont.truetype(font_path, size)
            bbox = draw_obj.textbbox((0, 0), text, font=font)
            if bbox[2] - bbox[0] <= max_width:
                return font
            size -= 2
        except IOError: # Manejar si la fuente no se encuentra
            print(f"⚠️ Warning: Font not found at {font_path}. Using default.")
            return ImageFont.load_default() # Retorna una fuente por defecto
    return ImageFont.load_default() # Si no se ajusta, retorna la por defecto


# Cargar imagen central si existe
art_y = 400 # Valor por defecto si no hay imagen
if os.path.exists(COVER_ART_PATH):
    cover_art = Image.open(COVER_ART_PATH).convert("RGB")
    max_w = IMG_WIDTH - 200
    max_h = IMG_HEIGHT // 2
    cover_art.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    art_x = (IMG_WIDTH - cover_art.width) // 2
    art_y = 150
    img.paste(cover_art, (art_x, art_y))
else:
    print(f"⚠️ Warning: Cover art not found at {COVER_ART_PATH}. Generating cover without central image.")
    art_y = 400  # Espacio vacío arriba si no hay imagen

font_title = fit_text(draw, book_title.upper(), FONT_PATH, IMG_WIDTH - 100, 150)
font_sub = fit_text(draw, book_intro.upper(), FONT_PATH, IMG_WIDTH - 100, 90)

def draw_centered_text(text, y, font, draw_obj):
    bbox = draw_obj.textbbox((0, 0), text, font=font)
    x = (IMG_WIDTH - (bbox[2] - bbox[0])) // 2
    draw_obj.text((x, y), text, font=font, fill=TEXT_COLOR)
    return y + (bbox[3] - bbox[1]) + 40

y_pos = art_y + (cover_art.height if os.path.exists(COVER_ART_PATH) else 0) + 80
y_pos = draw_centered_text(book_title.upper(), y_pos, font_title, draw) # Usa book_title
y_pos = draw_centered_text(book_intro.upper(), y_pos, font_sub, draw) # Usa book_intro

# Borde
for i in range(BORDER_THICKNESS):
    draw.rectangle([i, i, IMG_WIDTH - 1 - i, IMG_HEIGHT - 1 - i], outline=BORDER_COLOR)

# Guardar imagen
img.save(COVER_OUTPUT_PATH, quality=95)
print(f"✅ Portada generada como {COVER_OUTPUT_PATH}")
# =============================================================

print("\n✅ XHTML files generated successfully, with EPUB 3-compatible headers and full alt attributes.")