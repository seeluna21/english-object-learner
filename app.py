import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Auto-Detect Object Learner", page_icon="🤖")

# --- FUNCTION: Automatically find the best model ---
def find_vision_model():
    """
    Asks Google for a list of models and picks the best one for images.
    Priority: 1.5 Flash -> 1.5 Pro -> Pro Vision
    """
    try:
        models = list(genai.list_models())
        model_names = [m.name for m in models]
        
        # 1. Try to find the specific "Flash" model (Best for speed)
        for name in model_names:
            if "gemini-1.5-flash" in name:
                return name
        
        # 2. If no Flash, look for "Pro 1.5" (Best for quality)
        for name in model_names:
            if "gemini-1.5-pro" in name:
                return name

        # 3. If neither, look for the older "Vision" model
        for name in model_names:
            if "gemini-pro-vision" in name:
                return name
                
        return None
    except Exception as e:
        # If the API key is wrong, this fails
        return None

# --- MAIN APP UI ---
st.title("🤖 Smart English Object Learner")
st.write("Upload a photo, and I will auto-detect the best AI model to describe it.")

# 1. Sidebar for API Key
api_key = st.sidebar.text_input("Enter Google API Key", type="password")

# 2. Configure API immediately if key is present
valid_model_name = None

if api_key:
    genai.configure(api_key=api_key)
    
    # Run our auto-detector
    with st.spinner("Connecting to Google to find available models..."):
        valid_model_name = find_vision_model()
    
    if valid_model_name:
        st.sidebar.success(f"✅ Connected! Using model: `{valid_model_name}`")
    else:
        st.sidebar.error("❌ Could not find a vision model. Check your API Key or VPN.")

# 3. File Uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Your Photo', use_container_width=True)

    if st.button("Analyze Image"):
        if not api_key:
            st.error("Please enter your API Key in the sidebar first!")
        elif not valid_model_name:
            st.error("I couldn't find a valid AI model to use. Please check your connection.")
        else:
            with st.spinner(f'Analyzing with {valid_model_name}...'):
                try:
                    # Use the AUTO-DETECTED model name
                    model = genai.GenerativeModel(valid_model_name)
                    
                    prompt = """
                    Analyze this image. 
                    1. List the main objects visible in the image.
                    2. For each object, give the English name and a short example sentence.
                    3. Format it as a nice list.
                    """
                    
                    response = model.generate_content([prompt, image])
                    st.success("Analysis Complete!")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")
