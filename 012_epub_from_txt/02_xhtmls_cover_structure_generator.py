# 02_xhtmls_cover_structure_generator.py
#
# === SCRIPT DESCRIPTION ===
# This script is the core content generator. It performs the following tasks:
# 1. Reads metadata (TITLE, AUTHOR, PREFIX, etc.) from the header of input01.txt.
# 2. Generates the custom cover image (cover.jpg) using PIL, including the Title, Subtitle, and Author.
# 3. Creates the cover.xhtml and text_stats.xhtml pages.
# 4. Fragments the content (sentences and structural markers) into sequential XHTML files in the epub_parts folder.
# 5. Ensures all image references point correctly to the root 'Images/' folder (../Images/).
# 6. Builds and saves the final Table of Contents hierarchy data (toc_data.json) for Script 03.
#
# Input: epub_parts/input01.txt
# Output: Multiple XHTML files, cover.jpg, toc_data.json
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
AUTHOR_FONT_SIZE = 80 # New font size for author
MIN_FONT_SIZE = 50
TITLE_MAX_LINES = 2
SUBTITLE_MAX_LINES = 2
HORIZONTAL_TEXT_PADDING = 50
LINE_SPACING_FACTOR = 1.3
VERTICAL_SPACING = 70
TOP_MARGIN = 100

# =============================================================

# === METADATA EXTRACTION FUNCTION ===

