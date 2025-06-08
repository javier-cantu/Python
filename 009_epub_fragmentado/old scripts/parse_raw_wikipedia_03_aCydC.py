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

# === Abbreviation substitutions to protect them from breaking ===
abbrev_replacements = {
    "a. C.": "a__DOT__C__DOT__",
    "d. C.": "d__DOT__C__DOT__",
    "c. ": "c__DOT__ ",
    "e.g. ": "e__DOT__g__DOT__ ",
    "i.e. ": "i__DOT__e__DOT__ ",
    "etc. ": "etc__DOT__ ",
    "S. A.": "S__DOT__A__DOT__",
    # Add more as needed
}

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

        # Apply abbreviation protections
        for original, protected in abbrev_replacements.items():
            line = line.replace(original, protected)

        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', line)

        # Restore protected abbreviations
        restored_sentences = []
        for s in sentences:
            for original, protected in abbrev_replacements.items():
                s = s.replace(protected, original)
            restored_sentences.append(s)

        # Output sentences
        for sentence in restored_sentences:
            if sentence:
                output_lines.append(sentence.strip())

        # Mark end of paragraph
        output_lines.append("===")

# === Save result ===
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"✅ Done. Output saved to {output_file}")
