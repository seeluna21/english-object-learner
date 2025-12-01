import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import io
import json
import re

# --- Page Config ---
st.set_page_config(page_title="AI Contextual English", page_icon="🇬🇧", layout="wide")

# --- Custom CSS for the English UI ---
st.markdown("""
<style>
    /* Card Container */
    .word-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .word-card:hover {
        transform: scale(1.01);
        border-left: 5px solid #1f77b4;
    }
    
    /* Typography */
    .big-word {
        font-size: 26px;
        font-weight: 700;
        color: #2c3e50;
    }
    .phonetic {
        font-family: 'Courier New', monospace;
        color: #7f8c8d;
        font-size: 16px;
        margin-left: 10px;
    }
    .location-tag {
        background-color: #e8f4f9;
        color: #2980b9;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
        display: inline-block;
        margin-top: 5px;
        margin-bottom: 10px;
    }
    .definition {
        font-size: 16px;
        color: #34495e;
        line-height: 1.4;
        margin-bottom: 8px;
    }
    .example-sent {
        font-style: italic;
        color: #555;
        border-left: 3px solid #ddd;
        padding-left: 10px;
        margin-top: 8px;
    }

    /* Scenario Box */
    .scenario-box {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 25px;
        border-left: 6px solid #27ae60;
        margin-top: 20px;
    }
    .scenario-title {
        font-size: 20px;
        font-weight: bold;
        color: #27ae60;
        margin-bottom: 10px;
    }
    .scenario-text {
        font-size: 16px;
        line-height: 1.6;
        color: #2c3e50;
        white-space: pre-line; /* Keeps line breaks in dialogue */
    }
</style>
""", unsafe_allow_html=True)

st.title("🇬🇧 AI Contextual English")
st.markdown("Upload a photo to learn vocabulary in context.")

# --- Sidebar ---
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Google API Key", type="password")
    st.caption("Ensure your VPN is active (USA/JP nodes recommended).")

# --- Helper Functions ---
def get_model_name():
    try:
        # Prioritize 1.5 Flash for speed, then Pro
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m in models: 
            if "flash" in m: return m
        for m in models: 
            if "pro" in m and "vision" not in m: return m
        return models[0] if models else None
    except:
        return None

# Find this function in your app.py
def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='en')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        
        # --- ADD THIS LINE (CRITICAL FOR IPHONE) ---
        mp3_fp.seek(0)  # Rewind to the start of the file
        
        return mp3_fp
    except:
        return None

# --- Main Logic ---
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Layout: Image on Left, Results on Right
    col1, col2 = st.columns([1, 1.3])
    
    with col1:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Scene', use_container_width=True)
        analyze_btn = st.button("✨ Analyze Scene", use_container_width=True, type="primary")

    if analyze_btn:
        if not api_key:
            st.error("Please enter your Google API Key in the sidebar.")
        else:
            genai.configure(api_key=api_key)
            
            with col2:
                with st.spinner('🔍 Analyzing visual context & generating scenario...'):
                    model_name = get_model_name()
                    
                    if not model_name:
                        st.error("Connection failed. No AI models found.")
                        st.stop()

                    model = genai.GenerativeModel(model_name)
                    
                    # --- PROMPT: Requesting both Objects + Scenario in JSON ---
                    prompt = """
                    Act as an expert English teacher. Look at this image.
                    
                    Part 1: Identify 5 key objects visible in the image.
                    Part 2: Create a short, natural "Scenario Mode" text. This should be a short dialogue (A/B conversation) OR a descriptive story that *could* happen in this specific scene.
                    
                    Return ONLY raw JSON with this structure (no markdown tags):
                    {
                        "vocabulary": [
                            {
                                "word": "Object Name",
                                "phonetic": "/IPA/",
                                "location": "Where is it? (e.g. Bottom left, In the background)",
                                "definition": "Simple English definition",
                                "sentence": "A natural sentence using the word."
                            }
                        ],
                        "scenario_title": "A suitable title for the scene",
                        "scenario_text": "The dialogue or story text..."
                    }
                    """
                    
                    try:
                        response = model.generate_content([prompt, image])
                        
                        # Clean JSON (remove markdown ```json if present)
                        clean_text = response.text.replace("```json", "").replace("```", "").strip()
                        data = json.loads(clean_text)
                        
                        # --- 1. Vocabulary Section ---
                        st.subheader("📚 Key Vocabulary")
                        
                        vocab_list = data.get("vocabulary", [])
                        
                        for item in vocab_list:
                            with st.container():
                                # HTML Card
                                st.markdown(f"""
                                <div class="word-card">
                                    <div>
                                        <span class="big-word">{item['word']}</span>
                                        <span class="phonetic">{item['phonetic']}</span>
                                    </div>
                                    <div class="location-tag">📍 {item['location']}</div>
                                    <div class="definition">{item['definition']}</div>
                                    <div class="example-sent">"{item['sentence']}"</div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Audio Button (Compact)
                                audio_bytes = text_to_speech(item['word'])
                                if audio_bytes:
                                    st.audio(audio_bytes, format='audio/mpeg')

                        # --- 2. Scenario Mode Section ---
                        st.markdown("---")
                        st.subheader("🎭 Scenario Mode")
                        
                        scenario_title = data.get("scenario_title", "Scene Context")
                        scenario_text = data.get("scenario_text", "No scenario generated.")
                        
                        st.markdown(f"""
                        <div class="scenario-box">
                            <div class="scenario-title">{scenario_title}</div>
                            <div class="scenario-text">{scenario_text}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Audio for Scenario (Optional: Read the whole story)
                        st.caption("Listen to the scenario:")
                        scenario_audio = text_to_speech(scenario_text)
                        if scenario_audio:
                            st.audio(scenario_audio, format='audio/mp3')

                    except json.JSONDecodeError:
                        st.error("Error parsing AI response. Please try again.")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")

