import streamlit as st
import google.generativeai as genai
import sqlite3
import time
from datetime import datetime

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="🌾 Smart Farming AI Assistant - Kerala Edition",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# GEMINI CONFIG - Using Streamlit Secrets
# ==========================================================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

PRIMARY_MODEL = "gemini-2.0-flash-exp"

# Fixed AI Configuration (hidden from UI)
AI_TEMPERATURE = 0.7  # Balanced creativity for farming advice
AI_MAX_TOKENS = 2000   # Detailed responses


# ==========================================================
# SQLITE DATABASE FUNCTIONS
# ==========================================================
DB_FILE = "farmers_kerala.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            district TEXT NOT NULL,
            age INTEGER,
            language TEXT NOT NULL,
            farming_type TEXT NOT NULL,
            experience TEXT NOT NULL,
            farm_size REAL,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_user(name, district, age, language, farming_type, experience, farm_size):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO farmers (name, district, age, language, farming_type, experience, farm_size)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, district, age, language, farming_type, experience, farm_size))
    conn.commit()
    conn.close()
    return cursor.lastrowid

def get_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM farmers WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "name": row[1],
            "district": row[2],
            "age": row[3],
            "language": row[4],
            "farming_type": row[5],
            "experience": row[6],
            "farm_size": row[7]
        }
    return None


# Initialize database
init_db()


# ==========================================================
# KERALA-SPECIFIC DATA
# ==========================================================

# Kerala Districts
KERALA_DISTRICTS = [
    "Thiruvananthapuram", "Kollam", "Pathanamthitta", "Alappuzha",
    "Kottayam", "Idukki", "Ernakulam", "Thrissur", "Palakkad",
    "Malappuram", "Kozhikode", "Wayanad", "Kannur", "Kasaragod"
]

# Farming Types
FARMING_TYPES = [
    "Paddy (നെല്ല്)", "Coconut (തേങ്ങ)", "Spices (സുഗന്ധവ്യഞ്ജനങ്ങൾ)",
    "Vegetables (പച്ചക്കറികൾ)", "Banana (വാഴ)", "Mixed Farming (ഇടവിള)"
]

# Experience Levels
EXPERIENCE_LEVELS = ["Beginner (ആരംഭകൻ)", "Intermediate (ഇടത്തരം)", "Expert (വിദഗ്ദ്ധൻ)"]

# Language Options
LANGUAGE_OPTIONS = [
    "Malayalam (മലയാളം)", "English", "Bilingual (ഇരുഭാഷ)"
]


