import streamlit as st
import pyttsx3
import PyPDF2
import ebooklib
from ebooklib import epub
import mobi
import os
import tempfile
import time
from pydub import AudioSegment
from pydub.playback import play
import threading

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Set up the app layout
st.set_page_config(layout="wide")
st.title("Audiobook Reader")

# Available voices (adjust based on your system's available voices)
VOICES = {
    "David (English)": "english-m",
    "Zira (English)": "english-f",
    "Microsoft David": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_DAVID_11.0",
    "Microsoft Zira": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0",
    "Google US English": "com.apple.speech.synthesis.voice.Alex",
    "Google UK English": "com.apple.speech.synthesis.voice.Daniel",
    "Samantha (Premium)": "com.apple.speech.synthesis.voice.samantha.premium",
    "Moira (Irish)": "com.apple.speech.synthesis.voice.moira",
    "Tessa (South African)": "com.apple.speech.synthesis.voice.tessa",
    "Serena (Australian)": "com.apple.speech.synthesis.voice.serena"
}

# State management
if 'playing' not in st.session_state:
    st.session_state.playing = False
if 'current_position' not in st.session_state:
    st.session_state.current_position = 0
if 'text_content' not in st.session_state:
    st.session_state.text_content = ""
if 'audio_file' not in st.session_state:
    st.session_state.audio_file = None

# Function to extract text from different file types
def extract_text(uploaded_file):
    file_ext = uploaded_file.name.split('.')[-1].lower()
    text = ""
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name
    
    try:
        if file_ext == 'pdf':
            reader = PyPDF2.PdfReader(tmp_file_path)
            for page in reader.pages:
                text += page.extract_text()
        
        elif file_ext == 'epub':
            book = epub.read_epub(tmp_file_path)
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    text += item.get_content().decode('utf-8')
        
        elif file_ext == 'mobi':
            with mobi.open(tmp_file_path) as mobi_file:
                text = mobi_file.read()
        
        elif file_ext == 'txt':
            with open(tmp_file_path, 'r', encoding='utf-8') as f:
                text = f.read()
    
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
    finally:
        os.unlink(tmp_file_path)
    
    return text

# Function to convert text to speech
def text_to_speech(text, voice, speed):
    engine = pyttsx3.init()
    
    try:
        # Set voice
        if voice in VOICES.values():
            engine.setProperty('voice', voice)
        else:
            st.warning("Selected voice not found. Using default voice.")
        
        # Set speed
        engine.setProperty('rate', 150 + (speed * 50))  # Base 150, adjust by speed
        
        # Save to temporary file
        temp_file = "temp_audio.wav"
        engine.save_to_file(text, temp_file)
        engine.runAndWait()
        
        return temp_file
    except Exception as e:
        st.error(f"Error in text-to-speech: {str(e)}")
        return None

# Function to play audio
def play_audio():
    if st.session_state.audio_file:
        audio = AudioSegment.from_wav(st.session_state.audio_file)
        play(audio)

# Function to handle playback in a separate thread
def playback_control():
    while st.session_state.playing:
        play_audio()
        time.sleep(0.1)

# Sidebar for file upload
with st.sidebar:
    st.header("Upload Your Book")
    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'epub', 'mobi', 'txt'])
    
    if uploaded_file:
        st.session_state.text_content = extract_text(uploaded_file)
        st.success("File uploaded successfully!")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Book Content")
    if st.session_state.text_content:
        st.text_area("Text", st.session_state.text_content, height=500)
    else:
        st.info("Upload a book file to see its content here")

with col2:
    st.header("Playback Controls")
    
    if st.session_state.text_content:
        # Voice selection
        selected_voice = st.selectbox("Select Voice", list(VOICES.keys()))
        
        # Speed control
        speed = st.slider("Reading Speed", 0.0, 2.0, 1.0, 0.1)
        
        # Control buttons
        col_play, col_pause, col_back, col_forward = st.columns(4)
        
        with col_play:
            if st.button("▶️ Play"):
                st.session_state.playing = True
                st.session_state.audio_file = text_to_speech(
                    st.session_state.text_content, 
                    VOICES[selected_voice], 
                    speed
                )
                threading.Thread(target=playback_control).start()
        
        with col_pause:
            if st.button("⏸ Pause"):
                st.session_state.playing = False
        
        with col_back:
            if st.button("⏪ 15s"):
                st.session_state.current_position = max(0, st.session_state.current_position - 15)
        
        with col_forward:
            if st.button("⏩ 15s"):
                st.session_state.current_position += 15
        
        # Progress bar
        st.progress(st.session_state.current_position / max(1, len(st.session_state.text_content.split())))
        
        # Status
        if st.session_state.playing:
            st.success("Playing...")
        else:
            st.info("Ready to play")
    else:
        st.warning("Upload a book file to enable playback controls")

# Additional instructions
st.markdown("""
### How to Use:
1. Upload your book (PDF, EPUB, MOBI, or TXT) using the sidebar
2. View the extracted text content
3. Select a voice and adjust the reading speed
4. Use the playback controls to listen to your book
""")