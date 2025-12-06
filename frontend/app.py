import os
import io
import json
import time
from datetime import datetime
import streamlit as st
import pandas as pd
import requests
from PIL import Image
from openai import OpenAI


# ------------------------------
# STATIC KEYS
# ------------------------------
HF_TOKEN = "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"
HF_API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
HF_HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

IMGBB_KEY = "ee6addbb49443065a9f58ac5491b173a"


# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------
st.set_page_config(page_title="AI Social Media Bot", layout="wide")


# ----------------------------------------------------
# LOGIN SYSTEM
# ----------------------------------------------------
def ensure_auth():
    if "auth" not in st.session_state:
        st.session_state.auth = {"ok": False, "user": None}


ensure_auth()

with st.sidebar:
    st.title("🔐 Login")

    if not st.session_state.auth["ok"]:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if u.strip() and p.strip():
                st.session_state.auth = {"ok": True, "user": u}
                st.rerun()
            else:
                st.error("Enter valid login details")

    else:
        st.success(f"Logged in as **{st.session_state.auth['user']}**")
        if st.button("Logout"):
            st.session_state.auth = {"ok": False, "user": None}
            st.rerun()

    st.markdown("---")
    st.title("🔗 OpenAI API")
    api_key = st.text_input("OpenAI API Key", type="password")

    if st.button("Connect OpenAI"):
        if api_key.strip():
            st.session_state["api_key"] = api_key.strip()
            st.success("Connected!")
        else:
            st.error("Invalid API Key")

if not st.session_state.auth["ok"]:
    st.stop()


# ----------------------------------------------------
# SESSION STORE
# ----------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []


# ----------------------------------------------------
# OPENAI CLIENT
# ----------------------------------------------------
def get_client():
    if "api_key" not in st.session_state:
        st.error("Add OpenAI API Key first")
        return None
    try:
        return OpenAI(api_key=st.session_state["api_key"])
    except:
        st.error("Invalid API Key")
        return None


# ----------------------------------------------------
# BLANK IMAGE (fallback image)
# ----------------------------------------------------
def generate_blank_image():
    img = Image.new("RGB", (800, 800), (255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# ----------------------------------------------------
# AI CAPTION GENERATOR
# ----------------------------------------------------
def ai_caption(client, idea, tone):
    prompt = f"""
You are a world-class social media strategist.
Create a caption + hashtags.

IDEA: {idea}
TONE: {tone}

Return ONLY JSON:
{{
  "caption":"...",
  "hashtags":["#a","#b"]
}}
"""

    safe = prompt.encode("utf-8", "ignore").decode()
    r = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": safe}]
    )
    text = r.choices[0].message.content

    import re
    block = re.search(r"\{[\s\S]*\}", text)
    return json.loads(block.group(0)) if block else {"caption": text, "hashtags": []}


# ----------------------------------------------------
# TRENDING TAGS
# ----------------------------------------------------
def trending_tags(client, topic):
    prompt = f"Give 5 trending hashtags for {topic}. Return only list."

    r = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    import re
    block = re.search(r"\[[\s\S]*\]", r.choices[0].message.content)
    return json.loads(block.group(0)) if block else ["#trend", "#viral", "#explore", "#daily", "#update"]


# ----------------------------------------------------
# FLUX IMAGE GENERATOR
# ----------------------------------------------------
def generate_flux_image(prompt):
    try:
        r = requests.post(
            HF_API_URL,
            headers=HF_HEADERS,
            json={"inputs": prompt},
            timeout=200
        )
        return r.content if r.status_code == 200 else None
    except:
        return None


# ----------------------------------------------------
# UPLOAD TEMP IMAGE (For IG/Twitter)
# ----------------------------------------------------
def upload_temp_image(img_bytes):
    try:
        r = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": IMGBB_KEY},
            files={"image": img_bytes}
        )
        return r.json()["data"]["url"] if r.status_code == 200 else None
    except:
        return None


# ----------------------------------------------------
# FACEBOOK POST
# ----------------------------------------------------
def post_to_facebook(img_bytes, caption, token, page_id):
    try:
        r = requests.post(
            f"https://graph.facebook.com/{page_id}/photos",
            files={"source": ("image.jpg", img_bytes, "image/jpeg")},
            data={"caption": caption, "access_token": token}
        )
        return (True, "Facebook: Posted ✔️") if r.status_code == 200 else (False, r.text)
    except Exception as e:
        return False, str(e)


# ----------------------------------------------------
# INSTAGRAM POST
# ----------------------------------------------------
def post_to_instagram(img_bytes, caption, token, ig_id):

    public_url = upload_temp_image(img_bytes)
    if not public_url:
        return False, "❌ Cannot upload temp image"

    create_url = f"https://graph.facebook.com/v18.0/{ig_id}/media"
    payload = {"image_url": public_url, "caption": caption, "access_token": token}
    r = requests.post(create_url, data=payload)

    if r.status_code != 200:
        return False, r.text

    media_id = r.json().get("id")

    status_url = f"https://graph.facebook.com/v18.0/{media_id}?fields=status_code&access_token={token}"
    for _ in range(12):
        if requests.get(status_url).json().get("status_code") == "FINISHED":
            break
        time.sleep(1)

    publish_url = f"https://graph.facebook.com/v18.0/{ig_id}/media_publish"
    pr = requests.post(publish_url, data={"creation_id": media_id, "access_token": token})

    return (True, "Instagram: Posted ✔️") if pr.status_code == 200 else (False, pr.text)


