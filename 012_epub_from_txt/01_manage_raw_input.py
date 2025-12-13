import re
import os
from typing import Tuple, List

# === CONFIGURACIÓN BASE ===
input_file = "raw_content.txt"  # Nuevo nombre de archivo de entrada
output_dir = "epub_parts"       # Carpeta de salida requerida
output_file_name = "input01.txt" # Nombre de archivo de salida requerido
output_file = os.path.join(output_dir, output_file_name)

# --- Definición de Placeholders y Listas de Protección (Se mantienen igual) ---

# Abrevaciones comunes (con punto)
abbreviations = {
    "c.": "c__DOT__",
    "e.g.": "e__DOT__g__DOT__",
    "i.e.": "i__DOT__e__DOT__",
    "etc.": "etc__DOT__",
    "a. C.": "a__DOT__C__DOT__",
    "d. C.": "d__DOT__C__DOT__",
    "P.M.": "P__DOT__M__DOT__",
    "A.M.": "A__DOT__M__DOT__",
    "P.S.": "P__DOT__S__DOT__",
    "U.S.": "U__DOT__S__DOT__",
    "vs.": "vs__DOT__", # The stand vs.
}

# Títulos como Mr., Dr., etc.
titles = {
    "Mr.": "Mr__DOT__",
    "Mrs.": "Mrs__DOT__",
    "Ms.": "Ms__DOT__",
    "Dr.": "Dr__DOT__",
    "Prof.": "Prof__DOT__",
    "Sr.": "Sr__DOT__",
    "Jr.": "Jr__DOT__",
    "St.": "St__DOT__",
}

# Acrónimos con puntos
acronyms = {
    "O.W.L.": "O__DOT__W__DOT__L__DOT__", 
    "D.A.": "D__DOT__A__DOT__", 
    "N.E.W.T.": "N__DOT__E__DOT__W__DOT__T__DOT__", 
    "S.P.E.W.": "S__DOT__P__DOT__E__DOT__W__DOT__", 
    "R.A.B." : "R__DOT__A__DOT__B__DOT__", 
    "L.A.": "L__DOT__A__DOT__", 
    "U.S.A.": "U__DOT__S__DOT__A__DOT__", 
}
# Ordenar acrónimos de mayor a menor longitud
sorted_acronyms = sorted(acronyms.items(), key=lambda item: len(item[0]), reverse=True)


