import streamlit as st
from gtts import gTTS
from pydub import AudioSegment
import os

# ---------------- Helper Functions ----------------
def generate_voice(text, lang="en", filename="voice.wav"):
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    return filename

def add_background(voice_file, bg_file, output_file="final.wav"):
    narration = AudioSegment.from_file(voice_file)
    background = AudioSegment.from_file(bg_file).apply_gain(-15)
    mixed = narration.overlay(background, loop=True)
    mixed.export(output_file, format="wav")
    return output_file

def split_speakers(text):
    lines = text.split("\n")
    audio_segments = []
    female_voice = "voice_female.wav"
    male_voice = "voice_male.wav"

    for line in lines:
        if ":" in line:
            speaker, speech = line.split(":", 1)
            speech = speech.strip()
            tts_file = generate_voice(speech)
            audio_segments.append(AudioSegment.from_file(tts_file))
        else:
            tts_file = generate_voice(line)
            audio_segments.append(AudioSegment.from_file(tts_file))

    combined = sum(audio_segments)
    combined.export("story.wav", format="wav")
    return "story.wav"

def detect_mood(text):
    text_lower = text.lower()
    if any(word in text_lower for word in ["dark", "storm", "thunder", 
"night"]):
        return "sounds/thunder.mp3"
    elif any(word in text_lower for word in ["forest", "tree", "nature", 
"birds"]):
        return "sounds/forest.mp3"
    elif any(word in text_lower for word in ["coffee", "cafe", "relax", 
"chill"]):
        return "sounds/cafe.mp3"
    else:
        return None

# ---------------- Streamlit UI ----------------
st.title("🎙️ EchoVerse 2.0")
st.write("Audiobook & Study Narration with Multi-Voices and Background")

text_input = st.text_area("Enter your text here:", 
"""Alice: I think someone is following us. 
Bob: Stay calm, remember the first rule of electricity, Ohm’s Law — V = I 
× R.
Narrator: The forest grew darker, and thunder rumbled in the distance.""")

mode = st.radio("Select Mode:", ["Normal", "Story", "Study"])
rate = st.slider("Narration Speed", 0.5, 2.0, 1.0)
language = st.selectbox("Choose Language", ["en", "es", "fr", "hi"])
bg_option = st.checkbox("Add Background Audio?")

if st.button("Generate Audio"):
    if text_input.strip() == "":
        st.warning("Please enter some text!")
    else:
        if mode == "Story":
            output_file = split_speakers(text_input)
        else:
            output_file = generate_voice(text_input, lang=language)

        if bg_option:
            bg_file = detect_mood(text_input)
            if bg_file and os.path.exists(bg_file):
                output_file = add_background(output_file, bg_file)

        audio_bytes = open(output_file, "rb").read()
        st.audio(audio_bytes, format="audio/wav")
        st.download_button("💾 Download Narration", audio_bytes, 
file_name="echoverse_output.wav")
        st.success("✅ Narration generated successfully!")

