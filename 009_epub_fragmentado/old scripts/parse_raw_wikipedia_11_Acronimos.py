# === Wikipedia/Text to Sentence-per-Line Preprocessor ===
#
# 📘 Descripción:
# Este script está diseñado para procesar archivos de texto largos (por ejemplo, novelas o artículos de Wikipedia)
# y transformarlos en un formato donde cada oración aparece en una línea separada.
# Las líneas vacías o los marcadores de fin de párrafo se indican con `===`.
#
# ✅ Características Mejoradas:
# - Detecta y extrae títulos, subtítulos y jerarquías de secciones (#level1:, #level2:, etc.).
# - Soporta la inclusión de imágenes con líneas como: @img: archivo.jpg | descripción.
# - **Manejo robusto de puntos suspensivos:**
#   - Normaliza patrones inusuales (ej. ". . . .", "....", "...") a un formato estándar de "..." .
#   - Protege los puntos suspensivos para que NO sean interpretados como finales de oración.
# - **Manejo avanzado de abreviaciones:**
#   - Protege abreviaciones comunes (ej. "e.g.", "Mr.", "Dr.", "etc.") para evitar divisiones incorrectas.
#   - Manejo de puntos en listas numeradas (ej. "1. Item") para evitar divisiones.
#   - **Nuevo: Protección de acrónimos con puntos (ej. "O.W.L.", "U.S.A.") para mantenerlos intactos.**
# - Limpia referencias textuales como `[1]` y `[citation needed]`.
#
# ⚠️ Limitaciones:
# - Puede no detectar oraciones si no terminan explícitamente en un punto (`.`), signo de interrogación (`?`) o exclamación (`!`).
# - El éxito de la protección de abreviaturas y acrónimos depende de la lista predefinida; es posible que se necesiten añadir más.
#
# 🛠 Cómo extender:
# - Agrega más abreviaciones, títulos o acrónimos a las listas correspondientes según sea necesario.
# - Utiliza expresiones regulares más avanzadas para contextos de texto muy específicos.
#
# === CONFIGURACIÓN ===

import re

input_file = "raw_wikipedia.txt"
output_file = "input.txt"

# === Cargar y limpiar texto ===
with open(input_file, "r", encoding="utf-8") as f:
    raw_lines = [line.strip() for line in f if line.strip()]

output_lines = []
current_levels = {}

# === Procesar cada línea ===
for line in raw_lines:

    # --- Títulos y subtítulos ---
    if line.lower().startswith("title:"):
        output_lines.append("title: " + line[6:].strip())

    elif line.lower().startswith("subtitle:"):
        output_lines.append("subtitle: " + line[9:].strip())

    # --- Jerarquía de secciones ---
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

    # --- Imágenes ---
    elif line.lower().startswith("@img:"):
        output_lines.append(line)
        output_lines.append("===")

    # --- Párrafos normales ---
    else:
        # Limpiar referencias y caracteres invisibles primero
        line = re.sub(r"\[\d+\]", "", line)
        line = re.sub(r"\[citation needed\]", "", line, flags=re.IGNORECASE)
        line = line.replace('\u200b', '').replace('\u200c', '')

        # --- COMIENZO DEL PROCESAMIENTO AVANZADO DE TEXTO ---

        # PASO 0: Proteger números de lista (ej. "1.", "2.", etc.)
        # Esto debe hacerse ANTES de cualquier otra normalización o protección de puntos.
        line = re.sub(r'^\s*(\d+)\.\s*', r'\1__NUMDOT__ ', line)

        # PASO 1: Normalizar patrones de puntos suspensivos *antes* de protegerlos.
        line = re.sub(r'\.\s*\.\s*\.\s*\.', '...', line)  # Normaliza ". . . ." a "..."
        line = re.sub(r'\.{4,}', '...', line)  # Normaliza "...." a "..."
        line = re.sub(r'\u2026', '...', line)  # Normaliza el carácter de ellipsis Unicode (…) a "..."

        # PASO 2: Proteger abreviaciones, títulos Y ACRÓNIMOS.
        # Estas deben ser protegidas *antes* de los puntos suspensivos genéricos.
        # Abrevaciones comunes (con punto)
        abbreviations = {
            "c.": "c__DOT__",
            "e.g.": "e__DOT__g__DOT__",
            "i.e.": "i__DOT__e__DOT__",
            "etc.": "etc__DOT__",
            "a. C.": "a__DOT__C__DOT__",
            "d. C.": "d__DOT__C__DOT__",
            "P.M.": "P__DOT__M__DOT__",
            "A.M.": "A__DOT__M__DOT__"
        }
        for k, v in abbreviations.items():
            line = line.replace(k, v)

        # Títulos como Mr., Dr., etc.
        titles = {
            "Mr.": "Mr__DOT__",
            "Mrs.": "Mrs__DOT__",
            "Ms.": "Ms__DOT__",
            "Dr.": "Dr__DOT__",
            "Prof.": "Prof__DOT__",
            "Sr.": "Sr__DOT__",
            "Jr.": "Jr__DOT__",
            "St.": "St__DOT__"
        }
        for k, v in titles.items():
            line = line.replace(k, v)

        # NUEVO: Acrónimos con puntos (ej. O.W.L., U.S.A.)
        # Asegúrate de listar aquí los acrónimos exactos como aparecen en tu texto
        acronyms = {
            "O.W.L.": "O__DOT__W__DOT__L__DOT__",
            "U.S.A.": "U__DOT__S__DOT__A__DOT__",
            # Agrega más acrónimos con puntos aquí si los encuentras en tu texto
        }
        # Es importante reemplazar de la forma más larga a la más corta para evitar problemas
        # con acrónimos anidados (ej. "U.S.A." antes que "U.S.").
        for k, v in sorted(acronyms.items(), key=lambda item: len(item[0]), reverse=True):
            line = line.replace(k, v)

        # PASO 3: Proteger los puntos suspensivos normalizados
        line = re.sub(r"\s*\.\s*\.\s*\.\s*", " [ELLIPSIS] ", line)

        # Normalizar espacio después de punto/signo de interrogación/exclamación si hay mayúscula (ayuda a dividir)
        line = re.sub(r'([.!?])\s*([A-ZÁÉÍÓÚÑ])', r'\1 \2', line)

        # Separar en oraciones
        sentences = re.split(r'(?<=[.!?])\s+', line)

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
            for k, v in sorted(acronyms.items(), key=lambda item: len(item[0]), reverse=True):
                s = s.replace(v, k)
            
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

# === Guardar resultado ===
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"✅ Done. Output saved to {output_file}")