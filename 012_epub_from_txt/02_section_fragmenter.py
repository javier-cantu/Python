# 02_section_fragmenter.py
#
# === SCRIPT DESCRIPTION ===
# This script is an alternative content generator. It fragments content by Level 1/2 sections,
# grouping all sentences, subheadings (L3+), and images within those sections into a SINGLE XHTML file.
# Markers like '===' are converted into HTML <p> tags, creating a traditional book structure.
#
# Input: epub_parts/input01.txt
# Output: Fewer, larger XHTML files, cover.jpg, toc_data.json
#
# =========================================================

import os
import html
import re
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps
from math import ceil
from typing import Dict, List, Tuple

# === CONFIGURATION (Static Settings) ===

# Folders and Files
BASE_OUTPUT_FOLDER = "epub_parts"
INPUT_FILE_NAME = "input01.txt"
INPUT_FILE = os.path.join(BASE_OUTPUT_FOLDER, INPUT_FILE_NAME)
IMAGES_FOLDER = "Images" # Root folder containing cover_art.jpg and other content images.
FONT_PATH = "fonts/roboto-bold-condensed.ttf" # Assumed path to your font

# Default values, overwritten by Header
FILE_PREFIX = "default_book"
START_INDEX = 1 

# Cover Generation Dimensions and Styling
IMG_WIDTH, IMG_HEIGHT = 1600, 2560
JPEG_QUALITY = 85
WORDS_PER_PAGE_ESTIMATE = 275
BACKGROUND_COLOR = "black"
TEXT_COLOR = "white"
BORDER_COLOR = "white"
BORDER_THICKNESS = 10

# Text Size and Spacing Controls
COVER_ART_HEIGHT_PERCENTAGE = 0.45
TITLE_FONT_SIZE = 250
SUBTITLE_FONT_SIZE = 120
AUTHOR_FONT_SIZE = 80 
MIN_FONT_SIZE = 50
TITLE_MAX_LINES = 2
SUBTITLE_MAX_LINES = 2
HORIZONTAL_TEXT_PADDING = 50
LINE_SPACING_FACTOR = 1.3
VERTICAL_SPACING = 70
TOP_MARGIN = 100

# =============================================================

# === METADATA EXTRACTION FUNCTION (Unchanged) ===

