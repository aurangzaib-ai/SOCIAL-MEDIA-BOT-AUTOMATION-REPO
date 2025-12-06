import streamlit as st
import requests
import base64
import time

st.set_page_config(page_title="Instagram Auto Poster", layout="wide")

st.title("📸 Instagram Auto Posting App")

IG_BUSINESS_ID = "17841474703571324"
PAGE_ACCESS_TOKEN = st.text_input("🔐 Page Access Token", type="password")

uploaded_file = st.file_uploader("📤 Upload Image", type=["jpg", "jpeg", "png"])
caption = st.text_area("✏ Caption")

if st.button("🚀 Post to Instagram"):
    if uploaded_file is None:
        st.error("Please upload an image first.")
        st.stop()

    if not PAGE_ACCESS_TOKEN:
        st.error("Please enter PAGE ACCESS TOKEN.")
        st.stop()

    # Step 1: Upload the image to a temporary server
    file_bytes = uploaded_file.read()
    img_b64 = base64.b64encode(file_bytes).decode("utf-8")
    
    upload_url = f"https://graph.facebook.com/v19.0/{IG_BUSINESS_ID}/media"
    
    create_payload = {
        "image_data": img_b64,
        "caption": caption,
        "access_token": PAGE_ACCESS_TOKEN
    }
    
    st.info("📤 Creating media container...")
    create_resp = requests.post(upload_url, data=create_payload)

    st.write("🧾 Create Response:")
    st.json(create_resp.json())

    if "id" not in create_resp.json():
        st.error("❌ Failed to create media container. Check token or image.")
        st.stop()

    container_id = create_resp.json()["id"]

    time.sleep(2)   # little wait is required

    # Step 2: Publish the media container
    publish_url = f"https://graph.facebook.com/v19.0/{IG_BUSINESS_ID}/media_publish"
    publish_payload = {
        "creation_id": container_id,
        "access_token": PAGE_ACCESS_TOKEN
    }

    st.info("📬 Publishing media...")
    publish_resp = requests.post(publish_url, data=publish_payload)

    st.write("📬 Publish Response:")
    st.json(publish_resp.json())

    if "id" in publish_resp.json():
        st.success("🎉 POST SUCCESSFULLY PUBLISHED ON INSTAGRAM!")
    else:
        st.error("❌ Failed to publish.")
