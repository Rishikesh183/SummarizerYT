import streamlit as st
from dotenv import load_dotenv
import os
import re
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, VideoUnavailable


load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


prompt = """
You are a helpful assistant that summarizes YouTube videos. 
Given a transcript, your task is to summarize it clearly and concisely in bullet points. 
Make sure the summary:
- Covers the key ideas, arguments, and conclusions.
- Keeps things simple, avoiding technical jargon.
- Uses bullet points only.
- Does not exceed 250 words.

Here is the transcript text:
"""

def extract_video_id(youtube_url):
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", youtube_url)
    return video_id_match.group(1) if video_id_match else None


def extract_transcript_details(video_id):
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = " ".join([entry['text'] for entry in transcript_data])
        return full_transcript
    except TranscriptsDisabled:
        st.error("Transcripts are disabled for this video.")
    except VideoUnavailable:
        st.error("The video is unavailable.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    return None


def generate_gemini_summary(transcript_text):
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt + transcript_text)
    return response.text


st.set_page_config(page_title="YouTube Notes Generator", layout="centered")
st.title("📽️ YouTube Video to Notes Generator")
youtube_link = st.text_input("🔗 Enter YouTube Video URL:")

if st.button("📝 Get Detailed Notes"):
    if youtube_link:
        video_id = extract_video_id(youtube_link)
        # print(video_id)
        if video_id:
            st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
        else:
            st.warning("Could not extract video ID. Please check the URL.")
    if not youtube_link:
        st.warning("Please enter a YouTube link.")
    else:
        with st.spinner("Fetching transcript and generating summary..."):
            video_id = extract_video_id(youtube_link)
            transcript_text = extract_transcript_details(video_id)
            if transcript_text:
                summary = generate_gemini_summary(transcript_text)
                st.markdown("## 📌 Detailed Notes:")
                st.write(summary)
