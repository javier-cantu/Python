import os
import glob
import zipfile
from pathlib import Path
import re 
from PIL import Image 
import html 
import uuid 
import time 

# --- CONFIGURACIÓN ---
# Directorios de entrada que contienen los archivos generados por 02_generate_xhtml.py
XHTML_DIR = "xhtmls_sequences"
IMAGES_DIR = "Images"
STYLES_DIR = "Styles" 
FONTS_DIR = "fonts" 
OUTPUT_EPUB_FILE = "output_ebook.epub"

# Metadatos del libro (Ajusta estos valores)
BOOK_TITLE = "The Stand - Ch52 t"
BOOK_AUTHOR = "Stephen King"
# Genera un UUID v4 válido (exigido por el estándar EPUB3)
BOOK_ID = f"urn:uuid:{uuid.uuid4()}" 
FILE_PREFIX = "SK_TS_Ch52" 

# Nombre del archivo de portada generado por 02_generate_xhtml.py
COVER_IMAGE_FILENAME = "cover.jpg"
# Nombre del archivo de portada XHTML (el primero en la secuencia)
COVER_XHTML_FILENAME = f"{FILE_PREFIX}_0001.xhtml" 

# ====================================================================
# === 1. GENERACIÓN DE ARCHIVOS DE ESTRUCTURA Y METADATOS (XML/XHTML)
# ====================================================================

