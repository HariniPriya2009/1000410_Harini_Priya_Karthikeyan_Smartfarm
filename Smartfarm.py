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
import google.generativeai as genai
import sqlite3
import time

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
genai.configure(api_key="AIzaSyAdNYlCRqzxjWQ485WHAzmLS6kz27vhnPE")

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
    """Optimized & safe API call with retry logic and rate limit handling."""
    
    config = genai.types.GenerationConfig(
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
            )
            
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


##
##import streamlit as st
##import google.generativeai as genai
##import sqlite3
##import time
##
### ==========================================================
### PAGE CONFIG
### ==========================================================
##st.set_page_config(
##    page_title="🌾 Smart Farming AI Assistant",
##    page_icon="🌴",
##    layout="centered"
##)
##
### ==========================================================
### GEMINI CONFIG
### ==========================================================
##genai.configure(api_key="AIzaSyDjAduYCj8EI2VA71HYQG2VMXtaDwq4TxI")
##
##PRIMARY_MODEL = "models/gemini-2.0-flash"   # More stable model
##
##
### ==========================================================
### SQLITE DATABASE FUNCTIONS
### ==========================================================
##DB_FILE = "farmers.db"
##
##def init_db():
##    conn = sqlite3.connect(DB_FILE)
##    cursor = conn.cursor()
##    cursor.execute("""
##        CREATE TABLE IF NOT EXISTS farmers (
##            name TEXT PRIMARY KEY,
##            district TEXT,
##            age INTEGER,
##            language TEXT,
##            farming_type TEXT,
##            experience TEXT
##        )
##    """)
##    conn.commit()
##    conn.close()
##
##def add_user(name, district, age, language, farming_type, experience):
##    conn = sqlite3.connect(DB_FILE)
##    cursor = conn.cursor()
##    cursor.execute("""
##        INSERT OR REPLACE INTO farmers (name, district, age, language, farming_type, experience)
##        VALUES (?, ?, ?, ?, ?, ?)
##    """, (name, district, age, language, farming_type, experience))
##    conn.commit()
##    conn.close()
##
##def get_user(name):
##    conn = sqlite3.connect(DB_FILE)
##    cursor = conn.cursor()
##    cursor.execute("SELECT * FROM farmers WHERE name = ?", (name,))
##    row = cursor.fetchone()
##    conn.close()
##
##    if row:
##        return {
##            "name": row[0],
##            "district": row[1],
##            "age": row[2],
##            "language": row[3],
##            "farming_type": row[4],
##            "experience": row[5]
##        }
##    return None
##
##
### Initialize database
##init_db()
##
##
### ==========================================================
### PAGE STYLE
### ==========================================================
##st.markdown("""
##<style>
##body { background: linear-gradient(135deg, #1b4332, #081c15); color: white; }
##.stButton>button {
##    background-color: #52b788;
##    color: white;
##    font-weight: bold;
##    border-radius: 10px;
##}
##.stButton>button:hover {
##    background-color: #40916c;
##}
##</style>
##""", unsafe_allow_html=True)
##
##
### ==========================================================
### AI CALL FUNCTION WITH RETRY LOGIC
### ==========================================================
##def get_ai_response(prompt, temperature, max_tokens):
##    """Optimized & safe API call with retry logic and rate limit handling."""
##    
##    config = genai.types.GenerationConfig(
##        temperature=temperature,
##        max_output_tokens=max_tokens,
##    )
##
##    max_retries = 3
##    
##    for attempt in range(max_retries):
##        try:
##            # Add delay before each request
##            time.sleep(3)
##            
##            model = genai.GenerativeModel(PRIMARY_MODEL)
##            response = model.generate_content(
##                prompt,
##                generation_config=config,
##                safety_settings={
##                    "HARASSMENT": "BLOCK_NONE", 
##                    "HATE": "BLOCK_NONE"
##                }
##            )
##            
##            # Extract text from response
##            parts = response.candidates[0].content.parts
##            return "".join([p.text for p in parts if hasattr(p, "text")])
##            
##        except Exception as e:
##            error_str = str(e)
##            
##            # Handle rate limiting (429 error)
##            if "429" in error_str and attempt < max_retries - 1:
##                wait_time = (attempt + 1) * 5
##                st.warning(f"⏳ Rate limited. Retrying in {wait_time} seconds...")
##                time.sleep(wait_time)
##            
##            # Handle quota exceeded
##            elif "quota" in error_str.lower():
##                return "⚠️ API Quota Exceeded! Please check your billing plan at https://ai.dev/usage"
##            
##            # Last attempt failed
##            elif attempt == max_retries - 1:
##                return f"⚠️ Error after {max_retries} attempts: {e}"
##            
##            # Other errors, retry
##            else:
##                st.warning(f"⚠️ Error occurred, retrying... ({attempt + 1}/{max_retries})")
##                time.sleep(2)
##    
##    return "⚠️ No valid response returned."
##
##
### ==========================================================
### SIDEBAR SETTINGS
### ==========================================================
##st.sidebar.header("⚙️ AI Settings")
##
##temperature = st.sidebar.slider(
##    "Creativity (Temperature)", 0.0, 1.0, 0.5, 0.1
##)
##
##max_tokens = st.sidebar.slider(
##    "Max Output Tokens",
##    min_value=100,
##    max_value=1200,
##    value=300,
##    step=50
##)
##
##st.sidebar.markdown("---")
##st.sidebar.info("💡 **Tips:**\n- Lower temperature = More consistent\n- Higher tokens = Longer responses\n- Allow 3-5s between requests")
##
##
### ==========================================================
### APP HEADER
### ==========================================================
##st.title("🌴 Smart Farming AI Assistant — Kerala Edition")
##st.caption("Powered by Gemini 2.0 Flash — Accurate, Fast & Bilingual 🌾")
##
##
### ==========================================================
### LOGIN / SIGN UP
### ==========================================================
##if "current_user" not in st.session_state:
##    st.subheader("👩‍🌾 Login or Sign Up")
##
##    choice = st.radio("Select option:", ["Login", "Sign Up"])
##
##    # LOGIN
##    if choice == "Login":
##        name = st.text_input("Enter your name:")
##        if st.button("Login 🚜"):
##            user = get_user(name)
##            if user:
##                st.session_state.current_user = name
##                st.success(f"Welcome back, {name}! 🌴")
##                st.rerun()
##            else:
##                st.error("User not found. Please sign up first.")
##
##    # SIGN UP
##    else:
##        with st.form("signup"):
##            st.markdown("### 🧾 Farmer Details")
##            name = st.text_input("Name:")
##            district = st.text_input("District:")
##            age = st.number_input("Age:", 10, 100)
##            language = st.selectbox("Preferred Language:", ["English", "Malayalam", "Both"])
##            farming_type = st.selectbox("Type of Farming:", ["Paddy", "Coconut", "Spices", "Vegetables", "Mixed"])
##            experience = st.selectbox("Experience Level:", ["Beginner", "Intermediate", "Expert"])
##
##            submit = st.form_submit_button("Create Profile 🌾")
##
##            if submit:
##                if name.strip() == "":
##                    st.error("Name cannot be empty.")
##                else:
##                    add_user(name, district, age, language, farming_type, experience)
##                    st.session_state.current_user = name
##                    st.success("Profile created successfully! 🌿")
##                    st.rerun()
##
##
### ==========================================================
### MAIN APP (ONCE LOGGED IN)
### ==========================================================
##if "current_user" in st.session_state:
##
##    user = get_user(st.session_state.current_user)
##
##    st.markdown(f"### 👋 Hello {user['name']} from {user['district']}!")
##    st.caption(f"Language: {user['language']} | Experience: {user['experience']} Farmer")
##
##    # Challenges
##    challenges = {
##        "Waterlogging & Heavy Rainfall": "Monsoon floods damage my paddy field every year. What can I do?",
##        "Coconut Pests (Red Palm Weevil)": "My coconut trees are affected by red palm weevil pests. How to control them?",
##        "Soil Acidity (Laterite Soil)": "My soil is acidic. Which crops will grow well?",
##        "Pepper Price Fluctuations": "Pepper prices keep changing. Should I sell now?",
##        "Seasonal Crop Choice": "It's September — what crops are best to grow in Kerala now?",
##    }
##
##    option = st.radio("Select mode:", ["🧠 Choose Challenge", "✍️ Ask My Own Question"])
##
##    if option == "🧠 Choose Challenge":
##        selected = st.selectbox("Select a challenge:", list(challenges.keys()))
##        user_question = challenges[selected]
##    else:
##        user_question = st.text_area("Enter your farming question:")
##
##    # Ask AI button
##    if st.button("🌱 Get AI Advice"):
##        if not user_question.strip():
##            st.warning("❗ Please enter or select a question.")
##        else:
##
##            prompt = f"""
##You are an agriculture expert for Kerala with deep knowledge of local farming practices.
##
##Give short, practical farming advice in {user['language']}.
##Explain the reason for each recommendation.
##Keep responses concise and actionable.
##
##User details:
##Name: {user['name']}
##District: {user['district']}
##Farming type: {user['farming_type']}
##Experience: {user['experience']}
##
##Question: {user_question}
##
##Format your response as:
##- Use bullet points
##- Add short reasoning after each point
##- Keep language simple and farmer-friendly
##"""
##
##            with st.spinner("🌿 Generating advisory..."):
##                reply = get_ai_response(prompt, temperature, max_tokens)
##
##            if "Error" not in reply and "⚠️" not in reply:
##                st.success("✅ AI Response Ready!")
##            
##            st.markdown(reply)
##
##    # Additional info section
##    st.markdown("---")
##    col1, col2 = st.columns(2)
##    
##    with col1:
##        if st.button("📚 View My Profile"):
##            st.json(user)
##    
##    with col2:
##        if st.button("Logout 🔒"):
##            del st.session_state.current_user
##            st.rerun()
##
##
### FOOTER
##st.markdown("<center>🌴 Built for Kerala's Smart Farmers | Powered by Gemini 2.0 Flash</center>", unsafe_allow_html=True)
##


