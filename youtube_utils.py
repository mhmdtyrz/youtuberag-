from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import streamlit as st
import os
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

class YouTubeAPI:
    def __init__(self, api_key):
        # Explicitly disable using default credentials
        self.youtube = build('youtube', 'v3', 
                            developerKey=api_key,
                            static_discovery=False)

    def get_channel_video_ids(self, channel_id, max_videos=50):
        """
        Fetches video IDs from a given YouTube channel's uploads playlist.
        """
        video_ids = []
        try:
            # 1. Get uploads playlist ID
            res = self.youtube.channels().list(id=channel_id, part='contentDetails').execute()
            if not res['items']:
                st.error(f"Could not find channel with ID: {channel_id}")
                return []
            playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

            next_page_token = None
            while True:
                res = self.youtube.playlistItems().list(
                    playlistId=playlist_id,
                    part='contentDetails',
                    maxResults=min(50, max_videos - len(video_ids)), # Fetch up to 50 videos per page, respecting max_videos limit
                    pageToken=next_page_token
                ).execute()

                for item in res['items']:
                    video_ids.append(item['contentDetails']['videoId'])
                    if len(video_ids) >= max_videos:
                        break
                
                next_page_token = res.get('nextPageToken')
                if not next_page_token or len(video_ids) >= max_videos:
                    break
            
            return video_ids

        except HttpError as e:
            st.error(f"YouTube API error: {e}")
            st.error("Please check your GOOGLE_API_KEY and ensure the YouTube Data API v3 is enabled for your project.")
            return []
        except Exception as e:
            st.error(f"An unexpected error occurred while fetching video IDs: {e}")
            return []

    def get_video_details_and_transcripts(self, video_ids):
        """
        Fetches details and attempts to acquire transcripts for a list of video IDs.
        """
        st.info(f"Fetching details and transcripts for {len(video_ids)} videos...")
        processed_video_data = []
        for video_id in video_ids:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            try:
                # Get transcript for the video
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                
                # Concatenate the transcript text
                transcript_text = " ".join([d['text'] for d in transcript_list])

                processed_video_data.append({
                    'video_id': video_id,
                    'url': video_url,
                    'transcript': transcript_text
                })
                st.success(f"Successfully fetched transcript for video: {video_id}")
            except (NoTranscriptFound, TranscriptsDisabled) as e:
                st.warning(f"Could not retrieve transcript for video {video_id}: {e}")
                processed_video_data.append({
                    'video_id': video_id,
                    'url': video_url,
                    'transcript': "No transcript found or transcripts are disabled for this video."
                })
            except Exception as e:
                st.error(f"Failed to process video {video_id}: {e}")
                processed_video_data.append({
                    'video_id': video_id,
                    'url': video_url,
                    'transcript': f"Error: {e}"
                })
        return processed_video_data

api_key = os.getenv('YOUTUBE_API_KEY')
if api_key:
    youtube_api = YouTubeAPI(api_key)
else:
    youtube_api = None
