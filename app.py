import streamlit as st
import sqlite3
import time
import google.generativeai as genai

# ==========================================================
# PAGE CONFIG (MUST be first Streamlit command)
# ==========================================================
st.set_page_config(
    page_title="🌾 Smart Farming AI Assistant",
    page_icon="🌴",
    layout="centered"
)

# ==========================================================
# GEMINI SETUP (via Streamlit Secrets)
# ==========================================================
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ GEMINI_API_KEY missing. Add it in Streamlit → Manage App → Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

PRIMARY_MODEL = "models/gemini-2.5-flash"

# ==========================================================
# SQLITE DATABASE
# ==========================================================
DB_FILE = "farmers.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
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
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO farmers
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, district, age, language, farming_type, experience))
    conn.commit()
    conn.close()

def get_user(name):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM farmers WHERE name=?", (name,))
    row = cur.fetchone()
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
# UI STYLE
# ==========================================================
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #1b4332, #081c15); color: white; }
.stButton>button {
    background-color: #52b788;
    color: white;
    font-weight: bold;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# GEMINI CALL
# ==========================================================
def get_ai_response(prompt, temperature, max_tokens):
    time.sleep(1)  # rate-limit safety
    try:
        model = genai.GenerativeModel(PRIMARY_MODEL)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
        )
        return response.text
    except Exception as e:
        return f"⚠️ Error: {e}"

# ==========================================================
# SIDEBAR SETTINGS
# ==========================================================
st.sidebar.header("⚙️ AI Settings")
temperature = st.sidebar.slider("Creativity", 0.0, 1.0, 0.5, 0.1)
max_tokens = 1200
st.sidebar.markdown(f"**Max Tokens:** {max_tokens}")

# ==========================================================
# HEADER
# ==========================================================
st.title("🌴 Smart Farming AI Assistant — Kerala Edition")
st.caption("FA-2 | Gemini-powered | Streamlit Deployment 🌾")

# ==========================================================
# LOGIN / SIGN UP
# ==========================================================
if "current_user" not in st.session_state:
    choice = st.radio("Login or Sign Up", ["Login", "Sign Up"])

    if choice == "Login":
        name = st.text_input("Name")
        if st.button("Login 🚜"):
            user = get_user(name)
            if user:
                st.session_state.current_user = name
                st.rerun()
            else:
                st.error("User not found")

    else:
        with st.form("signup"):
            name = st.text_input("Name")
            district = st.text_input("District")
            age = st.number_input("Age", 10, 100)
            language = st.selectbox("Language", ["English", "Malayalam", "Both"])
            farming_type = st.selectbox("Farming Type",
                                        ["Paddy", "Coconut", "Spices", "Vegetables", "Mixed"])
            experience = st.selectbox("Experience",
                                      ["Beginner", "Intermediate", "Expert"])
            submit = st.form_submit_button("Create Profile")

            if submit and name:
                add_user(name, district, age, language, farming_type, experience)
                st.session_state.current_user = name
                st.rerun()

# ==========================================================
# MAIN APP
# ==========================================================
if "current_user" in st.session_state:
    user = get_user(st.session_state.current_user)

    st.markdown(f"### 👋 Hello {user['name']} from {user['district']}")

    challenges = {
        "Waterlogging": "Monsoon floods damage my paddy field every year. What can I do?",
        "Coconut Pests": "My coconut trees are affected by red palm weevil.",
        "Soil Acidity": "My soil is acidic. Which crops are suitable?",
        "Pepper Prices": "Pepper prices keep fluctuating. Should I sell now?",
        "Seasonal Crops": "It’s September. What should I grow in Kerala?"
    }

    mode = st.radio("Mode", ["Choose Challenge", "Ask Own Question"])

    if mode == "Choose Challenge":
        question = challenges[st.selectbox("Select", challenges.keys())]
    else:
        question = st.text_area("Your Question")

    if st.button("🌱 Get AI Advice"):
        prompt = f"""
You are an agriculture expert for Kerala farmers.
Give short, actionable advice with reasons.
Use bullet points. Simple language.

Farmer Info:
District: {user['district']}
Experience: {user['experience']}

Question: {question}
"""
        with st.spinner("Thinking..."):
            st.markdown(get_ai_response(prompt, temperature, max_tokens))

    if st.button("Logout 🔒"):
        del st.session_state.current_user
        st.rerun()

st.markdown("<center>🌾 FA-2 Smart Farming Assistant | Streamlit Cloud</center>",
            unsafe_allow_html=True)
