import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Clear Object Learner", page_icon="👀")
st.title("👀 Learn English by looking at pictures (Clear Mode)")

# 1. 输入 Key
api_key = st.sidebar.text_input("Google API Key", type="password")

# 2. 上传图片
uploaded_file = st.file_uploader("Upload image", type=["jpg", "png", "jpeg"])

# --- 自动寻找模型函数 ---
def get_available_model():
    try:
        all_models = list(genai.list_models())
        vision_models = [m.name for m in all_models if 'generateContent' in m.supported_generation_methods]
        
        # 优先找 flash (速度快)，其次 pro
        for name in vision_models:
            if "flash" in name: return name
        for name in vision_models:
            if "pro" in name and "vision" not in name: return name
        return vision_models[0] if vision_models else None
    except:
        return None

if uploaded_file and api_key:
    image = Image.open(uploaded_file)
    st.image(image, caption='Your Photo', use_container_width=True)

    if st.button("开始分析 (Start Learning)"):
        genai.configure(api_key=api_key)
        
        with st.spinner('AI is organizing Sheets...'):
            model_name = get_available_model()
            
            if model_name:
                model = genai.GenerativeModel(model_name)
                
                # --- 关键修改在这里：提示词 Prompt ---
                prompt = """
                Look at this image. Identify 8-10 key objects for an English learner.
                
                Please output the result ONLY as a Markdown Table with these 2 columns:
                1. **English Word** (The object name)
                2. **Location & Clue** (Where is it? e.g., "Bottom right, yellow color", "In the man's hand")
                
                Do not write any intro text, just the table.
                """
                
                try:
                    response = model.generate_content([prompt, image])
                    st.success(f"✅ Analysis complete! (Using {model_name})")
                    st.markdown("### 📝 word-matching table")
                    st.markdown(response.text) # Streamlit 会自动把 Markdown 渲染成漂亮的表格
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("No available model found，Check the API Key or network。")