# ==========================================================
# PAGE STYLE
# ==========================================================
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #2d6a4f 0%, #1b4332 100%);
    }
    .stApp {
        background-color: #2d6a4f;
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    .stButton>button {
        background-color: #40916c;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #52b788;
        transform: translateY(-2px);
    }
    .chat-container {
        background-color: rgba(11, 46, 33, 0.6);
        border: 1px solid #40916c;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .user-message {
        background-color: rgba(64, 145, 108, 0.25);
        border-left: 4px solid #40916c;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .ai-message {
        background-color: rgba(149, 213, 178, 0.15);
        border-left: 4px solid #95d5b2;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================================
# AI CALL FUNCTION
# ==========================================================
def get_ai_response(prompt, user_info):
    """Get AI response from Gemini with Kerala-specific context."""
    
    # Build Kerala-specific system prompt
    current_month = datetime.now().strftime("%B")
    system_prompt = f"""You are an expert agriculture advisor specializing in Kerala farming with deep knowledge of:
    
    - Kerala's unique climate: Tropical monsoon with heavy rainfall (3000mm+ annually)
    - Temperature: 20°C to 35°C with high humidity (70-90%)
    - Monsoon seasons: Southwest (June-September), Northeast (October-December)
    - Soil types: Laterite, red loam, sandy loam, coastal alluvium
    - Major crops: Paddy, coconut, pepper, vegetables, banana, tapioca, spices
    - Common challenges: Waterlogging, red palm weevil, soil acidity, price fluctuations
    - Local farming practices: Organic farming, mixed cropping, traditional methods
    - Kerala's agricultural culture: Smallholder farmers, traditional knowledge
    
    Current month: {current_month}
    
    User Profile:
    - Name: {user_info['name']}
    - District: {user_info['district']}
    - Farming Type: {user_info['farming_type']}
    - Experience: {user_info['experience']}
    - Language Preference: {user_info['language']}
    - Farm Size: {user_info.get('farm_size', 'Not specified')} acres
    
    Instructions:
    1. Provide practical, actionable advice specific to Kerala's context
    2. Consider the district, farming type, and season
    3. Use local crop names and farming terminology
    4. Include both traditional and modern methods
    5. Focus on sustainable and organic practices
    6. Give specific recommendations with reasoning
    7. Address Kerala-specific challenges (monsoon, humidity, pests)
    8. Response language: {user_info['language']}
    
    Format your response:
    - Use clear bullet points
    - Include reasoning for each recommendation
    - Add specific Kerala references when applicable
    - Keep language simple and farmer-friendly
    - Maximum 400 words
    - If bilingual is selected, provide both English and Malayalam"""
   
    config = genai.types.GenerationConfig(
        temperature=AI_TEMPERATURE,
        max_output_tokens=AI_MAX_TOKENS,
    )

    max_retries = 3
   
    for attempt in range(max_retries):
        try:
            # Add delay before each request
            time.sleep(2)
           
            model = genai.GenerativeModel(PRIMARY_MODEL, system_instruction=system_prompt)
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
# SIDEBAR - FARMER DETAILS
# ==========================================================
st.sidebar.header("👨‍🌾 Farmer Details")

name = st.sidebar.text_input("Name / പേര്:*")
district = st.sidebar.selectbox("District / ജില്ല:", KERALA_DISTRICTS)
age = st.sidebar.number_input("Age / പ്രായം:", 15, 100, 30)
language = st.sidebar.selectbox("Language / ഭാഷ:", LANGUAGE_OPTIONS)
farming_type = st.sidebar.selectbox("Farming Type / കൃഷി രീതി:", FARMING_TYPES)
experience = st.sidebar.selectbox("Experience / അനുഭവം:", EXPERIENCE_LEVELS)
farm_size = st.sidebar.number_input("Farm Size (acres) / കൃഷിയിടം (ഏക്കർ):", 0.1, 100.0, 1.0, 0.1)

st.sidebar.markdown("---")
st.sidebar.info("💡 Fill in your details and click 'Start Assistant' to begin chatting!")

# Start Assistant button
if st.sidebar.button("🚀 Start Assistant", use_container_width=True):
    if not name:
        st.sidebar.error("Please enter your name")
    else:
        # Save farmer to database
        farmer_id = add_user(name, district, age, language, farming_type, experience, farm_size)
        st.session_state.farmer_id = farmer_id
        st.session_state.chat_started = True
        st.session_state.user_info = {
            "name": name,
            "district": district,
            "age": age,
            "language": language,
            "farming_type": farming_type,
            "experience": experience,
            "farm_size": farm_size
        }
        st.sidebar.success("✅ Assistant Ready! / സഹായി തയ്യാറായി!")
        st.rerun()

# Logout button (only show when chat is started)
if "chat_started" in st.session_state and st.session_state.chat_started:
    st.sidebar.markdown("---")
    if st.sidebar.button("🔒 Logout", use_container_width=True):
        del st.session_state.farmer_id
        del st.session_state.chat_started
        if "user_info" in st.session_state:
            del st.session_state.user_info
        if "chat_history" in st.session_state:
            del st.session_state.chat_history
        st.rerun()

# Farmer info display when chat started
if "chat_started" in st.session_state and st.session_state.chat_started:
    user_info = st.session_state.user_info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👤 Your Profile")
    st.sidebar.markdown(f"**Name:** {user_info['name']}")
    st.sidebar.markdown(f"**District:** {user_info['district']}")
    st.sidebar.markdown(f"**Farming:** {user_info['farming_type']}")
    st.sidebar.markdown(f"**Language:** {user_info['language']}")


# ==========================================================
# MAIN CHAT INTERFACE
# ==========================================================

# Header
st.title("🌴 Smart Farming AI Assistant — Kerala Edition")
st.caption("കേരള കർഷകർക്ക് വേണ്ടി | For Kerala Farmers")
st.markdown("### 🌾 Powered by Gemini 2.0 Flash — Bilingual Support (English & Malayalam)")

# Chat interface
if "chat_started" in st.session_state and st.session_state.chat_started:
    st.markdown("---")
    st.subheader("💬 Chat with the AI Assistant")
    
    # Initialize chat history if not exists
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    if st.session_state.chat_history:
        for i, (question, answer) in enumerate(st.session_state.chat_history):
            st.markdown("---")
            st.markdown(f'<div class="user-message"><strong>👨‍🌾 You:</strong> {question}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ai-message"><strong>🤖 AI Assistant:</strong><br>{answer}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # New question input
    user_question = st.text_area(
        "Ask your farming question:",
        placeholder="Example: How to control red palm weevil in coconut trees organically? / തെങ്ങിലെ ചുവന്ന വണ്ടിനെ ജൈവ രീതിയിൽ എങ്ങനെ നിയന്ത്രിക്കാം?",
        height=100,
        key="new_question"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        ask_button = st.button("🌱 Ask", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️ Clear Chat", use_container_width=True)
    
    if ask_button:
        if user_question.strip() == "":
            st.warning("❗ Please enter a question / ചോദ്യം ചോദിക്കുക")
        else:
            # Get user info
            user_info = st.session_state.user_info
            
            # Add language instruction based on preference
            if "Malayalam" in user_info['language']:
                lang_instruction = "Provide the response in Malayalam (മലയാളം)."
            elif "Bilingual" in user_info['language']:
                lang_instruction = "Provide the response in both English and Malayalam."
            else:
                lang_instruction = "Provide the response in English."
            
            # Build prompt with language instruction
            enhanced_prompt = f"""
{lang_instruction}

Farmer's Question:
{user_question}

Please provide clear, practical advice that's easy to understand and implement.
"""
            
            # Get AI response
            with st.spinner("🌿 Generating response... / മറുപടി തയ്യാറാക്കുന്നു..."):
                ai_response = get_ai_response(enhanced_prompt, user_info)
            
            # Save to chat history
            st.session_state.chat_history.append((user_question, ai_response))
            
            # Display new response
            st.markdown("---")
            st.markdown(f'<div class="user-message"><strong>👨‍🌾 You:</strong> {user_question}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ai-message"><strong>🤖 AI Assistant:</strong><br>{ai_response}</div>', unsafe_allow_html=True)
            
            # Auto-scroll to bottom (by rerunning)
            st.rerun()
    
    if clear_button:
        st.session_state.chat_history = []
        st.success("✅ Chat cleared!")
        st.rerun()

else:
    # Welcome message when not started
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 40px;">
        <h2>👋 Welcome to the Smart Farming Assistant!</h2>
        <h3>കേരള കർഷകർക്കുള്ള സ്മാർട്ട് കാർഷിക സഹായിയിലേക്ക് സ്വാഗതം!</h3>
        <p style="font-size: 18px; margin: 20px 0;">
            Please fill in your details in the sidebar and click <strong>"Start Assistant"</strong> to begin chatting with the AI.
        </p>
        <p style="font-size: 18px; margin: 20px 0;">
            സൈഡ്‌ബാറിൽ നിങ്ങളുടെ വിശദാംശങ്ങൾ നൽകുക, <strong>"Start Assistant"</strong> ക്ലിക്ക് ചെയ്യുക.
        </p>
        <h3 style="color: #52b788;">Ask about:</h3>
        <ul style="list-style: none; padding: 0; font-size: 16px;">
            <li>🌱 Crop recommendations</li>
            <li>🐛 Pest and disease management</li>
            <li>🌧️ Weather-based farming advice</li>
            <li>🌿 Soil and fertilizer guidance</li>
            <li>♻️ Sustainable farming practices</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


# FOOTER
st.markdown("---")
st.markdown("<center>", unsafe_allow_html=True)
st.markdown("### 🌴 Built for Kerala's Smart Farmers")
st.markdown("**Powered by Gemini 2.0 Flash** | Bilingual Support (English & Malayalam)")
st.markdown("</center>", unsafe_allow_html=True)

# Helpful Resources
st.markdown("---")
st.markdown("## 📚 Helpful Resources")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🏛️ Official Sources")
    st.markdown("- [Kerala Agricultural University](https://kau.in/)")
    st.markdown("- [Krishi Vigyan Kendra](https://www.kvk.org.in/)")
    st.markdown("- [Kerala Agriculture Dept](https://keralaagriculture.gov.in/)")

with col2:
    st.markdown("### 🌤️ Weather & Climate")
    st.markdown("- [IMD Kerala](https://mausam.imd.gov.in/imd_latest/contents/)")

with col3:
    st.markdown("### 📊 Market Information")
    st.markdown("- [Spices Board India](https://www.indianspices.com/)")
    st.markdown("- [Agmarknet Price Info](https://agmarknet.gov.in/)")
