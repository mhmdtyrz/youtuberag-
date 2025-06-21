import os
from youtube_utils import YouTubeAPI
import streamlit as st

# Set API key directly with a clear name
os.environ['YOUTUBE_API_KEY'] = 'AIzaSyB9AI_2HOqxqui3NB4pN6cAVmY40imrJnE'

# Initialize YouTubeAPI
api_key = os.getenv('YOUTUBE_API_KEY')
if not api_key:
    st.error("YOUTUBE_API_KEY environment variable not set.")
    st.stop()

youtube_api = YouTubeAPI(api_key)

# Channel ID for @DanKoeTalks
channel_id = 'UCV0qA-eDDyazD_Jg0_J5x7A' 
max_videos_to_fetch = 5 # You can adjust this number for testing

st.title("YouTube RAG Test Run")

st.write(f"Fetching video IDs for channel: {channel_id}")
video_ids = youtube_api.get_channel_video_ids(channel_id, max_videos=max_videos_to_fetch)

if video_ids:
    st.write(f"Found {len(video_ids)} video IDs. Fetching details and transcripts...")
    processed_data = youtube_api.get_video_details_and_transcripts(video_ids)
    
    st.subheader("Processed Video Data:")
    for data in processed_data:
        st.write(f"**Video ID:** {data['video_id']}")
        st.write(f"**URL:** {data['url']}")
        st.text_area("Transcript", data['transcript'], height=150)
        st.write("---")
else:
    st.warning("No video IDs found or an error occurred.")