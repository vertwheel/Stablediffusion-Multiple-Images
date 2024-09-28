# Install requirements
import sys


# Import necessary libraries
import os
import json
import requests
import time
from PIL import Image

# Section 1: Connect to the Stability API
STABILITY_KEY = "ENTER YOUR KEY HERE"

def send_generation_request(host, params):
    headers = {
        "Accept": "image/*",
        "Authorization": f"Bearer {STABILITY_KEY}"
    }

    # Encode parameters
    files = {}
    image = params.pop("image", None)
    mask = params.pop("mask", None)
    if image:
        files["image"] = open(image, 'rb')
    if mask:
        files["mask"] = open(mask, 'rb')
    if not files:
        files["none"] = ''

    # Send request
    print(f"Sending REST request to {host} with prompt: '{params['prompt']}'")
    response = requests.post(
        host,
        headers=headers,
        files=files,
        data=params
    )
    if not response.ok:
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    return response

def sanitize_filename(name):
    # Remove invalid characters and replace spaces with underscores
    import re
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.strip().replace(" ", "_")
    return name

# Section 2: Define Parameters and Prompts
# Here you can specify the folder names and associate prompts with each folder
prompts = {
    "Villains": [
        "An ultra-realistic, high-definition image of Harley Quinn",
        "An ultra-realistic, high-definition image of Catwoman",
        "An ultra-realistic, high-definition image of Joker",
    ],
    "Heroes": [
        "An ultra-realistic, high-definition image of Batwoman",
        "An ultra-realistic, high-definition image of Supergirl",
        "An ultra-realistic, high-definition image of Wonder Woman",
    ],
    "Antiheroes": [
        "An ultra-realistic, high-definition image of Deadpool",
        "An ultra-realistic, high-definition image of Venom",
    ]
}

negative_prompt = (
    "Blurry, low-resolution, cartoonish, text overlays, watermarks, distorted proportions, "
    "overly dark or overexposed lighting, unnecessary background distractions"
)
aspect_ratio = "1:1"
seed = 0  # Use 0 for random seed
output_format = "jpeg"
host = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

# Section 3: Create Output Directory
output_folder = "generated_images"
os.makedirs(output_folder, exist_ok=True)

# Section 4: Generate Images and Organize into Specified Folders
for folder_name, folder_prompts in prompts.items():
    # Sanitize folder name to ensure it's valid
    sanitized_folder_name = sanitize_filename(folder_name)
    folder_path = os.path.join(output_folder, sanitized_folder_name)
    os.makedirs(folder_path, exist_ok=True)
    print(f"\n# Generating images for folder: {folder_name}")

    for idx, prompt in enumerate(folder_prompts, start=1):
        params = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "aspect_ratio": aspect_ratio,
            "seed": seed,
            "output_format": output_format,
            "model": "sd3-large",
            "mode": "text-to-image"
        }

        # Send the request and handle the response
        try:
            response = send_generation_request(host, params)

            # Decode response
            output_image = response.content
            finish_reason = response.headers.get("finish-reason")
            seed = response.headers.get("seed")

            # Check for NSFW classification
            if finish_reason == 'CONTENT_FILTERED':
                print(f"Image {idx} in folder '{folder_name}' failed NSFW classifier and was filtered.")
                continue

            # Save the result with a simple filename
            generated_filename = f"image_{idx}.{output_format}"
            generated_path = os.path.join(folder_path, generated_filename)

            with open(generated_path, "wb") as f:
                f.write(output_image)
            print(f"Saved image {generated_path}")

        except Exception as e:
            print(f"An error occurred while generating image {idx} in folder '{folder_name}': {e}")
