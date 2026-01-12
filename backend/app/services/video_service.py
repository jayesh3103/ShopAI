import logging
import os
import time
import shutil
from pathlib import Path
import google.generativeai as genai
from fastapi import UploadFile
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)

class VideoService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-flash-latest')
        self.upload_dir = Path("temp_videos")
        self.upload_dir.mkdir(exist_ok=True)

    async def analyze_video(self, file: UploadFile, context: str = "") -> str:
        """
        Uploads video to Gemini and asks for a diagnosis.
        """
        temp_file_path = self.upload_dir / file.filename
        
        try:
            # 1. Save locally
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"Saved video locally to {temp_file_path}")

            # 2. Upload to Gemini
            logger.info("Uploading to Gemini...")
            video_file = genai.upload_file(path=temp_file_path)
            logger.info(f"Upload complete: {video_file.name}")

            # 3. Wait for processing
            while video_file.state.name == "PROCESSING":
                logger.info("Waiting for video processing...")
                time.sleep(2)
                video_file = genai.get_file(video_file.name)

            if video_file.state.name == "FAILED":
                raise ValueError("Video processing failed by Gemini.")

            logger.info("Video is active. Generating content...")

            # 4. Generate Advanced Diagnosis
            prompt = f"""
            You are "Deep Seek", an advanced AI Technical Diagnostic Agent.
            Analyze this video footage of a malfunctioning product frame-by-frame.
            
            User Context: "{context}"

            ## MISSION:
            Provide a professional, actionable repair plan.

            ## OUTPUT FORMAT (Markdown):

            ### 🚨 Severity Assessment
            **Severity Score:** [1-10] / 10
            **Status:** [CRITICAL / MODERATE / MINOR]
            **Safety Warning:** [If applicable, e.g., "Disconnect power immediately"]

            ### 🕵️ Visual & Audio Analysis
            - **00:00 - 00:xx**: [Describe exactly what is seen/heard]
            - **Detected Component:** [Name of the part]
            - **Observed Fault:** [Specific symptom, e.g., "Capacitor whine", "Error Code E4"]

            ### 🛠️ Repair Action Plan
            **Tools Required:**
            - [Tool 1]
            - [Tool 2]

            **Step-by-Step Fix:**
            1. [Step 1]
            2. [Step 2]
            
            **Estimated Fix Time:** [e.g., 15 mins]
            **Parts Needed:** [If replacement is likely]

            **Estimated Fix Time:** [e.g., 15 mins]
            **Parts Needed:** [If replacement is likely]

            ---
            *Disclaimer: AI diagnosis. Consulting a professional is recommended for high-voltage devices.*

            **Language Guideline:**
            - If the user's context is in Hindi/Hinglish, output the report in **Hinglish**.
            - Else, default to English.
            """

            response = self.model.generate_content([video_file, prompt])
            
            # Clean up Gemini file (optional, but good practice)
            # genai.delete_file(video_file.name) 
            
            return response.text

        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            return f"❌ Analysis Failed: {str(e)}"
        finally:
            # Cleanup local file
            if temp_file_path.exists():
                os.remove(temp_file_path)
