# instagram_service.py
import requests

def instagram_post(caption, image_bytes, ig_token, ig_business_id):
    """
    Publish an image to Instagram Business Account using Graph API.
    Requires: Image URL → Container → Publish
    """
    if not ig_token or not ig_business_id:
        return False, "Missing IG token or business account ID."

    try:
        # STEP 1 — UPLOAD IMAGE TO TEMP HOST (imgbb etc.)
        upload_url = "https://api.imgbb.com/1/upload"
        params = {"key": "YOUR_IMGBB_KEY"}  # <- Replace with your own
        files = {"image": image_bytes}

        r = requests.post(upload_url, params=params, files=files)
        if r.status_code != 200:
            return False, "Image hosting failed"

        image_url = r.json()["data"]["url"]

        # STEP 2 — CREATE MEDIA CONTAINER
        create_url = f"https://graph.facebook.com/v18.0/{ig_business_id}/media"
        container_payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": ig_token
        }

        r2 = requests.post(create_url, data=container_payload)
        container_id = r2.json().get("id")

        if not container_id:
            return False, f"Error in container creation: {r2.text}"

        # STEP 3 — PUBLISH POST
        publish_url = f"https://graph.facebook.com/v18.0/{ig_business_id}/media_publish"
        publish_payload = {
            "creation_id": container_id,
            "access_token": ig_token
        }

        r3 = requests.post(publish_url, data=publish_payload)

        if r3.status_code == 200:
            return True, "Instagram Post Published Successfully!"

        return False, r3.text

    except Exception as e:
        return False, str(e)
