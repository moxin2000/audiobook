import streamlit as st
import pdfplumber
from gtts import gTTS

# Title of the Streamlit app
st.title("PDF Reader and Audio Generator")

# File uploader widget
uploaded_file = st.file_uploader("Upload your PDF file", type="pdf")

if uploaded_file is not None:
    # Use pdfplumber to extract text
    with pdfplumber.open(uploaded_file) as pdf:
        text_data = ""
        for page in pdf.pages:
            text_data += page.extract_text()

    # Display extracted text in the Streamlit app
    st.write("Extracted Text:")
    st.text_area("PDF Content", text_data, height=300)

    # Text-to-speech conversion using gTTS
    tts = gTTS(text=text_data, lang='en')
    audio_file_name = "output_audio.mp3"
    tts.save(audio_file_name)

    # Provide download link for the audio file
    with open(audio_file_name, "rb") as audio_file:
        st.download_button(
            label="Download Audio",
            data=audio_file,
            file_name=audio_file_name,
            mime="audio/mpeg"
        )
