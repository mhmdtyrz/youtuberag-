import streamlit as st
import os
import traceback

# Try to import database, fall back gracefully if not available
try:
    from database import DatabaseManager
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    DatabaseManager = None

# Import YouTube utilities
from youtube_utils import YouTubeAPI

# Page configuration
st.set_page_config(
    page_title="YouTube Knowledge Base",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set API keys from environment variables
os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY', 'AIzaSyAS2awU6wrptq8u7veqJk6fZJCCa93WFlg')
os.environ['YOUTUBE_API_KEY'] = os.getenv('YOUTUBE_API_KEY', 'AIzaSyB9AI_2HOqxqui3NB4pN6cAVmY40imrJnE')

# Set database configuration from environment variables
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', 'postgresql://neondb_owner:npg_BuTHn5S4flwZ@ep-broad-field-a6tawfjd.us-west-2.aws.neon.tech/neondb?sslmode=require')
os.environ['PGDATABASE'] = os.getenv('PGDATABASE', 'neondb')
os.environ['PGHOST'] = os.getenv('PGHOST', 'ep-broad-field-a6tawfjd.us-west-2.aws.neon.tech')
os.environ['PGPORT'] = os.getenv('PGPORT', '5432')
os.environ['PGUSER'] = os.getenv('PGUSER', 'neondb_owner')
os.environ['PGPASSWORD'] = os.getenv('PGPASSWORD', 'npg_BuTHn5S4flwZ')


def main():
    """Main application"""
    st.title("🎥 YouTube Knowledge Base")
    st.markdown("Ask questions about YouTube channel content using AI-powered search")
    
    # Initialize database connection if available
    db = None
    if DATABASE_AVAILABLE:
        @st.cache_resource
        def init_database():
            db_manager = DatabaseManager()
            if db_manager.connect():
                db_manager.create_tables()
                return db_manager
            return None
        
        db = init_database()
    
    # Check for API keys
    youtube_api_key = os.getenv("YOUTUBE_API_KEY", "")
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    
    # Determine which AI service is available
    ai_service = None
    if openai_api_key:
        ai_service = "OpenAI"
    elif gemini_api_key:
        ai_service = "Gemini"
    
    # Show API key status
    with st.sidebar:
        st.header("⚙️ API Configuration")
        
        # YouTube API status
        if youtube_api_key:
            st.success("✅ YouTube API Key: Connected")
        else:
            st.error("❌ YouTube API Key: Missing")
            st.markdown("Set `YOUTUBE_API_KEY` environment variable")
        
        # AI API status
        if ai_service:
            st.success(f"✅ {ai_service} API Key: Connected")
        else:
            st.error("❌ AI API Key: Missing")
            st.markdown("Set either `OPENAI_API_KEY` or `GEMINI_API_KEY` environment variable")
        
        # Database status
        if db:
            st.success("✅ Database: Connected")
            # Show database stats
            if db.conn:
                stats = db.get_database_stats()
                if stats:
                    st.metric("Channels", stats.get('total_channels', 0))
                    st.metric("Videos", stats.get('total_videos', 0))
                    st.metric("Text Chunks", stats.get('total_chunks', 0))
        elif DATABASE_AVAILABLE:
            st.error("❌ Database: Connection failed")
        else:
            st.warning("Could not import DatabaseManager. Database features disabled.")

        
        st.divider()
        
        # Show available features when APIs are ready
        if youtube_api_key and ai_service:
            st.subheader("🚀 Ready to Process")
            
            # Channel input
            channel_id = st.text_input(
                "YouTube Channel ID",
                placeholder="UC1234567890abcdef",
                help="Find the channel ID in the channel URL"
            )
            
            max_videos = st.number_input(
                "Max videos to process",
                min_value=1,
                max_value=100,
                value=20,
                help="Limit for testing and cost control"
            )
            
            if st.button("🚀 Process Channel", type="primary"):
                if channel_id:
                    if youtube_api_key:
                        st.info(f"Processing channel ID: {channel_id} for up to {max_videos} videos...")
                        youtube_api = YouTubeAPI(youtube_api_key)
                        
                        with st.spinner("Fetching video IDs..."):
                            video_ids = youtube_api.get_channel_video_ids(channel_id, max_videos)
                        
                        if video_ids:
                            st.success(f"Found {len(video_ids)} videos.")
                            st.write("Video IDs:", video_ids)
                            
                            # Placeholder for transcript acquisition
                            with st.spinner("Acquiring video details and transcripts..."):
                                processed_videos = youtube_api.get_video_details_and_transcripts(video_ids)
                            
                            if processed_videos:
                                st.success("Video processing complete!")
                                for video in processed_videos:
                                    st.write(f"**Video ID:** {video['video_id']}")
                                    st.write(f"**URL:** {video['url']}")
                                    st.text_area("Transcript", video['transcript'], height=150)

                            else:
                                st.warning("No videos processed or transcripts acquired.")
                        else:
                            st.error("No video IDs found for the given channel or an error occurred.")
                    else:
                        st.error("YouTube API Key is missing. Please configure it in the sidebar.")
                else:
                    st.error("Please enter a valid YouTube Channel ID")
    
    # Main content area
    if not youtube_api_key or not ai_service:
        st.info("Please configure your API keys in the sidebar to get started.")
        
        # Show setup instructions
        with st.expander("📋 Setup Instructions"):
            st.markdown("""
            ### Required API Keys
            
            **YouTube Data API Key:**
            1. Go to [Google Cloud Console](https://console.cloud.google.com/)
            2. Create a new project or select existing one
            3. Enable YouTube Data API v3
            4. Create credentials (API Key)
            5. Set as `YOUTUBE_API_KEY` environment variable
            
            **AI API Key (choose one):**
            
            **Option 1: OpenAI API**
            1. Go to [OpenAI Platform](https://platform.openai.com/)
            2. Sign up or log in
            3. Go to API Keys section
            4. Create new API key
            5. Set as `OPENAI_API_KEY` environment variable
            
            **Option 2: Google Gemini API**
            1. Go to [Google AI Studio](https://aistudio.google.com/)
            2. Sign up or log in
            3. Get API key
            4. Set as `GEMINI_API_KEY` environment variable
            
            ### How to Set Environment Variables in Replit
            1. Click on "Secrets" in the left sidebar
            2. Add your API keys as secrets
            3. Restart the application
            """)
    else:
        # Show that the app is ready and what it does
        st.markdown("""
        ### What this app does:
        
        1. **Fetch YouTube Videos**: Connect to any YouTube channel and get video metadata
        2. **Extract Transcripts**: Download video transcripts/captions automatically  
        3. **Process Content**: (Next Steps) Break down long videos into searchable chunks
        4. **Build Knowledge Base**: (Next Steps) Create a searchable database of video content
        5. **AI-Powered Q&A**: (Next Steps) Ask questions and get answers based on the actual video content
        
        ### Example Questions You Could Ask (Once fully implemented):
        - "How do I set up a Python virtual environment?"
        - "What are the best practices for web development?"
        - "Can you summarize the main points about machine learning?"
        
        The AI will search through all the processed videos and provide answers with source links.
        """)
        
        # Show example interface
        st.subheader("💬 Question Interface (Preview)")
        query = st.text_input(
            "What would you like to know?",
            placeholder="e.g., How do I deploy a web application?",
            disabled=True
        )
        st.button("🔍 Ask", disabled=True, help="Available once processing is complete")

if __name__ == "__main__":
    main()