def generate_container_xml():
    """Genera el contenido del archivo META-INF/container.xml."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>'''

def generate_opf(xhtml_files, image_files, style_files, font_files):
    """Genera el contenido del archivo OEBPS/content.opf (Manifest y Spine)."""
    
    # 1. MANIFEST (Listado de todos los archivos)
    manifest_items = []
    
    # Archivos obligatorios de estructura
    manifest_items.append('<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>')
    # CORRECCIÓN: nav.xhtml utiliza la propiedad 'nav', la cual es estándar en EPUB3
    manifest_items.append('<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')
    
    # Archivos de estilos 
    for style_file in style_files:
        filename = Path(style_file).name
        manifest_items.append(f'<item id="{filename.replace(".", "_")}" href="Styles/{filename}" media-type="text/css"/>')
        
    # Archivos de fuentes
    for font_file in font_files:
        filename = Path(font_file).name
        mime_type = ""
        if filename.lower().endswith(('.otf', '.ttf')):
            mime_type = "application/vnd.ms-opentype"
        
        if mime_type:
            manifest_items.append(f'<item id="{filename.replace(".", "_")}" href="Fonts/{filename}" media-type="{mime_type}"/>') 
        else:
            print(f"⚠️ Warning: Skipping font file {filename} due to unknown MIME type.")


    # Archivos de imágenes
    cover_image_manifest_id = "cover_img"
    
    for img_file in image_files:
        filename = Path(img_file).name
        mime_type = "image/jpeg" if filename.lower().endswith((".jpg", ".jpeg")) else "image/png"
        item_id = filename.replace(".", "_")
        properties = ""
        
        # Etiquetar la imagen de portada correctamente con properties="cover-image"
        if filename == COVER_IMAGE_FILENAME:
            item_id = cover_image_manifest_id
            properties = "cover-image"
        
        manifest_items.append(f'<item id="{item_id}" href="Images/{filename}" media-type="{mime_type}"{f" properties=\"{properties}\"" if properties else ""}/>')

    # Archivos XHTML de contenido
    for i, xhtml_file in enumerate(xhtml_files):
        file_id = Path(xhtml_file).stem
        filename = Path(xhtml_file).name
        properties = ""
        
        # Identificar el índice
        if filename == "index.xhtml":
            pass 
        
        # Elimina espacios extra
        properties = properties.strip()

        manifest_items.append(f'<item id="{file_id}" href="text/{filename}" media-type="application/xhtml+xml"{f" properties=\"{properties}\"" if properties else ""}/>')


    # 2. SPINE (Orden de lectura de los archivos XHTML)
    spine_items = []
    for xhtml_file in xhtml_files:
        file_id = Path(xhtml_file).stem
        
        if Path(xhtml_file).name == COVER_XHTML_FILENAME: # La portada es la única no linear
            spine_items.append(f'<itemref idref="{file_id}" linear="no"/>')
        else:
            spine_items.append(f'<itemref idref="{file_id}"/>')
    
    # Identificar la portada para la guía de EPUB2 (opcional, pero útil)
    guide_items = f'<reference type="cover" title="Cover" href="text/{Path(xhtml_files[0]).name}"/>'
    
    # 3. ENSAMBLAJE DEL OPF
    opf_template = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid" version="3.0"
         prefix="epub: https://idpf.org/epub/vocab/package/#"> <!-- Se mantiene prefix para EPUB3 -->
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:identifier id="bookid">{BOOK_ID}</dc:identifier>
    <dc:title>{BOOK_TITLE}</dc:title>
    <dc:creator id="creator">{BOOK_AUTHOR}</dc:creator>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2020-01-01T00:00:00Z</meta>
    <meta refines="#creator" property="role" scheme="marc:relators">aut</meta>
    <meta property="schema:accessibilityFeature">printPageNumbers</meta>
    <meta name="cover" content="{cover_image_manifest_id}"/> <!-- NUEVA CORRECCIÓN: Etiqueta de portada para compatibilidad EPUB2/IDPF -->
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

def generate_nav_xhtml(toc_entries, opf_filename, style_files):
    """Genera el contenido del archivo OEBPS/nav.xhtml (ToC Navigacional EPUB3)."""
    
    # Función recursiva para construir el índice
    def build_nav_list(entries, depth=0):
        if not entries:
            return ""

        html_list = ""
        current_level_groups = {}
        
        for entry in entries:
            if len(entry["levels"]) > depth:
                key = entry["levels"][depth]
                if key not in current_level_groups:
                    current_level_groups[key] = [] 
                current_level_groups[key].append(entry)

        html_list += "\n<ol>"
        for title, sub_entries in current_level_groups.items():
            first_entry = sub_entries[0]
            
            is_terminal = len(first_entry["levels"]) == depth + 1
            
            link_file = first_entry["file"] if is_terminal else next((e['file'] for e in sub_entries if 'file' in e), None)

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
    
    # NUEVO: Añadir la portada al inicio del nav
    cover_link = f'text/{COVER_XHTML_FILENAME}'
    
    # Generar la ToC Principal
    nav_list = build_nav_list(toc_entries)
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
        <!-- CORRECCIÓN: Añadir epub:type a los anchors en landmarks -->
        <li><a epub:type="cover" href="{cover_link}">Cover</a></li>
        <li><a epub:type="bodymatter" href="text/{toc_entries[0]['file']}">Beginning</a></li>
      </ol>
    </nav>
  </body>
</html>'''
    return nav_template

# === FUNCIÓN PARA GENERAR EL TOC.NCX (Requerido por compatibilidad) ===
def generate_toc_ncx(toc_entries, book_id, book_title):
    """Genera el contenido del archivo toc.ncx (EPUB2 Fallback)."""
    
    # Lista global para asegurar la unicidad del playOrder
    global_play_order_count = 1

    # Función recursiva para generar los navPoints
    def build_nav_points(entries, depth=1):
        nonlocal global_play_order_count
        nav_points_html = ""
        current_level_groups = {}
        
        # Agrupar entradas por el título en el nivel actual
        for entry in entries:
            if len(entry["levels"]) >= depth:
                key = entry["levels"][depth - 1]
                if key not in current_level_groups:
                    current_level_groups[key] = []
                current_level_groups[key].append(entry)

        for title, sub_entries in current_level_groups.items():
            first_entry = sub_entries[0]
            
            # Determinar el archivo de destino
            link_file = first_entry["file"]
            
            # Generar el navPoint (usa el contador global)
            nav_points_html += f'''
    <navPoint id="navpoint-{global_play_order_count}" playOrder="{global_play_order_count}">
      <navLabel>
        <text>{html.escape(title)}</text>
      </navLabel>
      <content src="text/{link_file}"/>'''
            
            # El contador avanza estrictamente para este navPoint
            global_play_order_count += 1
            
            # Recorrer niveles más profundos
            deeper_entries = [e for e in sub_entries if len(e["levels"]) > depth]
            if deeper_entries:
                # La recursión continúa, y la función recursiva actualizará el contador global
                nested_html = build_nav_points(deeper_entries, depth + 1)
                nav_points_html += nested_html

            nav_points_html += '</navPoint>'
        
        # Devuelve solo el HTML, ya que el contador global se maneja fuera
        return nav_points_html

    # Los puntos de navegación del cuerpo principal
    # CORRECCIÓN: Agregamos la portada como el primer navPoint antes de la recursión principal
    
    # 1. NavPoint para la Portada
    cover_nav_point = f'''
    <navPoint id="navpoint-1" playOrder="1">
      <navLabel>
        <text>Cover</text>
      </navLabel>
      <content src="text/{COVER_XHTML_FILENAME}"/>
    </navPoint>'''

    # 2. El contador global inicia después de la portada
    global_play_order_count = 2 
    
    # 3. Puntos de navegación del cuerpo principal (inicia desde el nivel 1 de la jerarquía)
    nav_map_content = build_nav_points(toc_entries)
    
    # Aseguramos que el contador global no se reinicie, pero aquí el problema era la portada.

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
# === 2. FUNCIÓN PRINCIPAL DE EMPAQUETADO ZIP
# ====================================================================

def pack_to_epub(output_file, xhtml_dir, images_dir, styles_dir, fonts_dir, file_prefix):
    """Ensambla todos los archivos en un archivo EPUB válido."""

    # 1. Recolectar Archivos y generar TOC/Manifest
    
    # 1.1 Listar y ordenar todos los archivos numerados
    xhtml_files_numbered = sorted(glob.glob(os.path.join(xhtml_dir, f"{file_prefix}_*.xhtml")))
    
    # 1.2 Separar la Portada, Métricas y Contenido
    cover_file = next((f for f in xhtml_files_numbered if Path(f).name == COVER_XHTML_FILENAME), None)
    metrics_file = next((f for f in xhtml_files_numbered if Path(f).name == f'{file_prefix}_0002.xhtml'), None)
    index_file = next((f for f in glob.glob(os.path.join(xhtml_dir, "index.xhtml"))), None)
    
    # Contenido principal (todos los demás numerados)
    content_files = [f for f in xhtml_files_numbered if f != cover_file and f != metrics_file]
    
    # 1.3 Ensamblar la lista de lectura (SPINE) en el orden correcto
    # Orden: [Portada, Métricas, Índice Visual, Contenido, ...]
    xhtml_files = []
    if cover_file:
        xhtml_files.append(cover_file)
    if metrics_file:
        xhtml_files.append(metrics_file)
    if index_file: # Se inserta el índice visual AQUI (después de métricas)
        xhtml_files.append(index_file)
    xhtml_files.extend(content_files)

    
    # --------------------------------------------------------------------------
    # RECOLECCIÓN DE TOC/TOC_ENTRIES (Solo títulos)
    # --------------------------------------------------------------------------
    
    toc_entries = []
    
    # Itera sobre los archivos que deben aparecer en la ToC (Métricas + Contenido)
    for xhtml_path in xhtml_files:
        filename = Path(xhtml_path).name
        
        # Excluye la portada y el índice visual de la ToC Navigacional (menú)
        if filename == "index.xhtml" or filename == COVER_XHTML_FILENAME: 
            continue
            
        try:
            with open(xhtml_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # REGLA CLAVE: Solo si contiene un tag de encabezado Hx
                match = re.search(r'<h(\d)>(.*?)</h\1>', content, re.IGNORECASE)
                
                # 1. Caso de la página de Métricas (Siempre Nivel 1 si tiene Hx)
                if filename == f"{FILE_PREFIX}_0002.xhtml":
                    # Busca el título H1 dentro de la página de métricas
                    metrics_match = re.search(r'<h1>(.*?)</h1>', content, re.IGNORECASE)
                    if metrics_match:
                        title = metrics_match.group(1).strip()
                        toc_entries.append({
                            "levels": [title], # Título de Nivel 1
                            "file": filename
                        })
                
                # 2. Caso de Secciones/Capítulos (debe tener un Hx tag)
                elif match:
                    level = int(match.group(1))
                    title = match.group(2).strip()
                    
                    # SIMULACIÓN DE LA JERARQUÍA:
                    simulated_levels = []
                    # Añade placeholders (Chapter/Section 1, Chapter/Section 2, etc.) hasta el nivel del heading encontrado
                    for i in range(1, level):
                        simulated_levels.append(f"Chapter/Section {i}")
                    
                    # El último elemento de la jerarquía es el título real
                    simulated_levels.append(title) 

                    toc_entries.append({
                        "levels": simulated_levels, # Usa la jerarquía simulada
                        "file": filename
                    })
                # Fragmentos de oración (sin Hx) son ignorados.
        except Exception:
             pass 

    # Archivos adicionales
    image_files = glob.glob(os.path.join(images_dir, "*"))
    style_files = glob.glob(os.path.join(styles_dir, "*"))
    font_files = glob.glob(os.path.join(fonts_dir, "*")) # Recolectar archivos de fuentes
    
    # 2. Generar Archivos de Estructura Dinámicamente
    opf_content = generate_opf(xhtml_files, image_files, style_files, font_files)
    
    # Se asegura que la lista de estilos no esté vacía antes de llamar a generate_nav_xhtml
    if not style_files:
        print("⚠️ Warning: No style files found. EPUB may not render correctly.")
        style_files.append(Path(os.path.join(STYLES_DIR, "placeholder.css")))
        
    nav_content = generate_nav_xhtml(toc_entries, "content.opf", style_files)
    # Generar el toc.ncx válido
    ncx_content = generate_toc_ncx(toc_entries, BOOK_ID, BOOK_TITLE)

    # 3. Ensamblaje ZIP (EL PASO CRÍTICO)
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        
        # A. Archivo mimetype (PRIMERO Y SIN COMPRIMIR)
        zf.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
        
        # B. Carpeta META-INF
        zf.writestr('META-INF/container.xml', generate_container_xml(), compress_type=zipfile.ZIP_DEFLATED)
        
        # C. Carpeta OEBPS (Metadata y Contenido)
        # 1. Metadatos
        zf.writestr('OEBPS/content.opf', opf_content, compress_type=zipfile.ZIP_DEFLATED)
        zf.writestr('OEBPS/nav.xhtml', nav_content, compress_type=zipfile.ZIP_DEFLATED)
        zf.writestr('OEBPS/toc.ncx', ncx_content, compress_type=zipfile.ZIP_DEFLATED)

        # 2. Archivos de Contenido (XHTML)
        for xhtml_path in xhtml_files:
            zf.write(xhtml_path, f'OEBPS/text/{Path(xhtml_path).name}')

        # 3. Archivos de Imágenes
        for img_path in image_files:
            zf.write(img_path, f'OEBPS/Images/{Path(img_path).name}')

        # 4. Archivos de Estilos
        for style_path in style_files:
            zf.write(style_path, f'OEBPS/Styles/{Path(style_path).name}')
            
        # 5. Archivos de Fuentes
        for font_path in font_files:
            # Crea un archivo vacío de prueba si el archivo de fuente no existe.
            if not os.path.exists(font_path):
                Path(font_path).touch()
                print(f"⚠️ Warning: Placeholder font created for manifest: {font_path}")
            
            zf.write(font_path, f'OEBPS/Fonts/{Path(font_path).name}')
            
    print(f"\n✅ EPUB file successfully created: {output_file}")
    print("   Please check the EPUB file using an EPUB validator (e.g., EPUBCheck) for maximum compatibility.")

if __name__ == "__main__":
    
    # === SIMULACIÓN DE LA CREACIÓN DE CARPETAS Y ARCHIVOS MÍNIMOS REQUERIDOS ===
    
    # Crear directorios
    os.makedirs(XHTML_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(STYLES_DIR, exist_ok=True)
    os.makedirs(FONTS_DIR, exist_ok=True) 

    # 1. Crear Style001.css (Placeholder)
    style_path = os.path.join(STYLES_DIR, "Style001.css")
    if not os.path.exists(style_path):
        with open(style_path, "w") as f:
            f.write("/* Basic Style */ body { font-family: sans-serif; }")
        print(f"Created placeholder style: {style_path}")
        
    # 2. Crear archivo de fuente de prueba
    font_test_path = os.path.join(FONTS_DIR, "roboto-bold-condensed.ttf")
    if not os.path.exists(font_test_path):
        # Creamos un archivo de fuente placeholder vacío si no existe
        Path(font_test_path).touch()
        print(f"Created placeholder font file: {font_test_path}")

    # 3. Crear cover.jpg (Placeholder)
    cover_output_path = os.path.join(IMAGES_DIR, COVER_IMAGE_FILENAME)
    if not os.path.exists(cover_output_path):
        try:
            img = Image.new("RGB", (1600, 2560), "black")
            img.save(cover_output_path, "JPEG")
            print(f"Created placeholder image: {cover_output_path}")
        except ImportError:
            with open(cover_output_path, "w") as f:
                f.write(" ")
            print(f"Created empty placeholder file: {cover_output_path} (Requires PIL for a real image)")
    
    # 4. Crear archivos XHTML mínimos (Placeholders)
    # NOTE: Estos placeholders son los que se leen para crear el TOC.
    placeholder_xhtmls = [
        (COVER_XHTML_FILENAME, "Cover Page", '<h1>Cover</h1>'), # Portada
        (f"{FILE_PREFIX}_0002.xhtml", "Metrics Summary", '<h1>Book Metrics Summary</h1>'), # Métricas
        (f"{FILE_PREFIX}_0003.xhtml", "Chapter 1", '<h2>Capítulo 1: La Llegada</h2>'), # Capítulo (h2)
        (f"{FILE_PREFIX}_0004.xhtml", "Section A", '<h3>Sección A: Introducción</h3>'), # Subtema (h3)
        (f"{FILE_PREFIX}_0005.xhtml", "Section B", '<h4>Sección B: Análisis</h4>'), # Sub-subtema (h4)
        (f"{FILE_PREFIX}_0006.xhtml", "Sentence Fragment", '<div>Esta es una línea de fragmento de texto.</div>'), # Fragmento (DEBE SER IGNORADO)
        ("index.xhtml", "Index", '<h2>Index</h2>') # Índice Visual
    ]

    for filename, title, content_html in placeholder_xhtmls:
        filepath = os.path.join(XHTML_DIR, filename)
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <meta charset="UTF-8"/>
    <title>{title}</title>
    <link rel="stylesheet" href="../Styles/Style001.css" type="text/css"/>
  </head>
  <body>
    <div class="centered">{content_html}</div>
  </body>
</html>''')
            print(f"Created placeholder XHTML: {filepath}")

    # === Ejecución del Empaquetador ===
    pack_to_epub(OUTPUT_EPUB_FILE, XHTML_DIR, IMAGES_DIR, STYLES_DIR, FONTS_DIR, FILE_PREFIX)