import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv(".env", override=True)

ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

MODEL = "@cf/black-forest-labs/flux-1-schnell"

CATEGORY_CONTEXT = {
    "bet": (
        "professional football and sports media photography, "
        "stadium atmosphere, realistic players, match context"
    ),
    "tech": (
        "professional technology and innovation photography, "
        "artificial intelligence, African entrepreneurs, modern devices"
    ),
    "crypto": (
        "professional cryptocurrency and financial technology photography, "
        "Bitcoin, blockchain, digital finance, modern African business"
    ),
}


def generate_visual(category, slot, message=None):

    if not ACCOUNT_ID:
        raise RuntimeError("CLOUDFLARE_ACCOUNT_ID absent du .env")

    if not API_TOKEN:
        raise RuntimeError("CLOUDFLARE_API_TOKEN absent du .env")

    context = CATEGORY_CONTEXT.get(
        category,
        CATEGORY_CONTEXT["tech"]
    )

    if message:
        clean_message = message[:1200]
    else:
        clean_message = f"General {category} publication"

    prompt = f"""
Create a realistic professional editorial photograph for a media publication.

Category:
{category}

Visual context:
{context}

Publication subject:
{clean_message}

Requirements:
- photorealistic
- cinematic professional photography
- realistic lighting
- high detail
- modern African context when appropriate
- visually attractive for Telegram and social media
- landscape composition, 16:9
- no text
- no captions
- no watermark
- no logos
- no distorted faces
- no unrealistic objects
"""

    url = (
        f"https://api.cloudflare.com/client/v4/accounts/"
        f"{ACCOUNT_ID}/ai/run/{MODEL}"
    )

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "prompt": prompt,
            "steps": 4
        },
        timeout=120,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Cloudflare Workers AI HTTP {response.status_code}: "
            f"{response.text[:500]}"
        )

    data = response.json()

    if not data.get("success"):
        raise RuntimeError(
            f"Cloudflare Workers AI erreur: {data}"
        )

    image_b64 = data.get("result", {}).get("image")

    if not image_b64:
        raise RuntimeError(
            f"Image absente de la réponse Cloudflare"
        )

    directory = os.path.join(
        "generated_images",
        category
    )

    os.makedirs(directory, exist_ok=True)

    filename = f"{slot.replace(':', '-')}.png"
    path = os.path.join(directory, filename)

    with open(path, "wb") as f:
        f.write(base64.b64decode(image_b64))

    return path