##import streamlit as st
##import google.generativeai as genai
##import sqlite3
##import time
##
### ==========================================================
### PAGE CONFIG
### ==========================================================
##st.set_page_config(
##    page_title="🌾 Smart Farming AI Assistant",
##    page_icon="🌴",
##    layout="centered"
##)
##
### ==========================================================
### GEMINI CONFIG
### ==========================================================
##genai.configure(api_key="AIzaSyDIhOKsUX8o-U7DV_wT6Z4CICJj8o3J-w0")
##
##PRIMARY_MODEL = "models/gemini-2.5-flash"   # Best available
##
##
### ==========================================================
### SQLITE DATABASE FUNCTIONS
### ==========================================================
##DB_FILE = "farmers.db"
##
##def init_db():
##    conn = sqlite3.connect(DB_FILE)
##    cursor = conn.cursor()
##    cursor.execute("""
##        CREATE TABLE IF NOT EXISTS farmers (
##            name TEXT PRIMARY KEY,
##            district TEXT,
##            age INTEGER,
##            language TEXT,
##            farming_type TEXT,
##            experience TEXT
##        )
##    """)
##    conn.commit()
##    conn.close()
##
##def add_user(name, district, age, language, farming_type, experience):
##    conn = sqlite3.connect(DB_FILE)
##    cursor = conn.cursor()
##    cursor.execute("""
##        INSERT OR REPLACE INTO farmers (name, district, age, language, farming_type, experience)
##        VALUES (?, ?, ?, ?, ?, ?)
##    """, (name, district, age, language, farming_type, experience))
##    conn.commit()
##    conn.close()
##
##def get_user(name):
##    conn = sqlite3.connect(DB_FILE)
##    cursor = conn.cursor()
##    cursor.execute("SELECT * FROM farmers WHERE name = ?", (name,))
##    row = cursor.fetchone()
##    conn.close()
##
##    if row:
##        return {
##            "name": row[0],
##            "district": row[1],
##            "age": row[2],
##            "language": row[3],
##            "farming_type": row[4],
##            "experience": row[5]
##        }
##    return None
##
##
### Initialize database
##init_db()
##
##
### ==========================================================
### PAGE STYLE
### ==========================================================
##st.markdown("""
##<style>
##body { background: linear-gradient(135deg, #1b4332, #081c15); color: white; }
##.stButton>button {
##    background-color: #52b788;
##    color: white;
##    font-weight: bold;
##    border-radius: 10px;
##}
##.stButton>button:hover {
##    background-color: #40916c;
##}
##</style>
##""", unsafe_allow_html=True)
##
##
### ==========================================================
### AI CALL FUNCTION
### ==========================================================
##@st.cache_data(show_spinner=False)
##def get_ai_response(prompt, temperature, max_tokens):
##    """Optimized & safe API call."""
##    time.sleep(1)   # Prevent rate limits
##
##    config = genai.types.GenerationConfig(
##        temperature=temperature,
##        max_output_tokens=max_tokens,
##    )
##
##    try:
##        model = genai.GenerativeModel(PRIMARY_MODEL)
##        response = model.generate_content(
##            prompt,
##            generation_config=config,
##            safety_settings={"HARASSMENT": "BLOCK_NONE", "HATE": "BLOCK_NONE"}
##        )
##    except Exception as e:
##        return f"⚠️ Error: {e}"
##
##    try:
##        parts = response.candidates[0].content.parts
##        return "".join([p.text for p in parts if hasattr(p, "text")])
##    except:
##        return "⚠️ No valid response returned."
##
##
### ==========================================================
### SIDEBAR SETTINGS
### ==========================================================
##st.sidebar.header("⚙️ AI Settings")
##
##temperature = st.sidebar.slider(
##    "Creativity (Temperature)", 0.0, 1.0, 0.5, 0.1
##)
##
##max_tokens = st.sidebar.slider(
##    "Max Output Tokens",
##    min_value=100,
##    max_value=1200,     # UPDATED TO 1200
##    value=300,
##    step=50
##)
##
##
### ==========================================================
### APP HEADER
### ==========================================================
##st.title("🌴 Smart Farming AI Assistant — Kerala Edition")
##st.caption("Powered by Gemini 2.5 Flash — Accurate, Fast & Bilingual 🌾")
##
##
### ==========================================================
### LOGIN / SIGN UP
### ==========================================================
##if "current_user" not in st.session_state:
##    st.subheader("👩‍🌾 Login or Sign Up")
##
##    choice = st.radio("Select option:", ["Login", "Sign Up"])
##
##    # LOGIN
##    if choice == "Login":
##        name = st.text_input("Enter your name:")
##        if st.button("Login 🚜"):
##            user = get_user(name)
##            if user:
##                st.session_state.current_user = name
##                st.success(f"Welcome back, {name}! 🌴")
##                st.rerun()
##            else:
##                st.error("User not found. Please sign up first.")
##
##    # SIGN UP
##    else:
##        with st.form("signup"):
##            st.markdown("### 🧾 Farmer Details")
##            name = st.text_input("Name:")
##            district = st.text_input("District:")
##            age = st.number_input("Age:", 10, 100)
##            language = st.selectbox("Preferred Language:", ["English", "Malayalam", "Both"])
##            farming_type = st.selectbox("Type of Farming:", ["Paddy", "Coconut", "Spices", "Vegetables", "Mixed"])
##            experience = st.selectbox("Experience Level:", ["Beginner", "Intermediate", "Expert"])
##
##            submit = st.form_submit_button("Create Profile 🌾")
##
##            if submit:
##                if name.strip() == "":
##                    st.error("Name cannot be empty.")
##                else:
##                    add_user(name, district, age, language, farming_type, experience)
##                    st.session_state.current_user = name
##                    st.success("Profile created successfully! 🌿")
##                    st.rerun()
##
##
### ==========================================================
### MAIN APP (ONCE LOGGED IN)
### ==========================================================
##if "current_user" in st.session_state:
##
##    user = get_user(st.session_state.current_user)
##
##    st.markdown(f"### 👋 Hello {user['name']} from {user['district']}!")
##    st.caption(f"Language: {user['language']} | Experience: {user['experience']} Farmer")
##
##    # Challenges
##    challenges = {
##        "Waterlogging & Heavy Rainfall": "Monsoon floods damage my paddy field every year. What can I do?",
##        "Coconut Pests (Red Palm Weevil)": "My coconut trees are affected by red palm weevil pests. How to control them?",
##        "Soil Acidity (Laterite Soil)": "My soil is acidic. Which crops will grow well?",
##        "Pepper Price Fluctuations": "Pepper prices keep changing. Should I sell now?",
##        "Seasonal Crop Choice": "It’s September — what crops are best to grow in Kerala now?",
##    }
##
##    option = st.radio("Select mode:", ["🧠 Choose Challenge", "✍️ Ask My Own Question"])
##
##    if option == "🧠 Choose Challenge":
##        selected = st.selectbox("Select a challenge:", list(challenges.keys()))
##        user_question = challenges[selected]
##    else:
##        user_question = st.text_area("Enter your farming question:")
##
##    # Ask AI button
##    if st.button("🌱 Get AI Advice"):
##        if not user_question.strip():
##            st.warning("❗ Please enter or select a question.")
##        else:
##
##            prompt = f"""
##You are an agriculture expert for Kerala.
##
##Give short, practical farming advice in {user['language']}.
##Explain the reason for each recommendation.
##
##User details:
##Name: {user['name']}
##District: {user['district']}
##Farming type: {user['farming_type']}
##Experience: {user['experience']}
##
##Question: {user_question}
##
##Format:
##- Bullet points
##- Short reasoning after each point
##"""
##
##            with st.spinner("🌿 Generating advisory..."):
##                reply = get_ai_response(prompt, temperature, max_tokens)
##
##            st.success("✅ AI Response Ready!")
##            st.markdown(reply)
##
##    # LOGOUT
##    if st.button("Logout 🔒"):
##        del st.session_state.current_user
##        st.rerun()
##
##
### FOOTER
##st.markdown("<center>🌴 Built for Kerala’s Smart Farmers | Powered by Gemini 2.5</center>", unsafe_allow_html=True)



