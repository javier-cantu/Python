import os
import html
import re
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path

# === CONFIGURATION ===
input_file = "input.txt"
output_folder = "xhtmls_sequences"
images_folder = "Images"
file_prefix = "HPATHBP_CH19"
start_index = 1

# === CONFIGURACIÓN DE LA PORTADA (AJUSTADA PARA 1600x2560) ===
COVER_ART_PATH = os.path.join(images_folder, "cover_art.jpg")
COVER_OUTPUT_PATH = os.path.join(images_folder, "cover.jpg")
FONT_PATH = "fonts/roboto-bold-condensed.ttf"

# Dimensiones de la imagen de portada FINAL (el canvas)
IMG_WIDTH, IMG_HEIGHT = 1600, 2560

# Colores
BACKGROUND_COLOR = "black"
TEXT_COLOR = "white"
BORDER_COLOR = "white"
BORDER_THICKNESS = 10

# --- Control del tamaño del arte de la portada ---
COVER_ART_HEIGHT_PERCENTAGE = 0.45

# --- Control del tamaño del texto (títulos) ---
TITLE_FONT_SIZE = 250
SUBTITLE_FONT_SIZE = 120
MIN_FONT_SIZE = 50

# --- PARÁMETROS PARA CONTROL DE LÍNEAS EN TÍTULOS Y SUBTÍTULOS ---
TITLE_MAX_LINES = 2
SUBTITLE_MAX_LINES = 2
# --------------------------------------------------------------------

# --- NUEVOS PARÁMETROS PARA PADDING Y ESPACIADO ENTRE LÍNEAS ---
HORIZONTAL_TEXT_PADDING = 50 # Espacio a cada lado del texto (nuevo)
LINE_SPACING_FACTOR = 1.1 # Multiplicador para el espacio entre líneas (1.0 = sin espacio extra)
# --------------------------------------------------------------------

# --- Espaciado vertical y márgenes ---
VERTICAL_SPACING = 70
TOP_MARGIN = 100

# =============================================================

# === NUEVA FUNCIÓN DE AYUDA PARA ESCAPAR Y PERMITIR TAGS HTML ===
def escape_and_allow_html_tags(text):
    """
    Escapa los caracteres HTML inseguros en el texto,
    pero permite que los tags <b>, </b>, <i>, </i> se interpreten como HTML.
    """
    # 1. Escapar todo el texto para seguridad general.
    #    Esto convierte '<' a '&lt;', '>' a '&gt;', etc.
    escaped_text = html.escape(text, quote=False) # quote=False para no escapar comillas que no son parte de tags

    # 2. Deshacer el escape SÓLO para los tags HTML que queremos permitir.
    #    Esto convertirá '&lt;b&gt;' de nuevo a '<b>', etc.
    escaped_text = escaped_text.replace("&lt;b&gt;", "<b>")
    escaped_text = escaped_text.replace("&lt;/b&gt;", "</b>")
    escaped_text = escaped_text.replace("&lt;i&gt;", "<i>")
    escaped_text = escaped_text.replace("&lt;/i&gt;", "</i>")
    # Agrega aquí cualquier otro tag que quieras permitir si lo añades en 01_parse_raw.py
    # Por ejemplo:
    # escaped_text = escaped_text.replace("&lt;u&gt;", "<u>")
    # escaped_text = escaped_text.replace("&lt;/u&gt;", "</u>")

    return escaped_text
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
                sentence_to_write = sentence
                if i == len(paragraph_buffer) - 1:
                    sentence_to_write += " ❖"
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
    <div class="centered">{escape_and_allow_html_tags(sentence_to_write)}</div>
  </body>
