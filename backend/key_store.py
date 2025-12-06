"""
key_store.py - Secure storage and retrieval of API keys
Uses encryption.py to store keys securely in JSON files
"""

import json
import os
from typing import Optional, Dict, Any
from encryption import encrypt, decrypt

# Path to store encrypted credentials
KEYS_STORAGE_PATH = "backend/encrypted_keys.json"


def init_storage():
    """Initialize the encrypted keys storage file"""
    if not os.path.exists(KEYS_STORAGE_PATH):
        os.makedirs("backend", exist_ok=True)
        default_data = {
            "users": {}
        }
        with open(KEYS_STORAGE_PATH, "w") as f:
            json.dump(default_data, f, indent=4)


def load_storage() -> dict:
    """Load encrypted keys storage"""
    init_storage()
    with open(KEYS_STORAGE_PATH, "r") as f:
        return json.load(f)


def save_storage(data: dict):
    """Save encrypted keys storage"""
    with open(KEYS_STORAGE_PATH, "w") as f:
        json.dump(data, f, indent=4)


def get_user_keys(username: str) -> dict:
    """
    Get all API keys for a specific user
    
    Args:
        username: Username to retrieve keys for
    
    Returns:
        {
            "openai_key": str or None,
            "facebook_keys": dict or None,
            "instagram_keys": dict or None,
            "twitter_keys": dict or None
        }
    """
    storage = load_storage()
    user_data = storage.get("users", {}).get(username, {})
    
    result = {
        "openai_key": None,
        "facebook_keys": None,
        "instagram_keys": None,
        "twitter_keys": None
    }
    
    # Decrypt and return keys if they exist
    if "openai_key" in user_data:
        try:
            result["openai_key"] = decrypt(user_data["openai_key"])
        except:
            pass
    
    if "facebook_keys" in user_data:
        try:
            decrypted = decrypt(user_data["facebook_keys"])
            result["facebook_keys"] = json.loads(decrypted)
        except:
            pass
    
    if "instagram_keys" in user_data:
        try:
            decrypted = decrypt(user_data["instagram_keys"])
            result["instagram_keys"] = json.loads(decrypted)
        except:
            pass
    
    if "twitter_keys" in user_data:
        try:
            decrypted = decrypt(user_data["twitter_keys"])
            result["twitter_keys"] = json.loads(decrypted)
        except:
            pass
    
    return result


def save_openai_key(username: str, api_key: str) -> dict:
    """
    Save OpenAI API key for a user (encrypted)
    
    Args:
        username: Username
        api_key: OpenAI API key to save
    
    Returns:
        {"success": bool, "message": str}
    """
    try:
        storage = load_storage()
        
        if username not in storage["users"]:
            storage["users"][username] = {}
        
        # Encrypt and save the key
        encrypted_key = encrypt(api_key)
        storage["users"][username]["openai_key"] = encrypted_key
        
        save_storage(storage)
        
        return {"success": True, "message": "OpenAI key saved successfully"}
    except Exception as e:
        return {"success": False, "message": f"Error saving key: {str(e)}"}


def save_social_keys(username: str, platform: str, keys: dict) -> dict:
    """
    Save social media platform API keys for a user (encrypted)
    
    Args:
        username: Username
        platform: Platform name ("facebook", "instagram", "twitter")
        keys: Dictionary of keys for the platform
    
    Returns:
        {"success": bool, "message": str}
    """
    try:
        storage = load_storage()
        
        if username not in storage["users"]:
            storage["users"][username] = {}
        
        # Encrypt and save the keys
        encrypted_keys = encrypt(json.dumps(keys))
        key_field = f"{platform}_keys"
        storage["users"][username][key_field] = encrypted_keys
        
        save_storage(storage)
        
        return {"success": True, "message": f"{platform.capitalize()} keys saved successfully"}
    except Exception as e:
        return {"success": False, "message": f"Error saving keys: {str(e)}"}


def delete_openai_key(username: str) -> dict:
    """
    Delete OpenAI key for a user
    
    Args:
        username: Username
    
    Returns:
        {"success": bool, "message": str}
    """
    try:
        storage = load_storage()
        
        if username in storage["users"] and "openai_key" in storage["users"][username]:
            del storage["users"][username]["openai_key"]
            save_storage(storage)
            return {"success": True, "message": "OpenAI key deleted successfully"}
        
        return {"success": False, "message": "No OpenAI key found for this user"}
    except Exception as e:
        return {"success": False, "message": f"Error deleting key: {str(e)}"}


def delete_social_keys(username: str, platform: str) -> dict:
    """
    Delete social media keys for a user
    
    Args:
        username: Username
        platform: Platform name
    
    Returns:
        {"success": bool, "message": str}
    """
    try:
        storage = load_storage()
        key_field = f"{platform}_keys"
        
        if username in storage["users"] and key_field in storage["users"][username]:
            del storage["users"][username][key_field]
            save_storage(storage)
            return {"success": True, "message": f"{platform.capitalize()} keys deleted successfully"}
        
        return {"success": False, "message": f"No {platform} keys found for this user"}
    except Exception as e:
        return {"success": False, "message": f"Error deleting keys: {str(e)}"}


def has_key(username: str, key_type: str) -> bool:
    """
    Check if a user has a specific key type saved
    
    Args:
        username: Username
        key_type: Key type ("openai", "facebook", "instagram", "twitter")
    
    Returns:
        bool - True if key exists, False otherwise
    """
    storage = load_storage()
    user_data = storage.get("users", {}).get(username, {})
    
    if key_type == "openai":
        return "openai_key" in user_data
    else:
        return f"{key_type}_keys" in user_data


if __name__ == "__main__":
    print("Key Store Demo\n")
    
    # Test saving and retrieving keys
    result = save_openai_key("alexis", "sk-1234567890abcdef")
    print(f"Save result: {result}")
    
    keys = get_user_keys("alexis")
    print(f"\nRetrieved OpenAI key: {keys['openai_key']}")
    
    # Test social keys
    fb_keys = {"access_token": "fb_token_123", "page_id": "page_456"}
    result = save_social_keys("alexis", "facebook", fb_keys)
    print(f"\nSave Facebook keys: {result}")
    
    keys = get_user_keys("alexis")
    print(f"Retrieved Facebook keys: {keys['facebook_keys']}")