##import streamlit as st
##import google.generativeai as genai
##import sqlite3
##import time
##
### ==========================================================
### PAGE CONFIG
### ==========================================================
##st.set_page_config(
##    page_title="🌾 Smart Farming AI Assistant",
##    page_icon="🌴",
##    layout="centered"
##)
##
### ==========================================================
### GEMINI CONFIG
### ==========================================================
##genai.configure(api_key="AIzaSyDIhOKsUX8o-U7DV_wT6Z4CICJj8o3J-w0")
##
##PRIMARY_MODEL = "models/gemini-2.5-flash"  # BEST MODEL AVAILABLE FOR YOU
##
##
### ==========================================================
### SQLITE DATABASE FUNCTIONS
### ==========================================================
##DB_FILE = "farmers.db"
##
##def init_db():
##    conn = sqlite3.connect(DB_FILE)
##    cursor = conn.cursor()
##    cursor.execute("""
##        CREATE TABLE IF NOT EXISTS farmers (
##            name TEXT PRIMARY KEY,
##            district TEXT,
##            age INTEGER,
##            language TEXT,
##            farming_type TEXT,
##            experience TEXT
##        )
##    """)
##    conn.commit()
##    conn.close()
##
##def add_user(name, district, age, language, farming_type, experience):
##    conn = sqlite3.connect(DB_FILE)
##    cursor = conn.cursor()
##    cursor.execute("""
##        INSERT OR REPLACE INTO farmers (name, district, age, language, farming_type, experience)
##        VALUES (?, ?, ?, ?, ?, ?)
##    """, (name, district, age, language, farming_type, experience))
##    conn.commit()
##    conn.close()
##
##def get_user(name):
##    conn = sqlite3.connect(DB_FILE)
##    cursor = conn.cursor()
##    cursor.execute("SELECT * FROM farmers WHERE name = ?", (name,))
##    row = cursor.fetchone()
##    conn.close()
##    if row:
##        return {
##            "name": row[0],
##            "district": row[1],
##            "age": row[2],
##            "language": row[3],
##            "farming_type": row[4],
##            "experience": row[5]
##        }
##    return None
##
##
### Initialize DB
##init_db()
##
##
### ==========================================================
### PAGE STYLE
### ==========================================================
##st.markdown("""
##<style>
##body { background: linear-gradient(135deg, #1b4332, #081c15); color: white; }
##.stButton>button {
##    background-color: #52b788;
##    color: white;
##    font-weight: bold;
##    border-radius: 10px;
##}
##.stButton>button:hover {
##    background-color: #40916c;
##}
##</style>
##""", unsafe_allow_html=True)
##
##
### ==========================================================
### AI CALL FUNCTION
### ==========================================================
##@st.cache_data(show_spinner=False)
##def get_ai_response(prompt, temperature, max_tokens):
##    """Optimized and safe API function"""
##    time.sleep(1)  # prevent rate limits
##
##    config = genai.types.GenerationConfig(
##        temperature=temperature,
##        max_output_tokens=max_tokens,
##    )
##
##    model = genai.GenerativeModel(PRIMARY_MODEL)
##
##    try:
##        response = model.generate_content(
##            prompt,
##            generation_config=config,
##            safety_settings={"HARASSMENT": "BLOCK_NONE", "HATE": "BLOCK_NONE"}
##        )
##    except Exception as e:
##        return f"⚠️ Error: {e}"
##
##    # Extract response text
##    try:
##        if response and response.candidates:
##            parts = response.candidates[0].content.parts
##            return "".join([p.text for p in parts if hasattr(p, "text")])
##    except:
##        pass
##
##    return "⚠️ No valid response returned."
##
##
### ==========================================================
### APP HEADER
### ==========================================================
##st.title("🌴 Smart Farming AI Assistant — Kerala Edition")
##st.caption("Powered by Gemini 2.5 Flash — Accurate, Fast, and Bilingual 🌾")
##
##
### ==========================================================
### LOGIN & SIGN UP
### ==========================================================
##if "current_user" not in st.session_state:
##    st.subheader("👩‍🌾 Login or Sign Up")
##
##    choice = st.radio("Select option:", ["Login", "Sign Up"])
##
##    # LOGIN
##    if choice == "Login":
##        name = st.text_input("Enter your name:")
##        if st.button("Login 🚜"):
##            user = get_user(name)
##            if user:
##                st.session_state.current_user = name
##                st.success(f"Welcome back, {name}! 🌴")
##                st.rerun()
##            else:
##                st.error("User not found. Please sign up first.")
##
##    # SIGN UP
##    else:
##        with st.form("signup"):
##            st.markdown("### 🧾 Farmer Details")
##            name = st.text_input("Name:")
##            district = st.text_input("District:")
##            age = st.number_input("Age:", 10, 100)
##            language = st.selectbox("Preferred Language:", ["English", "Malayalam", "Both"])
##            farming_type = st.selectbox("Type of Farming:", ["Paddy", "Coconut", "Spices", "Vegetables", "Mixed"])
##            experience = st.selectbox("Experience Level:", ["Beginner", "Intermediate", "Expert"])
##
##            submit = st.form_submit_button("Create Profile 🌾")
##
##            if submit:
##                if name.strip() == "":
##                    st.error("Name cannot be empty.")
##                else:
##                    add_user(name, district, age, language, farming_type, experience)
##                    st.session_state.current_user = name
##                    st.success("Profile created successfully! 🌿")
##                    st.rerun()
##
##
### ==========================================================
### MAIN APP INTERFACE
### ==========================================================
##if "current_user" in st.session_state:
##
##    user = get_user(st.session_state.current_user)
##
##    st.markdown(f"### 👋 Hello {user['name']} from {user['district']}!")
##    st.caption(f"Language: {user['language']} | Experience: {user['experience']} Farmer")
##
##    # PRESET CHALLENGES (from your PDF)
##    challenges = {
##        "Waterlogging & Heavy Rainfall": "Monsoon floods damage my paddy field every year. What can I do?",
##        "Coconut Pests (Red Palm Weevil)": "My coconut trees are affected by red palm weevil pests. How to control them?",
##        "Soil Acidity (Laterite Soil)": "My soil is acidic. Which crops will grow well?",
##        "Pepper Price Fluctuations": "Pepper prices keep changing. Should I sell now?",
##        "Seasonal Crop Choice": "It’s September — what crops are best to grow in Kerala now?",
##    }
##
##    option = st.radio("Select mode:", ["🧠 Choose Challenge", "✍️ Ask My Own Question"])
##
##    if option == "🧠 Choose Challenge":
##        selected = st.selectbox("Select a challenge:", list(challenges.keys()))
##        user_question = challenges[selected]
##    else:
##        user_question = st.text_area("Enter your farming question:")
##
##    if st.button("🌱 Get AI Advice"):
##        if not user_question.strip():
##            st.warning("❗ Please enter or select a question.")
##        else:
##
##            prompt = f"""
##You are an agriculture expert for Kerala.
##
##Give short, practical farming advice in {user['language']}.
##Explain the reason for each recommendation.
##
##User details:
##Name: {user['name']}
##District: {user['district']}
##Farming type: {user['farming_type']}
##Experience: {user['experience']}
##
##Question: {user_question}
##
##Format:
##- Bullet points
##- Short reasoning after each point
##"""
##
##            with st.spinner("🌿 Generating advisory..."):
##                reply = get_ai_response(prompt, st.sidebar.slider("Temperature", 0.0, 1.0, 0.5), 250)
##
##            st.success("✅ AI Response Ready!")
##            st.markdown(reply)
##
##    # LOGOUT
##    if st.button("Logout 🔒"):
##        del st.session_state.current_user
##        st.rerun()
##
##
### FOOTER
##st.markdown("<center>🌴 Built for Kerala’s Smart Farmers | Powered by Gemini 2.5</center>", unsafe_allow_html=True)
##
##