</html>''')
                counter += 1
            paragraph_buffer = []

        section_title = line[1:-1]
        level_titles = section_title.split(" > ")
        current_level = len(level_titles)
        tag = min(current_level, 6)
        current_title = level_titles[-1]
        # NOTA: Los títulos (h1, h2, etc.) generalmente no contienen formato inline como <b> o <i>
        # por lo que se sigue usando html.escape para ellos.
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
                sentence_to_write = sentence
                if i == len(paragraph_buffer) - 1:
                    sentence_to_write += " ❖"
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
    <div class="centered">{escape_and_allow_html_tags(sentence_to_write)}</div>
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
            sentence_to_write = sentence
            if i == len(paragraph_buffer) - 1:
                sentence_to_write += " ❖"
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
    <div class="centered">{escape_and_allow_html_tags(sentence_to_write)}</div>
  </body>
</html>''')
            counter += 1
        paragraph_buffer = []

    else:
        paragraph_buffer.append(line)

# Guardar cualquier párrafo restante al final del archivo
if paragraph_buffer:
    for i, sentence in enumerate(paragraph_buffer):
        sentence_to_write = sentence
        if i == len(paragraph_buffer) - 1:
            sentence_to_write += " ❖"
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
    <div class="centered">{escape_and_allow_html_tags(sentence_to_write)}</div>
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
                    current_level[key] = [] # Corregido: usar key no 'key'
                current_level[key].append(entry)

        if not current_level:
            return

        f.write("            " + "    " * depth + "<ul>\n")
        for key, subentries in current_level.items():
            item = subentries[0] # Corregido: usar subentries[0] para acceder al primer elemento
            link = item["file"] if depth + 1 == len(item["levels"]) else None # Corregido: usar item["file"] y item["levels"]

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

# --- Nueva función para envolver texto en líneas ---
def wrap_text(text, font, max_width):
    lines = []
    if not text:
        return [""]

    words = text.split(' ')
    current_line_words = []

    for word in words:
        test_line = " ".join(current_line_words + [word])
        if font.getlength(test_line) <= max_width:
            current_line_words.append(word)
        else:
            if not current_line_words: # If even the first word of a line is too long
                temp_word = ""
                for char in word:
                    if font.getlength(temp_word + char) <= max_width:
                        temp_word += char
                    else:
                        if temp_word: # Add the part that fits
                            lines.append(temp_word)
                        temp_word = char # Start a new line with the remaining char
                if temp_word: # Add any remaining part of the word
                    lines.append(temp_word)
                current_line_words = [] # Reset for next word
            else: # Add the current built line and start a new one with the current word
                lines.append(" ".join(current_line_words))
                current_line_words = [word]

    if current_line_words:
        lines.append(" ".join(current_line_words))

    return lines


