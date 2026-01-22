import streamlit as st
import google.generativeai as genai
import json
import os
import time

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="🌾 Smart Farming AI Assistant", page_icon="🌴", layout="centered")

# ---------- GEMINI CONFIG ----------
genai.configure(api_key="YOUR_API_KEY_HERE")

PRIMARY_MODEL = "models/gemini-2.5-flash"
BACKUP_MODEL = "models/gemini-1.5-flash"  # cheaper + higher free quota

USER_FILE = "farmers.json"


# ---------- USER FILE HANDLING ----------
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(data):
    with open(USER_FILE, "w") as f:
        json.dump(data, f, indent=4)

users = load_users()


# ---------- PAGE STYLE ----------
st.markdown("""
<style>
body { background: linear-gradient(135deg, #1b4332, #081c15); color: white; }
.main {
    background: rgba(255,255,255,0.1);
    padding: 2rem;
    border-radius: 20px;
    box-shadow: 0 0 20px rgba(255,255,255,0.3);
}
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


# ---------- AI CALL FUNCTION (Optimized) ----------
@st.cache_data(show_spinner=False)
def get_ai_response(prompt, temperature, max_tokens):
    """
    This function:
    ✔ Adds delay to avoid rate limit
    ✔ Uses cheaper backup model when needed
    ✔ Handles 429 errors safely
    ✔ Is cached (same question = no new API call)
    """

    # Cooldown: avoid hitting per-second limit
    time.sleep(1.1)

    config = genai.types.GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
    )

    # Try primary model
    try:
        model = genai.GenerativeModel(PRIMARY_MODEL)
        response = model.generate_content(
            prompt,
            generation_config=config,
            safety_settings={"HARASSMENT": "BLOCK_NONE", "HATE": "BLOCK_NONE"},
        )
    except Exception:
        # Fallback to cheaper + high-quota model
        model = genai.GenerativeModel(BACKUP_MODEL)
        response = model.generate_content(
            prompt,
            generation_config=config,
            safety_settings={"HARASSMENT": "BLOCK_NONE", "HATE": "BLOCK_NONE"},
        )

    # Safely extract text
    try:
        if response and response.candidates and response.candidates[0].content.parts:
            return "".join([
                part.text for part in response.candidates[0].content.parts
                if hasattr(part, "text")
            ])
    except:
        pass

    return "⚠️ Gemini could not generate a valid answer. Please try again."


# ---------- SIDEBAR SETTINGS ----------
st.sidebar.header("⚙️ AI Settings")
temperature = st.sidebar.slider("Creativity (Temperature)", 0.0, 1.0, 0.5, 0.1)
max_tokens = st.sidebar.slider("Max Output Tokens", 50, 300, 180, 10)
st.sidebar.info("💡 Lower temperature = more factual. Higher = more creative!")


# ---------- APP HEADER ----------
st.title("🌴 Smart Farming AI Assistant — Kerala Edition")
st.caption("Powered by Gemini — Smarter, faster, and bilingual 🌾")


# ---------- LOGIN / SIGN UP ----------
if "current_user" not in st.session_state:
    st.subheader("👩‍🌾 Login or Sign Up")

    choice = st.radio("Select option:", ["Login", "Sign Up"])

    if choice == "Login":
        name = st.text_input("Enter your name:")
        if st.button("Login 🚜"):
            if name in users:
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

            if submit and name:
                users[name] = {
                    "district": district,
                    "age": age,
                    "language": language,
                    "farming_type": farming_type,
                    "experience": experience,
                }
                save_users(users)
                st.session_state.current_user = name
                st.success("Profile saved successfully! 🌿")
                st.rerun()


# ---------- MAIN APP ----------
if "current_user" in st.session_state:
    user = users[st.session_state.current_user]

    st.markdown(f"### 👋 Hello {st.session_state.current_user} from {user['district']}!")
    st.caption(f"Language: {user['language']} | Experience: {user['experience']} Farmer")

    # ---------- CHALLENGES ----------
    st.subheader("🌾 Choose a Farming Challenge or Ask Your Own Question")

    challenges = {
        "Waterlogging & Heavy Rainfall": "Monsoon floods damage my paddy field every year. What can I do?",
        "Coconut Pests (Red Palm Weevil)": "My coconut trees are affected by red palm weevil pests. How to control them?",
        "Soil Acidity (Laterite Soil)": "My soil is acidic. Which crops will grow well?",
        "Market Fluctuations in Spices": "Pepper prices keep changing. Should I sell now?",
        "Seasonal Crop Choice": "It’s September — what crops are best to grow in Kerala now?",
    }

    option = st.radio("Select mode:", ["🧠 Choose from Challenges", "✍️ Type My Own Question"])

    if option == "🧠 Choose from Challenges":
        selected_challenge = st.selectbox("Select a challenge:", list(challenges.keys()))
        user_question = challenges[selected_challenge]
    else:
        user_question = st.text_area("Type your question here 👇", placeholder="e.g., How to prevent pest attacks in banana plants?")

    # ---------- AI BUTTON ----------
    if st.button("🌱 Ask Gemini for Help"):
        if not user_question.strip():
            st.warning("Please enter or select a question first!")
        else:
            st.markdown("#### 💬 Farmer’s Concern:")
            st.info(user_question)

            full_prompt = f"""
You are an AI farming expert for Kerala.
User: {st.session_state.current_user} from {user['district']}
Farming: {user['farming_type']}
Experience: {user['experience']}
Respond in {user['language']} with short, practical solutions.

Question: {user_question}

Format:
English: <solution>
Malayalam: <translation>
"""

            with st.spinner("🌿 Preparing your solution..."):
                reply = get_ai_response(full_prompt, temperature, max_tokens)

            st.success("✅ AI Response Ready!")
            st.markdown(reply)

    st.markdown("---")
    if st.button("Logout 🔒"):
        del st.session_state.current_user
        st.rerun()

st.markdown("<center>🌴 Built for Kerala’s Smart Farmers</center>", unsafe_allow_html=True)
