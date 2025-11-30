import streamlit as st
import google.generativeai as genai
from PIL import Image

st.title("Simple English Learner")

# 1. 在这里输入你的 Key
api_key = st.sidebar.text_input("Paste your API Key here", type="password")

# 2. 上传图片
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if uploaded_file and api_key:
    # 显示图片
    image = Image.open(uploaded_file)
    st.image(image, caption='Your Photo', use_container_width=True)

    if st.button("Start Learning"):
        try:
            # 配置 Google
            genai.configure(api_key=api_key)
            
            # 直接使用最通用的模型
            model = genai.GenerativeModel("gemini-1.5-pro")
            
            # 发送请求
            with st.spinner('Asking AI...'):
                prompt = "List every object in this image in English. Format as a list."
                response = model.generate_content([prompt, image])
                st.write(response.text)
                
        except Exception as e:
            st.error(f"出错啦 (Error): {e}")
            st.info("💡 如果显示 '404' 或 'User location'，请检查 VPN 是否开启了全局模式，且节点不是香港。")

