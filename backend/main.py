"""
main.py - FastAPI Backend for AI Social Media Automation Bot
Handles all API endpoints for caption generation, image creation, and posting
"""

from fastapi import FastAPI, HTTPException, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json

# Import services
from auth import verify_login, create_access_token, verify_token, register_user, init_default_user
from caption_service import generate_caption, set_openai_key as set_caption_openai_key
from image_service import generate_image, set_openai_key as set_image_openai_key
from social_poster import post_to_multiple_platforms
from key_store import (
    save_openai_key, save_social_keys, delete_openai_key, delete_social_keys,
    get_user_keys, has_key
)

# Initialize FastAPI app
app = FastAPI(
    title="AI Social Media Automation Bot",
    description="AI-powered social media posting system",
    version="1.0.0"
)

# Add CORS middleware for Streamlit compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize default user
init_default_user()


# ==================== Pydantic Models ====================

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    message: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class CaptionRequest(BaseModel):
    topic: str
    style: str = "professional"
    include_hashtags: bool = True
    num_hashtags: int = 5


class ImageRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"
    style: str = "natural"


class PostRequest(BaseModel):
    caption: str
    image_url: Optional[str] = None
    platforms: List[str] = ["facebook", "instagram", "twitter"]


class OpenAIKeyRequest(BaseModel):
    api_key: str


class SocialKeysRequest(BaseModel):
    platform: str  # "facebook", "instagram", "twitter"
    keys: dict  # Platform-specific keys


# ==================== Authentication Endpoints ====================

@app.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """
    Login endpoint - verify credentials and return JWT token
    
    Args:
        username: User's username
        password: User's password
    
    Returns:
        JWT token if credentials are valid
    """
    is_valid, message = verify_login(request.username, request.password)
    
    if is_valid:
        token = create_access_token(request.username)
        return LoginResponse(
            success=True,
            token=token,
            message=message
        )
    else:
        raise HTTPException(status_code=401, detail=message)


@app.post("/register", response_model=LoginResponse)
def register(request: RegisterRequest):
    """
    Register a new user account
    
    Args:
        username: New username
        password: New password
    
    Returns:
        Success message
    """
    result = register_user(request.username, request.password)
    
    if result["success"]:
        token = create_access_token(request.username)
        return LoginResponse(
            success=True,
            token=token,
            message=result["message"]
        )
    else:
        raise HTTPException(status_code=400, detail=result["message"])


def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """
    Dependency to verify JWT token from Authorization header
    Expects: Authorization: Bearer <token>
    
    Args:
        authorization: Authorization header value
    
    Returns:
        Username if token is valid
    
    Raises:
        HTTPException: If token is missing or invalid
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format. Use: Bearer <token>")
    
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return username


# ==================== API Key Management Endpoints ====================

@app.post("/save-openai-key")
def save_openai_key_endpoint(request: OpenAIKeyRequest, current_user: str = Depends(get_current_user)):
    """
    Save OpenAI API key for current user (encrypted)
    
    Args:
        api_key: OpenAI API key
        current_user: Current authenticated user (from token)
    
    Returns:
        Success message
    """
    result = save_openai_key(current_user, request.api_key)
    
    if result["success"]:
        # Set the key for current session
        set_caption_openai_key(request.api_key)
        set_image_openai_key(request.api_key)
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])


@app.post("/save-social-keys")
def save_social_keys_endpoint(request: SocialKeysRequest, current_user: str = Depends(get_current_user)):
    """
    Save social media API keys for current user (encrypted)
    
    Args:
        platform: Platform name (facebook, instagram, twitter)
        keys: Dictionary of keys for the platform
        current_user: Current authenticated user (from token)
    
    Returns:
        Success message
    """
    result = save_social_keys(current_user, request.platform, request.keys)
    
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])


@app.delete("/delete-openai-key")
def delete_openai_key_endpoint(current_user: str = Depends(get_current_user)):
    """Delete OpenAI key for current user"""
    result = delete_openai_key(current_user)
    
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])


@app.delete("/delete-social-keys/{platform}")
def delete_social_keys_endpoint(platform: str, current_user: str = Depends(get_current_user)):
    """Delete social media keys for current user"""
    result = delete_social_keys(current_user, platform)
    
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])


@app.get("/user-keys")
def get_user_keys_endpoint(current_user: str = Depends(get_current_user)):
    """Get all API keys for current user (decrypted)"""
    keys = get_user_keys(current_user)
    
    return {
        "success": True,
        "keys": keys
    }


# ==================== Content Generation Endpoints ====================

@app.post("/generate-caption")
def generate_caption_endpoint(request: CaptionRequest, current_user: str = Depends(get_current_user)):
    """
    Generate AI-powered caption using OpenAI GPT
    
    Args:
        topic: Main topic/idea for the post
        style: Caption style (professional, casual, funny, inspirational)
        include_hashtags: Whether to include hashtags
        num_hashtags: Number of hashtags to generate
        current_user: Current authenticated user (from token)
    
    Returns:
        Generated caption with hashtags
    """
    
    result = generate_caption(
        topic=request.topic,
        style=request.style,
        include_hashtags=request.include_hashtags,
        num_hashtags=request.num_hashtags
    )
    
    return {
        "success": True,
        "caption": result["caption"],
        "hashtags": result["hashtags"],
        "full_text": result["full_text"]
    }


@app.post("/generate-image")
def generate_image_endpoint(request: ImageRequest, current_user: str = Depends(get_current_user)):
    """
    Generate AI image using DALL·E 3
    
    Args:
        prompt: Image description/prompt
        size: Image size (1024x1024, 1024x1792, 1792x1024)
        style: Art style (natural, vivid)
        current_user: Current authenticated user (from token)
    
    Returns:
        Generated image URL and metadata
    """
    
    result = generate_image(
        prompt=request.prompt,
        size=request.size,
        style=request.style
    )
    
    return result


# ==================== Social Media Posting Endpoints ====================

@app.post("/post")
def post_to_platforms(request: PostRequest, current_user: str = Depends(get_current_user)):
    """
    Post content to selected social media platforms
    
    Args:
        caption: Post caption
        image_url: Image URL (optional)
        platforms: List of platforms to post to
        current_user: Current authenticated user (from token)
    
    Returns:
        Posting results for each platform
    """
    # Get user's saved API keys
    user_keys = get_user_keys(current_user)
    
    # Post to platforms
    result = post_to_multiple_platforms(
        caption=request.caption,
        image_url=request.image_url,
        platforms=request.platforms,
        user_keys=user_keys
    )
    
    return {
        "success": result["success"],
        "results": result["results"],
        "message": "Posted to all selected platforms"
    }


# ==================== Health Check Endpoint ====================

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Social Media Automation Bot API"
    }


@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": "AI Social Media Automation Bot",
        "version": "1.0.0",
        "description": "AI-powered social media posting system",
        "endpoints": {
            "auth": ["/login", "/register"],
            "keys": ["/save-openai-key", "/save-social-keys", "/user-keys"],
            "generation": ["/generate-caption", "/generate-image"],
            "posting": ["/post"],
            "health": ["/health"]
        }
    }


if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.environ.get("PORT", 8000))
    
    print("Starting AI Social Media Automation Bot Backend...")
    print(f"API Docs available at: http://localhost:{port}/docs")
    print("Default login: alexis / password123")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
