"""
social_poster.py - Multi-platform social media posting functionality
Handles posting to Facebook, Instagram, and Twitter with captions and images
"""

import requests
from typing import Optional, Dict, Any
import json


class FacebookPoster:
    """Posts content to Facebook"""
    
    @staticmethod
    def post(caption: str, image_url: Optional[str] = None, fb_keys: dict = None) -> dict:
        """
        Post to Facebook
        
        Args:
            caption: Post caption text
            image_url: URL of image to post
            fb_keys: Dictionary with "access_token" and "page_id"
        
        Returns:
            {"success": bool, "post_id": str, "message": str}
        """
        if not fb_keys or "access_token" not in fb_keys:
            return {"success": False, "post_id": None, "message": "Missing Facebook credentials"}
        
        try:
            # In production, replace with real Facebook Graph API call
            # For now, simulate the API call
            access_token = fb_keys.get("access_token")
            page_id = fb_keys.get("page_id", "me")
            
            # Simulated API endpoint
            endpoint = f"https://graph.facebook.com/v18.0/{page_id}/feed"
            
            payload = {
                "message": caption,
                "access_token": access_token
            }
            
            if image_url:
                payload["link"] = image_url
            
            # Demo: In production, uncomment actual request
            # response = requests.post(endpoint, json=payload)
            # if response.status_code == 200:
            #     post_id = response.json().get("id")
            # else:
            #     return {"success": False, "post_id": None, "message": f"Facebook API error: {response.text}"}
            
            # Demo response
            post_id = f"fb_post_{hash(caption) % 10000}"
            
            return {
                "success": True,
                "post_id": post_id,
                "message": f"Posted to Facebook successfully (Post ID: {post_id})"
            }
        
        except Exception as e:
            return {"success": False, "post_id": None, "message": f"Error posting to Facebook: {str(e)}"}


class InstagramPoster:
    """Posts content to Instagram"""
    
    @staticmethod
    def post(caption: str, image_url: Optional[str] = None, ig_keys: dict = None) -> dict:
        """
        Post to Instagram
        
        Args:
            caption: Post caption text
            image_url: URL of image to post
            ig_keys: Dictionary with "access_token" and "ig_user_id"
        
        Returns:
            {"success": bool, "post_id": str, "message": str}
        """
        if not ig_keys or "access_token" not in ig_keys:
            return {"success": False, "post_id": None, "message": "Missing Instagram credentials"}
        
        try:
            access_token = ig_keys.get("access_token")
            ig_user_id = ig_keys.get("ig_user_id", "me")
            
            # Instagram Graph API endpoint for content
            endpoint = f"https://graph.instagram.com/v18.0/{ig_user_id}/media"
            
            payload = {
                "caption": caption,
                "access_token": access_token
            }
            
            if image_url:
                payload["image_url"] = image_url
            
            # Demo: In production, uncomment actual request
            # response = requests.post(endpoint, json=payload)
            # if response.status_code == 200:
            #     media_id = response.json().get("id")
            # else:
            #     return {"success": False, "post_id": None, "message": f"Instagram API error: {response.text}"}
            
            # Demo response
            media_id = f"ig_post_{hash(caption) % 10000}"
            
            return {
                "success": True,
                "post_id": media_id,
                "message": f"Posted to Instagram successfully (Media ID: {media_id})"
            }
        
        except Exception as e:
            return {"success": False, "post_id": None, "message": f"Error posting to Instagram: {str(e)}"}


class TwitterPoster:
    """Posts content to Twitter using Tweepy"""
    
    @staticmethod
    def post(caption: str, image_url: Optional[str] = None, tw_keys: dict = None) -> dict:
        """
        Post to Twitter
        
        Args:
            caption: Tweet text (caption)
            image_url: URL of image to attach
            tw_keys: Dictionary with "api_key", "api_secret", "access_token", "access_secret"
        
        Returns:
            {"success": bool, "post_id": str, "message": str}
        """
        if not tw_keys or "api_key" not in tw_keys:
            return {"success": False, "post_id": None, "message": "Missing Twitter credentials"}
        
        try:
            # Demo: In production, use Tweepy
            # import tweepy
            # auth = tweepy.OAuthHandler(tw_keys["api_key"], tw_keys["api_secret"])
            # auth.set_access_token(tw_keys["access_token"], tw_keys["access_secret"])
            # api = tweepy.API(auth)
            # status = api.update_status(status=caption)
            
            # For now, simulate the post
            tweet_id = f"tw_{hash(caption) % 10000000}"
            
            return {
                "success": True,
                "post_id": tweet_id,
                "message": f"Posted to Twitter successfully (Tweet ID: {tweet_id})"
            }
        
        except Exception as e:
            return {"success": False, "post_id": None, "message": f"Error posting to Twitter: {str(e)}"}


def post_to_multiple_platforms(
    caption: str,
    image_url: Optional[str] = None,
    platforms: list = None,
    user_keys: dict = None
) -> dict:
    """
    Post to multiple social media platforms at once
    
    Args:
        caption: Post caption
        image_url: Image URL to attach
        platforms: List of platforms ("facebook", "instagram", "twitter")
        user_keys: Dictionary of user's saved API keys
    
    Returns:
        {
            "success": bool,
            "results": {
                "facebook": dict,
                "instagram": dict,
                "twitter": dict
            }
        }
    """
    if platforms is None:
        platforms = ["facebook", "instagram", "twitter"]
    
    if user_keys is None:
        user_keys = {}
    
    results = {}
    all_success = True
    
    # Post to Facebook
    if "facebook" in platforms:
        fb_result = FacebookPoster.post(caption, image_url, user_keys.get("facebook_keys"))
        results["facebook"] = fb_result
        all_success = all_success and fb_result["success"]
    
    # Post to Instagram
    if "instagram" in platforms:
        ig_result = InstagramPoster.post(caption, image_url, user_keys.get("instagram_keys"))
        results["instagram"] = ig_result
        all_success = all_success and ig_result["success"]
    
    # Post to Twitter
    if "twitter" in platforms:
        tw_result = TwitterPoster.post(caption, image_url, user_keys.get("twitter_keys"))
        results["twitter"] = tw_result
        all_success = all_success and tw_result["success"]
    
    return {
        "success": all_success,
        "results": results
    }


if __name__ == "__main__":
    print("Social Poster Demo\n")
    
    # Test posting without credentials (will fail gracefully)
    result = post_to_multiple_platforms(
        caption="Check out our new AI Social Media Bot! 🚀 #AI #Automation",
        platforms=["facebook", "instagram", "twitter"]
    )
    
    print(f"Post results: {json.dumps(result, indent=2)}")
