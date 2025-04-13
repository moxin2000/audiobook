import streamlit as st
from PyPDF2 import PdfReader
import pyttsx3

# Title of the Streamlit app
st.title("PDF Reader and Audio Generator")

# File uploader widget
uploaded_file = st.file_uploader("Upload your PDF file", type="pdf")

if uploaded_file is not None:
    # Read the uploaded PDF file
    pdf_reader = PdfReader(uploaded_file)
    text_data = ""

    # Extract text from each page of the PDF
    for page in pdf_reader.pages:
        text_data += page.extract_text()

    # Display extracted text in the Streamlit app
    st.write("Extracted Text:")
    st.text_area("PDF Content", text_data, height=300)

    # Text-to-speech conversion using pyttsx3
    speaker = pyttsx3.init()
    speaker.say(text_data)
    speaker.runAndWait()
    
    # Save audio to a file
    audio_file_name = "output_audio.mp3"
    speaker.save_to_file(text_data, audio_file_name)
    speaker.runAndWait()
    
    # Provide download link for the audio file
    with open(audio_file_name, "rb") as audio_file:
        st.download_button(
            label="Download Audio",
            data=audio_file,
            file_name=audio_file_name,
            mime="audio/mpeg"
        )