def extract_metadata_and_content(file_path: str) -> Tuple[Dict[str, str], List[str]]:
    """Reads the input file and separates metadata from content."""
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: Input file '{file_path}' not found. Did Script 01 run?")

    with open(file_path, "r", encoding="utf-8") as f:
        full_content = f.read()

    HEADER_DELIMITER = "=== START OF CONTENT ==="
    
    if HEADER_DELIMITER not in full_content:
        raise ValueError(f"Error: Header delimiter '{HEADER_DELIMITER}' not found in input file.")

    header_block, content_block = full_content.split(HEADER_DELIMITER, 1)

    # 1. Parse Metadata (KEY: VALUE)
    metadata = {}
    for line in header_block.split('\n'):
        match = re.match(r"([A-Z_]+):\s*(.+)", line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            metadata[key] = value

    # 2. Get Content Lines
    content_lines = [line.strip() for line in content_block.split('\n') if line.strip()]

    return metadata, content_lines

# =============================================================

## 📚 HELPER AND UTILITY FUNCTIONS 

# === 1. HTML ESCAPE FUNCTION ===
def escape_and_allow_html_tags(text: str) -> str:
    """Escapes HTML unsafe characters but allows <b>, <i> tags."""
    escaped_text = html.escape(text, quote=False)
    # Undo escape ONLY for whitelisted HTML tags
    escaped_text = escaped_text.replace("&lt;b&gt;", "<b>")
    escaped_text = escaped_text.replace("&lt;/b&gt;", "</b>")
    escaped_text = escaped_text.replace("&lt;i&gt;", "<i>")
    escaped_text = escaped_text.replace("&lt;/i&gt;", "</i>")
    return escaped_text

# === 2. WRITE SENTENCE FRAGMENT FUNCTION ===
def write_sentence_fragment(sentence_text: str, index: int, file_prefix: str, output_folder: str) -> int:
    """Writes an XHTML fragment for a single sentence."""
    filename = f"{file_prefix}_{str(index).zfill(4)}.xhtml"
    filepath = os.path.join(output_folder, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <meta charset="UTF-8"/>
    <title>Page {index}</title>
    <link rel="stylesheet" href="../Styles/Style001.css" type="text/css"/>
  </head>
  <body>
    <div class="centered">{escape_and_allow_html_tags(sentence_text)}</div>
  </body>
</html>''')
    return index + 1

# === 3. WRITE METRICS PAGE FUNCTION (Text Stats) ===
def write_summary_page(metrics: Dict, index: int, file_prefix: str, output_folder: str) -> int:
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
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
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

# === 4. TEXT DRAWING HELPERS (PIL/ImageDraw logic) ===

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    # (Implementation remains the same as original script)
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
    # (Implementation remains the same as original script)
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
    # (Implementation remains the same as original script)
    y_current = y_start
    for line in lines:
        bbox = draw_obj.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (IMG_WIDTH - text_width) // 2
        draw_obj.text((x, y_current), line, font=font, fill=TEXT_COLOR)

        y_current += text_height * line_spacing_factor
    return y_current + VERTICAL_SPACING

# === 5. GENERATE COVER IMAGE FUNCTION (Refactored to include Author) ===
def generate_cover_image(book_title: str, book_intro: str, book_author: str, cover_art_path_source: str, cover_output_path_target: str):
    """Generates the custom cover image using PIL/ImageDraw, including the Author."""
    
    img = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    current_y_position = TOP_MARGIN

    # 1. Load and position central image
    if os.path.exists(cover_art_path_source):
        cover_art = Image.open(cover_art_path_source).convert("RGB")
        original_width, original_height = cover_art.size
        cover_art_height_limit = int(IMG_HEIGHT * COVER_ART_HEIGHT_PERCENTAGE)

        # Image scaling logic (same as original script)
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

    # 2. Fit and wrap text (Title, Subtitle, Author)
    font_title, wrapped_title_lines = fit_text_and_wrap(draw, book_title, FONT_PATH, IMG_WIDTH, TITLE_FONT_SIZE, MIN_FONT_SIZE, TITLE_MAX_LINES, HORIZONTAL_TEXT_PADDING)
    font_sub, wrapped_subtitle_lines = fit_text_and_wrap(draw, book_intro, FONT_PATH, IMG_WIDTH, SUBTITLE_FONT_SIZE, MIN_FONT_SIZE, SUBTITLE_MAX_LINES, HORIZONTAL_TEXT_PADDING)
    font_author, wrapped_author_lines = fit_text_and_wrap(draw, book_author, FONT_PATH, IMG_WIDTH, AUTHOR_FONT_SIZE, MIN_FONT_SIZE, 1, HORIZONTAL_TEXT_PADDING)


    # 3. Draw titles and author
    current_y_position = draw_centered_multiline_text_and_update_y(wrapped_title_lines, current_y_position, font_title, draw, LINE_SPACING_FACTOR)
    current_y_position = draw_centered_multiline_text_and_update_y(wrapped_subtitle_lines, current_y_position, font_sub, draw, LINE_SPACING_FACTOR)
    current_y_position = draw_centered_multiline_text_and_update_y(wrapped_author_lines, current_y_position, font_author, draw, LINE_SPACING_FACTOR)


    # 4. Border
    for i in range(BORDER_THICKNESS):
        draw.rectangle([i, i, IMG_WIDTH - 1 - i, IMG_HEIGHT - 1 - i], outline=BORDER_COLOR)

    # 5. Save image
    img.save(cover_output_path_target, quality=JPEG_QUALITY)
    print(f"✅ Cover image generated as {cover_output_path_target} with JPEG quality={JPEG_QUALITY}")

# === 6. WRITE TOC (RECURSIVE HELPER) ===
def write_toc(f, entries: List[Dict], depth: int = 0):
    # (Implementation remains the same as original script)
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
    
# === 7. WRITE INDEX.XHTML FUNCTION ===
def write_index_xhtml(toc_entries: List[Dict], file_prefix: str, start_index: int, output_folder: str):
    """Generates the index.xhtml file with the visual Table of Contents."""
    # (Implementation remains the same as original script)
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
        f.write('        <div class="centered toc-visual" style="margin-top: 3em; text-align: center;">\n')
        f.write('            <h2 style="margin-bottom: 1em;">Index</h2>\n')
        f.write(f'            <p style="margin: 0.5em 0;"><a href="{file_prefix}_{str(start_index + 1).zfill(4)}.xhtml">Text Stats</a></p>\n')

        write_toc(f, toc_entries)

        f.write('        </div>\n')
        f.write('    </body>\n')
        f.write('</html>\n')

# === 8. FLUSH PARAGRAPH BUFFER ===
def flush_paragraph_buffer(paragraph_buffer: List[str], counter: int, file_prefix: str, output_folder: str) -> int:
    """Processes the sentence buffer and writes each sentence as an XHTML fragment."""
    # (Implementation remains the same as original script)
    if not paragraph_buffer: return counter
        
    new_counter = counter
    
    for i, sentence in enumerate(paragraph_buffer):
        sentence_to_write = sentence
        if i == len(paragraph_buffer) - 1:
            sentence_to_write += " ❖"
        new_counter = write_sentence_fragment(sentence_to_write, new_counter, file_prefix, output_folder)
        
    return new_counter

# =============================================================

## ⚙️ REFACTORED MAIN CODE

# === 1. Read input file and extract metadata ===
try:
    metadata, content_lines = extract_metadata_and_content(INPUT_FILE)
except (FileNotFoundError, ValueError) as e:
    print(str(e))
    exit(1)

# === 2. Configure dynamic variables from metadata ===
book_title = metadata.get("TITLE", "Untitled Book")
book_intro = metadata.get("SUBTITLE", "")
book_author = metadata.get("AUTHOR", "") # Extracted Author
file_prefix = metadata.get("PREFIX", FILE_PREFIX)
cover_art_filename = metadata.get("COVER_IMAGE_ART", "cover_art.jpg")

# Redefine dynamic paths
COVER_ART_PATH = os.path.join(IMAGES_FOLDER, cover_art_filename) # Source image path (Root: Images/cover_art.jpg)
COVER_OUTPUT_PATH = os.path.join(IMAGES_FOLDER, "cover.jpg") # Target generated cover path (Root: Images/cover.jpg)

# === Prepare output folders ===
os.makedirs(BASE_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(IMAGES_FOLDER, exist_ok=True) # Ensure root Images folder exists for generated cover.jpg


# === 3. CALCULATE METRICS BLOCK ===
# ... (Metric calculation remains the same)
total_sentences = 0
total_words = 0
total_characters_clean = 0

for line in content_lines:
    if line.startswith("[") and line.endswith("]"): continue
    if line.startswith("@img:"): continue
    if line == "===": continue
    # ⚠️ FIX: Skip comment/separator lines that are NOT level markers
    if line.startswith("#") and not line.lower().startswith("#level"): continue 
    
    total_sentences += 1
    words = line.split()
    total_words += len(words)
    total_characters_clean += len(line.replace(' ', ''))

estimated_pages = ceil(total_words / WORDS_PER_PAGE_ESTIMATE) if total_words > 0 else 0
avg_words_per_sentence = (total_words / total_sentences) if total_sentences > 0 else 0.0

book_metrics = {
    "total_sentences": total_sentences,
    "total_words": total_words,
    "total_characters_clean": total_characters_clean,
    "estimated_pages": estimated_pages,
    "avg_words_per_sentence": avg_words_per_sentence,
}

print(f"\n✨ Book Metrics Calculated: Sentences={total_sentences}, Words={total_words}, Pages={estimated_pages}")


# === 4. GENERATE COVER IMAGE AND XHTML ===
# 4.1. Generate the custom cover image (JPG)
generate_cover_image(book_title, book_intro, book_author, COVER_ART_PATH, COVER_OUTPUT_PATH)

# 4.2. Write Cover Page (XHTML)
cover_filename = f"{file_prefix}_{str(START_INDEX).zfill(4)}.xhtml"
cover_image_ref = os.path.basename(COVER_OUTPUT_PATH) 
with open(os.path.join(BASE_OUTPUT_FOLDER, cover_filename), "w", encoding="utf-8") as f:
    f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{metadata.get('LANGUAGE', 'en')}" xmlns:epub="http://www.idpf.org/2007/ops">
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


# === 5. WRITE METRICS PAGE ===
counter = START_INDEX + 1
counter = write_summary_page(book_metrics, counter, file_prefix, BASE_OUTPUT_FOLDER)


# === 6. Process Main Content ===
toc_entries = []
missing_images = []
paragraph_buffer = []

for line in content_lines:
    
    # ⚠️ FIX: Ignore lines that start with '#' but are NOT recognized as section levels
    if line.startswith("#") and not line.lower().startswith("#level"):
        continue

    if line.startswith("[") and line.endswith("]"):
        # 6.1. Flush previous paragraph buffer
        counter = flush_paragraph_buffer(paragraph_buffer, counter, file_prefix, BASE_OUTPUT_FOLDER)
        paragraph_buffer = []

        # 6.2. Write Heading Fragment
        section_title = line[1:-1]
        level_titles = section_title.split(" > ")
        current_level = len(level_titles)
        tag = min(current_level + 1, 6)
        current_title = level_titles[-1]

        # 🛑 CORRECTION APLICADA AQUÍ (Línea 485 corregida de </h{tag>} a </h{tag}>)
        html_heading = f"<h{tag}>{html.escape(current_title)}</h{tag}>"

        filename = f"{file_prefix}_{str(counter).zfill(4)}.xhtml"
        with open(os.path.join(BASE_OUTPUT_FOLDER, filename), "w", encoding="utf-8") as f:
            f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{metadata.get('LANGUAGE', 'en')}">
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
        # 6.3. Flush previous paragraph buffer
        counter = flush_paragraph_buffer(paragraph_buffer, counter, file_prefix, BASE_OUTPUT_FOLDER)
        paragraph_buffer = []

        # 6.4. Write Image Page Fragment
        try:
            parts = line[5:].split("|", 1)
            img_file = parts[0].strip()
            alt_text = parts[1].strip() if len(parts) > 1 else ""

            image_source_path = os.path.join(IMAGES_FOLDER, img_file)
            if not os.path.isfile(image_source_path):
                missing_images.append(img_file)
            
            alt_text_clean = html.escape(alt_text)
            alt_caption = html.escape(alt_text)

            filename = f"{file_prefix}_{str(counter).zfill(4)}.xhtml"
            with open(os.path.join(BASE_OUTPUT_FOLDER, filename), "w", encoding="utf-8") as f:
                f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{metadata.get('LANGUAGE', 'en')}">
  <head>
    <meta charset="UTF-8"/>
    <title>Image: {html.escape(img_file)}</title>
    <link rel="stylesheet" href="../Styles/Style001.css" type="text/css"/>
  </head>
  <body>
    <div class="image-page">
      <figure>
        <img src="../{IMAGES_FOLDER}/{html.escape(img_file)}" alt="{alt_text_clean}" />
        <figcaption>{alt_caption}</figcaption>
      </figure>
    </div>
  </body>
</html>''')
            counter += 1
        except Exception as e:
            print(f"⚠️ Error processing image line: {line}\n{e}")

    elif line == "===":
        # 6.5. Flush previous paragraph buffer (end of paragraph)
        counter = flush_paragraph_buffer(paragraph_buffer, counter, file_prefix, BASE_OUTPUT_FOLDER)
        paragraph_buffer = []

    else:
        # 6.6. Sentence line, add to buffer
        paragraph_buffer.append(line)

# === 7. Process any remaining paragraphs at the end of the file ===
counter = flush_paragraph_buffer(paragraph_buffer, counter, file_prefix, BASE_OUTPUT_FOLDER)


if missing_images:
    print("\n❌ Missing image files referenced:")
    for img in missing_images:
        print(f" - {img}")
else:
    print("✅ All image references verified.")


# === 8. Write index.xhtml ===
write_index_xhtml(toc_entries, file_prefix, START_INDEX, BASE_OUTPUT_FOLDER)


# === 9. Save TOC hierarchy data for Script 03 (Manifest Builder) ===
toc_data_path = os.path.join(BASE_OUTPUT_FOLDER, "toc_data.json")
with open(toc_data_path, "w", encoding="utf-8") as f:
    json.dump(toc_entries, f, indent=4)

print(f"✅ TOC hierarchy data saved to {toc_data_path}")
print("\n✅ XHTML files generated successfully, ready for Script 03.")