##import streamlit as st
##import google.generativeai as genai
##import json
##import os
##import time
##
### ---------- PAGE CONFIG ----------
##st.set_page_config(page_title="🌾 Smart Farming AI Assistant", page_icon="🌴", layout="centered")
##
### ---------- GEMINI CONFIG ----------
##genai.configure(api_key="AIzaSyD5n7NsOXkkctizaVfxHYnJP0s6abIrep0")
##
##PRIMARY_MODEL = "models/gemini-2.0-flash"
##BACKUP_MODEL = "models/gemini-1.5-flash-8b"
##
##USER_FILE = "farmers.json"
##
##
### ---------- USER FILE HANDLING ----------
##def load_users():
##    if os.path.exists(USER_FILE):
##        with open(USER_FILE, "r") as f:
##            return json.load(f)
##    return {}
##
##def save_users(data):
##    with open(USER_FILE, "w") as f:
##        json.dump(data, f, indent=4)
##
##users = load_users()
##
##
### ---------- PAGE STYLE ----------
##st.markdown("""
##<style>
##body { background: linear-gradient(135deg, #1b4332, #081c15); color: white; }
##.main {
##    background: rgba(255,255,255,0.1);
##    padding: 2rem;
##    border-radius: 20px;
##    box-shadow: 0 0 20px rgba(255,255,255,0.3);
##}
##.stButton>button {
##    background-color: #52b788;
##    color: white;
##    font-weight: bold;
##    border-radius: 10px;
##}
##.stButton>button:hover {
##    background-color: #40916c;
##}
##</style>
##""", unsafe_allow_html=True)
##
##
### ---------- AI CALL FUNCTION (Optimized) ----------
##@st.cache_data(show_spinner=False)
##def get_ai_response(prompt, temperature, max_tokens):
##    """
##    This function:
##    ✔ Adds delay to avoid rate limit
##    ✔ Uses cheaper backup model when needed
##    ✔ Handles 429 errors safely
##    ✔ Is cached (same question = no new API call)
##    """
##
##    # Cooldown: avoid hitting per-second limit
##    time.sleep(1.1)
##
##    config = genai.types.GenerationConfig(
##        temperature=temperature,
##        max_output_tokens=max_tokens,
##    )
##
##    # Try primary model
##    try:
##        model = genai.GenerativeModel(PRIMARY_MODEL)
##        response = model.generate_content(
##            prompt,
##            generation_config=config,
##            safety_settings={"HARASSMENT": "BLOCK_NONE", "HATE": "BLOCK_NONE"},
##        )
##    except Exception:
##        # Fallback to cheaper + high-quota model
##        model = genai.GenerativeModel(BACKUP_MODEL)
##        response = model.generate_content(
##            prompt,
##            generation_config=config,
##            safety_settings={"HARASSMENT": "BLOCK_NONE", "HATE": "BLOCK_NONE"},
##        )
##
##    # Safely extract text
##    try:
##        if response and response.candidates and response.candidates[0].content.parts:
##            return "".join([
##                part.text for part in response.candidates[0].content.parts
##                if hasattr(part, "text")
##            ])
##    except:
##        pass
##
##    return "⚠️ Gemini could not generate a valid answer. Please try again."
##
##
### ---------- SIDEBAR SETTINGS ----------
##st.sidebar.header("⚙️ AI Settings")
##temperature = st.sidebar.slider("Creativity (Temperature)", 0.0, 1.0, 0.5, 0.1)
##max_tokens = st.sidebar.slider("Max Output Tokens", 50, 300, 180, 10)
##st.sidebar.info("💡 Lower temperature = more factual. Higher = more creative!")
##
##
### ---------- APP HEADER ----------
##st.title("🌴 Smart Farming AI Assistant — Kerala Edition")
##st.caption("Powered by Gemini — Smarter, faster, and bilingual 🌾")
##
##
### ---------- LOGIN / SIGN UP ----------
##if "current_user" not in st.session_state:
##    st.subheader("👩‍🌾 Login or Sign Up")
##
##    choice = st.radio("Select option:", ["Login", "Sign Up"])
##
##    if choice == "Login":
##        name = st.text_input("Enter your name:")
##        if st.button("Login 🚜"):
##            if name in users:
##                st.session_state.current_user = name
##                st.success(f"Welcome back, {name}! 🌴")
##                st.rerun()
##            else:
##                st.error("User not found. Please sign up first.")
##
##    else:
##        with st.form("signup"):
##            st.markdown("### 🧾 Farmer Details")
##            name = st.text_input("Name:")
##            district = st.text_input("District:")
##            age = st.number_input("Age:", 10, 100)
##            language = st.selectbox("Preferred Language:", ["English", "Malayalam", "Both"])
##            farming_type = st.selectbox("Type of Farming:", ["Paddy", "Coconut", "Spices", "Vegetables", "Mixed"])
##            experience = st.selectbox("Experience Level:", ["Beginner", "Intermediate", "Expert"])
##            submit = st.form_submit_button("Create Profile 🌾")
##
##            if submit and name:
##                users[name] = {
##                    "district": district,
##                    "age": age,
##                    "language": language,
##                    "farming_type": farming_type,
##                    "experience": experience,
##                }
##                save_users(users)
##                st.session_state.current_user = name
##                st.success("Profile saved successfully! 🌿")
##                st.rerun()
##
##
### ---------- MAIN APP ----------
##if "current_user" in st.session_state:
##    user = users[st.session_state.current_user]
##
##    st.markdown(f"### 👋 Hello {st.session_state.current_user} from {user['district']}!")
##    st.caption(f"Language: {user['language']} | Experience: {user['experience']} Farmer")
##
##    # ---------- CHALLENGES ----------
##    st.subheader("🌾 Choose a Farming Challenge or Ask Your Own Question")
##
##    challenges = {
##        "Waterlogging & Heavy Rainfall": "Monsoon floods damage my paddy field every year. What can I do?",
##        "Coconut Pests (Red Palm Weevil)": "My coconut trees are affected by red palm weevil pests. How to control them?",
##        "Soil Acidity (Laterite Soil)": "My soil is acidic. Which crops will grow well?",
##        "Market Fluctuations in Spices": "Pepper prices keep changing. Should I sell now?",
##        "Seasonal Crop Choice": "It’s September — what crops are best to grow in Kerala now?",
##    }
##
##    option = st.radio("Select mode:", ["🧠 Choose from Challenges", "✍️ Type My Own Question"])
##
##    if option == "🧠 Choose from Challenges":
##        selected_challenge = st.selectbox("Select a challenge:", list(challenges.keys()))
##        user_question = challenges[selected_challenge]
##    else:
##        user_question = st.text_area("Type your question here 👇", placeholder="e.g., How to prevent pest attacks in banana plants?")
##
##    # ---------- AI BUTTON ----------
##    if st.button("🌱 Ask Gemini for Help"):
##        if not user_question.strip():
##            st.warning("Please enter or select a question first!")
##        else:
##            st.markdown("#### 💬 Farmer’s Concern:")
##            st.info(user_question)
##
##            full_prompt = f"""
##You are an AI farming expert for Kerala.
##User: {st.session_state.current_user} from {user['district']}
##Farming: {user['farming_type']}
##Experience: {user['experience']}
##Respond in {user['language']} with short, practical solutions.
##
##Question: {user_question}
##
##Format:
##English: <solution>
##Malayalam: <translation>
##"""
##
##            with st.spinner("🌿 Preparing your solution..."):
##                reply = get_ai_response(full_prompt, temperature, max_tokens)
##
##            st.success("✅ AI Response Ready!")
##            st.markdown(reply)
##
##    st.markdown("---")
##    if st.button("Logout 🔒"):
##        del st.session_state.current_user
##        st.rerun()
##
##st.markdown("<center>🌴 Built for Kerala’s Smart Farmers</center>", unsafe_allow_html=True)

