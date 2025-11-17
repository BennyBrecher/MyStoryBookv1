from openai import OpenAI
from dotenv import load_dotenv
import os, json, base64

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

STYLE_INJECTION_PROMPT = """Illustrate in a warm, nostalgic children’s storybook style reminiscent of classic print picture books.
Use soft, earthy watercolor washes layered over subtle pencil or ink outlines, with muted greens, browns, and ochres that feel cozy and natural.
Keep all shapes rounded and gentle, avoiding sharp edges or digital-looking precision.
Give the world a rustic, folktale quality — patterned farmland, rolling hills, and simple textured backgrounds that feel hand-painted.
Characters should appear soft and endearing, with expressive posture, minimal facial detail, and slightly exaggerated proportions that emphasize innocence.
Shading should be subtle and diffuse, using watercolor-style gradients instead of hard shadows.
Overall, aim for a tender, old-fashioned fairytale atmosphere with warm tones, organic edges, and the charm of a well-loved storybook.

Avoid yellow or sepia color casts, mustard washes, and vintage paper tints. 
Do not use the common AI watercolor look with yellow filters, muddy browns, beige clouds, or dirty paper textures. 
Use clean, natural colors with balanced lighting and neutral highlights. 
Keep whites truly white and greens naturally vibrant.
"""

with open("jack_and_the_beanstalk.json") as f:
    story = json.load(f)

def fill_text(template: str) -> str:
    # Keep all placeholders like [Child Name], [boy/girl], [their] EXACTLY as written
    return template

output_dir = "pictures/pages/jackandbeans"
os.makedirs(output_dir, exist_ok=True)

def save_image_from_response(res, out_path):
    img_b64 = res.data[0].b64_json
    with open(out_path, "wb") as f:
        f.write(base64.b64decode(img_b64))
    print("✓ Saved", out_path)

for page in story["pages"]:
    scene = page["scene"]
    raw_text = page["text_template"]
    final_text = fill_text(raw_text)

    # figure out filename to match your later pipeline
    if page["id"] == "cover":
        filename = "cover.png"
        display_page_num = "Cover"
    elif page["type"] == "tribute":
        filename = "tribute.png"
        display_page_num = "Tribute"
    else:
        # story pages 2..13 -> page1..12
        page_index = page["page_number"] - 1
        filename = f"page{page_index}.png"
        display_page_num = f"Page {page_index}"

    full_prompt = f"""
{STYLE_INJECTION_PROMPT}

This is a generic template page for a children's book. 
Do NOT personalize the character's face or invent a real child's identity. 
Keep the main character's face simple and generic so a later AI can replace it.

Very important:
- Keep ALL placeholder tokens like "[Child Name]", "[boy/girl]", and "[their]" exactly as written.
- Do NOT replace them with any real name or pronoun.
- Do NOT rephrase them or correct them.
- The text in quotes below must be rendered verbatim as storybook lettering inside the illustration.

Book: Jack and the Beanstalk template
{display_page_num}, type: {page['type']}

Scene description:
{scene}

Text to render inside the illustration (in storybook lettering):
"{final_text}"

Generate a full-bleed square illustration at 2048x2048 resolution in this exact style.
"""

    print(f"Generating {display_page_num} -> {filename}")

    res = client.images.generate(
        model="gpt-image-1",
        prompt=full_prompt,
        size="1024x1024",
        n=1
    )

    out_path = os.path.join(output_dir, filename)
    save_image_from_response(res, out_path)
