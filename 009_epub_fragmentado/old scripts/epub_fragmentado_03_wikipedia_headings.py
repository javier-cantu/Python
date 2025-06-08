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
    </div>
  </body>
</html>''')

# === Process the content ===
counter = start_index + 1
paragraph_buffer = []

for line in content_lines:
    # Section transition line like: [History > Western > Ancient]
    if line.startswith("[") and line.endswith("]"):
        section_title = line[1:-1]  # Remove brackets
        level_titles = section_title.split(" > ")

        # Create one <hX> per level
        html_hierarchy = ""
        for i, title in enumerate(level_titles):
            tag = min(i + 1, 6)  # h1 to h6
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
        counter += 1

    # Paragraph break
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

    # Sentence line
    else:
        paragraph_buffer.append(line)
