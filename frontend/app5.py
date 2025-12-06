import streamlit as st
import requests

st.set_page_config(page_title="FB Auto Post Tester", layout="centered")

st.title("📘 Facebook Auto Posting Tester (LIVE)")
st.write("Post an image to your **Facebook Page** using your Page Access Token.")

# -------------------------------------------------------
# 🔹 Input Fields
# -------------------------------------------------------
page_id = st.text_input("📄 Facebook Page ID:", "910572598805012")
token = st.text_input("🔑 Page Access Token:", "", type="password")
image_url = st.text_input("🖼 Image URL:", "https://images.unsplash.com/photo-1623387641168-d9803ddd3f35?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D")
caption = st.text_area("✏ Caption:", "🔥 Streamlit Auto Post Test – SUCCESSFUL via Python!")

# -------------------------------------------------------
# 🚀 POST Button
# -------------------------------------------------------
if st.button("🚀 Post to Facebook"):
    if not page_id or not token or not image_url:
        st.error("Please enter Page ID, Token, and Image URL")
    else:
        with st.spinner("Posting to Facebook… ⏳"):
            url = f"https://graph.facebook.com/{page_id}/photos"
            params = {
                "url": image_url,
                "caption": caption,
                "access_token": token
            }
            
            response = requests.post(url, params=params)
            result = response.json()

            st.subheader("📌 Facebook Response")
            st.code(result, language="json")

            if "id" in result:
                post_id = result["id"]
                fb_link = f"https://facebook.com/{post_id}"
                
                st.success("✅ Post Successfully Published!")
                st.markdown(f"👉 **View Post:** [{fb_link}]({fb_link})")