def extract_metadata_and_content(file_path: str) -> Tuple[Dict[str, str], List[str]]:
    """Reads the input file and separates metadata from content."""
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: Input file '{file_path}' not found. Did Script 01 run?")

    with open(file_path, "r", encoding="utf-8") as f:
        full_content = f.read()

    HEADER_DELIMITER = "=== START OF CONTENT ==="
    
    if HEADER_DELIMITER not in full_content:
        header_block = full_content
    else:
        header_block, content_block_raw = full_content.split(HEADER_DELIMITER, 1)

    metadata = {}
    for line in header_block.split('\n'):
        match = re.match(r"([A-Z_]+):\s*(.+)", line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            metadata[key] = value

    content_lines = [line.strip() for line in content_block_raw.split('\n') if line.strip()]

    return metadata, content_lines

# =============================================================

## 📚 HELPER AND UTILITY FUNCTIONS (Unchanged unless noted) 

# === 1. HTML ESCAPE FUNCTION ===
def escape_and_allow_html_tags(text: str) -> str:
    """Escapes HTML unsafe characters but allows <b>, <i> tags."""
    escaped_text = html.escape(text, quote=False)
    escaped_text = escaped_text.replace("&lt;b&gt;", "<b>")
    escaped_text = escaped_text.replace("&lt;/b&gt;", "</b>")
    escaped_text = escaped_text.replace("&lt;i&gt;", "<i>")
    escaped_text = escaped_text.replace("&lt;/i&gt;", "</i>")
    return escaped_text

# === 2. WRITE SUMMARY PAGE FUNCTION (Text Stats) ===
def write_summary_page(metrics: Dict, index: int, file_prefix: str, output_folder: str, metadata: Dict[str, str]) -> int:
    """Generates an XHTML file with document length metrics."""
    WPP = globals().get('WORDS_PER_PAGE_ESTIMATE', 275)
    
    filename = f"{file_prefix}_{str(index).zfill(4)}.xhtml"
    filepath = os.path.join(output_folder, filename)
    index_link = "index.xhtml"

    total_sentences_str = f"{metrics['total_sentences']:,}"
    total_words_str = f"{metrics['total_words']:,}"
    total_chars_clean_str = f"{metrics['total_characters_clean']:,}"
    avg_words_per_sentence_str = f"{metrics['avg_words_per_sentence']:.1f}"
    estimated_pages_str = f"{metrics['estimated_pages']}"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{metadata.get('LANGUAGE', 'en')}">
  <head>
    <meta charset="UTF-8"/>
    <title>Text Stats</title>
    <link rel="stylesheet" href="../Styles/Style001.css" type="text/css"/>
  </head>
  <body>
    <div class="centered" style="text-align: center; margin-top: 50px;">
      <h1 style="text-align: center;">Text Stats</h1>

      <p style="text-align: center;">Est. Pages: <b>{estimated_pages_str}</b> ({WPP} WPP)</p>
      <p style="text-align: center;">Avg. W/Sentence: <b>{avg_words_per_sentence_str}</b></p>
      <p style="text-align: center;">Total Sentences: <b>{total_sentences_str}</b></p>
      <p style="text-align: center;">Total Words: <b>{total_words_str}</b></p>
      <p style="text-align: center;">Chars (Clean): <b>{total_chars_clean_str}</b></p>

      <p style="margin-top: 40px; text-align: center;"><a href="{index_link}">Go to Index</a></p>
    </div>
  </body>
</html>''')
    return index + 1

# === 3. DRAWING HELPERS (Unchanged) ===

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    # (Implementation remains the same)
    lines = []
    if not text: return [""]
    words = text.split(' ')
    current_line_words = []
    for word in words:
        test_line = " ".join(current_line_words + [word])
        if font.getlength(test_line) <= max_width:
            current_line_words.append(word)
        else:
            if not current_line_words: 
                temp_word = ""
                for char in word:
                    if font.getlength(temp_word + char) <= max_width:
                        temp_word += char
                    else:
                        if temp_word: lines.append(temp_word)
                        temp_word = char
                if temp_word: lines.append(temp_word)
                current_line_words = []
            else:
                lines.append(" ".join(current_line_words))
                current_line_words = [word]
    if current_line_words: lines.append(" ".join(current_line_words))
    return lines

def fit_text_and_wrap(draw_obj, text: str, font_path: str, total_img_width: int, initial_font_size: int, min_font_size: int, max_lines: int, horizontal_padding: int):
    # (Implementation remains the same)
    available_width = total_img_width - (2 * horizontal_padding)
    current_size = initial_font_size

    while current_size >= min_font_size:
        try:
            font_candidate = ImageFont.truetype(font_path, current_size)
        except IOError:
            return ImageFont.load_default(), [text.upper()]

        wrapped_lines = wrap_text(text.upper(), font_candidate, available_width)

        if len(wrapped_lines) <= max_lines and all(font_candidate.getlength(line) <= available_width for line in wrapped_lines):
            return font_candidate, wrapped_lines

        current_size -= 1
    
    try:
        final_font = ImageFont.truetype(font_path, min_font_size)
    except IOError:
        final_font = ImageFont.load_default()
    
    wrapped_lines = wrap_text(text.upper(), final_font, available_width)

    if len(wrapped_lines) > max_lines:
        lines_to_use = wrapped_lines[:max_lines]
        last_line = lines_to_use[-1]
        ellipsis = "..."
        while final_font.getlength(last_line + ellipsis) > available_width and len(last_line) > 0:
            last_line = last_line[:-1]
        lines_to_use[-1] = last_line + ellipsis
        return final_font, lines_to_use

    return final_font, wrapped_lines

def draw_centered_multiline_text_and_update_y(lines: List[str], y_start: float, font: ImageFont.FreeTypeFont, draw_obj: ImageDraw.ImageDraw, line_spacing_factor: float) -> float:
    # (Implementation remains the same)
    y_current = y_start
    for line in lines:
        bbox = draw_obj.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (IMG_WIDTH - text_width) // 2
        draw_obj.text((x, y_current), line, font=font, fill=TEXT_COLOR)

        y_current += text_height * line_spacing_factor
    return y_current + VERTICAL_SPACING


# === 4. GENERATE COVER IMAGE FUNCTION (Unchanged) ===
def generate_cover_image(book_title: str, book_intro: str, book_author: str, cover_art_path_source: str, cover_output_path_target: str):
    """Generates the custom cover image using PIL/ImageDraw, including the Author."""
    
    img = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    current_y_position = TOP_MARGIN

    if os.path.exists(cover_art_path_source):
        cover_art = Image.open(cover_art_path_source).convert("RGB")
        original_width, original_height = cover_art.size
        cover_art_height_limit = int(IMG_HEIGHT * COVER_ART_HEIGHT_PERCENTAGE)

        scale_factor_by_height = cover_art_height_limit / original_height
        new_height = cover_art_height_limit
        new_width = int(original_width * scale_factor_by_height)
        max_allowed_width = IMG_WIDTH - BORDER_THICKNESS * 2
        if new_width > max_allowed_width:
            scale_factor_by_width = max_allowed_width / original_width
            new_width = max_allowed_width
            new_height = int(original_height * scale_factor_by_width)

        cover_art = cover_art.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        art_x = (IMG_WIDTH - cover_art.width) // 2
        img.paste(cover_art, (art_x, current_y_position))
        current_y_position += cover_art.height + VERTICAL_SPACING
    else:
        print(f"⚠️ Warning: Cover art not found at {cover_art_path_source}. Generating cover without central image.")

    font_title, wrapped_title_lines = fit_text_and_wrap(draw, book_title, FONT_PATH, IMG_WIDTH, TITLE_FONT_SIZE, MIN_FONT_SIZE, TITLE_MAX_LINES, HORIZONTAL_TEXT_PADDING)
    font_sub, wrapped_subtitle_lines = fit_text_and_wrap(draw, book_intro, FONT_PATH, IMG_WIDTH, SUBTITLE_FONT_SIZE, MIN_FONT_SIZE, SUBTITLE_MAX_LINES, HORIZONTAL_TEXT_PADDING)
    font_author, wrapped_author_lines = fit_text_and_wrap(draw, book_author, FONT_PATH, IMG_WIDTH, AUTHOR_FONT_SIZE, MIN_FONT_SIZE, 1, HORIZONTAL_TEXT_PADDING)

    current_y_position = draw_centered_multiline_text_and_update_y(wrapped_title_lines, current_y_position, font_title, draw, LINE_SPACING_FACTOR)
    current_y_position = draw_centered_multiline_text_and_update_y(wrapped_subtitle_lines, current_y_position, font_sub, draw, LINE_SPACING_FACTOR)
    current_y_position = draw_centered_multiline_text_and_update_y(wrapped_author_lines, current_y_position, font_author, draw, LINE_SPACING_FACTOR)

    for i in range(BORDER_THICKNESS):
        draw.rectangle([i, i, IMG_WIDTH - 1 - i, IMG_HEIGHT - 1 - i], outline=BORDER_COLOR)

    img.save(cover_output_path_target, quality=JPEG_QUALITY)
    print(f"✅ Cover image generated as {cover_output_path_target} with JPEG quality={JPEG_QUALITY}")

# === 5. TOC & INDEX WRITERS (Corrected) ===

def write_toc(f, entries: List[Dict], depth: int = 0):
    # (Implementation remains the same)
    current_level = {}
    for entry in entries:
        if len(entry["levels"]) > depth:
            key = entry["levels"][depth]
            if key not in current_level:
                current_level[key] = []
            current_level[key].append(entry)

    if not current_level: return

    f.write(" " * (12 + depth * 4) + "<ul>\n")
    for key, subentries in current_level.items():
        item = subentries[0]
        is_terminal = len(item["levels"]) == depth + 1
        link = item["file"] if is_terminal else next((e.get("file") for e in subentries if e.get("file")), None)
        indent_style = f"style='margin-left: {depth * 1.5}em; margin-top: 0.2em; text-align: left;'"

        f.write(" " * (12 + (depth + 1) * 4) + f"<li {indent_style}>")

        if link:
            f.write(f'<a href="{link}">{html.escape(key)}</a>')
        else:
            f.write(f"{html.escape(key)}")

        deeper = [e for e in subentries if len(e["levels"]) > depth + 1]

        if deeper:
            write_toc(f, deeper, depth + 1)

        f.write("</li>\n")
    f.write(" " * (12 + depth * 4) + "</ul>\n")
    
def write_index_xhtml(toc_entries: List[Dict], file_prefix: str, start_index: int, output_folder: str):
    """Generates the index.xhtml file with the visual Table of Contents."""
    index_file = os.path.join(output_folder, "index.xhtml")
    with open(index_file, "w", encoding="utf-8") as f:
        # A. Escribir la parte inicial del XHTML
        f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
    <head>
        <meta charset="UTF-8"/>
        <title>Index</title>
        <link rel="stylesheet" href="../Styles/Style001.css" type="text/css"/>
    </head>
    <body>
        <div class="centered toc-visual" style="margin-top: 3em; text-align: center;">
            <h2 style="margin-bottom: 1em;">Index</h2>
            <p style="margin: 0.5em 0;"><a href="{file_prefix}_{str(start_index + 1).zfill(4)}.xhtml">Text Stats</a></p>
''')
        
        # B. Llamar a la función Python para generar la lista anidada directamente en el archivo
        write_toc(f, toc_entries) 
        
        # C. Escribir la parte final del XHTML
        f.write('''
        </div>
    </body>
</html>''')