##import streamlit as st
##import google.generativeai as genai
##import json
##import os


##st.set_page_config(page_title="🌾 Smart Farming AI Assistant", page_icon="🌴", layout="centered")
##
##genai.configure(api_key="AIzaSyD5n7NsOXkkctizaVfxHYnJP0s6abIrep0")  # Replace with your Gemini API key
##model = genai.GenerativeModel("gemini-2.5-flash")
##
##USER_FILE = "farmers.json"
##
##def load_users():
##    if os.path.exists(USER_FILE):
##        with open(USER_FILE, "r") as f:
##            return json.load(f)
##    return {}
##
##def save_users(data):
##    with open(USER_FILE, "w") as f:
##        json.dump(data, f, indent=4)
##
##users = load_users()
##
### ---------- PAGE STYLE ----------
##st.markdown("""
##<style>
##body {
##    background: linear-gradient(135deg, #1b4332, #081c15);
##    color: white;
##}
##.main {
##    background: rgba(255,255,255,0.1);
##    padding: 2rem;
##    border-radius: 20px;
##    box-shadow: 0 0 20px rgba(255,255,255,0.3);
##}
##.stButton>button {
##    background-color: #52b788;
##    color: white;
##    font-weight: bold;
##    border-radius: 10px;
##}
##.stButton>button:hover {
##    background-color: #40916c;
##}
##</style>
##""", unsafe_allow_html=True)
##
### ---------- APP HEADER ----------
##st.title("🌾 Smart Farming AI Assistant — Kerala Edition 🇮🇳")
##st.caption("Powered by Gemini 1.5 — AI for resilient and sustainable agriculture 🌱")
##
### ---------- LOGIN / SIGNUP ----------
##if "current_user" not in st.session_state:
##    st.subheader("👩‍🌾 Login or Sign Up")
##
##    choice = st.radio("Select option:", ["Login", "Sign Up"])
##
##    if choice == "Login":
##        name = st.text_input("Enter your name:")
##        if st.button("Login 🚜"):
##            if name in users:
##                st.session_state.current_user = name
##                st.success(f"Welcome back, {name}! 🌴")
##                st.rerun()
##            else:
##                st.error("User not found. Please sign up first.")
##
##    else:
##        with st.form("signup"):
##            st.markdown("### 🧾 Farmer Details")
##            name = st.text_input("Name:")
##            district = st.text_input("District:")
##            age = st.number_input("Age:", 10, 100)
##            language = st.selectbox("Preferred Language:", ["English", "Malayalam", "Both"])
##            farming_type = st.selectbox("Type of Farming:", ["Paddy", "Coconut", "Spices", "Vegetables", "Mixed"])
##            experience = st.selectbox("Experience Level:", ["Beginner", "Intermediate", "Expert"])
##            submit = st.form_submit_button("Create Profile 🌾")
##
##            if submit and name:
##                users[name] = {
##                    "district": district,
##                    "age": age,
##                    "language": language,
##                    "farming_type": farming_type,
##                    "experience": experience,
##                }
##                save_users(users)
##                st.session_state.current_user = name
##                st.success("Profile saved successfully! 🌿")
##                st.rerun()
##
### ---------- MAIN APP ----------
##if "current_user" in st.session_state:
##    user = users[st.session_state.current_user]
##    st.markdown(f"### 👋 Hello {st.session_state.current_user} from {user['district']}!")
##    st.caption(f"Language: {user['language']} | Experience: {user['experience']} farmer")
##
##    # ---------- CHALLENGES ----------
##    st.subheader("🌧️ Choose a Farming Challenge to Get AI Help")
##
##    challenges = {
##        "Waterlogging & Heavy Rainfall": "Monsoon floods damage my paddy field every year. What can I do?",
##        "Coconut Pests (Red Palm Weevil)": "My coconut trees are affected by red palm weevil pests. How to control them?",
##        "Soil Acidity (Laterite Soil)": "My soil is acidic. Which crops will grow well?",
##        "Market Fluctuations in Spices": "Pepper prices keep changing. Should I sell now?",
##        "Seasonal Crop Choice": "It’s September — what crops are best to grow in Kerala now?"
##    }
##
##    selected_challenge = st.selectbox("Select a challenge:", list(challenges.keys()))
##    user_question = challenges[selected_challenge]
##
##    if st.button("🌱 Ask Gemini for Help"):
##        st.markdown("#### 💬 Farmer’s Concern:")
##        st.info(user_question)
##
##        full_prompt = f"""
##        You are an AI farming assistant helping Kerala farmers.
##        The user is {st.session_state.current_user}, from {user['district']}, doing {user['farming_type']} farming.
##        Respond in {user['language']} with simple, clear advice.
##        Include both:
##        English: <solution in English>
##        Malayalam: <translation in Malayalam>
##
##        Challenge: {selected_challenge}
##        Farmer's Question: {user_question}
##        """
##
##        with st.spinner("Gemini is analyzing the challenge... 🌾"):
##            response = model.generate_content(full_prompt)
##            reply = response.text
##
##        st.success("✅ Solution Generated!")
##        st.markdown(reply)
##
##    st.markdown("---")
##    if st.button("Logout 🔒"):
##        del st.session_state.current_user
##        st.rerun()
##
##st.markdown("<center>🌴 Built for Kerala’s Smart Farmers | Gemini + Streamlit</center>", unsafe_allow_html=True)
##



