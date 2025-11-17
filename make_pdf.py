
'''
from PIL import Image
import os

def create_pdf(image_dir, output_pdf_name):
    files = [
        "cover.png", "page1.png", "page2.png", "page3.png",
        "page4.png", "page5.png", "page6.png", "page7.png",
        "page8.png", "page9.png", "page10.png", "page11.png",
        "page12.png", "tribute.png"
    ]
    
    images = []
    for f in files:
        path = os.path.join(image_dir, f)
        if os.path.exists(path):
            images.append(Image.open(path).convert("RGB"))
    
    if not images:
        raise ValueError(f"No images found in {image_dir}")
    
    output_path = os.path.join(image_dir, output_pdf_name)
    images[0].save(output_path, save_all=True, append_images=images[1:])
    print(f"✅ PDF created: {output_path}")
    return output_path
    '''




from PIL import Image
import os

def create_pdf(image_dir, output_pdf_name):
    files = [
        "cover.png", "page1.png", "page2.png", "page3.png",
        "page4.png", "page5.png", "page6.png", "page7.png",
        "page8.png", "page9.png", "page10.png", "page11.png",
        "page12.png", "tribute.png"
    ]

    TARGET_SIZE = (2550, 2550)   # 8.5" x 8.5" at 300 DPI

    images = []
    for f in files:
        path = os.path.join(image_dir, f)
        if os.path.exists(path):
            img = Image.open(path).convert("RGB")

            # resize to exact page size for full bleed
            if img.size != TARGET_SIZE:
                img = img.resize(TARGET_SIZE, Image.LANCZOS)

            images.append(img)

    if not images:
        raise ValueError(f"No images found in {image_dir}")

    output_path = os.path.join(image_dir, output_pdf_name)

    # optional: embed DPI metadata for print
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        dpi=(300, 300)
    )

    print(f"✅ PDF created: {output_path}")
    return output_path
