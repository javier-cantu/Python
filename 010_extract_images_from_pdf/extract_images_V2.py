"""
===============================================================================
PDF IMAGE EXTRACTION SCRIPT
===============================================================================

Description:
    Extracts all images embedded within PDF files located in a specified input 
    folder and saves them to an output directory using a customizable filename 
    prefix and sequential numbering.

Prerequisites:
    PyMuPDF (fitz)
    Install via terminal: pip install pymupdf

Usage Instructions:
    1. Place your target PDF file(s) into the 'pdfs' folder (created in the 
       same directory as this script).
    2. Adjust the configuration variables below if needed:
       - FILE_PREFIX: Set your desired output image filename prefix.
       - PDF_FOLDER: Folder containing source PDF files.
       - IMAGE_FOLDER: Folder where extracted images will be stored.
    3. Run the script:
       python extract_images.py

===============================================================================
"""

import fitz  # PyMuPDF
import os

# CONFIGURATION
FILE_PREFIX = "extracted_img"  # Change this to your preferred image prefix
PDF_FOLDER = "pdfs"
IMAGE_FOLDER = "images"

def extract_images_from_pdfs(pdf_folder=PDF_FOLDER, image_folder=IMAGE_FOLDER, prefix=FILE_PREFIX):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(script_dir, pdf_folder)
    image_path = os.path.join(script_dir, image_folder)

    # Ensure the image output directory exists
    os.makedirs(image_path, exist_ok=True)

    # Get all PDF files in the pdfs folder
    pdf_files = [f for f in os.listdir(pdf_path) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print(f"No PDF files found in '{pdf_path}'. Please place PDFs in this folder.")
        return

    print(f"Found {len(pdf_files)} PDF(s) in '{pdf_path}'.")

    for pdf_file in pdf_files:
        pdf_filepath = os.path.join(pdf_path, pdf_file)
        print(f"\nProcessing '{pdf_file}'...")

        try:
            doc = fitz.open(pdf_filepath)
            image_count = 0
            
            for i in range(len(doc)):
                for img in doc.get_page_images(i):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    image_count += 1
                    
                    # Format: PREFIX_001.EXTENSION
                    image_filename = f"{prefix}_{image_count:03d}.{image_ext}"
                    output_filepath = os.path.join(image_path, image_filename)

                    with open(output_filepath, "wb") as img_file:
                        img_file.write(image_bytes)
                    print(f"  Extracted: {image_filename}")
                    
            doc.close()
            print(f"Finished processing '{pdf_file}'. Total images extracted: {image_count}")
        except Exception as e:
            print(f"Error processing '{pdf_file}': {e}")

if __name__ == "__main__":
    extract_images_from_pdfs()