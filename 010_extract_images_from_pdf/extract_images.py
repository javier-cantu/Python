import fitz  # PyMuPDF
import os

def extract_images_from_pdfs(pdf_folder="pdfs", image_folder="images"):
    """
    Extracts all images from PDF files in a specified PDF folder
    and saves them to an image folder.
    """
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
                for img_index, img in enumerate(doc.get_page_images(i)):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    # Construct a unique filename for each image
                    # Format: PDF_FILENAME_PAGE_NUMBER_IMAGE_INDEX.EXTENSION
                    image_filename = f"{os.path.splitext(pdf_file)[0]}_page{i+1}_img{img_index+1}.{image_ext}"
                    output_filepath = os.path.join(image_path, image_filename)

                    with open(output_filepath, "wb") as img_file:
                        img_file.write(image_bytes)
                    print(f"  Extracted: {image_filename}")
                    image_count += 1
            doc.close()
            print(f"Finished processing '{pdf_file}'. Total images extracted: {image_count}")
        except Exception as e:
            print(f"Error processing '{pdf_file}': {e}")

if __name__ == "__main__":
    extract_images_from_pdfs()