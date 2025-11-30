import streamlit as st
import google.generativeai as genai
from PIL import Image

st.title("🤖 Auto-Detect Model App")

# 1. 输入 Key
api_key = st.sidebar.text_input("Google API Key", type="password")

# 2. 上传图片
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

# --- 核心功能：自动寻找模型 ---
def get_available_model():
    """询问 Google 有哪些模型可用，并自动选一个"""
    try:
        # 获取所有模型列表
        all_models = list(genai.list_models())
        
        # 筛选：我们要找支持 'generateContent' (也就是能聊天的) 模型
        vision_models = []
        for m in all_models:
            if 'generateContent' in m.supported_generation_methods:
                vision_models.append(m.name)
        
        # 优先级排序：如果有 flash 用 flash，没有就找 pro，再没有就随便拿一个
        for name in vision_models:
            if "flash" in name: return name
        for name in vision_models:
            if "pro" in name and "vision" not in name: return name
        
        # 如果都没有，就返回列表里的第一个
        if vision_models:
            return vision_models[0]
            
        return None
    except Exception as e:
        return None

if uploaded_file and api_key:
    image = Image.open(uploaded_file)
    st.image(image, caption='Your Photo', use_container_width=True)

    if st.button("Start Learning"):
        # 配置 API
        genai.configure(api_key=api_key)
        
        with st.spinner('🔍正在自动寻找可用的模型 (Auto-detecting model)...'):
            # 自动找模型
            best_model_name = get_available_model()
            
        if best_model_name:
            st.success(f"✅ 成功连接! 使用模型: {best_model_name}")
            
            try:
                # 开始识别
                model = genai.GenerativeModel(best_model_name)
                response = model.generate_content(["Describe this image in English words list.", image])
                st.write("### Analysis Result:")
                st.write(response.text)
            except Exception as e:
                st.error(f"模型找到了，但生成失败: {e}")
        else:
            st.error("❌ 无法找到任何可用模型！")
            st.info("原因可能是：1. VPN节点是香港（请换美国/台湾）；2. API Key 无效；3. Python库太旧（请运行 `pip install --upgrade google-generativeai`）")
