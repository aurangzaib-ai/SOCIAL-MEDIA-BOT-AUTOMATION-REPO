# facebook_service.py
import requests

def facebook_post(message, image_bytes, facebook_token, page_id):
    """
    Publish a post to a Facebook Page using Graph API.
    Supports: Text-only post + Image+Caption post.
    """
    if not facebook_token or not page_id:
        return False, "Missing Facebook token or page ID."

    try:
        # ---------------------
        # POST WITH IMAGE
        # ---------------------
        if image_bytes:
            url = f"https://graph.facebook.com/{page_id}/photos"
            files = {"source": ("image.jpg", image_bytes, "image/jpeg")}
            params = {
                "caption": message,
                "access_token": facebook_token
            }
            r = requests.post(url, files=files, params=params)
            if r.status_code == 200:
                return True, "Facebook Image Posted Successfully!"
            return False, r.text

        # ---------------------
        # TEXT ONLY POST
        # ---------------------
        url = f"https://graph.facebook.com/{page_id}/feed"
        payload = {
            "message": message,
            "access_token": facebook_token
        }
        r = requests.post(url, data=payload)

        if r.status_code == 200:
            return True, "Facebook Text Posted Successfully!"

        return False, r.text

    except Exception as e:
        return False, str(e)
