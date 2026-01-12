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
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL_SMART)
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
                time.sleep(1) # Faster polling
                video_file = genai.get_file(video_file.name)

            if video_file.state.name == "FAILED":
                raise ValueError("Video processing failed by Gemini.")

            logger.info("Video is active. Generating content...")

            # 4. Generate Advanced "Deep Seek" Diagnosis
            prompt = f"""
            You are **Deep Seek**, an elite AI Diagnostic Engine for electromechanical devices.
            
            ## MISSION
            Perform a forensic analysis of the provided video footage to identify faults and prescribe a repair.
            
            ## USER CONTEXT
            "{context}"
            
            ## ANALYSIS PROTOCOL (Chain of Thought):
            1. **Visual Scan:** Scan frame-by-frame for physical damage, loose components, or irregular movement.
            2. **Audio Scan:** Analyze audio patterns for grinding, buzzing, or beeping (phantom simulation).
            3. **Hypothesis Generation:** Formulate 3 possible root causes.
            4. **Selection:** Choose the most probable cause based on evidence.
            
            ## OUTPUT REPORT (Markdown):
            
            ### 🚨 Executive Summary
            - **Fault Status:** [CRITICAL / WARNING / INFO]
            - **Confidence Score:** [0-100]%
            - **Primary Issue:** [Concise diagnosis]
            
            ### 🕵️ Forensic Observations
            - **[00:0X] Visual:** [Detailed observation]
            - **[00:0X] Audio:** [Detailed observation]
            
            ### 🧠 Root Cause Analysis
            > **Diagnosis:** [Detailed explanation of what failed and why]
            
            ### 🛠️ Repair Procedure
            **Difficulty:** [1-5 Wrenches]
            **Estimated Time:** [Minutes]
            
            **Steps:**
            1. [Step 1]
            2. [Step 2]
            3. [Step 3]
            
            **Parts Likely Needed:**
            - [Part Name] (Search SKU: [Generate a generic search term])
            
            ---
            *AI Diagnostic Confidence: High. Always disconnect power before servicing.*
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
