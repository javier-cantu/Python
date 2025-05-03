import os

# === CONFIGURACIÓN ===
input_file = "input.txt"
output_folder = "xhtmls_sequences"
file_prefix = "lovecraft_ch07"  # ← CAMBIA ESTO SEGÚN EL CUENTO O CAPÍTULO
start_index = 1

# === LEER Y PROCESAR EL ARCHIVO DE ENTRADA ===
with open(input_file, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip() != ""]

# === DETECTAR TÍTULO Y SUBTÍTULO ===
book_title = ""
book_intro = ""
content_start = 0

for i, line in enumerate(lines):
    if line.lower().startswith("titulo:"):
        book_title = line[len("titulo:"):].strip()
    elif line.lower().startswith("subtitulo:"):
        book_intro = line[len("subtitulo:"):].strip()
    else:
        content_start = i
        break

content_lines = lines[content_start:]

# === CREAR CARPETA DE SALIDA ===
os.makedirs(output_folder, exist_ok=True)

# === GENERAR ARCHIVO DE PORTADA ===
filename = f"{file_prefix}_{str(start_index).zfill(4)}.xhtml"
with open(os.path.join(output_folder, filename), "w", encoding="utf-8") as f:
    f.write(f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>{book_title}</title>
    <link rel="stylesheet" href="../Styles/Style001.css" type="text/css"/>
  </head>
  <body>
    <div class="centered">
      <h2>{book_title}</h2>
      <p>{book_intro}</p>
    </div>
  </body>
</html>''')

# === PROCESAR ENUNCIADOS CON SOPORTE PARA [ ... ] ===
counter = start_index + 1
paragraph_buffer = []
inside_block = False
block_lines = []

for line in content_lines:
    if line == "[":
        inside_block = True
        block_lines = []
    elif line == "]":
        inside_block = False
        paragraph_buffer.append("<br/>".join(block_lines))
    elif inside_block:
        block_lines.append(line)
    elif line == "===":
        for i, enunciado in enumerate(paragraph_buffer):
            if i == len(paragraph_buffer) - 1:
                enunciado += " ❖"

            filename = f"{file_prefix}_{str(counter).zfill(4)}.xhtml"
            with open(os.path.join(output_folder, filename), "w", encoding="utf-8") as f_out:
                f_out.write(f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>{book_title}</title>
    <link rel="stylesheet" href="../Styles/Style001.css" type="text/css"/>
  </head>
  <body>
    <div class="centered">{enunciado}</div>
  </body>
</html>''')
            counter += 1
        paragraph_buffer = []
    else:
        paragraph_buffer.append(line)
