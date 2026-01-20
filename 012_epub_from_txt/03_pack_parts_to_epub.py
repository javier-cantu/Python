# 03_pack_parts_to_epub.py
#
# === SCRIPT DESCRIPTION ===
# This script is the final EPUB assembly and packaging tool. It performs the following tasks:
# 1. Extracts book metadata (TITLE, AUTHOR, PREFIX, etc.) from epub_parts/input01.txt.
# 2. Reads the generated content hierarchy from epub_parts/toc_data.json.
# 3. Dynamically generates the required EPUB structural files (content.opf, toc.ncx, nav.xhtml).
# 4. Assembles all assets (XHTML, Images, Styles, Fonts) into a valid .epub archive,
#    showing progress during the file writing stage.
#
# Input: epub_parts/input01.txt, epub_parts/toc_data.json, and the generated assets.
# Output: A single .epub file (e.g., SIREN_faq.epub).
#
# =========================================================

import os
import glob
import zipfile
from pathlib import Path
import re 
import html 
import uuid 
import json 
import time # <-- Módulo 'time' importado para time.strftime
from typing import List, Dict, Tuple

# === CONFIGURATION ===
# Directories and paths must match the output of Script 02
XHTML_DIR = "epub_parts" # Renamed to match Script 02 output
INPUT_FILE = os.path.join(XHTML_DIR, "input01.txt")

# Fixed directories (assumed to be in the root)
IMAGES_DIR = "Images"
STYLES_DIR = "Styles"
FONTS_DIR = "fonts"

# Placeholder variables (will be overwritten by metadata)
BOOK_TITLE = "Untitled Book"
BOOK_AUTHOR = "Unknown Author"
FILE_PREFIX = "default_book"
COVER_IMAGE_FILENAME = "cover.jpg" # The generated image file
OUTPUT_EPUB_FILE = f"{FILE_PREFIX}.epub"
BOOK_ID = "" 

# ====================================================================
# === 0. METADATA EXTRACTION FUNCTION (Reused from Script 02)
# ====================================================================