# =============================================================
# === 6. CORE NEW LOGIC: BUFFER RENDERING AND SECTION WRITING ===
# =============================================================

def render_section_buffer_to_html(section_buffer: List[str], metadata: Dict[str, str], images_folder: str) -> str:
    """Processes accumulated lines, converting sentences into <p> tags, and markers into structural HTML."""
    
    html_blocks = []
    current_paragraph_lines = []
    
    def flush_paragraph():
        nonlocal current_paragraph_lines
        if current_paragraph_lines:
            paragraph_text = " ".join(current_paragraph_lines).strip()
            
            if paragraph_text:
                html_blocks.append(f"<p>{escape_and_allow_html_tags(paragraph_text)}</p>")
            current_paragraph_lines = []

    for line in section_buffer:
        
        if not line.strip(): continue

        if line.startswith("[") and line.endswith("]"):
            # A. Heading marker (L3, L4, etc.): Flush existing paragraph, then add new heading
            flush_paragraph()
            
            section_title_parts = line[1:-1].split(" > ")
            current_title = section_title_parts[-1]
            current_level = len(section_title_parts)
            
            # Tags start at H3 for L3, H4 for L4, etc. (Level + 1)
            # The base_level is handled by write_section_fragment
            tag = min(current_level + 1, 6)
            html_blocks.append(f"<h{tag}>{html.escape(current_title)}</h{tag}>")
            
        elif line.startswith("@img:"):
            # B. Image marker: Flush existing paragraph, then add image structure
            flush_paragraph()
            
            try:
                parts = line[5:].split("|", 1)
                img_file = parts[0].strip()
                alt_text = parts[1].strip() if len(parts) > 1 else ""
                
                alt_text_clean = html.escape(alt_text)
                alt_caption = html.escape(alt_text)

                img_html = f'''
    <div class="image-page">
      <figure>
        <img src="../{images_folder}/{html.escape(img_file)}" alt="{alt_text_clean}" />
        <figcaption>{alt_caption}</figcaption>
      </figure>
    </div>'''
                html_blocks.append(img_html)
                
            except Exception as e:
                html_blocks.append(f"<p class='error'>[Image Error: {html.escape(str(e))}]</p>")
                print(f"⚠️ Error processing image line in buffer: {line}")


        elif line == "===":
            # C. Paragraph break: Flush sentences into a <p> tag
            flush_paragraph()
        
        else:
            # D. Sentence line: Accumulate in the current paragraph buffer
            current_paragraph_lines.append(line)
            
    # Flush any remaining lines at the end of the section buffer
    flush_paragraph()
            
    return "\n".join(html_blocks)


