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

PRIMARY_MODEL = "models/gemini-2.0-flash-exp"


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

def get_user(name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM farmers WHERE name = ? ORDER BY id DESC LIMIT 1", (name,))
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

# 5 Core Features with Kerala Context
CORE_FEATURES = {
    "🌱 Crop Recommendation": {
        "description": "Get crop suggestions based on Kerala's seasons and soil types",
        "prompts": [
            "What crops should I plant this month in my district?",
            "Which crops grow best in laterite soil during monsoon?",
            "What vegetables can I cultivate now with minimal water?"
        ],
        "malayalam_prompts": [
            "എന്റെ ജില്ലയിൽ ഈ മാസം എന്ത് വിളകൾ നടണം?",
            "മഴക്കാലത്ത് പശിമരണ്ണി മണ്ണിൽ ഏത് വിളകൾ നന്നായി വളരും?",
            "ഇപ്പോൾ കുറഞ്ഞ വെള്ളത്തിൽ ഏത് പച്ചക്കറികൾ കൃഷി ചെയ്യാം?"
        ]
    },
    "🐛 Pest & Disease Management": {
        "description": "Identify and treat pests and diseases common in Kerala",
        "prompts": [
            "How to control red palm weevil in coconut trees organically?",
            "My paddy has blast disease - what treatment do you recommend?",
            "Natural pest control for pepper plants in Wayanad?",
            "Neem-based pest control methods for vegetables?"
        ],
        "malayalam_prompts": [
            "തെങ്ങിലെ ചുവന്ന വണ്ടിനെ ജൈവ രീതിയിൽ എങ്ങനെ നിയന്ത്രിക്കാം?",
            "എന്റെ നെൽവയലിൽ കായ്‌നാശം പിടിപെട്ടു - എന്ത് ചികിത്സ നിർദ്ദേശിക്കും?",
            "വയനാട്ടിലെ കുരുമുളക് ചെടികൾക്ക് പ്രകൃതിദത്ത കീടനിയന്ത്രണം?",
            "പച്ചക്കറികൾക്ക് വേപ്പെണ്ണ അടിസ്ഥാനമാക്കിയുള്ള കീടനിയന്ത്രണ മാർഗങ്ങൾ?"
        ]
    },
    "🌧️ Weather-Based Farming Alerts": {
        "description": "Get farming advice based on Kerala's monsoon patterns",
        "prompts": [
            "Monsoon starting next week - how to prepare my paddy field?",
            "Heavy rain predicted - what precautions should I take for my crops?",
            "Drought conditions in my area - water management tips?",
            "How to protect crops during northeast monsoon?"
        ],
        "malayalam_prompts": [
            "അടുത്ത ആഴ്ച മഴക്കാലം ആരംഭിക്കുന്നു - എന്റെ നെൽവയലിനെ എങ്ങനെ തയ്യാറാക്കാം?",
            "കനത്ത മഴ പ്രവചിക്കുന്നു - എന്റെ വിളകൾക്ക് എന്ത് മുൻകരുതലുകൾ എടുക്കണം?",
            "എന്റെ പ്രദേശത്ത് വരൾച്ച - ജല മാനേജ്മെന്റ് നുറുങ്ങുകൾ?",
            "വടക്കുകിഴക്കൻ മഴക്കാലത്ത് വിളകളെ എങ്ങനെ സംരക്ഷിക്കാം?"
        ]
    },
    "🌿 Soil & Fertilizer Advice": {
        "description": "Improve soil health and choose right fertilizers for Kerala's soil types",
        "prompts": [
            "How to reduce acidity in laterite soil for vegetable farming?",
            "What organic fertilizers are best for paddy fields in Kerala?",
            "Soil testing recommendations for spice plantations?",
            "How to improve soil fertility using cow dung and compost?"
        ],
        "malayalam_prompts": [
            "പച്ചക്കറി കൃഷിക്ക് പശിമരണ്ണി മണ്ണിലെ അമ്ലത എങ്ങനെ കുറയ്ക്കാം?",
            "കേരളത്തിലെ നെൽവയലുകൾക്ക് ഏത് ജൈവ വളങ്ങൾ ഏറ്റവും നല്ലത്?",
            "സുഗന്ധവ്യഞ്ജന തോട്ടങ്ങൾക്ക് മണ്ണ് പരിശോധന നിർദ്ദേശങ്ങൾ?",
            "പശുക്കാവ്യും കമ്പോസ്റ്റും ഉപയോഗിച്ച് മണ്ണിന്റെ ഫലപുഷ്ടി എങ്ങനെ വർദ്ധിപ്പിക്കാം?"
        ]
    },
    "♻️ Sustainable & Organic Farming": {
        "description": "Eco-friendly farming practices for Kerala farmers",
        "prompts": [
            "Organic pest control methods for coconut trees?",
            "How to practice mixed farming in Kerala successfully?",
            "Zero-budget natural farming techniques for smallholders?",
            "Vermicompost preparation for home gardening?"
        ],
        "malayalam_prompts": [
            "തെങ്ങിന് ജൈവ കീടനിയന്ത്രണ മാർഗങ്ങൾ?",
            "കേരളത്തിൽ ഇടവിള കൃഷി എങ്ങനെ വിജയകരമായി ചെയ്യാം?",
            "ചെറിയ കർഷകർക്ക് പൂജ്യ ബജറ്റ് പ്രകൃതി കൃഷി സാങ്കേതികവിദ്യകൾ?",
            "വീട്ടുതോട്ടത്തിന് വേമികമ്പോസ്റ്റ് തയ്യാറാക്കൽ?"
        ]
    }
}

# Kerala-Specific Challenges
KERALA_CHALLENGES = {
    "Monsoon Waterlogging in Paddy": "Heavy southwest monsoon causes severe waterlogging in paddy fields, leading to crop damage. What drainage solutions and flood-resistant varieties do you recommend?",
    "Red Palm Weevil in Coconut": "My coconut trees are affected by red palm weevil pests. How can I identify, treat organically, and prevent future infestations?",
    "Acidic Laterite Soil Issues": "My farm has acidic laterite soil (pH 4.5-5.5). Which crops will grow well and how can I improve soil health organically?",
    "Pepper Price Fluctuations": "Pepper prices keep changing in the market. Should I sell now or store? What's the best timing for maximum profit?",
    "Unpredictable Weather Patterns": "Kerala's monsoon patterns are becoming unpredictable. How can I adapt my farming schedule to changing weather conditions?"
}


# ==========================================================
# PAGE STYLE
# ==========================================================
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #1b4332 0%, #081c15 100%);
    }
    .stApp {
        background-color: #1b4332;
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    .stButton>button {
        background-color: #52b788;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #40916c;
        transform: translateY(-2px);
    }
    .info-box {
        background-color: rgba(82, 183, 136, 0.1);
        border: 2px solid #52b788;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .feature-card {
        background-color: rgba(8, 28, 21, 0.8);
        border: 1px solid #52b788;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .success-message {
        background-color: rgba(82, 183, 136, 0.2);
        border: 2px solid #52b788;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================================
# AI CALL FUNCTION WITH RETRY LOGIC
# ==========================================================
def get_ai_response(prompt, user_info):
    """Optimized & safe API call with Kerala-specific context and retry logic."""
    
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
        temperature=0.7,  # Balanced creativity for farming advice
        max_output_tokens=2000,  # Detailed responses
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
# SIDEBAR SETTINGS
# ==========================================================
st.sidebar.header("⚙️ AI Settings")

temperature = st.sidebar.slider(
    "Creativity (Temperature)", 0.0, 1.0, 0.7, 0.1
)

max_tokens = 2000  # Standard token set to 2000

st.sidebar.markdown(f"**Max Output Tokens:** {max_tokens}")

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tips:**\n- Lower temperature = More consistent\n- Higher tokens = Longer responses\n- Allow 2-3s between requests")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌴 Kerala Farming Facts")
st.sidebar.markdown("- **Climate:** Tropical monsoon")
st.sidebar.markdown("- **Rainfall:** 3000mm+ annually")
st.sidebar.markdown("- **Soil:** Laterite, Red loam")
st.sidebar.markdown("- **Main Crops:** Paddy, Coconut, Spices")


# ==========================================================
# APP HEADER
# ==========================================================
st.title("🌴 Smart Farming AI Assistant — Kerala Edition")
st.caption("കേരള കർഷകർക്ക് വേണ്ടി | For Kerala Farmers")
st.markdown("### 🌾 Powered by Gemini 2.0 Flash — Bilingual Support (English & Malayalam)")


# ==========================================================
# LOGIN / SIGN UP
# ==========================================================
if "current_user" not in st.session_state:
    st.markdown("---")
    st.subheader("👩‍🌾 Login or Sign Up")
    st.markdown("Create your farmer profile to get personalized advice")

    choice = st.radio("Select option:", ["Login", "Sign Up"], horizontal=True)

    # LOGIN
    if choice == "Login":
        st.markdown("### 🔐 Login")
        name = st.text_input("Enter your name:")
        if st.button("Login 🚜"):
            user = get_user(name)
            if user:
                st.session_state.current_user = name
                st.success(f"Welcome back, {name}! 🌴\nവീണ്ടും സ്വാഗതം, {name}! 🌴")
                st.rerun()
            else:
                st.error("User not found. Please sign up first.\nഉപയോക്താവിനെ കണ്ടെത്തിയില്ല. ആദ്യം സൈൻ അപ്പ് ചെയ്യുക.")

    # SIGN UP
    else:
        st.markdown("### 🧾 Create Farmer Profile")
        with st.form("signup", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name / പേര്:*")
                district = st.selectbox("District / ജില്ല:", KERALA_DISTRICTS)
                age = st.number_input("Age / പ്രായം:", 15, 100, 30)
            
            with col2:
                language = st.selectbox("Language / ഭാഷ:", LANGUAGE_OPTIONS)
                farming_type = st.selectbox("Farming Type / കൃഷി രീതി:", FARMING_TYPES)
                experience = st.selectbox("Experience / അനുഭവം:", EXPERIENCE_LEVELS)
            
            farm_size = st.number_input("Farm Size (acres) / കൃഷിയിടം (ഏക്കർ):", 0.1, 100.0, 1.0, 0.1)

            submit = st.form_submit_button("Create Profile 🌾", use_container_width=True)

            if submit:
                if name.strip() == "":
                    st.error("Name cannot be empty / പേര് ശൂന്യമാകരുത്")
                else:
                    add_user(name, district, age, language, farming_type, experience, farm_size)
                    st.session_state.current_user = name
                    st.success(f"Profile created successfully! 🌿\nപ്രൊഫൈൽ വിജയകരമായി സൃഷ്ടിച്ചു! 🌿")
                    st.rerun()


# ==========================================================
# MAIN APP (ONCE LOGGED IN)
# ==========================================================
if "current_user" in st.session_state:
    user = get_user(st.session_state.current_user)
    
    # User Welcome Section
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"### 👋 Hello {user['name']}!")
        st.markdown(f"**{user['district']}** | {user['farming_type']} | {user['experience']}")
    
    with col2:
        if st.button("📚 My Profile"):
            with st.expander("👤 Farmer Profile", expanded=True):
                st.json(user)
    
    with col3:
        if st.button("🔒 Logout"):
            del st.session_state.current_user
            st.rerun()
    
    st.markdown("---")

    # Feature Selection
    st.markdown("## 🎯 Choose Your Challenge")
    
    # Tabs for different interaction modes
    tab1, tab2, tab3 = st.tabs(["🏆 Kerala Challenges", "🧠 Core Features", "✍️ Ask Custom Question"])
    
    # Tab 1: Kerala-Specific Challenges
    with tab1:
        st.markdown("### Select a Kerala-specific farming challenge:")
        selected_challenge = st.selectbox(
            "Challenges:",
            list(KERALA_CHALLENGES.keys()),
            key="challenge_select"
        )
        st.info(KERALA_CHALLENGES[selected_challenge])
        
        user_question = KERALA_CHALLENGES[selected_challenge]
        
        if st.button("🌱 Get AI Advice", key="challenge_btn", use_container_width=True):
            with st.spinner("🌿 Generating Kerala-specific advisory..."):
                reply = get_ai_response(user_question, user)
            
            if "Error" not in reply and "⚠️" not in reply:
                st.success("✅ AI Response Ready!")
            
            st.markdown("---")
            st.markdown("### 📝 AI Response")
            st.markdown(reply)
    
    # Tab 2: Core Features
    with tab2:
        st.markdown("### Select a feature to explore:")
        
        feature_cols = st.columns(3)
        feature_list = list(CORE_FEATURES.keys())
        
        selected_feature = st.selectbox(
            "Features:",
            feature_list,
            key="feature_select"
        )
        
        feature_info = CORE_FEATURES[selected_feature]
        
        # Display feature description
        st.markdown(f"**{feature_info['description']}**")
        
        # Display sample prompts
        st.markdown("#### 💬 Sample Prompts:")
        
        if user['language'] in ["English", "Bilingual (ഇരുഭാഷ)"]:
            for i, prompt in enumerate(feature_info['prompts'][:2], 1):
                st.markdown(f"{i}. {prompt}")
        
        if user['language'] in ["Malayalam (മലയാളം)", "Bilingual (ഇരുഭാഷ)"]:
            st.markdown("**മലയാളം:**")
            for i, prompt in enumerate(feature_info['malayalam_prompts'][:2], 1):
                st.markdown(f"{i}. {prompt}")
        
        # Custom prompt for the feature
        st.markdown("---")
        custom_feature_prompt = st.text_area(
            "Ask your question related to this feature:",
            placeholder="Type your question here...",
            height=100,
            key="feature_prompt"
        )
        
        if st.button("🌱 Get AI Advice", key="feature_btn", use_container_width=True):
            if not custom_feature_prompt.strip():
                st.warning("❗ Please enter a question.")
            else:
                with st.spinner("🌿 Generating response..."):
                    reply = get_ai_response(custom_feature_prompt, user)
                
                if "Error" not in reply and "⚠️" not in reply:
                    st.success("✅ AI Response Ready!")
                
                st.markdown("---")
                st.markdown("### 📝 AI Response")
                st.markdown(reply)
    
    # Tab 3: Custom Question
    with tab3:
        st.markdown("### Ask any farming question:")
        
        user_question = st.text_area(
            "Your Question:",
            placeholder="Example: What organic pest control methods work for coconut trees in Kollam during monsoon?",
            height=150,
            key="custom_prompt"
        )
        
        if st.button("🌱 Get AI Advice", key="custom_btn", use_container_width=True):
            if not user_question.strip():
                st.warning("❗ Please enter a question.")
            else:
                with st.spinner("🌿 Generating advisory..."):
                    reply = get_ai_response(user_question, user)
                
                if "Error" not in reply and "⚠️" not in reply:
                    st.success("✅ AI Response Ready!")
                
                st.markdown("---")
                st.markdown("### 📝 AI Response")
                st.markdown(reply)


# FOOTER
st.markdown("---")
st.markdown("<center>", unsafe_allow_html=True)
st.markdown("### 🌴 Built for Kerala's Smart Farmers")
st.markdown("**Powered by Gemini 2.0 Flash** | Bilingual Support (English & Malayalam)")
st.markdown("</center>", unsafe_allow_html=True)

# Additional Resources
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
</create-file>
