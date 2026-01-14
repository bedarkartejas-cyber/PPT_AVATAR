import asyncio
import logging
import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# --- 1. SETUP PATHS & LOGGING ---
CURRENT_DIR = Path(__file__).parent.absolute()
PARENT_DIR = CURRENT_DIR.parent
sys.path.append(str(PARENT_DIR))

# Load .env from agent folder or root
if (CURRENT_DIR / ".env").exists():
    load_dotenv(CURRENT_DIR / ".env")
elif (PARENT_DIR / ".env").exists():
    load_dotenv(PARENT_DIR / ".env")

from livekit import rtc
from livekit.agents import (
    Agent,
    AgentSession,
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
)
from livekit.agents.voice import VoiceActivityVideoSampler, room_io
from livekit.plugins import anam, google

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ppt-agent")

# --- 2. LOAD PRESENTATION DATA ---
def get_presentation_data():
    """Reads the JSON file created by the server"""
    json_path = PARENT_DIR / "presentation.json"
    
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Convert list/dict to string for the AI prompt
                context_str = json.dumps(data, indent=2, ensure_ascii=False)
                return context_str, len(data)
        except Exception as e:
            logger.error(f"Error reading JSON: {e}")
    return None, 0

# --- 3. SYSTEM INSTRUCTIONS ---
def build_instructions():
    context_str, slide_count = get_presentation_data()
    
    if context_str:
        intro = f"I have loaded your presentation with {slide_count} slides. I am ready to present. Shall I start with the first slide?"
        source_material = f"### PRESENTATION CONTENT:\n{context_str}"
    else:
        intro = "Hello! I am ready to present, but I don't see a presentation file yet. Please upload your PPT."
        source_material = "No presentation loaded yet."

    instructions = f"""
    You are an **Expert Presentation Speaker**.

    {source_material}

    ### YOUR JOB:
    1.  **Explain in Detail:** Do not just read the text. Explain the concepts on each slide like a professor or professional speaker.
    2.  **Navigation:** If the user says "Next", move to the content of the next slide.
    3.  **Q&A:** Answer any questions the user has about the specific slide content.

    ### CRITICAL RULES:
    - **Voice Style:** Professional, engaging, and clear.
    - **Start:** Immediately welcome the user and confirm you have the slides (if loaded).
    """
    return instructions, intro

async def entrypoint(ctx: JobContext):
    logger.info(f"🚀 Connecting to room: {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)

    try:
        anam_api_key = os.environ.get("ANAM_API_KEY")
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        avatar_id = os.environ.get("ANAM_AVATAR_ID")

        if not all([anam_api_key, gemini_api_key, avatar_id]):
            logger.error("❌ Missing API Keys in .env file")
            return

        # Load fresh instructions
        instructions_text, greeting_text = build_instructions()

        # --- FIX: USE THE CORRECT MODEL NAME ---
        # gemini-2.0-flash-exp is the current stable experimental version for audio
        llm = google.realtime.RealtimeModel(
            model="gemini-2.5-flash-native-audio-preview-09-2025", 
            api_key=gemini_api_key,
            voice="Aoede", 
            instructions=instructions_text,
            temperature=0.8,
        )

        avatar = anam.AvatarSession(
            persona_config=anam.PersonaConfig(name="Presenter", avatarId=avatar_id),
            api_key=anam_api_key,
            api_url="https://api.anam.ai",
        )

        session = AgentSession(
            llm=llm,
            video_sampler=VoiceActivityVideoSampler(speaking_fps=0.5, silent_fps=0.1),
            preemptive_generation=True, 
        )

        await avatar.start(session, room=ctx.room)
        await session.start(
            agent=Agent(instructions=instructions_text),
            room=ctx.room,
            room_input_options=room_io.RoomInputOptions(video_enabled=True),
        )

        # Force the greeting to ensure audio starts
        session.generate_reply(instructions=f"Say exactly: '{greeting_text}'")
        
        logger.info("✅ Agent Active & Speaking")

    except Exception as e:
        logger.error(f"❌ Runtime Error: {e}", exc_info=True)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))