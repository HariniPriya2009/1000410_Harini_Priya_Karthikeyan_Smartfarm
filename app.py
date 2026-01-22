import streamlit as st
import sqlite3
import google.generativeai as genai
import os

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="🌾 Smart Farming AI Assistant",
    page_icon="🌴",
    layout="centered"
)

# ==========================================================
# GEMINI API KEY
# ==========================================================
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY and "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]

if not API_KEY:
    st.sidebar.warning("⚠️ GEMINI_API_KEY not found.")
    API_KEY = st.sidebar.text_input("Enter Gemini API Key", type="password")

if not API_KEY:
    st.error("❌ GEMINI_API_KEY is required.")
    st.stop()

# ==========================================================
# GEMINI CLIENT (NEW SDK)
# ==========================================================
try:
    client = genai.Client(api_key=API_KEY)

    test_response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Hello"
    )

    st.sidebar.success("✅ Gemini API connected successfully!")

except Exception as e:
    st.sidebar.error(f"❌ Gemini connection failed: {e}")
    st.stop()


# ==========================================================
# SQLITE DATABASE FUNCTIONS
# ==========================================================
DB_FILE = "farmers.db"

def init_db():
    """Initialize the database with required tables"""
    try:
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
    except Exception as e:
        st.error(f"❌ Database initialization error: {e}")

