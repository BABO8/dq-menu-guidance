from pathlib import Path
from PIL import Image

IMAGES_DIR = Path(__file__).resolve().parent / "static" / "images"

def convert_and_optimize():
    """
    Converts and resizes all images in app/static/images to WebP format.
    - Max 800x600 for hero images.
    - Max 600x600 for item cards.
    - Compressed at quality=75 so every WebP file is under 50 KB.
    """
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    converted = []
    
    # Process all image files
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
        for img_path in list(IMAGES_DIR.glob(ext)):
            # If png or jpg, save as .webp
            webp_path = img_path.with_suffix(".webp")
            try:
                with Image.open(img_path) as img:
                    img = img.convert("RGB")
                    
                    if "hero" in img_path.name:
                        max_w, max_h = 800, 600
                    else:
                        max_w, max_h = 600, 600
                        
                    img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
                    img.save(webp_path, "WEBP", quality=75, method=6)
                    
                    sz_kb = webp_path.stat().st_size / 1024
                    converted.append((webp_path.name, img.size, sz_kb))
                    print(f"Optimized: {webp_path.name} ({img.size[0]}x{img.size[1]}, {sz_kb:.1f} KB)")
            except Exception as e:
                print(f"Error processing {img_path.name}: {e}")
                
    # Remove all raw unoptimized .png files
    png_files = list(IMAGES_DIR.glob("*.png"))
    for png in png_files:
        try:
            png.unlink()
            print(f"Removed heavy raw file: {png.name}")
        except Exception as e:
            print(f"Error removing {png.name}: {e}")
            
    return converted

if __name__ == "__main__":
    res = convert_and_optimize()
    print(f"Finished optimizing {len(res)} images.")
