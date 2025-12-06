import streamlit as st
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

st.set_page_config(page_title="Twitter Poster", layout="centered")
st.title("🐦 Twitter Auto Poster (2025 Working Fix)")


tweet_text = st.text_area("Your Tweet:", "Testing autopost ✔")


def attach_chrome():
    try:
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        return webdriver.Chrome(options=options)
    except:
        return None


def post_tweet(text):
    try:
        driver = attach_chrome()
        if driver is None:
            return {"error": "Chrome not connected. Run Chrome with port 9222."}

        # 🚀 OPEN THE HIDDEN WORKING TWEET COMPOSER
        driver.get("https://x.com/i/flow/create/tweet")
        time.sleep(4)

        # CLICK TEXTBOX FIRST
        box = driver.find_element(By.XPATH, "//div[@contenteditable='true']")
        box.click()
        time.sleep(1)

        # TYPE THE TWEET
        box.send_keys(text)
        time.sleep(1)

        # CLICK THE BUTTON (NEW 2025 SELECTOR)
        post_btn = driver.find_element(By.XPATH, "//button[@data-testid='tweetButton']")
        post_btn.click()
        time.sleep(2)

        return {"success": True, "message": "Tweet posted successfully ✔"}

    except Exception as e:
        return {"error": str(e)}



if st.button("🚀 POST TWEET"):
    st.info("Posting...")
    res = post_tweet(tweet_text)
    st.json(res)
