import streamlit as st
import sqlite3
import requests
import json
from datetime import datetime

# ==========================================================
# PAGE CONFIG (MUST BE FIRST)
# ==========================================================
st.set_page_config(
    page_title="🌾 Smart Farming AI Assistant",
    page_icon="🌱",
    layout="centered"
)

# ==========================================================
# GEMINI API CONFIG (REST API)
# ==========================================================
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ GEMINI_API_KEY not found in Streamlit secrets")
    st.stop()

API_KEY = st.secrets["GEMINI_API_KEY"]
GEMINI_MODEL = "gemini-1.5-flash"

# ==========================================================
# DATABASE SETUP
# ==========================================================
DB_FILE = "farmers.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            location TEXT,
            crop TEXT,
            language TEXT,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER,
            user_msg TEXT,
            ai_msg TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ==========================================================
# GEMINI AI FUNCTION (REST)
# ==========================================================
def get_ai_response(prompt, temperature=0.4, max_tokens=400):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens
        }
    }

    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        params={"key": API_KEY},
        data=json.dumps(payload)
    )

    if response.status_code != 200:
        return "⚠️ Error connecting to AI service."

    try:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return "⚠️ AI returned no response."

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================
def save_farmer(name, location, crop, language):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO farmers (name, location, crop, language, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (name, location, crop, language, datetime.now().isoformat()))

    conn.commit()
    farmer_id = cursor.lastrowid
    conn.close()
    return farmer_id

def save_chat(farmer_id, user_msg, ai_msg):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chat_history (farmer_id, user_msg, ai_msg, timestamp)
        VALUES (?, ?, ?, ?)
    """, (farmer_id, user_msg, ai_msg, datetime.now().isoformat()))

    conn.commit()
    conn.close()

# ==========================================================
# UI – HEADER
# ==========================================================
st.title("🌾 Smart Farming AI Assistant")
st.caption("Helping farmers with crop advice, pests, soil & weather guidance")

# ==========================================================
# SIDEBAR – FARMER DETAILS
# ==========================================================
st.sidebar.header("👨‍🌾 Farmer Details")

name = st.sidebar.text_input("Farmer Name")
location = st.sidebar.text_input("Location")
crop = st.sidebar.text_input("Main Crop")
language = st.sidebar.selectbox("Preferred Language", ["English", "Tamil"])

start = st.sidebar.button("Start Assistant")

if start:
    if not name or not location or not crop:
        st.sidebar.error("Please fill all fields")
    else:
        farmer_id = save_farmer(name, location, crop, language)
        st.session_state.farmer_id = farmer_id
        st.session_state.chat_started = True
        st.success("✅ Assistant Ready")

# ==========================================================
# CHAT INTERFACE
# ==========================================================
if "chat_started" in st.session_state and st.session_state.chat_started:

    st.subheader("💬 Ask Your Farming Question")

    user_question = st.text_area(
        "Enter your question",
        placeholder="Example: Why are my rice leaves turning yellow?"
    )

    if st.button("Get Advice 🌱"):
        if user_question.strip() == "":
            st.warning("Please enter a question")
        else:
            lang_instruction = (
                "Answer only in Tamil."
                if language == "Tamil"
                else "Answer in simple English."
            )

            prompt = f"""
You are an agricultural expert.

Farmer details:
Location: {location}
Crop: {crop}

Instruction:
{lang_instruction}

Question:
{user_question}

Give clear, practical advice for farmers.
"""

            with st.spinner("🤖 Thinking..."):
                ai_response = get_ai_response(prompt)

            save_chat(
                st.session_state.farmer_id,
                user_question,
                ai_response
            )

            st.markdown("### 🌾 AI Advice")
            st.write(ai_response)

# ==========================================================
# FOOTER
# ==========================================================
st.markdown("---")
st.caption("📚 Educational AI Project | Built with Streamlit & Gemini API")
