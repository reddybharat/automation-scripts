import pypdfium2 as pdfium
import os

def pdf_to_images(input_pdf, output_dir="output_images", dpi=300):
    """
    Convert a PDF file to images (one per page) and save them to the specified directory.
    
    Args:
        input_pdf (str): Path to the input PDF file
        output_dir (str): Directory to save output images (default: "output_images")
        dpi (int): Resolution in dots per inch (default: 300)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Calculate scale factor based on DPI (PDFs are typically 72 DPI)
    scale = dpi / 72
    
    # Load the PDF document
    pdf = pdfium.PdfDocument(input_pdf)
    
    # Iterate through each page and convert to image
    for page_number in range(len(pdf)):
        page = pdf.get_page(page_number)
        
        # Render page to a PIL Image
        image = page.render(scale=scale).to_pil()
        
        # Save image
        image.save(os.path.join(output_dir, f"page_{page_number + 1}.png"), quality=95)
        print(f"Saved page {page_number + 1} as image")
    
    print(f"Conversion complete. Images saved to {output_dir}")

if __name__ == "__main__":
    # Example usage
    pdf_to_images(
        input_pdf="",  # Replace with your PDF file path
        output_dir="pdf_images_output",
        dpi=300
    )