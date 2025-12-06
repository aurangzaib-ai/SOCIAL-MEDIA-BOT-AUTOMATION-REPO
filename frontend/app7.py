import streamlit as st
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

st.set_page_config(page_title="Twitter Auto Poster", layout="centered")
st.title("🐦 Twitter Auto Poster (Real Chrome Session)")

tweet = st.text_area("✏️ Your Tweet:", "Testing Tweet via Selenium ✔")

def attach_chrome():
    try:
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        st.error(f"Chrome attach error: {e}")
        return None

# Universal selectors
TEXTBOX = "//div[@contenteditable='true']"

POST_BUTTONS = [
    "//button[@data-testid='tweetButton']",
    "//div[@data-testid='tweetButtonInline']",
    "//button[@data-testid='tweetButtonInline']",
    "//div[@data-testid='tweetButton']",
    "//span[text()='Post']/ancestor::button",
    "//span[text()='Tweet']/ancestor::button",
]

def find_post_button(driver):
    for selector in POST_BUTTONS:
        try:
            btn = driver.find_element(By.XPATH, selector)
            return btn
        except:
            pass
    return None

def post_tweet(text):
    try:
        driver = attach_chrome()
        if driver is None:
            return {"error": "Chrome NOT connected. Run with debugging mode."}

        # IMPORTANT → New working composer page
        driver.get("https://x.com/compose/post")
        time.sleep(4)

        # Type into tweet textbox
        box = driver.find_element(By.XPATH, TEXTBOX)
        box.click()
        time.sleep(1)
        box.send_keys(text)

        # Post button detection
        btn = find_post_button(driver)
        if btn is None:
            return {"error": "Post button not found. Layout issue."}

        btn.click()
        time.sleep(2)

        return {"success": True, "message": "Tweet posted successfully ✔🔥"}

    except Exception as e:
        return {"error": str(e)}


if st.button("🚀 POST TWEET"):
    st.info("Posting…")
    res = post_tweet(tweet)
    st.json(res)
