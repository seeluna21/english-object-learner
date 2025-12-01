import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import io
import json
import re

# --- 页面设置 ---
st.set_page_config(page_title="AI Visual English", page_icon="🎧", layout="wide")

# --- 自定义 CSS (让界面更漂亮) ---
st.markdown("""
<style>
    .word-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 5px solid #ff4b4b;
    }
    .big-word {
        font-size: 24px;
        font-weight: bold;
        color: #1f77b4;
    }
    .meaning {
        font-size: 18px;
        color: #333;
    }
    .sentence {
        font-style: italic;
        color: #666;
        font-size: 14px;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎧 AI 看图学英语 (Pro版)")

# --- 侧边栏设置 ---
with st.sidebar:
    st.header("⚙️ 设置")
    api_key = st.text_input("Google API Key", type="password")
    st.info("💡 提示: 请确保 VPN 开启且节点不是香港。")

# --- 核心函数 ---
def get_model_name():
    """自动寻找可用模型"""
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m in models: 
            if "flash" in m: return m
        return models[0] if models else None
    except:
        return None

def text_to_speech(text):
    """把文字变成语音 Bytes"""
    try:
        tts = gTTS(text=text, lang='en')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        return mp3_fp
    except:
        return None

# --- 主界面 ---
uploaded_file = st.file_uploader("📸 上传一张图片", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # 左右分栏：左边显示图，右边显示学习卡片
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        image = Image.open(uploaded_file)
        st.image(image, caption='Your Photo', use_container_width=True)
        
        start_btn = st.button("🚀 开始分析 (Analyze)", use_container_width=True)

    if start_btn and api_key:
        genai.configure(api_key=api_key)
        
        with col2:
            with st.spinner('🤖 AI 正在识别物体并生成发音... (可能需要几秒钟)'):
                model_name = get_model_name()
                
                if not model_name:
                    st.error("❌ 无法连接 Google，请检查网络。")
                    st.stop()

                model = genai.GenerativeModel(model_name)
                
                # --- Prompt Engineering: 强制要求返回 JSON 格式 ---
                prompt = """
                Analyze this image. Identify 5-7 distinct objects suitable for an English learner.
                
                Return the result strictly as a JSON list. Do not output Markdown code blocks (```json).
                Format:
                [
                    {
                        "word": "English Word",
                        "phonetic": "/IPA/",
                        "chinese": "中文意思",
                        "sentence": "A simple example sentence containing the word."
                    },
                    ...
                ]
                """
                
                try:
                    response = model.generate_content([prompt, image])
                    
                    # 清洗数据：有时候 AI 会加 ```json ... ```，我们要去掉
                    clean_text = response.text.replace("```json", "").replace("```", "").strip()
                    
                    # 解析 JSON
                    vocab_list = json.loads(clean_text)
                    
                    st.success(f"✅ 识别成功! (Found {len(vocab_list)} words)")
                    
                    # --- 循环生成精美的单词卡片 ---
                    for item in vocab_list:
                        # 使用 Streamlit 的容器来做卡片
                        with st.container():
                            st.markdown(f"""
                            <div class="word-card">
                                <span class="big-word">{item['word']}</span> 
                                <span style="color:gray;">{item.get('phonetic', '')}</span>
                                <br>
                                <span class="meaning">{item['chinese']}</span>
                                <div class="sentence">例句: {item['sentence']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # 生成音频
                            audio_bytes = text_to_speech(item['word'])
                            if audio_bytes:
                                st.audio(audio_bytes, format='audio/mp3')
                            else:
                                st.caption("🔇 语音生成失败 (网络原因)")
                                
                except json.JSONDecodeError:
                    st.error("AI 返回的数据格式乱了，请重试一次。")
                except Exception as e:
                    st.error(f"发生错误: {e}")

    elif start_btn and not api_key:
        st.warning("请在左侧侧边栏输入 API Key！")
