import streamlit as st
import requests

# -------------------------------------------------------
# Streamlit Page Config
# -------------------------------------------------------
st.set_page_config(page_title="IG Auto Post Tester", layout="centered")

st.title("🔥 Instagram Auto Post Tester")
st.write("Test posting an image to your **Instagram Business Account** using the Page Token.")

# -------------------------------------------------------
# IG Credentials Input
# -------------------------------------------------------
instagram_id = st.text_input("📸 Instagram Business Account ID:", "")
page_token = st.text_input("🔑 Page Access Token:", "", type="password")
image_url = st.text_input("🖼 Image URL:", "")
caption = st.text_area("✏ Caption:", "")

# -------------------------------------------------------
# IG POSTING PROCESS
# -------------------------------------------------------
def create_media(instagram_id, image_url, caption, token):
    url = f"https://graph.facebook.com/v19.0/{instagram_id}/media"
    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": token
    }
    return requests.post(url, data=payload).json()

def publish_media(instagram_id, creation_id, token):
    url = f"https://graph.facebook.com/v19.0/{instagram_id}/media_publish"
    payload = {
        "creation_id": creation_id,
        "access_token": token
    }
    return requests.post(url, data=payload).json()

# -------------------------------------------------------
# POST BUTTON
# -------------------------------------------------------
if st.button("🚀 Post to Instagram"):
    if not instagram_id or not page_token or not image_url:
        st.error("Please enter Instagram ID, Page Token, and Image URL.")
    else:
        st.info("⏳ Creating IG Media Container...")

        media_response = create_media(instagram_id, image_url, caption, page_token)
        st.write("📦 Media Response:", media_response)

        if "id" in media_response:
            creation_id = media_response["id"]
            st.success("Media container created! Publishing now...")

            publish_response = publish_media(instagram_id, creation_id, page_token)
            st.write("🚀 Publish Response:", publish_response)

            if "id" in publish_response:
                st.success("✅ Post Successfully Published on Instagram!")
            else:
                st.error("❌ Failed to publish media. Check error above.")
        else:
            st.error("❌ Media container creation failed. Check error above.")
