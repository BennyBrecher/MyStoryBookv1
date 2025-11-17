import os
import base64
import datetime
import shutil
from openai import OpenAI
from dotenv import load_dotenv
from make_pdf import create_pdf

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def save_result(res, out_path):
    """Save AI-generated image from base64 response"""
    img_b64 = res.data[0].b64_json
    with open(out_path, "wb") as f:
        f.write(base64.b64decode(img_b64))
    print("✓ Saved:", out_path)
    #return out_path                claude added this for logging probably, idk. if errors maybe uncomment

def generate_storybook(face_path, story_type="littlered", child_name="Hero", gender="boy", progress_callback=None):
    """
    Generate a personalized storybook
    
    Args:
        face_path (str): Path to the uploaded face image
        story_type (str): "littlered" or "jackbeanstalk"
        child_name (str): Name of the child
        gender (str): "boy" or "girl"
        progress_callback (callable): Optional function to call with progress updates
                                     Should accept (current_page, total_pages, status_message)
    
    Returns:
        str: Path to the output directory containing all generated images
    """
    
    # Story configuration
    story_config = {
        "littlered": {
            "cover": "pictures/covers/littlered.jpg",
            "pages_dir": "pictures/pages/littlered",
            "skip_pages": [8, 9],  # Pages without main character
            "total_pages": 12
        },
        "jackbeanstalk": {
            "cover": "pictures/covers/jackbeanstalk.jpg",
            "pages_dir": "pictures/pages/jackbeanstalk",
            "skip_pages": [],
            "total_pages": 12
        }
    }
    
    config = story_config.get(story_type, story_config["littlered"])
    cover_path = config["cover"]
    pages_dir = config["pages_dir"]
    skip_pages = config["skip_pages"]
    total_pages = config["total_pages"]
    
    # Create unique output directory for this book
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_child_name = child_name.replace(" ", "_")
    out_dir = f"pictures/out/{story_type}_{safe_child_name}_{timestamp}"
    os.makedirs(out_dir, exist_ok=True)
    
    # AI prompt for face replacement
    prompt = (
        f"Use the second image (the face photo) to seamlessly place that person onto the "
        f"{'boy' if gender == 'boy' else 'girl'} character/subject of the first image (storybook page). "
        f"Keep the page's typography, logo, and background unchanged. Replace only the character's "
        f"face/head so it looks natural, with matching lighting, color, perspective, and proportions, "
        f"and general fairytale/storybook artstyle."
    )
    
    def update_progress(current, total, message):
        """Helper to call progress callback if provided"""
        if progress_callback:
            progress_callback(current, total, message)
        print(f"[{current}/{total}] {message}")
    
    # 1) Generate cover
    update_progress(0, total_pages + 1, "Generating cover page...")
    try:
        with open(cover_path, "rb") as cover, open(face_path, "rb") as face:
            res = client.images.edit(
                model="gpt-image-1",
                image=[cover, face],
                prompt=prompt,
                size="1024x1024"
            )
        save_result(res, f"{out_dir}/cover.png")
    except Exception as e:
        print(f"Error generating cover: {e}")
        raise
    
    # 2) Generate pages 1-12
    for i in range(1, total_pages + 1):
        update_progress(i, total_pages + 1, f"Creating page {i} of {total_pages}...")
        
        base = f"{pages_dir}/page{i}.png"
        
        if not os.path.exists(base):
            print(f"Skipping (missing): {base}")
            continue
        
        # Skip pages without main character
        if i in skip_pages:
            out_path = f"{out_dir}/page{i}.png"
            shutil.copy(base, out_path)
            print(f"✓ No character edit needed for page {i}")
            continue
        
        try:
            with open(base, "rb") as page, open(face_path, "rb") as face:
                res = client.images.edit(
                    model="gpt-image-1",
                    image=[page, face],
                    prompt=prompt,
                    size="1024x1024"
                )
            save_result(res, f"{out_dir}/page{i}.png")
        except Exception as e:
            print(f"Error generating page {i}: {e}")
            raise
    
    # 3) Optional tribute page
    tribute = f"{pages_dir}/tribute.png"
    if os.path.exists(tribute):
        update_progress(total_pages + 1, total_pages + 1, "Adding tribute page...")
        try:
            with open(tribute, "rb") as page, open(face_path, "rb") as face:
                res = client.images.edit(
                    model="gpt-image-1",
                    image=[page, face],
                    prompt=prompt,
                    size="1024x1024"
                )
            save_result(res, f"{out_dir}/tribute.png")
        except Exception as e:
            print(f"Error generating tribute: {e}")
            # Don't raise - tribute is optional
    
    update_progress(total_pages + 1, total_pages + 1, "Complete!")
    #return out_dir
    # Generate the PDF
    pdf_path = create_pdf(out_dir, f"{story_type}_{child_name}.pdf")
    return pdf_path


# For testing directly
if __name__ == '__main__':
    face_path = "pictures/faces/prof.png"
    output_dir = generate_storybook(
        face_path=face_path,
        story_type="littlered",
        child_name="TestKid",
        gender="boy"
    )
    print(f"\n✅ Book generated in: {output_dir}")