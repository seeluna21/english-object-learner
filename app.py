import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Setup
st.set_page_config(page_title="English Object Learner", page_icon="🎓")
st.title("🎓 English Object Learner")
st.write("Upload a photo, and I will tell you what is inside!")

# 2. Sidebar for API Key (Keeps it safe)
api_key = st.sidebar.text_input("Enter Google API Key", type="password")

# 3. File Uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the image to the user
    image = Image.open(uploaded_file)
    st.image(image, caption='Your Photo', use_container_width=True)

    # 4. The Analysis Button
    if st.button("Analyze Image"):
        if not api_key:
            st.error("Please enter your API Key in the sidebar first!")
        else:
            with st.spinner('Asking Gemini...'):
                try:
                    # Configure Gemini
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')

                    # Prompt designed for language learning
                    prompt = """
                    Analyze this image. 
                    1. List the main objects visible in the image.
                    2. For each object, give the English name and a short example sentence.
                    3. Format it as a nice list.
                    """

                    # Get response
                    response = model.generate_content([prompt, image])

                    # Display result
                    st.success("Analysis Complete!")
                    st.markdown(response.text)

                except Exception as e:
                    st.error(f"An error occurred: {e}")