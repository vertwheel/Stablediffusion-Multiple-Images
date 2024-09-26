# Install requirements
import os
import json
import requests
import time
import getpass
from PIL import Image

# Connect to the Stability API
STABILITY_KEY = getpass.getpass('Enter your Stability API Key: ')

# Define functions
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

# Parameters for image generation
prompts = [
    "An ultra-realistic, high-definition image of a sleek and modern hat inspired by sonic the hedgehog. The hat features aerodynamic curves and vibrant blue accents, incorporating subtle quill-like textures reminiscent of hedgehog spines. Designed with dynamic lines and a futuristic aesthetic, the hat exudes energy and motion. Set against a clean, minimalist background to emphasize the intricate details and craftsmanship",
    
]

negative_prompt = "Blurry, low-resolution, cartoonish, text overlays, watermarks, distorted proportions, overly dark or overexposed lighting, unnecessary background distractions"  # You can set negative prompts if needed
aspect_ratio = "1:1"  # Aspect ratio for all images
seed = 0  # Use 0 for random seed
output_format = "jpeg"  # Output format

host = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

# Create a folder to save generated images
output_folder = "generated_images"
os.makedirs(output_folder, exist_ok=True)

# Loop over each prompt and generate images
for idx, prompt in enumerate(prompts, start=1):
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
            print(f"Image {idx} failed NSFW classifier and was filtered.")
            continue

        # Save the result with a simple filename
        generated_filename = f"image_{idx}.{output_format}"
        generated_path = os.path.join(output_folder, generated_filename)

        with open(generated_path, "wb") as f:
            f.write(output_image)
        print(f"Saved image {generated_path}")

        # The code to display the image has been removed

    except Exception as e:
        print(f"An error occurred while generating image {idx}: {e}")