# === NUEVA FUNCIÓN: Separar Header y Contenido ===
def split_header_and_content(file_path: str) -> Tuple[str, List[str]]:
    """Lee el archivo, separa el Header del Contenido y devuelve ambos bloques."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            full_content = f.read()
    except FileNotFoundError:
        print(f"Error: El archivo de entrada '{file_path}' no fue encontrado.")
        exit()

    header_delimiter = "=== START OF CONTENT ==="
    
    if header_delimiter not in full_content:
        # Si no hay header, todo es contenido
        print("Advertencia: No se encontró el delimitador de Header. Procesando todo el archivo como contenido.")
        header_block = ""
        content_block = full_content
    else:
        # Separación estándar del header y el contenido
        header_block, content_block = full_content.split(header_delimiter, 1)
        # Incluir el delimitador de vuelta en el header para la salida
        header_block += header_delimiter + "\n"

    # Procesar el bloque de contenido en líneas limpias
    raw_lines = [line.strip() for line in content_block.split('\n') if line.strip()]
    
    return header_block, raw_lines


# === Cargar el Header y el Contenido de Entrada ===
# full_header contendrá el bloque de texto con todos los metadatos y el delimitador.
# raw_lines contendrá solo el contenido a procesar.
full_header, raw_lines = split_header_and_content(input_file)

# Crear la carpeta de salida si no existe
os.makedirs(output_dir, exist_ok=True)


# === Procesamiento Principal del Contenido ===

output_lines = []
current_levels = {}

# === Procesar cada línea de contenido ===
for line in raw_lines:

    # --- Títulos y subtítulos (Se mantienen) ---
    if line.lower().startswith("title:"):
        output_lines.append("title: " + line[6:].strip())

    elif line.lower().startswith("subtitle:"):
        output_lines.append("subtitle: " + line[9:].strip())

    # --- Jerarquía de secciones (Se mantienen) ---
    elif line.lower().startswith("#level"):
        match = re.match(r"#level(\d+):\s*(.+)", line, re.IGNORECASE)
        if match:
            level = int(match.group(1))
            title = match.group(2).strip()
            current_levels[level] = title

            for key in list(current_levels.keys()):
                if key > level:
                    del current_levels[key]

            hierarchy = " > ".join(current_levels[i] for i in sorted(current_levels))
            output_lines.append(f"[{hierarchy}]")
            output_lines.append("===")

    # --- Imágenes (Se mantienen) ---
    elif line.lower().startswith("@img:"):
        output_lines.append(line)
        output_lines.append("===")

    # --- Párrafos normales (Lógica de división de oraciones, se mantiene) ---
    else:
        # Limpiar referencias y caracteres invisibles primero
        line = re.sub(r"\[\d+\]", "", line)
        line = re.sub(r"\[citation needed\]", "", line, flags=re.IGNORECASE)
        line = line.replace('\u200b', '').replace('\u200c', '')

        # --- COMIENZO DEL PROCESAMIENTO AVANZADO DE TEXTO ---

        # PASO 0: Proteger números de lista (ej. "1.", "2.", etc.)
        line = re.sub(r'^\s*(\d+)\.\s*', r'\1__NUMDOT__ ', line)

        # PASO 1: Normalizar patrones de puntos suspensivos *antes* de protegerlos.
        line = re.sub(r'\.\s*\.\s*\.\s*\.', '...', line)
        line = re.sub(r'\.{4,}', '...', line)
        line = re.sub(r'\u2026', '...', line)

        # PASO 2: Proteger abreviaciones, títulos Y ACRÓNIMOS.

        # Protege iniciales en nombres (ej. "H. Keeley")
        line = re.sub(r'([A-Z])\.\s+([A-ZÁÉÍÓÚÑ][a-zA-ZáéíóúñÁÉÍÓÚÑ]+)', r'\1__INITIALDOT__ \2', line)

        # Abrevaciones comunes
        for k, v in abbreviations.items():
            line = line.replace(k, v)

        # Títulos
        for k, v in titles.items():
            line = line.replace(k, v)

        # Acrónimos (ordenados de mayor a menor)
        for k, v in sorted_acronyms:
            line = line.replace(k, v)

        # PASO 3: Proteger los puntos suspensivos normalizados
        line = re.sub(r"\s*\.\s*\.\s*\.\s*", " [ELLIPSIS] ", line)

        # MEJORA CLAVE: Marcar finales de oración para una división precisa.
        # Primer paso: Marcar la mayoría de los casos de final de oración
        line = re.sub(
            r'([.!?])(["”\'\]]?)\s*([“"\'A-ZÁÉÍÓÚÑ])',
            r'\1\2__SPLIT_MARKER__\3',
            line
        )
        # Segundo paso: Marcar casos donde la oración termina al final de la línea/párrafo.
        # Se agrega soporte para el separador "• • •" que no termina con puntuación
        line = re.sub(r'([.!?])(["”\'\]]?)$', r'\1\2__SPLIT_MARKER__', line)
        
        # Separar en oraciones utilizando el marcador único
        sentences = [s.strip() for s in line.split('__SPLIT_MARKER__') if s.strip()]


        # PASO 4: Restaurar abreviaciones, títulos, acrónimos y los puntos suspensivos.
        restored_sentences = []
        for s in sentences:
            # Restaurar abreviaciones comunes
            for k, v in abbreviations.items():
                s = s.replace(v, k)

            # Restaurar títulos
            for k, v in titles.items():
                s = s.replace(v, k)

            # Restaurar acrónimos
            for k, v in sorted_acronyms:
                s = s.replace(v, k)
            
            # Restaurar iniciales en nombres
            s = re.sub(r'__INITIALDOT__\s*', r'. ', s) 

            # Restaurar el placeholder de ellipsis
            s = s.replace("[ELLIPSIS]", "...")

            # Restaurar puntos en números de lista
            s = re.sub(r'(\d+)__NUMDOT__\s*', r'\1. ', s)

            # Eliminar espacios en blanco al inicio y al final de la oración.
            restored_sentences.append(s.strip())

        # Agregar al output
        for sentence in restored_sentences:
            if sentence:
                output_lines.append(sentence.strip())

        output_lines.append("===")

# --- Manejo de Separadores Sueltos (como "• • •") ---
# El "• • •" no es un párrafo ni un encabezado, es un separador.
# Se añade una pequeña corrección para preservar estos marcadores sueltos:
if output_lines and output_lines[-1] == "===":
    if line.strip() == "• • •": # Si el contenido original era solo el separador
        output_lines.pop() # Quita el '===' que se puso al final del bloque 'else'
        output_lines.append(line.strip())
        output_lines.append("===")

# === Guardar resultado ===

with open(output_file, "w", encoding="utf-8") as f:
    # 1. Escribir el HEADER completo (incluyendo el delimitador)
    f.write(full_header) 
    
    # 2. Escribir el Contenido Procesado (oración por línea)
    f.write("\n".join(output_lines))
    f.write("\n") # Asegura un salto de línea final para la limpieza
    

print(f"✅ Done. Output saved to {output_file}")