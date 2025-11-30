import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- CRITICAL FIX FOR VPN USERS ---
# Replace '7890' with YOUR specific VPN port if it's different.
# If you don't know, try 7890 first, then 10809.
PROXY_PORT = "7890" 
os.environ["HTTP_PROXY"] = f"http://127.0.0.1:{PROXY_PORT}"
os.environ["HTTPS_PROXY"] = f"http://127.0.0.1:{PROXY_PORT}"

st.set_page_config(page_title="Auto-Detect Object Learner", page_icon="🤖")

# --- FUNCTION: Debugging version ---
def find_vision_model():
    try:
        models = list(genai.list_models())
        # Print what we found to the terminal for debugging
        print(f"DEBUG: Found {len(models)} models.") 
        
        for m in models:
            print(f" - {m.name}") # Print names to terminal
            if "gemini-1.5-flash" in m.name: return m.name
            if "gemini-1.5-pro" in m.name: return m.name
            if "gemini-pro-vision" in m.name: return m.name
        
        return None
    except Exception as e:
        # RETURN THE ACTUAL ERROR MESSAGE
        return f"ERROR: {str(e)}"

# --- MAIN APP UI ---
st.title("🤖 Smart English Object Learner")

# 1. Sidebar
api_key = st.sidebar.text_input("Enter Google API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    
    with st.spinner("Connecting..."):
        result = find_vision_model()
    
    # CHECK IF RESULT IS AN ERROR
    if result and result.startswith("ERROR"):
        st.sidebar.error("❌ Connection Failed!")
        st.error(f"⚠️ **Detailed Error:** {result}")
        st.warning("If the error says 'ConnectTimeout', your VPN Port in the code is wrong.")
    elif result:
        st.sidebar.success(f"✅ Connected! Using: `{result}`")
        valid_model_name = result
    else:
        st.sidebar.error("❌ No models found (List was empty).")

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