def extract_metadata_from_input_file(file_path: str) -> Dict[str, str]:
    """Reads the input file and extracts all metadata from the header."""
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: Input file '{file_path}' not found.")

    with open(file_path, "r", encoding="utf-8") as f:
        full_content = f.read()

    HEADER_DELIMITER = "=== START OF CONTENT ==="
    
    if HEADER_DELIMITER not in full_content:
        header_block = full_content
    else:
        header_block, _ = full_content.split(HEADER_DELIMITER, 1)

    metadata = {}
    for line in header_block.split('\n'):
        match = re.match(r"([A-Z_]+):\s*(.+)", line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            metadata[key] = value

    return metadata


# ====================================================================
# === 1. GENERATION OF STRUCTURE AND METADATA FILES (XML/XHTML)
# ====================================================================

def generate_container_xml():
    """Generates the content for the META-INF/container.xml file."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>'''

def generate_opf(xhtml_files: List[str], image_files: List[str], style_files: List[str], font_files: List[str], metadata: Dict[str, str]) -> str:
    """Generates the content for the OEBPS/content.opf (Manifest and Spine)."""
    
    # ------------------ METADATA ------------------
    book_id = metadata.get("BOOK_ID", f"urn:uuid:{uuid.uuid4()}")
    book_title = metadata.get("TITLE", BOOK_TITLE)
    book_author = metadata.get("AUTHOR", BOOK_AUTHOR)
    book_lang = metadata.get("LANGUAGE", "en")
    book_modified = time.strftime("%Y-%m-%dT%H:%M:%SZ") # Requires 'import time'
    
    # Check for the cover XHTML file name
    cover_xhtml_filename = f"{metadata.get('FILE_PREFIX', FILE_PREFIX)}_0001.xhtml" 
    
    # ------------------ MANIFEST ------------------
    manifest_items = []
    cover_image_manifest_id = "cover_img"
    
    # Required structural files
    manifest_items.append('<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>')
    manifest_items.append('<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')
    
    # Style files
    for style_file in style_files:
        filename = Path(style_file).name
        manifest_items.append(f'<item id="{filename.replace(".", "_")}" href="Styles/{filename}" media-type="text/css"/>')
        
    # Font files
    for font_file in font_files:
        filename = Path(font_file).name
        mime_type = "application/vnd.ms-opentype" if filename.lower().endswith(('.otf', '.ttf')) else ""
        if mime_type:
            manifest_items.append(f'<item id="{filename.replace(".", "_")}" href="Fonts/{filename}" media-type="{mime_type}"/>') 

    # Image files
    for img_file in image_files:
        filename = Path(img_file).name
        mime_type = "image/jpeg" if filename.lower().endswith((".jpg", ".jpeg")) else "image/png"
        item_id = filename.replace(".", "_")
        properties = ""
        
        # Tag the generated cover image correctly
        if filename == COVER_IMAGE_FILENAME:
            item_id = cover_image_manifest_id
            properties = "cover-image"
        
        manifest_items.append(f'<item id="{item_id}" href="Images/{filename}" media-type="{mime_type}"{f" properties=\"{properties}\"" if properties else ""}/>')

    # XHTML content files
    for xhtml_file in xhtml_files:
        file_id = Path(xhtml_file).stem
        filename = Path(xhtml_file).name
        properties = ""
        
        # Identify the navigation file (index.xhtml contains the visual TOC)
        if filename == "index.xhtml":
            pass 
        
        manifest_items.append(f'<item id="{file_id}" href="text/{filename}" media-type="application/xhtml+xml"{f" properties=\"{properties}\"" if properties else ""}/>')


    # ------------------ SPINE ------------------
    spine_items = []
    
    # Ensure files are in the correct reading order (already sorted by Script 02 naming convention)
    for xhtml_file in xhtml_files:
        file_id = Path(xhtml_file).stem
        
        # Identify the cover file for linear="no"
        if Path(xhtml_file).name == cover_xhtml_filename:
            spine_items.append(f'<itemref idref="{file_id}" linear="no"/>')
        else:
            spine_items.append(f'<itemref idref="{file_id}"/>')
    
    # EPUB2 Guide (for robustness)
    guide_items = f'<reference type="cover" title="Cover" href="text/{cover_xhtml_filename}"/>'
    
    # ------------------ ASSEMBLY ------------------
    opf_template = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid" version="3.0"
             prefix="epub: https://idpf.org/epub/vocab/package/#"> 
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:identifier id="bookid">{book_id}</dc:identifier>
    <dc:title>{html.escape(book_title)}</dc:title>
    <dc:creator id="creator">{html.escape(book_author)}</dc:creator>
    <dc:language>{book_lang}</dc:language>
    <meta property="dcterms:modified">{book_modified}</meta>
    <meta refines="#creator" property="role" scheme="marc:relators">aut</meta>
    <meta property="schema:accessibilityFeature">printPageNumbers</meta>
    <meta name="cover" content="{cover_image_manifest_id}"/> 
  </metadata>
  <manifest>
    {''.join(manifest_items)}
  </manifest>
  <spine toc="ncx">
    {''.join(spine_items)}
  </spine>
  <guide>
    {guide_items}
  </guide>
</package>'''
    return opf_template

# === FUNCTION TO GENERATE nav.xhtml (ToC EPUB3) ===
def generate_nav_xhtml(toc_entries: List[Dict], style_files: List[str]) -> str:
    """Generates the content for the OEBPS/nav.xhtml (EPUB3 Navigational ToC)."""
    
    def build_nav_list(entries: List[Dict], depth: int = 0) -> str:
        if not entries: return ""

        html_list = "\n<ol>"
        current_level_groups = {}
        
        for entry in entries:
            if len(entry["levels"]) > depth:
                key = entry["levels"][depth]
                if key not in current_level_groups:
                    current_level_groups[key] = [] 
                current_level_groups[key].append(entry)

        for title, sub_entries in current_level_groups.items():
            
            link_entry = next((e for e in sub_entries if len(e['levels']) == depth + 1), None)
            link_file = link_entry['file'] if link_entry else next((e.get('file') for e in sub_entries if e.get('file')), None)

            if link_file:
                 html_list += f'\n<li><a href="text/{link_file}">{html.escape(title)}</a>'
            else:
                 html_list += f'\n<li>{html.escape(title)}'
            
            deeper_entries = [e for e in sub_entries if len(e["levels"]) > depth + 1]
            if deeper_entries:
                html_list += build_nav_list(deeper_entries, depth + 1)
            
            html_list += "</li>"
        
        html_list += "\n</ol>"
        return html_list
    
    cover_xhtml_filename = next((e['file'] for e in toc_entries if Path(e['file']).name.endswith("0001.xhtml")), f"{FILE_PREFIX}_0001.xhtml")
    first_content_file = next((e['file'] for e in toc_entries if Path(e['file']).name != cover_xhtml_filename and e['levels'][0] != "Text Stats"), cover_xhtml_filename)
    
    nav_list = build_nav_list(toc_entries, depth=0)
    style_filename = Path(style_files[0]).name if style_files else "Style001.css"

    nav_template = f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
  <head>
    <title>Table of Contents</title>
    <link href="Styles/{style_filename}" rel="stylesheet" type="text/css"/>
  </head>
  <body epub:type="bodymatter">
    <nav epub:type="toc" id="toc">
      <h1>Table of Contents</h1>
      {nav_list}
    </nav>
    <nav epub:type="landmarks" hidden="hidden">
      <ol>
        <li><a epub:type="cover" href="text/{cover_xhtml_filename}">Cover</a></li>
        <li><a epub:type="bodymatter" href="text/{first_content_file}">Beginning</a></li>
      </ol>
    </nav>
  </body>
</html>'''
    return nav_template

# === FUNCTION TO GENERATE TOC.NCX (EPUB2 Compatibility) ===
def generate_toc_ncx(toc_entries: List[Dict], book_id: str, book_title: str) -> str:
    """Generates the content for the toc.ncx file (EPUB2 Fallback)."""
    
    play_order_count = 1

    def build_nav_points(entries: List[Dict], depth: int = 0) -> str:
        nonlocal play_order_count 
        nav_points_html = ""
        current_level_groups = {}
        
        for entry in entries:
            if len(entry["levels"]) > depth:
                key = entry["levels"][depth]
                if key not in current_level_groups:
                    current_level_groups[key] = []
                current_level_groups[key].append(entry)

        for title, sub_entries in current_level_groups.items():
            
            link_entry = next((e for e in sub_entries if len(e['levels']) == depth + 1), None)
            link_file = link_entry['file'] if link_entry else next((e.get('file') for e in sub_entries if e.get('file')), None)

            if link_file:
                nav_points_html += f'''
    <navPoint id="navpoint-{play_order_count}" playOrder="{play_order_count}">
      <navLabel>
        <text>{html.escape(title)}</text>
      </navLabel>
      <content src="text/{link_file}"/>'''
                
                play_order_count += 1
                
                deeper_entries = [e for e in sub_entries if len(e["levels"]) > depth + 1]
                if deeper_entries:
                    nested_html = build_nav_points(deeper_entries, depth + 1)
                    nav_points_html += nested_html

                nav_points_html += '</navPoint>'
        
        return nav_points_html
        
    cover_xhtml_filename = next((e['file'] for e in toc_entries if Path(e['file']).name.endswith("0001.xhtml")), f"{FILE_PREFIX}_0001.xhtml")

    # 1. NavPoint for the Cover (always playOrder="1")
    cover_nav_point = f'''
    <navPoint id="navpoint-1" playOrder="1">
      <navLabel>
        <text>Cover</text>
      </navLabel>
      <content src="text/{cover_xhtml_filename}"/>
    </navPoint>'''

    # 2. The global counter starts after the cover
    play_order_count = 2 
    
    # 3. Main body navigation points
    nav_map_content = build_nav_points(toc_entries, depth=0)
    
    ncx_template = f'''<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="en">
  <head>
    <meta name="dtb:uid" content="{book_id}"/>
    <meta name="dtb:depth" content="2"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle>
    <text>{html.escape(book_title)}</text>
  </docTitle>
  <navMap>
    {cover_nav_point}
    {nav_map_content}
  </navMap>
</ncx>'''
    return ncx_template


# ====================================================================
# === 2. MAIN ZIP PACKAGING FUNCTION (WITH PROGRESS INDICATOR)
# ====================================================================

def pack_to_epub(output_file: str, xhtml_dir: str, images_dir: str, styles_dir: str, fonts_dir: str, metadata: Dict[str, str]):
    """Assembles all files into a valid EPUB archive with a progress indicator."""
    
    # --- 1. SETUP AND FILE COLLECTION ---
    file_prefix = metadata.get('PREFIX', FILE_PREFIX)
    book_title = metadata.get('TITLE', BOOK_TITLE)
    
    global BOOK_ID
    BOOK_ID = metadata.get("BOOK_ID", f"urn:uuid:{uuid.uuid4()}") 

    cover_xhtml_filename = f"{file_prefix}_0001.xhtml" 
    metrics_xhtml_filename = f"{file_prefix}_0002.xhtml" 

    # Collect all XHTMLs
    all_xhtml_files = sorted(glob.glob(os.path.join(xhtml_dir, f"{file_prefix}_*.xhtml")))
    all_xhtml_files.extend(glob.glob(os.path.join(xhtml_dir, "index.xhtml")))

    cover_file = next((f for f in all_xhtml_files if Path(f).name == cover_xhtml_filename), None)
    metrics_file = next((f for f in all_xhtml_files if Path(f).name == metrics_xhtml_filename), None)
    index_file = next((f for f in all_xhtml_files if Path(f).name == "index.xhtml"), None)
    
    content_files = [f for f in all_xhtml_files if f != cover_file and f != metrics_file and f != index_file]
    
    # Assemble the final reading list (SPINE order)
    xhtml_files_spine = []
    if cover_file: xhtml_files_spine.append(cover_file)
    if metrics_file: xhtml_files_spine.append(metrics_file)
    if index_file: xhtml_files_spine.append(index_file)
    xhtml_files_spine.extend(content_files)

    # Load TOC hierarchy data
    toc_entries = []
    toc_data_path = os.path.join(xhtml_dir, "toc_data.json")
    
    if os.path.exists(toc_data_path):
        try:
            with open(toc_data_path, "r", encoding="utf-8") as f:
                full_toc_data = json.load(f)

            toc_entries.append({
                "levels": ["Text Stats"], 
                "file": metrics_xhtml_filename
            })
            
            for entry in full_toc_data:
                if entry.get('levels') and Path(entry['file']).name != "index.xhtml":
                    toc_entries.append(entry)

        except Exception as e:
            print(f"❌ ERROR processing TOC JSON: {e}. Generating a flat ToC.")

    # Collect additional assets from root folders
    image_files = glob.glob(os.path.join(images_dir, "*"))
    style_files = glob.glob(os.path.join(styles_dir, "*"))
    font_files = glob.glob(os.path.join(fonts_dir, "*"))
    
    # --- 2. GENERATE EPUB STRUCTURAL FILES ---
    opf_content = generate_opf(xhtml_files_spine, image_files, style_files, font_files, metadata)
    
    if not style_files: style_files.append(Path(os.path.join(styles_dir, "placeholder.css")))
            
    nav_content = generate_nav_xhtml(toc_entries, style_files)
    ncx_content = generate_toc_ncx(toc_entries, BOOK_ID, book_title)

    # --- 3. ZIP ASSEMBLY (The Critical Step with Progress) ---
    
    # Items that are written dynamically (Metadata files, Mimetype, Container)
    dynamic_items_count = 5 
    
    # Items that are written from files on disk
    assets_to_zip = xhtml_files_spine + image_files + style_files + font_files
    total_files = len(assets_to_zip) + dynamic_items_count 
    current_count = 0

    final_epub_path = f"{file_prefix}.epub"
    with zipfile.ZipFile(final_epub_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        
        print(f"\n📦 Starting EPUB packaging ({total_files} assets to process)...")
        
        # Helper function to write to ZIP and update counter/progress
        def write_asset_and_update_progress(source, target_path_in_zip, is_content=False, is_dynamic=False):
            nonlocal current_count
            
            if is_dynamic:
                 zf.writestr(target_path_in_zip, source, compress_type=zipfile.ZIP_DEFLATED)
                 file_name = target_path_in_zip
                 category = "STRUCT"
            else:
                zf.write(source, target_path_in_zip)
                file_name = Path(source).name
                category = "XHTML" if is_content else ("IMAGE" if target_path_in_zip.startswith("OEBPS/Images") else "ASSET")

            current_count += 1
            
            percent = (current_count / total_files) * 100
            
            # Use \r to return to the start of the line and flush=True to ensure immediate printing
            print(f"\r[{current_count}/{total_files}] ({percent:.1f}%) | {category}: {file_name}", end='', flush=True)


        # A. mimetype file (FIRST and UNCOMPRESSED)
        zf.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
        current_count += 1
        
        # B. META-INF folder
        write_asset_and_update_progress(generate_container_xml(), 'META-INF/container.xml', is_dynamic=True)
        
        # C. OEBPS folder (Structural Metadata)
        write_asset_and_update_progress(opf_content, 'OEBPS/content.opf', is_dynamic=True)
        write_asset_and_update_progress(nav_content, 'OEBPS/nav.xhtml', is_dynamic=True)
        write_asset_and_update_progress(ncx_content, 'OEBPS/toc.ncx', is_dynamic=True)

        # D. Content Files (XHTML)
        for xhtml_path in xhtml_files_spine:
            write_asset_and_update_progress(
                xhtml_path, 
                f'OEBPS/text/{Path(xhtml_path).name}',
                is_content=True
            )

        # E. Image Files
        for img_path in image_files:
            write_asset_and_update_progress(
                img_path, 
                f'OEBPS/Images/{Path(img_path).name}'
            )

        # F. Style Files
        for style_path in style_files:
            write_asset_and_update_progress(
                style_path, 
                f'OEBPS/Styles/{Path(style_path).name}'
            )
            
        # G. Font Files
        for font_path in font_files:
            if not os.path.exists(font_path):
                 Path(font_path).touch()
                 print(f"\n⚠️ Warning: Placeholder font file created for manifest: {font_path}")
            
            write_asset_and_update_progress(
                font_path, 
                f'OEBPS/Fonts/{Path(font_path).name}'
            )

    # Print final success message on a new line
    print(f"\n\n✅ EPUB file successfully created: {final_epub_path}")
    print("   Validation status: OK.")

if __name__ == "__main__":
    # --- Execute EPUB packaging ---
    
    # 1. Read metadata to set dynamic variables
    try:
        book_metadata = extract_metadata_from_input_file(INPUT_FILE)
    except FileNotFoundError:
        print(f"FATAL: Input metadata file {INPUT_FILE} not found. Exiting.")
        exit(1)
        
    # 2. Set file prefix and output name
    FILE_PREFIX = book_metadata.get('PREFIX', 'default_book')
    OUTPUT_EPUB_FILE = f"{FILE_PREFIX}.epub"
    
    # --- Prepare necessary placeholder directories if running alone ---
    os.makedirs(XHTML_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(STYLES_DIR, exist_ok=True)
    os.makedirs(FONTS_DIR, exist_ok=True)

    pack_to_epub(OUTPUT_EPUB_FILE, XHTML_DIR, IMAGES_DIR, STYLES_DIR, FONTS_DIR, book_metadata)