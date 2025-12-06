# twitter_selenium.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import os

def twitter_post(message, image_bytes=None):
    """
    Posts a Tweet using Selenium & your logged-in Chrome profile.
    """
    try:
        chrome_options = Options()

        # IMPORTANT: Your Chrome Profile Path (edit only this)
        chrome_options.add_argument(r"user-data-dir=C:\Users\TOSHIBA\AppData\Local\Google\Chrome\User Data")
        chrome_options.add_argument("profile-directory=Default")

        chrome_options.add_argument("--start-maximized")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://x.com/home")
        time.sleep(5)

        # TYPE THE TWEET
        tweet_box = driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true']")
        tweet_box.send_keys(message)
        time.sleep(2)

        # OPTIONAL — UPLOAD IMAGE
        if image_bytes:
            image_path = "temp_twitter.jpg"
            with open(image_path, "wb") as f:
                f.write(image_bytes)

            file_input = driver.find_element(By.XPATH, "//input[@type='file']")
            file_input.send_keys(os.path.abspath(image_path))
            time.sleep(4)

        # CLICK POST BUTTON
        btn = driver.find_element(By.XPATH, "//span[text()='Post' or text()='Tweet']")
        btn.click()
        time.sleep(3)

        driver.quit()
        return True, "Tweet Posted Successfully!"

    except Exception as e:
        return False, f"Twitter Error: {str(e)}"
