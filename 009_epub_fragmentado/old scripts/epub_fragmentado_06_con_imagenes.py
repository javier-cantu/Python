import os
import html
import re

# === CONFIGURATION ===
input_file = "input.txt"
output_folder = "xhtmls_sequences"
images_folder = "Images"
file_prefix = "Siren_fandom_wiki"
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

toc_entries = []
missing_images = []

# === Write cover page ===
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
        section_title = line[1:-1]
        level_titles = section_title.split(" > ")
        current_level = len(level_titles)
        tag = min(current_level, 6)
        current_title = level_titles[-1]
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
            if i == len(paragraph_buffer) - 1:
                sentence += " ❖"
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
    <div class="centered">{html.escape(sentence)}</div>
  </body>
</html>''')
            counter += 1
        paragraph_buffer = []

    else:
        paragraph_buffer.append(line)

# === Write index.xhtml ===
index_file = os.path.join(output_folder, "index.xhtml")
with open(index_file, "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">\n')
    f.write('  <head>\n')
    f.write('    <meta charset="UTF-8"/>\n')
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
                f.write(f'<a href="{link}">{html.escape(key)}</a>')
            else:
                f.write(f"{html.escape(key)}")
            deeper = [e for e in subentries if len(e["levels"]) > depth + 1]
            if deeper:
                write_toc(deeper, depth + 1)
            f.write("</li>\n")
        f.write("      " + "  " * depth + "</ul>\n")

    write_toc(toc_entries)

    f.write('    </div>\n')
    f.write('  </body>\n')
    f.write('</html>\n')

if missing_images:
    print("\n❌ Missing image files:")
    for img in missing_images:
        print(f" - {img}")
else:
    print("✅ All image references verified.")

print("✅ XHTML files generated using EPUB 3-compatible headers and full alt attributes.")
