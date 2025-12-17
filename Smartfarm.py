import streamlit as st
import sqlite3
import time
import os
import google.generativeai as genai

# ==========================================================
# GEMINI CLIENT SETUP (FIXED)
# ==========================================================
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="🌾 Smart Farming AI Assistant",
    page_icon="🌴",
    layout="centered"
)

PRIMARY_MODEL = "gemini-2.5-flash"

# ==========================================================
# SQLITE DATABASE FUNCTIONS (UNCHANGED)
# ==========================================================
DB_FILE = "farmers.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
            name TEXT PRIMARY KEY,
            district TEXT,
            age INTEGER,
            language TEXT,
            farming_type TEXT,
            experience TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_user(name, district, age, language, farming_type, experience):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO farmers (name, district, age, language, farming_type, experience)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, district, age, language, farming_type, experience))
    conn.commit()
    conn.close()

def get_user(name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM farmers WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "name": row[0],
            "district": row[1],
            "age": row[2],
            "language": row[3],
            "farming_type": row[4],
            "experience": row[5]
        }
    return None

init_db()

# ==========================================================
# PAGE STYLE (UNCHANGED)
# ==========================================================
st.markdown("""
<style>
body { background: linear-gradient(135deg, #1b4332, #081c15); color: white; }
.stButton>button {
    background-color: #52b788;
    color: white;
    font-weight: bold;
    border-radius: 10px;
}
.stButton>button:hover {
    background-color: #40916c;
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# AI CALL FUNCTION (FIXED, CLEAN, WORKING)
# ==========================================================
def get_ai_response(prompt, temperature, max_tokens):
    try:
        response = client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"⚠️ Error: {e}"

# ==========================================================
# SIDEBAR SETTINGS
# ==========================================================
st.sidebar.header("⚙️ AI Settings")

temperature = st.sidebar.slider(
    "Creativity (Temperature)", 0.0, 1.0, 0.5, 0.1
)

max_tokens = 2000
st.sidebar.markdown(f"**Max Output Tokens:** {max_tokens}")
st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Tips:**\n"
    "- Lower temperature = More consistent\n"
    "- Higher tokens = Longer responses\n"
    "- Allow 3–5s between requests"
)

# ==========================================================
# APP HEADER
# ==========================================================
st.title("🌴 Smart Farming AI Assistant — Kerala Edition")
st.caption("Powered by Gemini 2.5 Flash — Accurate, Fast & Bilingual 🌾")

# ==========================================================
# LOGIN / SIGN UP
# ==========================================================
if "current_user" not in st.session_state:
    st.subheader("👩‍🌾 Login or Sign Up")
    choice = st.radio("Select option:", ["Login", "Sign Up"])

    if choice == "Login":
        name = st.text_input("Enter your name:")
        if st.button("Login 🚜"):
            user = get_user(name)
            if user:
                st.session_state.current_user = name
                st.success(f"Welcome back, {name}! 🌴")
                st.rerun()
            else:
                st.error("User not found. Please sign up first.")

    else:
        with st.form("signup"):
            st.markdown("### 🧾 Farmer Details")
            name = st.text_input("Name:")
            district = st.text_input("District:")
            age = st.number_input("Age:", 10, 100)
            language = st.selectbox("Preferred Language:", ["English", "Malayalam", "Both"])
            farming_type = st.selectbox("Type of Farming:", ["Paddy", "Coconut", "Spices", "Vegetables", "Mixed"])
            experience = st.selectbox("Experience Level:", ["Beginner", "Intermediate", "Expert"])
            submit = st.form_submit_button("Create Profile 🌾")

            if submit:
                if name.strip() == "":
                    st.error("Name cannot be empty.")
                else:
                    add_user(name, district, age, language, farming_type, experience)
                    st.session_state.current_user = name
                    st.success("Profile created successfully! 🌿")
                    st.rerun()

# ==========================================================
# MAIN APP
# ==========================================================
if "current_user" in st.session_state:
    user = get_user(st.session_state.current_user)

    st.markdown(f"### 👋 Hello {user['name']} from {user['district']}!")
    st.caption(f"Language: {user['language']} | Experience: {user['experience']} Farmer")

    challenges = {
        "Waterlogging & Heavy Rainfall": "Monsoon floods damage my paddy field every year. What can I do?",
        "Coconut Pests (Red Palm Weevil)": "My coconut trees are affected by red palm weevil pests. How to control them?",
        "Soil Acidity (Laterite Soil)": "My soil is acidic. Which crops will grow well?",
        "Pepper Price Fluctuations": "Pepper prices keep changing. Should I sell now?",
        "Seasonal Crop Choice": "It's September — what crops are best to grow in Kerala now?"
    }

    option = st.radio("Select mode:", ["🧠 Choose Challenge", "✍️ Ask My Own Question"])

    user_question = (
        challenges[st.selectbox("Select a challenge:", challenges)]
        if option == "🧠 Choose Challenge"
        else st.text_area("Enter your farming question:")
    )

    if st.button("🌱 Get AI Advice"):
        if not user_question.strip():
            st.warning("❗ Please enter or select a question.")
        else:
            prompt = f"""
You are an agriculture expert for Kerala.

Give short, practical farming advice in {user['language']}.
Explain reasons briefly.
Use bullet points.
Max 250 words.

User:
Name: {user['name']}
District: {user['district']}
Farming Type: {user['farming_type']}
Experience: {user['experience']}

Question: {user_question}
"""
            with st.spinner("🌿 Generating advisory..."):
                reply = get_ai_response(prompt, temperature, max_tokens)

            if "⚠️" not in reply:
                st.success("✅ AI Response Ready!")
            st.markdown(reply)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📚 View My Profile"):
            st.json(user)

    with col2:
        if st.button("Logout 🔒"):
            del st.session_state.current_user
            st.rerun()

st.markdown(
    "<center>🌴 Built for Kerala's Smart Farmers | Powered by Gemini</center>",
    unsafe_allow_html=True
)

