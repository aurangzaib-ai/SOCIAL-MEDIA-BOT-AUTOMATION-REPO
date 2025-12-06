import streamlit as st
import requests
import base64

st.set_page_config(page_title="Auto Posting Tester", layout="centered")

st.title("📤 Auto Posting Tester (Facebook + Instagram)")
st.write("Yeh chhota app sirf post test karne ke liye banaya gaya hai.")

st.divider()

# -----------------------------
# USER INPUTS
# -----------------------------
fb_token = st.text_input("🔑 Long-Lived Facebook Token", type="password")
page_id = st.text_input("📘 Facebook Page ID (DD Tech Agency)", "")
ig_id = st.text_input("📸 Instagram Business Account ID", "")
image_file = st.file_uploader("🖼 Upload Image", type=["jpg", "jpeg", "png"])
caption = st.text_area("📝 Caption", "Testing autopost from Streamlit ✔")

# -----------------------------
# CONVERT IMAGE TO BYTES
# -----------------------------
def save_temp_image(upload):
    if upload is None:
        return None
    return upload.read()

# -----------------------------
# FACEBOOK POSTING
# -----------------------------
def post_to_facebook(img_bytes):
    url = f"https://graph.facebook.com/{page_id}/photos"
    files = {"source": img_bytes}
    data = {"caption": caption, "access_token": fb_token}

    r = requests.post(url, files=files, data=data)
    return r.json()

# -----------------------------
# INSTAGRAM CONTAINER CREATION
# -----------------------------
def post_to_instagram(img_bytes):
    # STEP 1: UPLOAD IMAGE TO FB CDN
    upload_url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
    files = {"source": img_bytes}
    data = {"published": "false", "access_token": fb_token}

    upload_res = requests.post(upload_url, files=files, data=data).json()

    if "id" not in upload_res:
        return {"error": "Image upload failed", "details": upload_res}

    photo_url = f"https://graph.facebook.com/{upload_res['id']}?fields=source&access_token={fb_token}"
    source = requests.get(photo_url).json().get("source")

    # STEP 2: CREATE CONTAINER
    create_url = f"https://graph.facebook.com/v19.0/{ig_id}/media"
    payload = {"image_url": source, "caption": caption, "access_token": fb_token}

    container = requests.post(create_url, data=payload).json()

    if "id" not in container:
        return {"error": "Container error", "details": container}

    container_id = container["id"]

    # STEP 3: PUBLISH
    publish_url = f"https://graph.facebook.com/v19.0/{ig_id}/media_publish"
    publish_res = requests.post(
        publish_url, data={"creation_id": container_id, "access_token": fb_token}
    ).json()

    return publish_res


# -----------------------------
# BUTTON
# -----------------------------
if st.button("🚀 POST TO BOTH (FB + IG)"):
    if not fb_token or not page_id or not ig_id:
        st.error("⚠ Token, Page ID, IG ID required!")
    elif not image_file:
        st.error("⚠ Please upload an image!")
    else:
        st.info("⏳ Uploading... please wait")

        img_bytes = save_temp_image(image_file)

        st.subheader("📘 Facebook Result")
        fb_result = post_to_facebook(img_bytes)
        st.json(fb_result)

        st.subheader("📸 Instagram Result")
        ig_result = post_to_instagram(img_bytes)
        st.json(ig_result)

        st.success("👍 Process Completed! Check FB + IG to confirm.")
