import re
import os
from typing import Tuple, List

# === BASE CONFIGURATION ===
input_file = "raw_content.txt"  # Raw input source
output_dir = "epub_parts"       # Target output directory
output_file_name = "input01.txt" # Standardized output filename
output_file = os.path.join(output_dir, output_file_name)

# --- Protection Lists and Placeholders (Remains identical) ---

# Common abbreviations
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

# Professional titles
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

# Acronyms with periods
acronyms = {
    "O.W.L.": "O__DOT__W__DOT__L__DOT__", 
    "D.A.": "D__DOT__A__DOT__", 
    "N.E.W.T.": "N__DOT__E__DOT__W__DOT__T__DOT__", 
    "S.P.E.W.": "S__DOT__P__DOT__E__DOT__W__DOT__", 
    "R.A.B." : "R__DOT__A__DOT__B__DOT__", 
    "L.A.": "L__DOT__A__DOT__", 
    "U.S.A.": "U__DOT__S__DOT__A__DOT__", 
}
# Sort acronyms by length descending to prevent partial matching
sorted_acronyms = sorted(acronyms.items(), key=lambda item: len(item[0]), reverse=True)


# === HELPER FUNCTION: Separate Header and Content ===
def split_header_and_content(file_path: str) -> Tuple[str, List[str]]:
    """Reads the file, separates metadata header from main content."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            full_content = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{file_path}' not found.")
        exit()

    header_delimiter = "=== START OF CONTENT ==="
    
    if header_delimiter not in full_content:
        # If no header is found, treat everything as content
        print("Warning: Header delimiter not found. Processing entire file as content.")
        header_block = ""
        content_block = full_content
    else:
        # Standard separation
        header_block, content_block = full_content.split(header_delimiter, 1)
        # Include delimiter back in header for the output file
        header_block += header_delimiter + "\n"

    # Clean lines from the content block
    raw_lines = [line.strip() for line in content_block.split('\n') if line.strip()]
    
    return header_block, raw_lines


# === Initialization ===
full_header, raw_lines = split_header_and_content(input_file)
os.makedirs(output_dir, exist_ok=True)

output_lines = []
current_levels = {}

# === Main Processing Loop ===
for line in raw_lines:

    # --- Title and Subtitle handling ---
    if line.lower().startswith("title:"):
        output_lines.append("title: " + line[6:].strip())

    elif line.lower().startswith("subtitle:"):
        output_lines.append("subtitle: " + line[9:].strip())

    # --- Hierarchy levels handling ---
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

    # --- Image handling ---
    elif line.lower().startswith("@img:"):
        output_lines.append(line)
        output_lines.append("===")

    # --- Paragraph processing (Sentence Splitting) ---
    else:
        # Clean references and invisible characters
        line = re.sub(r"\[\d+\]", "", line)
        line = re.sub(r"\[citation needed\]", "", line, flags=re.IGNORECASE)
        line = line.replace('\u200b', '').replace('\u200c', '')

        # STEP 0: Protect list numbers (e.g., "1.", "2.")
        line = re.sub(r'^\s*(\d+)\.\s*', r'\1__NUMDOT__ ', line)

        # STEP 1: Normalize ellipsis patterns
        line = re.sub(r'\.\s*\.\s*\.\s*\.', '...', line)
        line = re.sub(r'\.{4,}', '...', line)
        line = re.sub(r'\u2026', '...', line)

        # STEP 2: Protect abbreviations, titles, and acronyms
        line = re.sub(r'([A-Z])\.\s+([A-ZÁÉÍÓÚÑ][a-zA-ZáéíóúñÁÉÍÓÚÑ]+)', r'\1__INITIALDOT__ \2', line)

        for k, v in abbreviations.items():
            line = line.replace(k, v)

        for k, v in titles.items():
            line = line.replace(k, v)

        for k, v in sorted_acronyms:
            line = line.replace(k, v)

        # STEP 3: Protect normalized ellipsis
        line = re.sub(r"\s*\.\s*\.\s*\.\s*", " [ELLIPSIS] ", line)

        # --- CRITICAL IMPROVEMENT: DIALOGUE SPLIT LOGIC ---
        # We don't split if punctuation is immediately followed by a closing quote or bracket.
        # We only split if followed by space and then an uppercase letter or start of a quote.
        line = re.sub(
            r'([.!?])\s+(?=[A-ZÁÉÍÓÚÑ“"\'\s])', 
            r'\1__SPLIT_MARKER__', 
            line
        )

        # Mark end of line/paragraph to ensure final cuts
        line = re.sub(r'([.!?])(["”\'\]]?)$', r'\1\2__SPLIT_MARKER__', line)
        
        # Split sentences using the unique marker
        sentences = [s.strip() for s in line.split('__SPLIT_MARKER__') if s.strip()]

        # STEP 4: Restore protections
        restored_sentences = []
        for s in sentences:
            for k, v in abbreviations.items():
                s = s.replace(v, k)

            for k, v in titles.items():
                s = s.replace(v, k)

            for k, v in sorted_acronyms:
                s = s.replace(v, k)
            
            s = re.sub(r'__INITIALDOT__\s*', r'. ', s) 
            s = s.replace("[ELLIPSIS]", "...")
            s = re.sub(r'(\d+)__NUMDOT__\s*', r'\1. ', s)

            restored_sentences.append(s.strip())

        # --- DIALOGUE UNIFICATION LOGIC ---
        for sentence in restored_sentences:
            if sentence:
                # If sentence starts with closing quote/bracket, or is just a single quote,
                # merge it with the last line in output_lines to prevent orphan punctuation.
                if sentence[0] in ["'", '"', "”", "’", "]", ")"] and output_lines and output_lines[-1] != "===":
                    prev_line = output_lines.pop()
                    output_lines.append(prev_line + " " + sentence)
                else:
                    output_lines.append(sentence.strip())

        output_lines.append("===")

# --- Handle Loose Separators (e.g., "• • •") ---
if output_lines and output_lines[-1] == "===":
    if raw_lines and raw_lines[-1].strip() == "• • •": 
        output_lines.pop()
        output_lines.append(raw_lines[-1].strip())
        output_lines.append("===")

# === Save Results ===
with open(output_file, "w", encoding="utf-8") as f:
    # 1. Write the full metadata header
    f.write(full_header) 
    
    # 2. Write processed content (one sentence per line)
    f.write("\n".join(output_lines))
    f.write("\n") # Final newline for cleanliness
    

print(f"✅ Preprocessing complete. File saved to {output_file}")