# --- Función para ajustar el tamaño de texto (revisada para multilínea, padding y evitar desbordamiento) ---
def fit_text_and_wrap(draw_obj, text, font_path, total_img_width, initial_font_size, min_font_size, max_lines, horizontal_padding):
    current_size = initial_font_size
    best_font = None
    best_wrapped_lines = []

    # El ancho disponible real para el texto es el ancho total menos el padding de ambos lados
    available_width = total_img_width - (2 * horizontal_padding)

    while current_size >= min_font_size:
        try:
            font_candidate = ImageFont.truetype(font_path, current_size)
        except IOError:
            print(f"⚠️ Warning: Font not found at {font_path}. Using default.")
            # Si la fuente no se encuentra, retorna la fuente por defecto y el texto original (sin envolver)
            return ImageFont.load_default(), [text.upper()] 
        
        # Envuelve el texto con el ancho disponible con padding
        wrapped_lines = wrap_text(text.upper(), font_candidate, available_width)

        # Verifica si el texto envuelto no excede el número máximo de líneas
        if len(wrapped_lines) <= max_lines:
            all_lines_fit_width = True
            for line in wrapped_lines:
                if font_candidate.getlength(line) > available_width: # Asegura que cada línea individual quepa dentro del ancho disponible
                    all_lines_fit_width = False
                    break
            
            if all_lines_fit_width:
                # Si todo el texto cabe en ancho y número de líneas, esta es la mejor opción (iterando hacia abajo)
                best_font = font_candidate
                best_wrapped_lines = wrapped_lines
                return best_font, best_wrapped_lines
        
        current_size -= 1 # Intenta con un tamaño de fuente más pequeño

    # Si se llega aquí, significa que ningún tamaño de fuente desde initial_font_size hasta min_font_size
    # permitió que el texto encajara perfectamente en ancho y número de líneas.
    # Se usa el tamaño mínimo de fuente y se trunca si aún excede el número de líneas.

    print(f"⚠️ Warning: Text '{text}' could not perfectly fit within available width {available_width} and {max_lines} lines. Using min font size and truncating if necessary.")
    try:
        final_font = ImageFont.truetype(font_path, min_font_size)
    except IOError:
        final_font = ImageFont.load_default()

    # Vuelve a envolver con el tamaño de fuente mínimo y el ancho disponible
    wrapped_lines = wrap_text(text.upper(), final_font, available_width)
    
    # Trunca si aún hay demasiadas líneas después de envolver con el tamaño de fuente mínimo
    if len(wrapped_lines) > max_lines:
        lines_to_use = wrapped_lines[:max_lines]
        last_line = lines_to_use[-1]
        ellipsis = "..."
        # Acorta la última línea hasta que los puntos suspensivos quepan, o la línea sea solo los puntos suspensivos
        while final_font.getlength(last_line + ellipsis) > available_width and len(last_line) > 0:
            last_line = last_line[:-1]
        lines_to_use[-1] = last_line + ellipsis
        return final_font, lines_to_use
    
    return final_font, wrapped_lines


# Función para dibujar texto multilínea centrado y actualizar la posición Y
def draw_centered_multiline_text_and_update_y(lines, y_start, font, draw_obj, line_spacing_factor):
    y_current = y_start
    for i, line in enumerate(lines):
        # Obtener el bounding box del texto para la línea actual
        bbox = draw_obj.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1] # Altura de una sola línea

        # Calcular la posición X para centrar el texto
        x = (IMG_WIDTH - text_width) // 2
        
        # Dibujar el texto
        draw_obj.text((x, y_current), line, font=font, fill=TEXT_COLOR)
        
        # Mover la posición Y para la siguiente línea, aplicando el factor de espaciado
        y_current += text_height * line_spacing_factor
    return y_current + VERTICAL_SPACING # Añadir espaciado después de todo el bloque de texto


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


# Obtener fuentes y líneas envueltas, pasando el padding horizontal
font_title, wrapped_title_lines = fit_text_and_wrap(draw, book_title, FONT_PATH, IMG_WIDTH, TITLE_FONT_SIZE, MIN_FONT_SIZE, TITLE_MAX_LINES, HORIZONTAL_TEXT_PADDING)
font_sub, wrapped_subtitle_lines = fit_text_and_wrap(draw, book_intro, FONT_PATH, IMG_WIDTH, SUBTITLE_FONT_SIZE, MIN_FONT_SIZE, SUBTITLE_MAX_LINES, HORIZONTAL_TEXT_PADDING)


# Dibujar títulos con padding y espaciado entre líneas
current_y_position = draw_centered_multiline_text_and_update_y(wrapped_title_lines, current_y_position, font_title, draw, LINE_SPACING_FACTOR)
current_y_position = draw_centered_multiline_text_and_update_y(wrapped_subtitle_lines, current_y_position, font_sub, draw, LINE_SPACING_FACTOR)

# Borde
for i in range(BORDER_THICKNESS):
    draw.rectangle([i, i, IMG_WIDTH - 1 - i, IMG_HEIGHT - 1 - i], outline=BORDER_COLOR)

# Guardar imagen
img.save(COVER_OUTPUT_PATH, quality=95)
print(f"✅ Portada generada como {COVER_OUTPUT_PATH}")
# =============================================================

print("\n✅ XHTML files generated successfully, with EPUB 3-compatible headers and full alt attributes.")