def write_section_fragment(title: str, content_html: str, filename: str, output_folder: str, metadata: Dict[str, str], base_level: int = 1):
    """Writes the accumulated HTML content into a single XHTML file."""
    
    filepath = os.path.join(output_folder, filename)
    
    # Determine the primary heading tag: L1 -> H1, L2 -> H2
    primary_h_tag = f"h{min(base_level, 2)}" 
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{metadata.get('LANGUAGE', 'en')}">
    <head>
        <meta charset="UTF-8"/>
        <title>{html.escape(title)}</title>
        <link rel="stylesheet" href="../Styles/Style001.css" type="text/css"/>
    </head>
    <body>
        <div class="section-container">
            <{primary_h_tag}>{html.escape(title)}</{primary_h_tag}>
            {content_html}
        </div>
    </body>
</html>''')
    print(f"   > Fragment written: {filename}")


# =============================================================

## ⚙️ MAIN CODE (Section Fragmentation Logic)

# === 1. Read input file and extract metadata ===
try:
    metadata, content_lines = extract_metadata_and_content(INPUT_FILE)
except (FileNotFoundError, ValueError) as e:
    print(str(e))
    exit(1)

# === 2. Configure dynamic variables from metadata ===
book_title = metadata.get("TITLE", "Untitled Book")
book_intro = metadata.get("SUBTITLE", "")
book_author = metadata.get("AUTHOR", "")
file_prefix = metadata.get("PREFIX", FILE_PREFIX)
cover_art_filename = metadata.get("COVER_IMAGE_ART", "cover_art.jpg")
book_language = metadata.get('LANGUAGE', 'en')

COVER_ART_PATH = os.path.join(IMAGES_FOLDER, cover_art_filename) 
COVER_OUTPUT_PATH = os.path.join(IMAGES_FOLDER, "cover.jpg") 

os.makedirs(BASE_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(IMAGES_FOLDER, exist_ok=True) 

# Calculate Metrics (Condensed for brevity)
total_sentences = 0
total_words = 0
for line in content_lines:
    if line.startswith("[") or line.startswith("@img:") or line == "===" or line.startswith("#"): continue
    total_sentences += 1
    total_words += len(line.split())
book_metrics = { 
    "total_sentences": total_sentences, "total_words": total_words,
    "total_characters_clean": total_words * 5, 
    "estimated_pages": ceil(total_words / WORDS_PER_PAGE_ESTIMATE) if total_words > 0 else 0,
    "avg_words_per_sentence": (total_words / total_sentences) if total_sentences > 0 else 0.0,
}
print(f"\n✨ Book Metrics Calculated...")

# Generate Cover and Metrics Page (Condensed for brevity)
generate_cover_image(book_title, book_intro, book_author, COVER_ART_PATH, COVER_OUTPUT_PATH)
cover_filename = f"{file_prefix}_{str(START_INDEX).zfill(4)}.xhtml"
cover_image_ref = os.path.basename(COVER_OUTPUT_PATH) 
with open(os.path.join(BASE_OUTPUT_FOLDER, cover_filename), "w", encoding="utf-8") as f:
    f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{book_language}" xmlns:epub="http://www.idpf.org/2007/ops">
  <head>
    <meta charset="UTF-8"/>
    <title>{html.escape(book_title)}</title>
    <link rel="stylesheet" href="../Styles/Style001.css" type="text/css"/>
  </head>
  <body epub:type="cover">
    <div class="centered">
      <img src="../{IMAGES_FOLDER}/{cover_image_ref}" alt="{html.escape(book_title)} Cover" style="max-width:100%; height:auto;"/>
      <p style="text-indent: 0; text-align: center;"><a href="index.xhtml">Go to Index</a></p>
    </div>
  </body>
</html>''')
counter = START_INDEX + 1
counter = write_summary_page(book_metrics, counter, file_prefix, BASE_OUTPUT_FOLDER, metadata)


