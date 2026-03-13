# EPUB GENERATION PIPELINE DOCUMENTATION

This document outlines the purpose and execution flow of the custom three-script pipeline designed to convert structured source content into a validated EPUB 3 file, ready for platforms like Google Play Books.

## 1. Overview of the Pipeline

The process takes content from a single, structured source file and transforms it through three distinct stages to produce a correctly formatted and packaged EPUB file.

| Script | Input | Output | Primary Function |
| :--- | :--- | :--- | :--- |
| **01** | `raw_content.txt` | `epub_parts/input01.txt` | **Preprocessing:** Cleans text, handles initial sentence splitting, and preserves metadata. |
| **02** | `epub_parts/input01.txt` | `.xhtml` fragments, `cover.jpg`, `toc_data.json` | **Content Generation:** Creates book assets, cover image, and defines structural hierarchy. |
| **03** | `epub_parts/*` | `[PREFIX].epub` | **Assembly & Packaging:** Builds the EPUB structure and compresses the final container. |

## 2. The Input: `raw_content.txt`

The pipeline starts with this file, which must contain two parts:

* **Metadata Header:** A configuration block at the top (e.g., `TITLE: My Book`, `PREFIX: my_book`). This metadata drives the entire EPUB generation.
* **Structured Content:** The main text, divided into sentences, paragraphs (using `===`), and hierarchy markers (using `[Level 1 > Subtitle]`).

## 3. Stage 1: Preprocessing and Structuring

### `01_manage_raw_input.py`

**Purpose:** To clean and normalize the input text, making it suitable for the HTML fragmentation engine (Script 02).

* **Key Action:** Reads the original `raw_content.txt`. It executes necessary text cleanup (normalizing quotes, spacing, and ellipses) and prepares the content lines.
* **Dialogue & Punctuation Intelligence:** * The script uses advanced Regular Expressions (Regex) to detect sentence boundaries without breaking dialogue. 
    * It ensures that closing quotes (`'`, `"`, `”`) or brackets remains attached to the preceding sentence.
    * It features a **Unification Rule**: If punctuation or a quote is accidentally orphaned on a new line, the script automatically merges it back to the previous sentence to maintain narrative flow.
* **Output:** Creates the file **`epub_parts/input01.txt`**.

## 4. Stage 2: Content and Structure Generation (Traditional Mode)

### `02_section_fragmenter.py`

**Purpose:** This is the core engine, implementing the "Block Fragmentation" strategy. It converts the abstract structure from `input01.txt` into concrete, conventionally structured XHTML files.

* **Metadata & Cover:** It extracts the book's metadata (Title, Author, Prefix) and uses it to generate the custom **`cover.jpg`** image.
* **Fragment Logic (Traditional):** The script enforces a hierarchical fragmentation rule:
    * It treats **Level 1** and **Level 2** markers as **new file boundaries**.
    * All content (Level 3+ headings, images, and paragraphs) falling between two L1/L2 markers is grouped into a **single XHTML file**.
* **Content Rendering:** It converts internal paragraph breaks (`===`) into HTML `<p>` tags, and L3+ headers are converted into appropriate internal tags (`<h3>`, `<h4>`, etc.).
* **Output:**
    * Multiple XHTML files in **`epub_parts/`** (fewer, larger files).
    * **`Images/cover.jpg`**.
    * **`epub_parts/toc_data.json`**: A JSON file that maps the section hierarchy to the generated filenames.

## 5. Stage 3: Assembly and Packaging

### `03_pack_parts_to_epub.py`

**Purpose:** To collect all generated assets, create the required manifest and navigation files, and compress everything into the final, valid EPUB container format.

* **Metadata Injection:** Reads the metadata (Title, Author, UUID) and the structural map (`toc_data.json`).
* **Structural File Generation:** Creates the files that define the EPUB standard:
    * `META-INF/container.xml`
    * `OEBPS/content.opf` (The book's manifest and reading order/spine).
    * `OEBPS/toc.ncx` / `OEBPS/nav.xhtml` (The hierarchical Table of Contents for e-readers).
* **Packaging:** Compresses the entire structure into a single **`[PREFIX].epub`** file, ensuring the `mimetype` file is uncompressed and placed first for strict EPUB 3 validation.
* **Progress Indicator:** Includes a progress bar to visually track the compression of assets.