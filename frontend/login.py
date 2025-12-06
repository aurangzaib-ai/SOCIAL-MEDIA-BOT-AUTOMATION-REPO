# login_page.py — SOCIAL MEDIA BOT
# Professional login interface
# On success -> switch to main_app.py

import os, json, hashlib
from datetime import datetime
import streamlit as st

APP_NAME = "SOCIAL MEDIA BOT"
DATA_DIR = "./data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")

st.set_page_config(page_title=f"{APP_NAME} — Login", layout="centered")

# ---------- Styles - Professional Background ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
html, body, [class*="css"] {
  font-family: 'Poppins', sans-serif;
}
.stApp {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  color: #2c3e50;
}
.card {
  background: rgba(255,255,255,0.95);
  padding: 36px 40px;
  width: 420px;
  margin: 8vh auto;
  border-radius: 16px;
  border: 1px solid rgba(52,152,219,0.2);
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  color: #2c3e50;
}
.card h2 { margin: 0 0 6px 0; color: #2c3e50; }
.sub { margin: 0 0 20px 0; color: #7f8c8d; font-size: 14px; }
.stButton>button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  font-weight: 700;
  border-radius: 10px;
  padding: 10px 14px;
  width: 100%;
}
.stTextInput>div>div>input, .stPassword>div>div>input {
  background: #f8f9fa !important;
  color: #2c3e50 !important;
  border-radius: 10px !important;
  border: 1px solid #e0e0e0 !important;
}
a, .stMarkdown a { color: #3498db; text-decoration: none; }
.title-wrap { text-align:center; margin-top: 6vh; }
.title { font-size: 28px; font-weight: 700; color: #2c3e50; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

# ---------- Storage helpers ----------
def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": {}}, f)

def load_users():
    ensure_storage()
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

data = load_users()

# Create default user "alexis" if not exists
if "alexis" not in data.get("users", {}):
    data["users"]["alexis"] = {
        "full_name": "Alexis",
        "password_hash": hash_pw("123"),
        "created_at": datetime.utcnow().isoformat(),
        "openai_key": "",
        "selected_accounts": [],
        "connections": {
            "facebook": {"page_id": "", "page_token": ""},
            "instagram": {"user_id": "", "access_token": ""},
            "twitter": {"api_key": "", "api_secret": "", "access_token": "", "access_token_secret": ""}
        },
        "location_pref": {"mode":"Global","city":"","country":"","latitude":"","longitude":""},
        "history": [],
        "scheduled": []
    }
    save_users(data)

has_any_user = len(data.get("users", {})) > 0

st.markdown(f"<div class='title-wrap'><div class='title'>{APP_NAME}</div></div>", unsafe_allow_html=True)

# ---------- Login ----------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<h2>Sign in</h2><div class='sub'>Access your dashboard</div>", unsafe_allow_html=True)
with st.form("login_form", clear_on_submit=False):
    username = st.text_input("Username", value="alexis")
    password = st.text_input("Password", type="password", value="123")
    submit   = st.form_submit_button("Login")
if submit:
    u = data["users"].get(username)
    if not u or u["password_hash"] != hash_pw(password):
        st.error("Invalid username or password.")
    else:
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.user_data = u
        st.success("Login successful.")
        st.switch_page("main_app.py")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<p style='text-align:center; color:#7f8c8d; margin-top:40px;'>Demo: Username: <b>alexis</b> | Password: <b>123</b></p>", unsafe_allow_html=True)
