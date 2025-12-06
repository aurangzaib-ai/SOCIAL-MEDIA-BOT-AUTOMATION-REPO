"""
image_service.py - AI image generation using DALL·E 3
Generates images from text prompts and returns URLs
"""

import os
import base64
from typing import Optional, Dict
from pathlib import Path

# Check if OpenAI package is available
try:
    from openai import OpenAI
    from PIL import Image
    import io
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI/PIL package not installed. Install with: pip install openai pillow")

# Global client
_openai_client: Optional[OpenAI] = None

# Directory to store generated images
IMAGES_DIR = "backend/generated_images"


def init_images_dir():
    """Create images directory if it doesn't exist"""
    os.makedirs(IMAGES_DIR, exist_ok=True)


def set_openai_key(api_key: str):
    """
    Set OpenAI API key for image generation
    
    Args:
        api_key: OpenAI API key with DALL·E access
    """
    global _openai_client
    
    if not api_key:
        _openai_client = None
        return
    
    if OPENAI_AVAILABLE:
        _openai_client = OpenAI(api_key=api_key)
    
    os.environ["OPENAI_API_KEY"] = api_key


def _get_client() -> Optional[OpenAI]:
    """Get or create OpenAI client"""
    global _openai_client
    
    if not OPENAI_AVAILABLE:
        return None
    
    if _openai_client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            _openai_client = OpenAI(api_key=api_key)
    
    return _openai_client


def generate_image(prompt: str, size: str = "1024x1024", style: str = "natural") -> Dict:
    """
    Generate an image using DALL·E 3 based on text prompt
    
    Args:
        prompt: Detailed description of the image to generate
        size: Image size - "1024x1024", "1024x1792", or "1792x1024"
        style: "vivid" for hyper-real and dramatic, "natural" for realistic
    
    Returns:
        {
            "success": bool,
            "image_url": str (DALL·E URL) or None,
            "local_path": str (saved local path) or None,
            "base64": str (base64 encoded image) or None,
            "message": str
        }
    """
    
    init_images_dir()
    
    if not OPENAI_AVAILABLE:
        return {
            "success": False,
            "image_url": None,
            "local_path": None,
            "base64": None,
            "message": "OpenAI not installed. Install with: pip install openai"
        }
    
    client = _get_client()
    if not client:
        return {
            "success": False,
            "image_url": None,
            "local_path": None,
            "base64": None,
            "message": "No OpenAI API key configured"
        }
    
    try:
        # Create an improved prompt for DALL·E
        enhanced_prompt = f"{prompt}. High quality, professional, detailed."
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=enhanced_prompt,
            size=size,
            quality="hd",
            n=1
        )
        
        image_url = response.data[0].url
        
        # Generate a local filename based on hash
        local_filename = f"generated_image_{hash(prompt) % 10000}.png"
        local_path = os.path.join(IMAGES_DIR, local_filename)
        
        return {
            "success": True,
            "image_url": image_url,
            "local_path": local_path,
            "base64": None,  # Would encode downloaded image here in production
            "message": "Image generated successfully"
        }
    
    except Exception as e:
        error_msg = f"Error generating image: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "image_url": None,
            "local_path": None,
            "base64": None,
            "message": error_msg
        }


def generate_image_from_file(image_path: str) -> Optional[str]:
    """
    Convert an image file to base64 string
    
    Args:
        image_path: Path to the image file
    
    Returns:
        Base64 encoded image string, or None if error
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception as e:
        print(f"Error encoding image: {str(e)}")
        return None


def save_base64_image(base64_string: str, filename: str = "generated_image.png") -> str:
    """
    Save a base64 encoded image to file
    
    Args:
        base64_string: Base64 encoded image data
        filename: Output filename
    
    Returns:
        Full path to saved image
    """
    try:
        init_images_dir()
        
        image_data = base64.b64decode(base64_string)
        file_path = os.path.join(IMAGES_DIR, filename)
        
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        return file_path
    except Exception as e:
        print(f"Error saving image: {str(e)}")
        return None


def enhance_image_prompt(user_prompt: str, style: str = "professional") -> str:
    """
    Enhance a simple image prompt with professional details
    
    Args:
        user_prompt: Simple description from user
        style: Art style (professional, artistic, photorealistic, cartoon)
    
    Returns:
        Enhanced prompt for DALL·E
    """
    style_descriptors = {
        "professional": "professional, polished, corporate, clean design",
        "artistic": "artistic, creative, colorful, expressive, modern art style",
        "photorealistic": "photorealistic, detailed, high resolution, professional photography",
        "cartoon": "cartoon style, vibrant, fun, playful, illustration"
    }
    
    descriptor = style_descriptors.get(style, style_descriptors["professional"])
    
    return f"{user_prompt}. Style: {descriptor}. High quality, 4K resolution."


def create_placeholder_image(width: int = 400, height: int = 400) -> str:
    """
    Create a placeholder image (for demo without DALL·E key)
    
    Args:
        width: Image width
        height: Image height
    
    Returns:
        Base64 encoded placeholder image
    """
    if not OPENAI_AVAILABLE:
        return None
    
    try:
        # Create a simple colored image as placeholder
        img = Image.new("RGB", (width, height), color=(100, 150, 200))
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        base64_image = base64.b64encode(buffer.getvalue()).decode()
        
        return base64_image
    except:
        return None


if __name__ == "__main__":
    print("Image Service Demo\n")
    
    # Demo image generation (won't work without API key)
    result = generate_image(
        prompt="A futuristic AI robot working at a desk with multiple screens",
        style="natural"
    )
    
    print(f"Image generation result: {result['message']}")
