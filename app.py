import streamlit as st
import PyPDF2
import ebooklib
from ebooklib import epub
import os
import tempfile
import time
from gtts import gTTS
import base64
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play
import threading

# Set up the app layout
st.set_page_config(layout="wide")
st.title("Audiobook Reader")

# Available languages and voices
LANGUAGES = {
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Italian': 'it',
    'Portuguese': 'pt',
    'Dutch': 'nl',
    'Hindi': 'hi',
    'Chinese': 'zh',
    'Japanese': 'ja'
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
if 'audio_bytes' not in st.session_state:
    st.session_state.audio_bytes = None

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
        
        elif file_ext == 'txt':
            with open(tmp_file_path, 'r', encoding='utf-8') as f:
                text = f.read()
    
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
    finally:
        os.unlink(tmp_file_path)
    
    return text

# Function to convert text to speech using gTTS
def text_to_speech(text, lang, speed):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Adjust speed by modifying the audio
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        # Load audio and adjust speed
        audio = AudioSegment.from_file(audio_bytes, format="mp3")
        audio = audio.speedup(playback_speed=1.0 + (speed * 0.5))  # Speed adjustment
        
        # Save to bytes
        output_bytes = BytesIO()
        audio.export(output_bytes, format="mp3")
        output_bytes.seek(0)
        
        return output_bytes
    except Exception as e:
        st.error(f"Error in text-to-speech: {str(e)}")
        return None

# Function to play audio
def play_audio():
    if st.session_state.audio_bytes:
        st.session_state.audio_bytes.seek(0)
        audio = AudioSegment.from_file(st.session_state.audio_bytes, format="mp3")
        play(audio)

# Function to handle playback in a separate thread
def playback_control():
    while st.session_state.playing:
        play_audio()
        time.sleep(0.1)

# Sidebar for file upload
with st.sidebar:
    st.header("Upload Your Book")
    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'epub', 'txt'])
    
    if uploaded_file:
        st.session_state.text_content = extract_text(uploaded_file)
        st.success("File uploaded successfully!")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Book Content")
    if st.session_state.text_content:
        st.text_area("Text", st.session_state.text_content, height=500, key="text_display")
    else:
        st.info("Upload a book file to see its content here")

with col2:
    st.header("Playback Controls")
    
    if st.session_state.text_content:
        # Language selection
        selected_lang = st.selectbox("Select Language", list(LANGUAGES.keys()))
        
        # Speed control
        speed = st.slider("Reading Speed", 0.0, 2.0, 1.0, 0.1)
        
        # Control buttons
        col_play, col_pause, col_back, col_forward = st.columns(4)
        
        with col_play:
            if st.button("▶️ Play"):
                st.session_state.playing = True
                st.session_state.audio_bytes = text_to_speech(
                    st.session_state.text_content, 
                    LANGUAGES[selected_lang], 
                    speed
                )
                if st.session_state.audio_bytes:
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
            
        # Audio download option
        if st.session_state.audio_bytes:
            st.download_button(
                label="Download Audio",
                data=st.session_state.audio_bytes,
                file_name="audiobook.mp3",
                mime="audio/mpeg"
            )
    else:
        st.warning("Upload a book file to enable playback controls")

# Additional instructions
st.markdown("""
### How to Use:
1. Upload your book (PDF, EPUB, or TXT) using the sidebar
2. View the extracted text content
3. Select a language and adjust the reading speed
4. Use the playback controls to listen to your book
5. Download the audio if you want to save it
""")
