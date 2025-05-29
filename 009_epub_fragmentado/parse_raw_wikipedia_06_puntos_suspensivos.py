# === Parse Wikipedia Text to Sentence-per-Line Format ===
#
# Now with image support via lines like:
# @img: filename.jpg | caption text
#
# These will be preserved as-is in input.txt with paragraph breaks (===).

import re

# === CONFIGURATION ===
input_file = "raw_wikipedia.txt"
output_file = "input.txt"

# === Load and clean input ===
with open(input_file, "r", encoding="utf-8") as f:
    raw_lines = [line.strip() for line in f if line.strip()]

output_lines = []
current_levels = {}

# === Process each line ===
for line in raw_lines:

    # --- Title and subtitle ---
    if line.lower().startswith("title:"):
        output_lines.append("title: " + line[6:].strip())

    elif line.lower().startswith("subtitle:"):
        output_lines.append("subtitle: " + line[9:].strip())

    # --- Section levels ---
    elif line.lower().startswith("#level"):
        match = re.match(r"#level(\d+):\s*(.+)", line, re.IGNORECASE)
        if match:
            level = int(match.group(1))
            title = match.group(2).strip()
            current_levels[level] = title

            # Clear deeper levels
            for key in list(current_levels.keys()):
                if key > level:
                    del current_levels[key]

            # Build hierarchy
            hierarchy = " > ".join(current_levels[i] for i in sorted(current_levels))
            output_lines.append(f"[{hierarchy}]")
            output_lines.append("===")

    # --- Image line (@img: file.jpg | alt text) ---
    elif line.lower().startswith("@img:"):
        output_lines.append(line)
        output_lines.append("===")

    # --- Regular paragraph ---
    else:
        line = re.sub(r"\[\d+\]", "", line)
        line = re.sub(r"\[citation needed\]", "", line, flags=re.IGNORECASE)
        line = line.replace('\u200b', '').replace('\u200c', '')

        # Escape abbreviations
        line = line.replace("c. ", "c__DOT__ ")
        line = line.replace("e.g. ", "e__DOT__g__DOT__ ")
        line = line.replace("i.e. ", "i__DOT__e__DOT__ ")
        line = line.replace("etc. ", "etc__DOT__ ")
        line = line.replace("a. C.", "a__DOT__C__DOT__")
        line = line.replace("d. C.", "d__DOT__C__DOT__")

        # Protect ellipses
        line = line.replace(". . .", "[ELLIPSIS]")
        line = line.replace("...", "[ELLIPSIS]")

        # Sentence boundary fix
        line = re.sub(r'([.!?])\s*([A-ZÁÉÍÓÚÑ])', r'\1 \2', line)

        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', line)

        # Unescape everything
        sentences = [s.replace("a__DOT__C__DOT__", "a. C.")
                       .replace("d__DOT__C__DOT__", "d. C.")
                       .replace("c__DOT__", "c.")
                       .replace("e__DOT__g__DOT__", "e.g.")
                       .replace("i__DOT__e__DOT__", "i.e.")
                       .replace("etc__DOT__", "etc.")
                       .replace("[ELLIPSIS]", "...")
                    for s in sentences]

        for sentence in sentences:
            if sentence:
                output_lines.append(sentence.strip())

        output_lines.append("===")

# === Save result ===
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"✅ Done. Output saved to {output_file}")
