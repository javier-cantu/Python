import os

# === CONFIGURATION ===
input_file = "input.txt"
output_folder = "xhtmls_sequences"
file_prefix = "Wikipedia_Philosophy"  # Change per article/chapter
start_index = 1

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

# === Prepare output folder ===
os.makedirs(output_folder, exist_ok=True)

# === Track TOC as list of dicts
toc_entries = []

# === Write cover page ===
cover_filename = f"{file_prefix}_{str(start_index).zfill(4)}.xhtml"
with open(os.path.join(output_folder, cover_filename), "w", encoding="utf-8") as f:
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
      <p><a href="index.xhtml">Go to Index</a></p>
    </div>
  </body>
</html>''')

# === Process the content ===
counter = start_index + 1
paragraph_buffer = []

for line in content_lines:
    # Section header like [History > Western > Ancient]
    if line.startswith("[") and line.endswith("]"):
        section_title = line[1:-1]
        level_titles = section_title.split(" > ")

        # Generate HTML header structure
        html_hierarchy = ""
        for i, title in enumerate(level_titles):
            tag = min(i + 1, 6)
            html_hierarchy += f"<h{tag}>{title}</h{tag}>\n"

        filename = f"{file_prefix}_{str(counter).zfill(4)}.xhtml"
        with open(os.path.join(output_folder, filename), "w", encoding="utf-8") as f:
            f.write(f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>{level_titles[-1]}</title>
    <link rel="stylesheet" href="../Styles/Style001.css" type="text/css"/>
  </head>
  <body>
    <div class="context">
      {html_hierarchy.strip()}
    </div>
  </body>
</html>''')

        # Save full hierarchy to TOC
        toc_entries.append({
            "levels": level_titles,
            "file": filename
        })
        counter += 1

    # End of paragraph
    elif line == "===":
        for i, sentence in enumerate(paragraph_buffer):
            if i == len(paragraph_buffer) - 1:
                sentence += " ❖"
            filename = f"{file_prefix}_{str(counter).zfill(4)}.xhtml"
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
    <div class="centered">{sentence}</div>
  </body>
</html>''')
            counter += 1
        paragraph_buffer = []

    # Regular sentence
    else:
        paragraph_buffer.append(line)

# === Write index.xhtml as nested list ===
index_file = os.path.join(output_folder, "index.xhtml")

with open(index_file, "w", encoding="utf-8") as f:
    f.write('''<?xml version="1.0" encoding="utf-8"?>\n''')
    f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"\n')
    f.write('  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n')
    f.write('<html xmlns="http://www.w3.org/1999/xhtml">\n')
    f.write('  <head>\n')
    f.write('    <title>Index</title>\n')
    f.write('    <link rel="stylesheet" href="../Styles/Style001.css" type="text/css"/>\n')
    f.write('  </head>\n')
    f.write('  <body>\n')
    f.write('    <div class="centered">\n')
    f.write('      <h2>Index</h2>\n')

    def write_toc(entries, depth=0):
        current_level = {}
        for entry in entries:
            key = entry["levels"][depth]
            if key not in current_level:
                current_level[key] = []
            current_level[key].append(entry)

        f.write("      " + "  " * depth + "<ul>\n")
        for key, subentries in current_level.items():
            item = subentries[0]
            link = item["file"] if depth + 1 == len(item["levels"]) else None

            f.write("      " + "  " * (depth + 1) + "<li>")
            if link:
                f.write(f'<a href="{link}">{key}</a>')
            else:
                f.write(f"{key}")
            # Si hay más niveles, seguir anidando
            deeper = [e for e in subentries if len(e["levels"]) > depth + 1]
            if deeper:
                write_toc(deeper, depth + 1)
            f.write("</li>\n")
        f.write("      " + "  " * depth + "</ul>\n")

    write_toc(toc_entries)

    f.write('    </div>\n')
    f.write('  </body>\n')
    f.write('</html>\n')

print("✅ XHTML files generated, including index.xhtml with nested structure.")
