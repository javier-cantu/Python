# === Wikipedia/Text to Sentence-per-Line Preprocessor ===
#
# 📘 Descripción:
# Este script convierte un archivo de texto largo (estilo Wikipedia o novela) 
# en otro archivo donde cada oración aparece en una línea separada.
# Las líneas vacías o divisores de párrafos se marcan con `===`.
#
# ✅ Características:
# - Detecta títulos, subtítulos y niveles jerárquicos (#level1:, #level2:, etc.)
# - Soporta imágenes con líneas como: @img: archivo.jpg | descripción
# - Divide oraciones correctamente incluso si hay:
#   - Puntos suspensivos (`...`)
#   - Abreviaciones con punto (`e.g.`, `Mr.`, `Dr.`)
# - Limpia referencias como `[1]` y `[citation needed]`
#
# ⚠️ Limitaciones:
# - No detecta oraciones si no terminan en `.`, `?`, `!`
# - Puede fallar si las abreviaturas no están en la lista predefinida
#
# 🛠 Cómo extender:
# - Agrega más abreviaciones a `titles` si lo necesitas
# - Puedes usar expresiones regulares más avanzadas para contextos específicos
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
        line = re.sub(r"\[\d+\]", "", line)
        line = re.sub(r"\[citation needed\]", "", line, flags=re.IGNORECASE)
        line = line.replace('\u200b', '').replace('\u200c', '')

        # Abreviaciones y títulos protegidos
        line = line.replace("c. ", "c__DOT__ ")
        line = line.replace("e.g. ", "e__DOT__g__DOT__ ")
        line = line.replace("i.e. ", "i__DOT__e__DOT__ ")
        line = line.replace("etc. ", "etc__DOT__ ")
        line = line.replace("a. C.", "a__DOT__C__DOT__")
        line = line.replace("d. C.", "d__DOT__C__DOT__")

        # Proteger títulos como Mr., Dr., etc.
        titles = {
            "Mr.": "Mr__DOT__",
            "Mrs.": "Mrs__DOT__",
            "Ms.": "Ms__DOT__",
            "Dr.": "Dr__DOT__",
            "Prof.": "Prof__DOT__",
            "Sr.": "Sr__DOT__",
            "Jr.": "Jr__DOT__"
        }
        for k, v in titles.items():
            line = line.replace(k, v)

        # Proteger puntos suspensivos
        line = re.sub(r"\s*\.\s*\.\s*\.\s*", " [ELLIPSIS] ", line)

        # Normalizar espacio después de punto si hay mayúscula (ayuda a dividir)
        line = re.sub(r'([.!?])\s*([A-ZÁÉÍÓÚÑ])', r'\1 \2', line)

        # Separar en oraciones
        sentences = re.split(r'(?<=[.!?])\s+', line)

        # Restaurar abreviaciones y títulos
        restored_sentences = []
        for s in sentences:
            s = s.replace("a__DOT__C__DOT__", "a. C.")
            s = s.replace("d__DOT__C__DOT__", "d. C.")
            s = s.replace("c__DOT__", "c.")
            s = s.replace("e__DOT__g__DOT__", "e.g.")
            s = s.replace("i__DOT__e__DOT__", "i.e.")
            s = s.replace("etc__DOT__", "etc.")
            s = s.replace("[ELLIPSIS]", "...")
            for k, v in titles.items():
                s = s.replace(v, k)
            restored_sentences.append(s)

        # Agregar al output
        for sentence in restored_sentences:
            if sentence:
                output_lines.append(sentence.strip())

        output_lines.append("===")

# === Guardar resultado ===
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"✅ Done. Output saved to {output_file}")
