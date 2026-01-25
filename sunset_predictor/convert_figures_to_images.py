"""Convert PDF figures to PNG images for embedding in paper."""

from pdf2image import convert_from_path
from pathlib import Path

def convert_pdfs_to_images():
    """Convert all PDF figures to PNG."""
    figures_dir = Path("figures")
    images_dir = Path("figure_images")
    images_dir.mkdir(exist_ok=True)
    
    pdf_files = list(figures_dir.glob("*.pdf"))
    print(f"Converting {len(pdf_files)} PDF figures to images...")
    
    for pdf_file in pdf_files:
        try:
            # Convert PDF to image (300 DPI for quality)
            images = convert_from_path(str(pdf_file), dpi=300)
            if images:
                # Save first page as PNG
                image_path = images_dir / f"{pdf_file.stem}.png"
                images[0].save(image_path, "PNG")
                print(f"✓ Converted: {pdf_file.name} → {image_path.name}")
        except Exception as e:
            print(f"✗ Error converting {pdf_file.name}: {e}")
            # Try alternative: use PIL to create placeholder
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((400, 300), f"Figure: {pdf_file.stem}", 
                     fill='black', anchor='mm')
            image_path = images_dir / f"{pdf_file.stem}.png"
            img.save(image_path)
            print(f"  Created placeholder: {image_path.name}")

if __name__ == "__main__":
    convert_pdfs_to_images()

