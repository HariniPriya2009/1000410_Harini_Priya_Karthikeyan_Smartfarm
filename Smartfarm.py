##import google.generativeai as genai
##
### Put your API key INSIDE quotes
##genai.configure(api_key="AIzaSyAdNYlCRqzxjWQ485WHAzmLS6kz27vhnPE")
##
##try:
##    model = genai.GenerativeModel("gemini-2.5-flash")
##
##    response = model.generate_content("Write a short poem about sunshine.")
##
##    print("API Key is VALID ✓")
##    print("\nGemini Response:")
##    print(response.text)
##
##except Exception as e:
##    print("API Key is INVALID ✗")
##    print("Error:", e)
##



import streamlit as st
import sqlite3
import time
from google import genai
import os

client = genai.Client(api_key=os.getenv("AIzaSyAdNYlCRqzxjWQ485WHAzmLS6kz27vhnPE"))

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="🌾 Smart Farming AI Assistant",
    page_icon="🌴",
    layout="centered"
)

# ==========================================================
# GEMINI CONFIG
# ==========================================================
import os
##genai.configure(api_key=os.getenv("AIzaSyAdNYlCRqzxjWQ485WHAzmLS6kz27vhnPE"))

PRIMARY_MODEL = "models/gemini-2.5-flash"   # More stable model


# ==========================================================
# SQLITE DATABASE FUNCTIONS
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


# Initialize database
init_db()


# ==========================================================
# PAGE STYLE
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
# AI CALL FUNCTION WITH RETRY LOGIC
# ==========================================================
def get_ai_response(prompt, temperature, max_tokens):
    def get_ai_response(prompt, temperature, max_tokens):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"⚠️ Error: {e}"

    """Optimized & safe API call with retry logic and rate limit handling."""
    
 '''   config = genai.types.GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
    )

    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            # Add delay before each request
            time.sleep(3)
            
            model = genai.GenerativeModel(PRIMARY_MODEL)
            response = model.generate_content(
                prompt,
                generation_config=config,
                safety_settings={
                    "HARASSMENT": "BLOCK_NONE", 
                    "HATE": "BLOCK_NONE"
                }
            )'''
            
            # Extract text from response
            parts = response.candidates[0].content.parts
            return "".join([p.text for p in parts if hasattr(p, "text")])
            
        except Exception as e:
            error_str = str(e)
            
            # Handle rate limiting (429 error)
            if "429" in error_str and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                st.warning(f"⏳ Rate limited. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            
            # Handle quota exceeded
            elif "quota" in error_str.lower():
                return "⚠️ API Quota Exceeded! Please check your billing plan at https://ai.dev/usage"
            
            # Last attempt failed
            elif attempt == max_retries - 1:
                return f"⚠️ Error after {max_retries} attempts: {e}"
            
            # Other errors, retry
            else:
                st.warning(f"⚠️ Error occurred, retrying... ({attempt + 1}/{max_retries})")
                time.sleep(2)
    
    return "⚠️ No valid response returned."


# ==========================================================
# SIDEBAR SETTINGS
# ==========================================================
st.sidebar.header("⚙️ AI Settings")

temperature = st.sidebar.slider(
    "Creativity (Temperature)", 0.0, 1.0, 0.5, 0.1
)

max_tokens = 2000  # Standard token set to 2000

st.sidebar.markdown(f"**Max Output Tokens:** {max_tokens}")

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tips:**\n- Lower temperature = More consistent\n- Higher tokens = Longer responses\n- Allow 3-5s between requests")


# ==========================================================
# APP HEADER
# ==========================================================
st.title("🌴 Smart Farming AI Assistant — Kerala Edition")
st.caption("Powered by Gemini 2.0 Flash — Accurate, Fast & Bilingual 🌾")


# ==========================================================
# LOGIN / SIGN UP
# ==========================================================
if "current_user" not in st.session_state:
    st.subheader("👩‍🌾 Login or Sign Up")

    choice = st.radio("Select option:", ["Login", "Sign Up"])

    # LOGIN
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

    # SIGN UP
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
# MAIN APP (ONCE LOGGED IN)
# ==========================================================
if "current_user" in st.session_state:

    user = get_user(st.session_state.current_user)

    st.markdown(f"### 👋 Hello {user['name']} from {user['district']}!")
    st.caption(f"Language: {user['language']} | Experience: {user['experience']} Farmer")

    # Challenges
    challenges = {
        "Waterlogging & Heavy Rainfall": "Monsoon floods damage my paddy field every year. What can I do?",
        "Coconut Pests (Red Palm Weevil)": "My coconut trees are affected by red palm weevil pests. How to control them?",
        "Soil Acidity (Laterite Soil)": "My soil is acidic. Which crops will grow well?",
        "Pepper Price Fluctuations": "Pepper prices keep changing. Should I sell now?",
        "Seasonal Crop Choice": "It's September — what crops are best to grow in Kerala now?",
    }

    option = st.radio("Select mode:", ["🧠 Choose Challenge", "✍️ Ask My Own Question"])

    if option == "🧠 Choose Challenge":
        selected = st.selectbox("Select a challenge:", list(challenges.keys()))
        user_question = challenges[selected]
    else:
        user_question = st.text_area("Enter your farming question:")

    # Ask AI button
    if st.button("🌱 Get AI Advice"):
        if not user_question.strip():
            st.warning("❗ Please enter or select a question.")
        else:

            prompt = f"""
You are an agriculture expert for Kerala with deep knowledge of local farming practices.

Give short, practical farming advice in {user['language']}.
Explain the reason for each recommendation.
Keep responses concise and actionable.

User details:
Name: {user['name']}
District: {user['district']}
Farming type: {user['farming_type']}
Experience: {user['experience']}

Question: {user_question}

Format your response as:
- Use bullet points
- Add short reasoning after each point
- Keep language simple and farmer-friendly
- Give in 250 words
- Give in both Malayalam and English if selected
"""

            with st.spinner("🌿 Generating advisory..."):
                reply = get_ai_response(prompt, temperature, max_tokens)

            if "Error" not in reply and "⚠️" not in reply:
                st.success("✅ AI Response Ready!")
            
            st.markdown(reply)

    # Additional info section
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📚 View My Profile"):
            st.json(user)
    
    with col2:
        if st.button("Logout 🔒"):
            del st.session_state.current_user
            st.rerun()


# FOOTER
st.markdown("<center>🌴 Built for Kerala's Smart Farmers | Powered by Gemini 2.0 Flash</center>", unsafe_allow_html=True)