def add_user(name, district, age, language, farming_type, experience):
    """Add or update a user in the database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO farmers (name, district, age, language, farming_type, experience)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, district, age, language, farming_type, experience))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Error adding user: {e}")
        return False

def get_user(name):
    """Get user details from database"""
    try:
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
    except Exception as e:
        st.error(f"❌ Error retrieving user: {e}")
        return None

# Initialize database
init_db()

# ==========================================================
# BILINGUAL TRANSLATIONS
# ==========================================================
translations = {
    "English": {
        "title": "🌴 Smart Farming AI Assistant — Kerala Edition",
        "caption": "Powered by Gemini 1.5 Flash — Accurate, Fast & Bilingual 🌾",
        "login_signup": "👩‍🌾 Login or Sign Up",
        "select_option": "Select option:",
        "login": "Login",
        "signup": "Sign Up",
        "enter_name": "Enter your name:",
        "login_btn": "Login 🚜",
        "welcome_back": "Welcome back,",
        "user_not_found": "User not found. Please sign up first.",
        "farmer_details": "### 🧾 Farmer Details",
        "name": "Name:",
        "district": "District:",
        "age": "Age:",
        "preferred_language": "Preferred Language:",
        "farming_type": "Type of Farming:",
        "experience_level": "Experience Level:",
        "create_profile": "Create Profile 🌾",
        "name_empty": "Name cannot be empty.",
        "profile_created": "Profile created successfully! 🌿",
        "hello": "### 👋 Hello",
        "from": "from",
        "language_label": "Language:",
        "experience_label": "Experience:",
        "farmer": "Farmer",
        "select_mode": "Select mode:",
        "choose_challenge": "🧠 Choose Challenge",
        "ask_question": "✍️ Ask My Own Question",
        "select_challenge": "Select a challenge:",
        "enter_question": "Enter your farming question:",
        "get_advice": "🌱 Get AI Advice",
        "enter_question_warning": "❗ Please enter or select a question.",
        "generating": "🌿 Generating advisory...",
        "response_ready": "✅ AI Response Ready!",
        "view_profile": "📚 View My Profile",
        "logout": "Logout 🔒",
        "footer": "🌴 Built for Kerala's Smart Farmers | Powered by Gemini"
    },
    "Malayalam": {
        "title": "🌴 സ്മാർട്ട് കൃഷി എഐ അസിസ്റ്റന്റ് — കേരള പതിപ്പ്",
        "caption": "Gemini 1.5 Flash നൽകുന്നത് — കൃത്യവും വേഗവും ദ്വിഭാഷിയും 🌾",
        "login_signup": "👩‍🌾 ലോഗിൻ അല്ലെങ്കിൽ സൈൻ അപ്പ്",
        "select_option": "ഓപ്ഷൻ തിരഞ്ഞെടുക്കുക:",
        "login": "ലോഗിൻ",
        "signup": "സൈൻ അപ്പ്",
        "enter_name": "നിങ്ങളുടെ പേര് നൽകുക:",
        "login_btn": "ലോഗിൻ 🚜",
        "welcome_back": "തിരികെ സ്വാഗതം,",
        "user_not_found": "ഉപയോക്താവിനെ കണ്ടെത്തിയില്ല. ദയവായി ആദ്യം സൈൻ അപ്പ് ചെയ്യുക.",
        "farmer_details": "### 🧾 കർഷക വിവരങ്ങൾ",
        "name": "പേര്:",
        "district": "ജില്ല:",
        "age": "പ്രായം:",
        "preferred_language": "ഇഷ്ടപ്പെടുന്ന ഭാഷ:",
        "farming_type": "കൃഷി തരം:",
        "experience_level": "അനുഭവ നില:",
        "create_profile": "പ്രൊഫൈൽ സൃഷ്ടിക്കുക 🌾",
        "name_empty": "പേര് ശൂന്യമാകരുത്.",
        "profile_created": "പ്രൊഫൈൽ വിജയകരമായി സൃഷ്ടിച്ചു! 🌿",
        "hello": "### 👋 നമസ്കാരം",
        "from": "",
        "language_label": "ഭാഷ:",
        "experience_label": "അനുഭവം:",
        "farmer": "കർഷകർ",
        "select_mode": "മോഡ് തിരഞ്ഞെടുക്കുക:",
        "choose_challenge": "🧠 വെല്ലുവിളി തിരഞ്ഞെടുക്കുക",
        "ask_question": "✍️ സ്വന്തം ചോദ്യം ചോദിക്കുക",
        "select_challenge": "വെല്ലുവിളി തിരഞ്ഞെടുക്കുക:",
        "enter_question": "നിങ്ങളുടെ കൃഷി ചോദ്യം നൽകുക:",
        "get_advice": "🌱 എഐ ഉപദേശം നേടുക",
        "enter_question_warning": "❗ ദയവായി ചോദ്യം നൽകുക.",
        "generating": "🌿 ഉപദേശം തയ്യാറാക്കുന്നു...",
        "response_ready": "✅ എഐ മറുപടി തയ്യാറാണ്!",
        "view_profile": "📚 എന്റെ പ്രൊഫൈൽ കാണുക",
        "logout": "ലോഗ് ഔട്ട് 🔒",
        "footer": "🌴 കേരളത്തിലെ സ്മാർട്ട് കർഷകർക്കായി | Gemini പ്രവർത്തിപ്പിക്കുന്നു"
    }
}

def get_text(language, key):
    """Get translated text based on language preference"""
    return translations.get(language, translations["English"]).get(key, key)

# ==========================================================
# PAGE STYLE
# ==========================================================
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #1b4332, #081c15); color: white; }
.stButton>button {
    background-color: #52b788;
    color: white;
    font-weight: bold;
    border-radius: 10px;
    transition: all 0.3s;
}
.stButton>button:hover {
    background-color: #40916c;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
.sidebar .sidebar-content {
    background: linear-gradient(180deg, #2d6a4f, #1b4332);
}
.info-box {
    background: rgba(255,255,255,0.1);
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
}
.success-box {
    background: rgba(82, 183, 136, 0.3);
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 4px solid #52b788;
}
.warning-box {
    background: rgba(251, 206, 21, 0.2);
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 4px solid #fec107;
}
.error-box {
    background: rgba(220, 53, 69, 0.2);
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 4px solid #dc3545;
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# AI CALL FUNCTION
# ==========================================================
def get_ai_response(prompt, temperature, max_tokens):
    """Get response from Gemini AI with improved error handling"""
    try:
        model = genai.GenerativeModel(PRIMARY_MODEL)
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        )
        
        if response.text:
            return response.text
        else:
            return "⚠️ No response received from the AI. Please try again."
            
    except genai.types.BlockedPromptException as e:
        return f"⚠️ Safety filter blocked the request: {e}"
    except genai.types.StopCandidateException as e:
        return f"⚠️ Response was stopped: {e}"
    except Exception as e:
        return f"⚠️ Error getting AI response: {str(e)}"

# ==========================================================
# SIDEBAR SETTINGS
# ==========================================================
st.sidebar.header("⚙️ AI Settings")
temperature = st.sidebar.slider("Creativity (Temperature)", 0.0, 1.0, 0.5, 0.1)
max_tokens = st.sidebar.number_input("Max Output Tokens", 100, 4000, 2000, 100)
st.sidebar.markdown("---")

# Language selector for the interface
if "interface_language" not in st.session_state:
    st.session_state.interface_language = "English"

st.sidebar.header("🌐 Interface Language")
interface_lang = st.sidebar.radio(
    "Choose Interface Language:",
    ["English", "Malayalam"],
    index=0 if st.session_state.interface_language == "English" else 1
)
st.session_state.interface_language = interface_lang

st.sidebar.markdown("---")

# ==========================================================
# APP HEADER
# ==========================================================
st.title(get_text(interface_lang, "title"))
st.caption(get_text(interface_lang, "caption"))

# ==========================================================
# LOGIN / SIGN UP
# ==========================================================
if "current_user" not in st.session_state:
    st.subheader(get_text(interface_lang, "login_signup"))
    choice = st.radio(get_text(interface_lang, "select_option"), 
                      [get_text(interface_lang, "login"), get_text(interface_lang, "signup")])

    if choice == get_text(interface_lang, "login"):
        name = st.text_input(get_text(interface_lang, "enter_name"))
        if st.button(get_text(interface_lang, "login_btn")):
            if name.strip():
                user = get_user(name)
                if user:
                    st.session_state.current_user = name
                    st.success(f"{get_text(interface_lang, 'welcome_back')} {name}! 🌴")
                    st.rerun()
                else:
                    st.error(get_text(interface_lang, "user_not_found"))
            else:
                st.warning(get_text(interface_lang, "name_empty"))
    else:
        with st.form("signup"):
            st.markdown(get_text(interface_lang, "farmer_details"))
            name = st.text_input(get_text(interface_lang, "name"))
            
            # Kerala districts
            districts = [
                "Alappuzha", "Ernakulam", "Idukki", "Kannur", "Kasaragod",
                "Kollam", "Kottayam", "Kozhikode", "Malappuram", "Palakkad",
                "Pathanamthitta", "Thiruvananthapuram", "Thrissur", "Wayanad"
            ]
            district = st.selectbox(get_text(interface_lang, "district"), districts)
            
            age = st.number_input(get_text(interface_lang, "age"), 10, 100)
            language = st.selectbox(get_text(interface_lang, "preferred_language"), 
                                   ["English", "Malayalam", "Both"])
            
            farming_types = ["Paddy (നെല്ല്)", "Coconut (തേങ്ങ)", "Spices (സുഗന്ധവ്യഞ്ജനങ്ങൾ)", 
                           "Vegetables (പച്ചക്കറികൾ)", "Mixed (മിശ്രിത)"]
            farming_type = st.selectbox(get_text(interface_lang, "farming_type"), farming_types)
            
            experience = st.selectbox(get_text(interface_lang, "experience_level"), 
                                    ["Beginner (പ്രാരംഭകൻ)", "Intermediate (ഇടനില)", "Expert (വിദഗ്ദ്ധൻ)"])
            
            submit = st.form_submit_button(get_text(interface_lang, "create_profile"))

            if submit:
                if name.strip() == "":
                    st.error(get_text(interface_lang, "name_empty"))
                else:
                    if add_user(name, district, age, language, farming_type, experience):
                        st.session_state.current_user = name
                        st.success(get_text(interface_lang, "profile_created"))
                        st.rerun()

# ==========================================================
# MAIN APP
# ==========================================================
if "current_user" in st.session_state:
    user = get_user(st.session_state.current_user)
    
    if user:
        # Greeting
        st.markdown(f"{get_text(interface_lang, 'hello')} {user['name']} {get_text(interface_lang, 'from')} {user['district']}! 🌴")
        st.caption(f"{get_text(interface_lang, 'language_label')} {user['language']} | "
                   f"{get_text(interface_lang, 'experience_label')} {user['experience']} {get_text(interface_lang, 'farmer')}")

        # Challenges in both languages
        challenges = {
            "Waterlogging & Heavy Rainfall / വെള്ളപ്പൊക്കവും കനത്ത മഴയും": 
                "Monsoon floods damage my paddy field every year. What can I do? / എല്ലാ വർഷവും മൺസൂൺ വെള്ളപ്പൊക്കം എന്റെ നെൽവയലിന് കേടുപാടുകൾ വരുത്തുന്നു. എന്ത് ചെയ്യണം?",
            
            "Coconut Pests (Red Palm Weevil) / തേങ്ങ കീടങ്ങൾ (ചുവന്ന ഈനാമ്പേച്ചി)": 
                "My coconut trees are affected by red palm weevil pests. How to control them? / എന്റെ തെങ്ങുകളെ ചുവന്ന ഈനാമ്പേച്ചി കീടങ്ങൾ ബാധിക്കുന്നു. അവയെ എങ്ങനെ നിയന്ത്രിക്കാം?",
            
            "Soil Acidity (Laterite Soil) / മണ്ണിന്റെ അമ്ലത (പശ്ചിമഘട്ട മണ്ണ്)": 
                "My soil is acidic. Which crops will grow well? / എന്റെ മണ്ണ് അമ്ല സ്വഭാവമുള്ളതാണ്. ഏതൊക്കെ വിളകൾ നന്നായി വളരും?",
            
            "Pepper Price Fluctuations / കുരുമുളക് വില വ്യത്യാസം": 
                "Pepper prices keep changing. Should I sell now? / കുരുമുളക് വില മാറിക്കൊണ്ടിരിക്കുകയാണ്. ഇപ്പോൾ വിൽക്കണോ?",
            
            "Seasonal Crop Choice / സീസണൽ വിള തിരഞ്ഞെടുപ്പ്": 
                "It's September — what crops are best to grow in Kerala now? / ഇപ്പോൾ സെപ്റ്റംബർ ആണ് — കേരളത്തിൽ ഇപ്പോൾ ഏതൊക്കെ വിളകൾ കൃഷി ചെയ്യാൻ നല്ലത്?"
        }

        option = st.radio(get_text(interface_lang, "select_mode"), 
                         [get_text(interface_lang, "choose_challenge"), get_text(interface_lang, "ask_question")])
        
        if option == get_text(interface_lang, "choose_challenge"):
            selected_challenge = st.selectbox(get_text(interface_lang, "select_challenge"), 
                                            list(challenges.keys()))
            user_question = challenges[selected_challenge]
        else:
            user_question = st.text_area(get_text(interface_lang, "enter_question"), height=100)

        if st.button(get_text(interface_lang, "get_advice")):
            if not user_question.strip():
                st.warning(get_text(interface_lang, "enter_question_warning"))
            else:
                # Determine response language
                response_lang = user['language'] if user['language'] != "Both" else interface_lang
                
                prompt = f"""
                You are an expert agriculture advisor for Kerala farmers. You are bilingual in English and Malayalam.
                
                IMPORTANT INSTRUCTIONS:
                1. Respond in {response_lang} language
                2. Provide short, practical, and actionable farming advice
                3. Use bullet points for clarity
                4. Maximum 250 words
                5. Include specific Kerala context where relevant
                6. Consider the farmer's experience level: {user['experience']}
                7. Focus on their farming type: {user['farming_type']}
                
                USER PROFILE:
                - Name: {user['name']}
                - District: {user['district']}
                - Farming Type: {user['farming_type']}
                - Experience: {user['experience']}
                - Preferred Language: {user['language']}
                
                QUESTION: {user_question}
                
                Provide advice in a friendly, helpful tone suitable for {user['experience']} farmers.
                """
                
                with st.spinner(get_text(interface_lang, "generating")):
                    reply = get_ai_response(prompt, temperature, max_tokens)
                    
                    if "⚠️" not in reply:
                        st.success(get_text(interface_lang, "response_ready"))
                        st.markdown("---")
                    
                    st.markdown(reply)

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(get_text(interface_lang, "view_profile")):
                st.json(user)
        with col2:
            if st.button(get_text(interface_lang, "logout")):
                del st.session_state.current_user
                st.rerun()

st.markdown(f"<center>{get_text(interface_lang, 'footer')}</center>", unsafe_allow_html=True)


