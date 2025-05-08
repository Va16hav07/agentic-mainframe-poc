#!/usr/bin/env python3

import os
from PIL import Image, ImageDraw, ImageFont

def create_placeholder():
    """Create a placeholder image for visualizations"""
    # Ensure static directory exists
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    os.makedirs(static_dir, exist_ok=True)
    
    # Create a white image
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    message = "Visualization not available."
    command = "Generate with: python vector_explorer.py --visualize documents"
    
    # Draw text centered
    text_width = draw.textlength(message, font=font)
    text_x = (width - text_width) // 2
    draw.text((text_x, height//2 - 30), message, fill='black', font=font)
    
    cmd_width = draw.textlength(command, font=font)
    cmd_x = (width - cmd_width) // 2
    draw.text((cmd_x, height//2 + 10), command, fill='black', font=font)
    
    # Save the image
    output_path = os.path.join(static_dir, "placeholder.png")
    image.save(output_path)
    print(f"Created placeholder image: {output_path}")

if __name__ == "__main__":
    try:
        create_placeholder()
    except Exception as e:
        print(f"Error creating placeholder: {e}")
        # Create an extremely simple fallback if PIL fails
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
        os.makedirs(static_dir, exist_ok=True)
        with open(os.path.join(static_dir, "placeholder.png"), "wb") as f:
            # Minimal valid PNG file
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x01\x00\x00\x00\x007n\xf9$\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82')