##import streamlit as st
##import openai
##
### Set your Gemini 1.5 API key
##openai.api_key = "AIzaSyD5n7NsOXkkctizaVfxHYnJP0s6abIrep0"
##
##st.title("Smart Farming Assistant 🌱")
##
### Chat history
##if "history" not in st.session_state:
##    st.session_state.history = []
##
### User input
##user_input = st.text_input("Ask your farming question:")
##
##if st.button("Send") and user_input:
##    # Send user input to Gemini 1.5
##    response = openai.ChatCompletion.create(
##        model="gemini-1.5-chat",
##        messages=[
##            {"role": "system", "content": "You are a helpful farming assistant for Kerala farmers."},
##            *[
##                {"role": "user", "content": item["user"]} if item["role"]=="user" else {"role": "assistant", "content": item["assistant"]}
##                for item in st.session_state.history
##            ],
##            {"role": "user", "content": user_input}
##        ],
##        temperature=0.7
##    )
##
##    answer = response.choices[0].message.content
##
##    # Store in chat history
##    st.session_state.history.append({"role":"user", "user": user_input})
##    st.session_state.history.append({"role":"assistant", "assistant": answer})
##
### Display chat
##for chat in st.session_state.history:
##    if chat["role"] == "user":
##        st.markdown(f"**Farmer:** {chat['user']}")
##    else:
##        st.markdown(f"**AI Assistant:** {chat['assistant']}")
##