# ----------------------------------------------------
# BEST TIME AI
# ----------------------------------------------------
def get_best_time(client, niche):
    prompt = f"Give best posting times for Facebook and Instagram for niche: {niche}"
    r = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content


# ----------------------------------------------------
# TWITTER PAID (Image + Caption)
# ----------------------------------------------------
def post_to_twitter_paid(img_bytes, caption, token, account_id):
    headers = {"Authorization": f"Bearer {token}"}

    upload_r = requests.post(
        "https://upload.twitter.com/1.1/media/upload.json",
        headers=headers,
        files={"media": img_bytes}
    )
    if upload_r.status_code != 200:
        return False, upload_r.text

    media_id = upload_r.json().get("media_id_string")

    tweet_r = requests.post(
        "https://api.twitter.com/2/tweets",
        headers=headers,
        json={
            "text": caption,
            "media": {"media_ids": [media_id]}
        }
    )

    return (True, "Twitter (Paid): Posted ✔️") if tweet_r.status_code in (200, 201) else (False, tweet_r.text)


# ----------------------------------------------------
# TWITTER FREE (Caption Only)
# ----------------------------------------------------
def post_to_twitter_free(caption, token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(
        "https://api.twitter.com/2/tweets",
        headers=headers,
        json={"text": caption}
    )
    return (True, "Twitter (Free): Posted ✔️") if r.status_code in (200, 201) else (False, r.text)


# ----------------------------------------------------
# UI
# ----------------------------------------------------
st.title("✨ AI Social Media Bot — ULTIMATE VERSION")

tab1, tab2 = st.tabs(["📸 Smart Posting", "📊 Dashboard"])


# ----------------------------------------------------
# TAB 1 — Smart Posting
# ----------------------------------------------------
with tab1:

    col1, col2 = st.columns([0.55, 0.45])

    # -------------------------
    # LEFT SIDE
    # -------------------------
    with col1:

        img_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

        idea = st.text_area("Base Idea")
        tone = st.selectbox("Tone", ["Friendly", "Bold", "Professional", "Funny"])

        if st.button("✨ Generate Caption"):
            client = get_client()
            if client:
                out = ai_caption(client, idea, tone)
                st.session_state["final_cap"] = out["caption"] + "\n\n" + " ".join(out["hashtags"])
                st.success("Caption Ready!")

        final_caption = st.text_area("Final Caption", st.session_state.get("final_cap", ""))

        if st.button("🔥 Trending Hashtags"):
            client = get_client()
            if client:
                tags = trending_tags(client, idea)
                st.text_area("Hashtags", "\n".join(tags))

        st.markdown("---")
        st.subheader("🎨 Flux Image Generator")
        flux_prompt = st.text_input("Image Prompt")

        if st.button("Generate Flux"):
            img_bytes = generate_flux_image(flux_prompt)
            if img_bytes:
                st.image(Image.open(io.BytesIO(img_bytes)))
                st.session_state["flux_image"] = img_bytes

        st.markdown("---")
        st.subheader("⏰ Best Posting Time (AI)")
        niche = st.text_input("Your Niche")

        if st.button("Get Best Time"):
            client = get_client()
            if client:
                st.info(get_best_time(client, niche))

    # -------------------------
    # RIGHT SIDE
    # -------------------------
    with col2:

        st.subheader("🌍 Posting Options")

        fb_token = st.text_input("Facebook / Instagram Token", type="password")
        fb_page_id = st.text_input("Facebook Page ID")
        ig_id = st.text_input("Instagram Business ID")

        st.markdown("---")

        st.subheader("🐦 Twitter Options")
        twitter_token = st.text_input("Twitter Bearer Token", type="password")
        twitter_account_id = st.text_input("Twitter Account ID")

        opt_tw_paid = st.checkbox("Post to Twitter (Paid - Image + Caption)")
        opt_tw_free = st.checkbox("Post to Twitter (Free - Caption Only)")

        st.markdown("---")

        opt_fb = st.checkbox("Post to Facebook")
        opt_ig = st.checkbox("Post to Instagram")

        st.markdown("---")
        opt_caption_only = st.checkbox("Post even without image (Caption-only mode)")

        if st.button("🚀 POST NOW"):

            if not final_caption.strip():
                st.error("Caption cannot be empty")
            else:

                # IMAGE HANDLING
                if img_file:
                    img_bytes = img_file.read()
                else:
                    img_bytes = generate_blank_image() if opt_caption_only else None

                # FACEBOOK
                if opt_fb:
                    ok, msg = post_to_facebook(img_bytes, final_caption, fb_token, fb_page_id)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

                # INSTAGRAM
                if opt_ig:
                    ok, msg = post_to_instagram(img_bytes, final_caption, fb_token, ig_id)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

                # TWITTER PAID
                if opt_tw_paid:
                    ok, msg = post_to_twitter_paid(img_bytes, final_caption, twitter_token, twitter_account_id)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

                # TWITTER FREE
                if opt_tw_free:
                    ok, msg = post_to_twitter_free(final_caption, twitter_token)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

                # HISTORY
                st.session_state.history.append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "caption": final_caption[:60],
                    "platforms":
                        ("FB " if opt_fb else "") +
                        ("IG " if opt_ig else "") +
                        ("X(Paid) " if opt_tw_paid else "") +
                        ("X(Free) " if opt_tw_free else "")
                })


# ----------------------------------------------------
# TAB 2 — Dashboard
# ----------------------------------------------------
with tab2:
    st.subheader("📊 Posting History")

    if len(st.session_state.history) == 0:
        st.info("No posts yet")
    else:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, use_container_width=True)
