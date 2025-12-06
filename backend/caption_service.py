"""
caption_service.py - AI caption generation using OpenAI GPT
Generates optimized captions with hashtags for social media posts
Supports both GPT-4o and GPT-3.5-turbo with automatic fallback
"""

import os
from typing import Optional, Dict

# Check if OpenAI package is available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI package not installed. Install with: pip install openai")

# Global client (will be initialized when API key is set)
_openai_client: Optional[OpenAI] = None
_current_api_key: Optional[str] = None


def set_openai_key(api_key: str):
    """
    Set OpenAI API key for the session
    
    Args:
        api_key: OpenAI API key
    """
    global _openai_client, _current_api_key
    
    if not api_key:
        _openai_client = None
        _current_api_key = None
        return
    
    if OPENAI_AVAILABLE:
        _openai_client = OpenAI(api_key=api_key)
        _current_api_key = api_key
    
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


def generate_caption(
    topic: str,
    style: str = "professional",
    include_hashtags: bool = True,
    num_hashtags: int = 5
) -> Dict:
    """
    Generate an optimized social media caption using OpenAI GPT
    Falls back from GPT-4o to GPT-3.5-turbo if needed
    
    Args:
        topic: Main topic/idea for the post
        style: Style of caption (e.g., "professional", "casual", "funny", "inspirational")
        include_hashtags: Whether to include hashtags
        num_hashtags: Number of hashtags to generate
    
    Returns:
        {
            "caption": str (generated caption),
            "hashtags": list (suggested hashtags),
            "full_text": str (caption + hashtags combined)
        }
    """
    
    if not OPENAI_AVAILABLE:
        return {
            "caption": f"[Demo] {topic} - OpenAI not installed",
            "hashtags": ["#demo", "#placeholder"],
            "full_text": f"[Demo] {topic}\n\n#demo #placeholder"
        }
    
    client = _get_client()
    if not client:
        return {
            "caption": f"[Demo] {topic} - No API key configured",
            "hashtags": ["#demo", "#placeholder"],
            "full_text": f"[Demo] {topic}\n\n#demo #placeholder"
        }
    
    try:
        prompt = f"""Generate a {style} social media caption based on this topic:
        
Topic: {topic}

Requirements:
1. Write a compelling, engaging caption (2-3 sentences)
2. Make it suitable for Facebook, Instagram, and Twitter
3. Include a call-to-action
4. Make it concise and impactful

Format your response EXACTLY like this:
CAPTION: [Your caption here]
HASHTAGS: [hashtag1, hashtag2, hashtag3, etc.]"""

        # Try GPT-4o first, fallback to GPT-3.5-turbo
        models_to_try = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        response = None
        
        for model in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an expert social media content creator."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=300
                )
                break  # Success, exit the loop
            except Exception as model_error:
                if model != models_to_try[-1]:
                    continue
                else:
                    raise model_error
        
        if not response:
            raise Exception("Failed to get response from OpenAI")
        
        response_text = response.choices[0].message.content.strip()
        
        # Parse response
        caption = ""
        hashtags = []
        
        lines = response_text.split("\n")
        for line in lines:
            if line.startswith("CAPTION:"):
                caption = line.replace("CAPTION:", "").strip()
            elif line.startswith("HASHTAGS:"):
                hashtags_str = line.replace("HASHTAGS:", "").strip()
                hashtags = [h.strip() for h in hashtags_str.split(",")]
        
        # Limit hashtags to requested number
        hashtags = hashtags[:num_hashtags]
        
        # Combine caption and hashtags
        full_text = caption
        if include_hashtags and hashtags:
            full_text += "\n\n" + " ".join(hashtags)
        
        return {
            "caption": caption,
            "hashtags": hashtags,
            "full_text": full_text
        }
    
    except Exception as e:
        error_msg = f"Error generating caption: {str(e)}"
        print(error_msg)
        return {
            "caption": f"[Error] {error_msg}",
            "hashtags": [],
            "full_text": f"Error generating caption: {str(e)}"
        }


def generate_multiple_captions(topic: str, styles: list[str] = None, count: int = 3) -> list[dict]:
    """
    Generate multiple caption variations for A/B testing
    
    Args:
        topic: Main topic for the post
        styles: List of caption styles to generate
        count: Number of variations per style
    
    Returns:
        List of caption dictionaries
    """
    if styles is None:
        styles = ["professional", "casual", "funny"]
    
    captions = []
    for style in styles[:count]:
        caption_result = generate_caption(topic, style=style)
        caption_result["style"] = style
        captions.append(caption_result)
    
    return captions


if __name__ == "__main__":
    # Demo without real API key
    print("Caption Service Demo (without OpenAI key)\n")
    
    result = generate_caption(
        topic="New product launch - AI-powered social media automation",
        style="professional"
    )
    
    print("Generated Caption:")
    print(result["caption"])
    print("\nHashtags:")
    print(", ".join(result["hashtags"]))
