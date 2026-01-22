import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import os
from io import BytesIO
import hashlib
import json
import re

st.set_page_config(
    page_title="AgriSoul – Smart Farming Assistant", 
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'language' not in st.session_state:
    st.session_state.language = 'English'


TRANSLATIONS = {
    'English': {
        'welcome': 'Welcome',
        'app_title': '🌾 AgriSoul: Smart Farming + Wellbeing Assistant',
        'subtitle': 'Helping farmers with region-based advice, local languages, and emotional support 💚',
        'farming_tab': '🌿 Farming Assistant',
        'mental_tab': '🧠 Mental Health Bot',
        'location': '📍 Location',
        'advice_type': '💬 Select Farming Challenge',
        'extra_info': '📝 Additional details',
        'get_advice': 'Get Expert Advice',
        'logout': 'Logout',
        'login': 'Login',
        'register': 'Register',
        'username': 'Username',
        'password': 'Password',
        'full_name': 'Full Name',
        'age': 'Age',
        'district': 'District',
        'state': 'State',
        'farm_size': 'Farm Size (acres)',
        'primary_crops': 'Primary Crops',
        'language_pref': 'Language Preference',
        'mental_prompt': 'Your message',
        'send': 'Send',
        'voice_output': '🔊 Voice Output',
        'advice_response': "🌾 AgriSoul's Expert Advice",
        'mental_response': '💬 AgriSoul Response',
        'current_season': '🌤️ Current Season',
        'day_type': '☀️ Current Weather',
        'precision_mode': '✨ Precision Mode Active - Detailed & Accurate Advice',
        'select_challenge': 'Select Your Challenge',
        'season_kharif': 'Kharif (Monsoon/Jun-Oct)',
        'season_rabi': 'Rabi (Winter/Nov-Mar)',
        'season_summer': 'Summer (Apr-Jun)',
        'season_offseason': 'Off-Season',
        'weather_rainy': 'Rainy',
        'weather_sunny': 'Sunny',
        'weather_cloudy': 'Cloudy',
        'weather_windy': 'Windy'
    },
    'Tamil': {
        'welcome': 'வரவேற்கிறோம்',
        'app_title': '🌾 அக்ரிசோல்: ஸ்மார்ட் விவசாயம் + நல்வாழ்வு உதவியாளர்',
        'subtitle': 'பிராந்திய அடிப்படையிலான ஆலோசனை, உள்ளூர் மொழிகள் மற்றும் உணர்ச்சி ஆதரவுடன் விவசாயிகளுக்கு உதவுதல் 💚',
        'farming_tab': '🌿 விவசாய உதவியாளர்',
        'mental_tab': '🧠 மன நல ஆதரவு',
        'location': '📍 இடம்',
        'advice_type': '💬 விவசாய சவாலைத் தேர்ந்தெடுக்கவும்',
        'extra_info': '📝 கூடுதல் விவரங்கள்',
        'get_advice': 'நிபுணர் ஆலோசனையைப் பெறுங்கள்',
        'logout': 'வெளியேறு',
        'login': 'உள்நுழைய',
        'register': 'பதிவு செய்ய',
        'username': 'பயனர்பெயர்',
        'password': 'கடவுச்சொல்',
        'full_name': 'முழு பெயர்',
        'age': 'வயது',
        'district': 'மாவட்டம்',
        'state': 'மாநிலம்',
        'farm_size': 'பண்ணை அளவு (ஏக்கர்)',
        'primary_crops': 'முதன்மை பயிர்கள்',
        'language_pref': 'மொழி விருப்பம்',
        'mental_prompt': 'உங்கள் செய்தி',
        'send': 'அனுப்பு',
        'voice_output': '🔊 குரல் வெளியீடு',
        'advice_response': '🌾 அக்ரிசோலின் நிபுணர் ஆலோசனை',
        'mental_response': '💬 அக்ரிசோல் பதில்',
        'current_season': '🌤️ தற்போதைய பருவம்',
        'day_type': '☀️ தற்போதைய வானிலை',
        'precision_mode': '✨ துல்லியமான பயன்முறை செயலில் உள்ளது - விரிவான மற்றும் துல்லியமான ஆலோசனை',
        'select_challenge': 'உங்கள் சவாலைத் தேர்ந்தெடுக்கவும்',
        'season_kharif': 'கரீஃப் (பருவமழை/ஜூன்-அக்டோபர்)',
        'season_rabi': 'ரபி (குளிர்காலம்/நவம்பர்-மார்ச்)',
        'season_summer': 'கோடை (ஏப்ரல்-ஜூன்)',
        'season_offseason': 'பருவம் அல்லாத காலம்',
        'weather_rainy': 'மழை',
        'weather_sunny': 'வெயில்',
        'weather_cloudy': 'மேகமூட்டம்',
        'weather_windy': 'காற்று'
    }
}


FIXED_TEMPERATURE = 0.3  
FIXED_MAX_TOKENS = 2900  

FARMING_CHALLENGES = {
    'English': {
        '🧠 Mental Health & Wellbeing': 'mental_health',
        '🐛 Pest & Disease Attack': 'pest_disease',
        '🌱 Soil Health Issues': 'soil_health',
        '💧 Water Usage Efficiency': 'water_efficiency',
        '📋 Crop Insurance Prediction': 'crop_insurance'
    },
    'Tamil': {
        '🧠 மன நலம் மற்றும் நல்வாழ்வு': 'mental_health',
        '🐛 பூச்சி மற்றும் நோய் தாக்குதல்': 'pest_disease',
        '🌱 மண் நல பிரச்சினைகள்': 'soil_health',
        '💧 நீர் பயன்பாட்டு திறன்': 'water_efficiency',
        '📋 பயிர் காப்பீடு கணிப்பு': 'crop_insurance'
    }
}

def get_text(key):
    """Get translated text based on current language"""
    return TRANSLATIONS[st.session_state.language].get(key, key)


def load_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #1a5f3c, #2d8659, #3db76f, #52d681, #6ef59c);
        background-size: 300% 300%;
        animation: gradient-animation 20s ease infinite;
        font-family: 'Poppins', sans-serif;
    }
    
    @keyframes gradient-animation {
        0% { background-position: 0% 50%; }
        33% { background-position: 50% 100%; }
        66% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(12px) saturate(180%);
        -webkit-backdrop-filter: blur(12px) saturate(180%);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.4);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
        padding: 30px;
        margin: 20px 0;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #0f4c2a 0%, #1a7a3e 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 12px;
        padding: 12px 32px;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(15, 76, 42, 0.5);
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(15, 76, 42, 0.7);
        background: linear-gradient(135deg, #1a7a3e 0%, #0f4c2a 100%);
    }
    
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background: rgba(255, 255, 255, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 12px;
        color: #0a3d1f;
        padding: 12px;
        font-size: 14px;
        font-weight: 500;
    }
    
    .stTextInput>div>div>input::placeholder, .stTextArea>div>div>textarea::placeholder {
        color: rgba(10, 61, 31, 0.7);
    }
    
    .stSelectbox>div>div>select {
        background: rgba(255, 255, 255, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 12px;
        color: #0a3d1f;
        padding: 10px;
        font-weight: 500;
    }
    
    .stSelectbox>div>div>select option {
        background: #2d8659;
        color: white;
    }
    
    .stNumberInput>div>div>input {
        background: rgba(255, 255, 255, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 12px;
        color: #0a3d1f;
        font-weight: 500;
    }
    
    h1, h2, h3 {
        color: #ffffff;
        text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.4);
        font-weight: 700;
    }
    
    .main-title {
        font-size: 48px;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff, #e0f5ea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
        text-shadow: 2px 2px 20px rgba(0, 0, 0, 0.3);
        filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.3));
    }
    
    .subtitle {
        color: #ffffff;
        text-align: center;
        font-size: 18px;
        margin-bottom: 30px;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(255, 255, 255, 0.15);
        border-radius: 15px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.25);
        border-radius: 12px;
        color: white;
        font-weight: 600;
        padding: 12px 24px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0f4c2a 0%, #1a7a3e 100%);
    }
    
    audio {
        width: 100%;
        border-radius: 12px;
        margin-top: 15px;
    }
    
    .stSuccess {
        background: rgba(82, 214, 129, 0.3);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .stInfo {
        background: rgba(61, 183, 111, 0.3);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .stWarning {
        background: rgba(255, 193, 7, 0.3);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .stError {
        background: rgba(220, 53, 69, 0.3);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Style for markdown text in cards */
    .glass-card p, .glass-card li {
        color: #f0f9f4;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    /* Style for labels */
    label {
        color: #ffffff !important;
        font-weight: 600 !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    /* Horizontal rule */
    hr {
        border-color: rgba(255, 255, 255, 0.3);
    }
    
    /* Caption text */
    .css-1629p8f, .css-10trblm {
        color: #e0f5ea !important;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    .floating {
        animation: float 3s ease-in-out infinite;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_specialized_prompt(challenge_type, location, season, day_type, extra_info, language):
    """Generate challenge-specific prompts with expertise context"""
    
    base_context = f"Location: {location}\nSeason: {season}\nWeather: {day_type}\nAdditional Context: {extra_info}\n\n"
    
    prompts = {
        'mental_health': f"""You are a compassionate mental health counselor specializing in farmer wellbeing and rural mental health.
{base_context}
Provide empathetic, practical mental health guidance for farmers in tamilnadu,india. Include:
1. Emotional validation and support
2. Stress management techniques specific to farming life
3. Community resources and helplines
4. Practical daily wellness habits
5. Warning signs to watch for and when to seek professional help

Be warm, understanding, and culturally sensitive. and dont add any bold charecters, in 250 words""",

        'pest_disease': f"""You are an expert agricultural entomologist and plant pathologist in tamilnadu,india.
{base_context}
Provide precise pest and disease management advice including:
1. Identify likely pests/diseases for this region, season, and weather
2. Symptoms to look for (with urgency indicators)
3. Immediate action steps (organic and chemical options)
4. Preventive measures for future
5. Economic threshold levels
6. Follow-up monitoring schedule

Be specific about timing, dosages, and safety precautions.and dont add any bold charecters, in 250 words""",

        'soil_health': f"""You are a soil scientist specializing in sustainable agriculture in tamilnadu,india.
{base_context}
Provide comprehensive soil health improvement advice including:
1. Soil testing recommendations (what parameters to check)
2. Nutrient deficiency diagnosis based on season/crop
3. Organic and chemical amendment strategies
4. Soil structure improvement techniques
5. Crop rotation suggestions
6. Expected timeline for improvements

Prioritize sustainable, cost-effective solutions.and dont add any bold charecters, in 250 words""",

        'water_efficiency': f"""You are an irrigation specialist and water conservation expert in tamilnadu,india.
{base_context}
Provide water optimization strategies including:
1. Irrigation scheduling for current weather and season
2. Water-saving techniques (drip, sprinkler, mulching)
3. Rainwater harvesting opportunities
4. Moisture monitoring methods
5. Crop-specific water requirements
6. Cost-benefit analysis of different systems

Focus on practical, implementable solutions for small to medium farmers.and dont add any bold charecters, in 250 words""",

        'crop_insurance': f"""You are a crop insurance advisor and agricultural economist in tamilnadu,india.
{base_context}
Provide crop insurance guidance including:
1. Types of insurance suitable for this region/season/crop
2. Risk assessment for current conditions
3. Documentation requirements
4. Claim process overview
5. Government schemes available
6. Premium vs. coverage analysis

Include specific policy names and eligibility criteria.and dont add any bold charecters, in 250 words"""
    }
    
    prompt = prompts.get(challenge_type, prompts['pest_disease'])
   
    if language == 'Tamil':
        prompt += "\n\n**CRITICAL INSTRUCTION: Your ENTIRE response MUST be in Tamil language only. Do not mix English words. Write everything in Tamil script (தமிழில்). Translate all technical terms to Tamil.**"
    else:
        prompt += "only  in english"
    return prompt

def get_gemini_response(prompt, temperature=0.3, max_tokens=1500):
    """
    Safely get response from Gemini API with comprehensive error handling
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                candidate_count=1,
            ),
            safety_settings=safety_settings
        )

        if response.candidates:
            candidate = response.candidates[0]
            if candidate.finish_reason == 1:
                if hasattr(candidate, "text") and candidate.text:
                    return candidate.text
                elif hasattr(candidate.content, "parts") and candidate.content.parts:
                    return candidate.content.parts[0].text
                else:
                    return None
            elif candidate.finish_reason == 2:
                st.warning("⚠️ Gemini: Response blocked or incomplete (possibly safety/max tokens).")
                return None
            else:
                st.warning(f"⚠️ Gemini: Finish reason {candidate.finish_reason} -- response may be incomplete.")
                return None
        else:
            st.error("❌ Gemini: No valid response received.")
            return None
    except Exception as e:
        st.error(f"❌ Error from Gemini: {str(e)}")
        return None


def login_page():
    st.markdown('<h1 class="main-title floating">🌾 AgriSoul</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Smart Farming Assistant with AI-Powered Guidance</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs([get_text('login'), get_text('register')])
        
        with tab1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### " + get_text('login'))
            username = st.text_input(get_text('username'), key="login_user")
            password = st.text_input(get_text('password'), type="password", key="login_pass")
            
            if st.button(get_text('login'), key="login_btn"):
                hashed_pw = hash_password(password)
                if username in st.session_state.users and st.session_state.users[username]['password'] == hashed_pw:
                    st.session_state.authenticated = True
                    st.session_state.current_user = username
                    st.session_state.language = st.session_state.users[username].get('language', 'English')
                    st.success(f"{get_text('welcome')}, {st.session_state.users[username]['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials!")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### " + get_text('register'))
            reg_name = st.text_input(get_text('full_name'), key="reg_name")
            reg_age = st.number_input(get_text('age'), min_value=18, max_value=100, key="reg_age")
            
            col_a, col_b = st.columns(2)
            with col_a:
                reg_district = st.text_input(get_text('district'), key="reg_district")
            with col_b:
                reg_state = st.text_input(get_text('state'), key="reg_state")
            
            reg_farm_size = st.number_input(get_text('farm_size'), min_value=0.0, key="reg_farm")
            reg_crops = st.text_input(get_text('primary_crops'), key="reg_crops")
            reg_lang = st.selectbox(get_text('language_pref'), ['English', 'Tamil'], key="reg_lang")
            reg_username = st.text_input(get_text('username'), key="reg_user")
            reg_password = st.text_input(get_text('password'), type="password", key="reg_pass")
            
            if st.button(get_text('register'), key="reg_btn"):
                if reg_username and reg_password and reg_name:
                    st.session_state.users[reg_username] = {
                        'name': reg_name,
                        'age': reg_age,
                        'district': reg_district,
                        'state': reg_state,
                        'farm_size': reg_farm_size,
                        'crops': reg_crops,
                        'language': reg_lang,
                        'password': hash_password(reg_password)
                    }
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Please fill all required fields!")
            st.markdown('</div>', unsafe_allow_html=True)

def main_app():
    user_data = st.session_state.users[st.session_state.current_user]
    
    st.markdown(f'<h1 class="main-title">{get_text("app_title")}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{get_text("subtitle")}</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### {get_text('welcome')}, {user_data['name']}! 👋")
    with col2:
        lang_options = ['English', 'Tamil']
        current_lang = st.selectbox("🌐", lang_options, 
                                     index=lang_options.index(st.session_state.language),
                                     key="lang_select")
        if current_lang != st.session_state.language:
            st.session_state.language = current_lang
            st.rerun()
    with col3:
        if st.button(get_text('logout')):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.rerun()
    
    st.markdown("---")
  
    tab1, tab2 = st.tabs([get_text('farming_tab'), get_text('mental_tab')])
    
    with tab1:
        st.info(f"✨ {get_text('precision_mode')}")
        
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("📝 " + get_text('select_challenge'))
           
            location = st.text_input(
                get_text('location'), 
                value=f"{user_data['district']}, {user_data['state']}"
            )
          
            challenge_options = list(FARMING_CHALLENGES[st.session_state.language].keys())
            selected_challenge = st.selectbox(
                get_text('advice_type'),
                challenge_options
            )
            challenge_type = FARMING_CHALLENGES[st.session_state.language][selected_challenge]
            
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                season_options = [
                    get_text('season_kharif'),
                    get_text('season_rabi'),
                    get_text('season_summer'),
                    get_text('season_offseason')
                ]
                selected_season = st.selectbox(
                    get_text('current_season'),
                    season_options
                )
            
            with col_s2:
                weather_options = [
                    get_text('weather_rainy'),
                    get_text('weather_sunny'),
                    get_text('weather_cloudy'),
                    get_text('weather_windy')
                ]
                selected_weather = st.selectbox(
                    get_text('day_type'),
                    weather_options
                )
            
            extra_info = st.text_area(
                get_text('extra_info'),
                placeholder="E.g., specific symptoms, soil type, crop stage...",
                height=100
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button(get_text('get_advice'), key="get_advice_btn", use_container_width=True):
                with st.spinner("🌱 Generating advice..."):
                    try:
                        genai.configure(api_key="AIzaSyA4O1PoIJtYlJfVqHnSEODRfbvWAmMwAPI")                          
                        prompt = generate_specialized_prompt(
                            challenge_type,
                            location,
                            selected_season,
                            selected_weather,
                            extra_info,
                            st.session_state.language
                        )
                      
                        model = genai.GenerativeModel("models/gemini-2.5-flash")
                        response = model.generate_content(
                            prompt,
                            generation_config=genai.types.GenerationConfig(
                                temperature=FIXED_TEMPERATURE,
                                max_output_tokens=FIXED_MAX_TOKENS,
                            )
                        )
                        
                        advice_text = response.text if response.text else "No response received."
                        
                        st.session_state.farming_advice = advice_text
                        
                        lang_code = 'ta' if st.session_state.language == 'Tamil' else 'en'
                        tts = gTTS(text=advice_text, lang=lang_code, slow=False)
                        audio_file = BytesIO()
                        tts.write_to_fp(audio_file)
                        audio_file.seek(0)
                        st.session_state.farming_audio = audio_file.getvalue()
                        
                        st.success("✅ Advice generated successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        with col_right:
            if 'farming_advice' in st.session_state:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.subheader(get_text('advice_response'))
                st.markdown(st.session_state.farming_advice)
                
                st.markdown("---")
                st.subheader(get_text('voice_output'))
                st.audio(st.session_state.farming_audio, format='audio/mp3')
                st.caption(f"🎙️ Generated in {st.session_state.language}")
                st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("💚 " + get_text('mental_tab'))
        
        st.info(f"✨ {get_text('precision_mode')}")
        
        user_msg = st.text_area(
            get_text('mental_prompt'),
            placeholder="Share how you're feeling today...",
            height=150
        )
        
        if st.button(get_text('send'), key="send_mental_btn", use_container_width=True):
            if user_msg:
                with st.spinner("💭 don't worry..."):
                    try:
                        genai.configure(api_key="AIzaSyA4O1PoIJtYlJfVqHnSEODRfbvWAmMwAPI")
                        
                        prompt = f"""You are a compassionate mental health companion for farmers. 
                        Provide empathetic, supportive, and practical guidance.and dont add any bold charecters, in 250 words
                        
                        Farmer's message: {user_msg}
                        
                        Respond with:
                        1. Emotional validation
                        2. Practical coping strategies
                        3. Encouragement
                        4. Resources if needed"""
                        
                        if st.session_state.language == "Tamil":
                            prompt += "\n\n**CRITICAL: Respond ENTIRELY in Tamil. No English words.**"
                        
                        model = genai.GenerativeModel("models/gemini-2.5-flash")
                        response = model.generate_content(
                            prompt,
                            generation_config=genai.types.GenerationConfig(
                                temperature=0.5, 
                                max_output_tokens=3000,
                            )
                        )
                        
                        reply_text = response.text if response.text else "I'm here for you."
                        
                        st.session_state.mental_response = reply_text
                        
                        
                        text_1 = reply_text
                        clean_text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text_1)
                        
                        lang_code = 'ta' if st.session_state.language == 'Tamil' else 'en'
                        tts = gTTS(text=clean_text, lang=lang_code, slow=False)
                        audio_file = BytesIO()
                        tts.write_to_fp(audio_file)
                        audio_file.seek(0)
                        st.session_state.mental_audio = audio_file.getvalue()
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        if 'mental_response' in st.session_state:
            st.markdown("---")
            st.subheader(get_text('mental_response'))
            st.success(st.session_state.mental_response)
            
            st.subheader(get_text('voice_output'))
            st.audio(st.session_state.mental_audio, format='audio/mp3')
            st.caption(f"🎙️ Generated in {st.session_state.language}")
        
        st.markdown('</div>', unsafe_allow_html=True)


load_custom_css()

if not st.session_state.authenticated:
    login_page()
else:
    main_app()


st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: rgba(255,255,255,0.9); font-weight: 500; text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);">💻 Developed for Generative AI FA-2 Project • Powered by Gemini AI</p>',
    unsafe_allow_html=True
)