# === 6. MAIN CONTENT PROCESSING (Level 2 Fragmenter) ===

current_section_buffer = []
toc_entries = []
current_section_title = None 
current_section_file = None 
current_section_base_level = 0

for line in content_lines:
    
    if line.startswith("#") and not line.lower().startswith("#level"):
        continue

    # --- 1. DETECTAR UN NUEVO PUNTO DE FRAGMENTACIÓN DE NIVEL 2/1 ---
    if line.startswith("[") and line.endswith("]"):
        
        section_title_parts = line[1:-1].split(" > ")
        current_level = len(section_title_parts)
        
        # 1.1. FRAGMENTACIÓN: Solo si encontramos un Level 1 o Level 2
        if current_level <= 2:
            
            # Si ya hay una sección en curso, la fragmentamos y guardamos
            if current_section_file:
                
                # --- FRAGMENTAR LA SECCIÓN ANTERIOR ---
                print(f"   > Fragmenting previous section: {current_section_title}")
                
                section_html_content = render_section_buffer_to_html(current_section_buffer, metadata, IMAGES_FOLDER)
                
                write_section_fragment(
                    title=current_section_title, 
                    content_html=section_html_content, 
                    filename=current_section_file, 
                    output_folder=BASE_OUTPUT_FOLDER, 
                    metadata=metadata,
                    base_level=current_section_base_level
                )
                
                # Reiniciar el buffer
                current_section_buffer = []

            # --- 1.2. PREPARAR LA NUEVA SECCIÓN (Solo se hace para L1/L2) ---
            
            # 1. Establecer título, archivo y agregar a TOC
            current_section_title = section_title_parts[-1]
            current_section_file = f"{file_prefix}_{str(counter).zfill(4)}.xhtml"
            current_section_base_level = current_level
            
            toc_entries.append({
                "levels": section_title_parts,
                "file": current_section_file
            })
            counter += 1
            
            # NOTA: NO SE AÑADE ESTE ENCABEZADO L1/L2 AL BUFFER.
            
        # 1.3. ACUMULACIÓN PARA L3, L4, etc.
        else: # current_level > 2
             # Esto es un encabezado L3/L4. NO dispara fragmentación, solo se acumula
             if current_section_file:
                 current_section_buffer.append(line)
             # Si no hay current_section_file, se ignora hasta encontrar el primer L1/L2


    # --- 2. ACUMULAR CONTENIDO (Texto, ===, @img: o L3+ si ya hay sección activa) ---
    elif current_section_file:
        # Se acumula CUALQUIER otra línea (L3+, @img, ===, texto)
        current_section_buffer.append(line)


# --- 3. PROCESAR EL ÚLTIMO FRAGMENTO (FUERA DEL BUCLE) ---

if current_section_buffer and current_section_file:
    print(f"   > Fragmenting final section: {current_section_title}")
    
    section_html_content = render_section_buffer_to_html(current_section_buffer, metadata, IMAGES_FOLDER)

    write_section_fragment(
        title=current_section_title, 
        content_html=section_html_content, 
        filename=current_section_file, 
        output_folder=BASE_OUTPUT_FOLDER, 
        metadata=metadata,
        base_level=current_section_base_level
    )


# === 7. WRITE index.xhtml (Unchanged) ===
write_index_xhtml(toc_entries, file_prefix, START_INDEX, BASE_OUTPUT_FOLDER)


# === 8. Save TOC hierarchy data for Script 03 (Unchanged) ===
toc_data_path = os.path.join(BASE_OUTPUT_FOLDER, "toc_data.json")
with open(toc_data_path, "w", encoding="utf-8") as f:
    json.dump(toc_entries, f, indent=4)

print(f"✅ TOC hierarchy data saved to {toc_data_path}")
print("\n✅ Section XHTML files generated successfully, ready for Script 03.")