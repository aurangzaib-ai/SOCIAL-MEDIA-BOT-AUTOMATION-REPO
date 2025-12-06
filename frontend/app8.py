import os
import io
import json
import time
import tempfile
import requests
import streamlit as st
import pandas as pd
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI

# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


# ----------------------------------------------------
# LOAD ENV
# ----------------------------------------------------
load_dotenv()

HF_TOKEN = "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"
HF_API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
HF_HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

IMGBB_KEY = "ee6addbb49443065a9f58ac5491b173a"


# ----------------------------------------------------
# GLOBAL STYLE
# ----------------------------------------------------
st.set_page_config(page_title="AI Social Media Bot", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(120deg,#eaf4ff,#ffffff,#eef6ff);
}
.stButton>button {
    background:#0066ff; color:white;
    border-radius:10px; padding:8px 25px; font-size:16px;
}
textarea, input { border-radius:10px !important; }
</style>
""", unsafe_allow_html=True)



# ----------------------------------------------------
# AUTH SYSTEM
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
            if u and p:
                st.session_state.auth = {"ok": True, "user": u}
                st.rerun()
            else:
                st.error("Enter valid credentials")
    else:
        st.success(f"Logged in as **{st.session_state.auth['user']}**")
        if st.button("Logout"):
            st.session_state.auth = {"ok": False, "user": None}
            st.rerun()

if not st.session_state.auth["ok"]:
    st.stop()



# ----------------------------------------------------
# SESSION STORE
# ----------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "api_key" not in st.session_state:
    st.session_state.api_key = ""



# ----------------------------------------------------
# API KEY HANDLING
# ----------------------------------------------------
st.sidebar.title("🔗 OpenAI API Key")

key_in = st.sidebar.text_input("Enter Key", type="password")

if st.sidebar.button("Connect Key"):
    st.session_state.api_key = key_in
    st.sidebar.success("Connected ✔")



# ----------------------------------------------------
# OPENAI CLIENT
# ----------------------------------------------------
def get_client():
    key = st.session_state.api_key
    if not key:
        st.error("Missing OpenAI Key")
        return None
    try:
        return OpenAI(api_key=key)
    except:
        st.error("Invalid API Key")
        return None



# ----------------------------------------------------
# SAVE HISTORY
# ----------------------------------------------------
def save_history(platform, status, caption, img_name):
    st.session_state.history.append({
        "platform": platform,
        "status": status,
        "caption": caption[:50] + "...",
        "image": img_name,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    })



# ----------------------------------------------------
# AI CAPTION
# ----------------------------------------------------
def ai_caption(client, idea, tone):
    prompt = f"""
Create a high-converting caption.

IDEA: {idea}
TONE: {tone}

Return ONLY JSON:
{{ "caption":"...", "hashtags":["#a","#b"] }}
"""
    r = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role":"user","content":prompt}]
    )
    txt = r.choices[0].message.content

    import re, json
    block = re.search(r"\{[\s\S]*\}", txt)
    if block:
        return json.loads(block.group(0))
    return {"caption": txt, "hashtags":[]}



# ----------------------------------------------------
# TRENDING TAGS
# ----------------------------------------------------
def trending_tags(client, topic):
    prompt = f"Give top 5 hashtags for {topic} in JSON list."
    r = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role":"user","content":prompt}]
    )
    import re, json
    block = re.search(r"\[[\s\S]*\]", r.choices[0].message.content)
    if block:
        return json.loads(block.group(0))
    return []


# ----------------------------------------------------
# Flux Image Generator
# ----------------------------------------------------
def generate_flux_image(prompt):
    try:
        payload = {"inputs": prompt}
        r = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload, timeout=200)
        if r.status_code == 200:
            return r.content
        return None
    except:
        return None



# ----------------------------------------------------
# IMG-BB UPLOAD → PUBLIC URL
# ----------------------------------------------------
def upload_temp_image(img_bytes):
    url = "https://api.imgbb.com/1/upload"
    payload = {"key": IMGBB_KEY}
    files = {"image": img_bytes}
    r = requests.post(url, data=payload, files=files)
    if r.status_code == 200:
        return r.json()["data"]["url"]
    return None



# ----------------------------------------------------
# FACEBOOK POSTING
# ----------------------------------------------------
def post_to_facebook(img_bytes, caption, token, page_id):
    try:
        url = f"https://graph.facebook.com/{page_id}/photos"
        files = {"source":("image.jpg", img_bytes, "image/jpeg")}
        data = {"caption":caption, "access_token":token}
        r = requests.post(url, files=files, data=data)
        if r.status_code == 200:
            return True, "Facebook: Posted ✔"
        return False, r.text
    except Exception as e:
        return False, str(e)



# ----------------------------------------------------
# INSTAGRAM POSTING
# ----------------------------------------------------
def post_to_instagram(img_bytes, caption, token, ig_id):

    # Step 1 — Upload to ImgBB
    public_url = upload_temp_image(img_bytes)
    if not public_url:
        return False, "Could NOT upload to ImgBB!"

    # Step 2 — Create container
    create = f"https://graph.facebook.com/v18.0/{ig_id}/media"
    payload = {"image_url":public_url,"caption":caption,"access_token":token}

    r = requests.post(create, data=payload)
    if r.status_code != 200:
        return False, r.text

    media_id = r.json().get("id")

    # Step 3 — Wait for READY
    status_url = f"https://graph.facebook.com/v18.0/{media_id}?fields=status_code&access_token={token}"

    for _ in range(12):
        s = requests.get(status_url).json().get("status_code")
        if s == "FINISHED":
            break
        time.sleep(1)

    # Step 4 — Publish
    pub = f"https://graph.facebook.com/v18.0/{ig_id}/media_publish"
    rr = requests.post(pub, data={"creation_id":media_id,"access_token":token})

    if rr.status_code == 200:
        return True, "Instagram: Posted ✔"
    return False, rr.text



# ----------------------------------------------------
# TWITTER POSTING
# ----------------------------------------------------
CHROME_DRIVER = r"C:\Users\LAPTOP  OUTLET\Downloads\social media app\frontend\chromedriver-win64\chromedriver.exe"

def post_to_twitter(tw_user, tw_pass, post_caption, img_bytes):
    try:
        # Save temporary image
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_img.write(img_bytes)
        temp_img.close()

        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--start-maximized")

        # ⭐ Selenium v4 FIX — correct way
        service = Service(CHROME_DRIVER)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get("https://twitter.com/login")
        time.sleep(5)

        # Username
        user_box = driver.find_element(By.NAME, "text")
        user_box.send_keys(tw_user)
        user_box.send_keys(Keys.ENTER)
        time.sleep(3)

        # Password
        pass_box = driver.find_element(By.NAME, "password")
        pass_box.send_keys(tw_pass)
        pass_box.send_keys(Keys.ENTER)
        time.sleep(5)

        # Tweet Box
        tweet_box = driver.find_element(By.XPATH, "//div[@aria-label='Tweet text']")
        tweet_box.send_keys(post_caption)
        time.sleep(2)

        # Upload image
        upload_btn = driver.find_element(By.XPATH, "//input[@type='file']")
        upload_btn.send_keys(temp_img.name)
        time.sleep(4)

        # Tweet
        post_button = driver.find_element(By.XPATH, "//div[@data-testid='tweetButtonInline']")
        post_button.click()

        time.sleep(5)
        driver.quit()

        return True, "🐦 Twitter: Tweet Posted Successfully ✔️"

    except Exception as e:
        return False, f"❌ Twitter Error: {str(e)}"


        # ---- CHROME OPTIONS ----
        chrome_opts = Options()
        chrome_opts.add_argument("--disable-blink-features=AutomationControlled")
        chrome_opts.add_argument("--start-maximized")

        # ---- CORRECT WEBDRIVER INITIALIZATION ----
        driver_path = ChromeDriverManager().install()
        service = Service(driver_path)

        driver = webdriver.Chrome(service=service, options=chrome_opts)

        driver.get("https://twitter.com/login")
        time.sleep(6)

        # Username
        box = driver.find_element(By.NAME, "text")
        box.send_keys(tw_user)
        box.send_keys(Keys.ENTER)
        time.sleep(3)

        # Password
        box = driver.find_element(By.NAME, "password")
        box.send_keys(tw_pass)
        box.send_keys(Keys.ENTER)
        time.sleep(6)

        # Tweet Box
        tweet = driver.find_element(By.XPATH, "//div[@aria-label='Tweet text']")
        tweet.send_keys(caption)
        time.sleep(2)

        # Upload image
        upload = driver.find_element(By.XPATH, "//input[@type='file']")
        upload.send_keys(temp_path)
        time.sleep(4)

        # Tweet Button
        btn = driver.find_element(By.XPATH, "//div[@data-testid='tweetButtonInline']")
        btn.click()

        time.sleep(4)
        driver.quit()

        return True, "Twitter: Tweet Posted Successfully ✔️"

    except Exception as e:
        return False, f"❌ Twitter Error: {str(e)}"

        # Username
        box = driver.find_element(By.NAME, "text")
        box.send_keys(tw_user)
        box.send_keys(Keys.ENTER)
        time.sleep(3)

        # Password
        box = driver.find_element(By.NAME, "password")
        box.send_keys(tw_pass)
        box.send_keys(Keys.ENTER)
        time.sleep(5)

        # Tweet Box
        tweet = driver.find_element(By.XPATH, "//div[@aria-label='Tweet text']")
        tweet.send_keys(caption)
        time.sleep(2)

        # Upload image
        upload = driver.find_element(By.XPATH, "//input[@type='file']")
        upload.send_keys(temp.name)
        time.sleep(4)

        # Post button
        btn = driver.find_element(By.XPATH, "//div[@data-testid='tweetButtonInline']")
        btn.click()

        time.sleep(4)
        driver.quit()

        return True, "Twitter: Tweet Posted ✔"

    except Exception as e:
        return False, str(e)



# ----------------------------------------------------
# MAIN UI
# ----------------------------------------------------
st.title("✨ AI Social Media Bot — FINAL VERSION")

tab1, tab2, tab3 = st.tabs(["📸 Auto Posting", "🤖 Agentic AI", "📊 History"])



# ----------------------------------------------------
# TAB 1 — AUTO POSTING
# ----------------------------------------------------
with tab1:

    left, right = st.columns([0.58, 0.42])

    # LEFT SIDE ----------------------------------
    with left:
        img_file = st.file_uploader("Upload Image", ["jpg","jpeg","png"], key="imgA")
        idea = st.text_area("Base Idea")
        tone = st.selectbox("Tone", ["Friendly","Bold","Professional","Funny"])

        if st.button("✨ Generate Caption"):
            client = get_client()
            if client:
                out = ai_caption(client, idea, tone)
                final = out["caption"] + "\n\n" + " ".join(out["hashtags"])
                st.session_state["cap_final"] = final
                st.success("Caption Ready ✔")

        final_cap = st.text_area("Final Caption", st.session_state.get("cap_final",""))

        if st.button("🔥 Trending Hashtags"):
            client = get_client()
            if client:
                tags = trending_tags(client, idea)
                st.text_area("Hashtags", "\n".join(tags))

        st.markdown("---")
        st.subheader("🎨 Flux Image Generator")
        fp = st.text_input("Prompt")
        if st.button("Generate Image"):
            img_bytes = generate_flux_image(fp)
            if img_bytes:
                st.image(Image.open(io.BytesIO(img_bytes)))



    # RIGHT SIDE ---------------------------------
    with right:
        st.subheader("🚀 FB + IG Posting")

        fb_token = st.text_input("Facebook Token", type="password")
        fb_page = st.text_input("Facebook Page ID")
        ig_id = st.text_input("Instagram Business ID")

        img2 = st.file_uploader("Upload Posting Image", ["jpg","jpeg","png"], key="postIMG")
        cap2 = st.text_area("Posting Caption", st.session_state.get("cap_final",""))

        if st.button("🚀 POST TO BOTH"):
            if img2:
                b = img2.read()

                ok1, msg1 = post_to_facebook(b, cap2, fb_token, fb_page)
                save_history("Facebook", msg1, cap2, img2.name)

                ok2, msg2 = post_to_instagram(b, cap2, fb_token, ig_id)
                save_history("Instagram", msg2, cap2, img2.name)

                st.success(msg1)
                st.success(msg2)
            else:
                st.error("Upload image first")

        st.markdown("---")

        st.subheader("🐦 Twitter Posting")
        tu = st.text_input("Twitter Username")
        tp = st.text_input("Twitter Password", type="password")

        if st.button("🚀 POST TO TWITTER"):
            if img2:
                b = img2.read()
                ok, msg = post_to_twitter(tu, tp, cap2, b)
                save_history("Twitter", msg, cap2, img2.name)
                if ok: st.success(msg)
                else: st.error(msg)
            else:
                st.error("Upload image first")



# ----------------------------------------------------
# TAB 2 — AGENTIC AI
# ----------------------------------------------------
with tab2:
    st.subheader("🤖 Ask Agentic AI")
    q = st.text_area("Ask Anything")

    if st.button("Ask Now"):
        client = get_client()
        if client:
            r = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role":"user","content":q}]
            )
            st.success(r.choices[0].message.content)

    st.markdown("---")

    st.subheader("⏰ Best Posting Time")
    niche = st.text_input("Your Niche")

    if st.button("Best Time"):
        client = get_client()
        if client:
            prompt = f"Give best IG + FB posting times for: {niche}"
            r = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role":"user","content":prompt}]
            )
            st.info(r.choices[0].message.content)



# ----------------------------------------------------
# TAB 3 — HISTORY
# ----------------------------------------------------
with tab3:
    st.subheader("📊 Real Posting History")

    if len(st.session_state.history) == 0:
        st.info("No posts yet.")
    else:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "history.csv", "text/csv")
