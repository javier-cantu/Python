# === Parse Wikipedia Text to Sentence-per-Line Format ===
# 
# This script processes a raw Wikipedia-like article text (`raw_wikipedia.txt`) and converts it into
# a structured output file (`input.txt`). The goal is to split the text into individual sentences
# for each screen or EPUB page, and insert markers (`===`) to indicate paragraph breaks.
#
# Headings like #level1, #level2, etc. are interpreted as section markers and are transformed
# into visual hierarchy markers ([A > B > C]) followed by a paragraph break.
#
# Special handling is included to:
# - Remove citation numbers like [1], [2], or [citation needed]
# - Preserve common abbreviations like "c.", "e.g.", "i.e.", "etc."
# - Preserve era markers like "a. C." and "d. C." used in historical dates
# - Clean invisible characters
# - Avoid splitting sentences incorrectly due to formatting issues

import re

# === CONFIGURATION ===
input_file = "raw_wikipedia.txt"   # Input file with #levelX and paragraphs
output_file = "input.txt"          # Output file with one sentence per line

# === Load input lines, stripping blanks ===
with open(input_file, "r", encoding="utf-8") as f:
    raw_lines = [line.strip() for line in f if line.strip()]

# === Prepare output and track active section levels ===
output_lines = []
current_levels = {}

# === Process each line ===
for line in raw_lines:
    # --- Handle title and subtitle ---
    if line.lower().startswith("title:"):
        output_lines.append("title: " + line[6:].strip())
    elif line.lower().startswith("subtitle:"):
        output_lines.append("subtitle: " + line[9:].strip())

    # --- Handle level headings like #level2: Western ---
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

            # Build hierarchy display
            hierarchy = " > ".join(current_levels[i] for i in sorted(current_levels))
            output_lines.append(f"[{hierarchy}]")
            output_lines.append("===")

    # --- Handle regular paragraphs ---
    else:
        # Remove [1], [23], [citation needed]
        line = re.sub(r"\[\d+\]", "", line)
        line = re.sub(r"\[citation needed\]", "", line, flags=re.IGNORECASE)

        # Clean invisible characters and fix malformed punctuation
        line = line.replace('\u200b', '')  # Zero-width space
        line = line.replace('\u200c', '')  # Zero-width non-joiner

        # Protect common abbreviations
        line = line.replace("c. ", "c__DOT__ ")
        line = line.replace("e.g. ", "e__DOT__g__DOT__ ")
        line = line.replace("i.e. ", "i__DOT__e__DOT__ ")
        line = line.replace("etc. ", "etc__DOT__ ")

        # Protect era markers like "a. C." and "d. C."
        line = line.replace("a. C.", "a__DOT__C__DOT__")
        line = line.replace("d. C.", "d__DOT__C__DOT__")

        # Ensure proper punctuation spacing before capital letters
        line = re.sub(r'([.!?])\s*([A-ZÁÉÍÓÚÑ])', r'\1 \2', line)

        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', line)

        # Restore protected dots
        sentences = [s.replace("a__DOT__C__DOT__", "a. C.")
                       .replace("d__DOT__C__DOT__", "d. C.")
                       .replace("c__DOT__", "c.")
                       .replace("e__DOT__g__DOT__", "e.g.")
                       .replace("i__DOT__e__DOT__", "i.e.")
                       .replace("etc__DOT__", "etc.")
                    for s in sentences]

        # Output sentences
        for sentence in sentences:
            if sentence:
                output_lines.append(sentence.strip())

        # Mark end of paragraph
        output_lines.append("===")

# === Save result ===
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"✅ Done. Output saved to {output_file}")
