# import asyncio
# import logging
# import os
# import json
# import sys
# import time # NEW: For debouncing
# from pathlib import Path
# from dotenv import load_dotenv

# # --- 1. SETUP PATHS ---
# CURRENT_DIR = Path(__file__).parent.absolute()
# PARENT_DIR = CURRENT_DIR.parent
# sys.path.append(str(PARENT_DIR))

# if (CURRENT_DIR / ".env").exists():
#     load_dotenv(CURRENT_DIR / ".env")
# elif (PARENT_DIR / ".env").exists():
#     load_dotenv(PARENT_DIR / ".env")

# from livekit import rtc
# from livekit.agents import (
#     Agent,
#     AgentSession,
#     AutoSubscribe,
#     JobContext,
#     WorkerOptions,
#     cli,
#     function_tool,
# )
# from livekit.agents.voice import VoiceActivityVideoSampler, room_io
# from livekit.plugins import anam, google

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("ppt-agent")

# # Global variable to prevent slide spamming
# last_slide_time = 0

# # --- 2. LOAD DATA ---
# def get_presentation_data():
#     json_path = PARENT_DIR / "presentation.json"
#     if json_path.exists():
#         try:
#             with open(json_path, "r", encoding="utf-8") as f:
#                 data = json.load(f)
#                 context_str = json.dumps(data, indent=2, ensure_ascii=False)
#                 return context_str, len(data)
#         except Exception as e:
#             logger.error(f"Error reading JSON: {e}")
#     return None, 0

# # --- 3. BUILD PROMPT (Optimized for Stability) ---
# def build_instructions():
#     context_str, slide_count = get_presentation_data()
    
#     if context_str:
#         intro = f"Namaste! I have loaded {slide_count} slides. I am ready. Shall I start?"
#         source_material = f"### PRESENTATION CONTENT:\n{context_str}"
#     else:
#         intro = "Namaste! Please upload a presentation."
#         source_material = "No presentation loaded."

#     instructions = f"""
#     You are **Dia**, an energetic Indian Presentation Assistant.

#     {source_material}

#     ### YOUR GOAL:
#     Present every slide from start to finish without crashing.

#     ### CRITICAL PERFORMANCE RULES (MUST FOLLOW):
#     1.  **BE CONCISE:** Explain each slide in **MAXIMUM 3 SENTENCES**. Do not give long speeches. Long speeches cause connection errors.
#     2.  **ONE TOPIC PER TURN:** Say the 3 sentences, then IMMEDIATELY ask: "Shall I move to the next?"
#     3.  **NO REPEATS:** Do not repeat the same point.

#     ### TOOLS:
#     - `update_slide(slide_number)`: Changes the screen.

#     ### FLOW:
#     1.  User says "Start" -> Call `update_slide(1)` -> Explain Slide 1 (3 sentences).
#     2.  Ask "Next slide?" -> User says "Yes" -> Call `update_slide(2)` -> Explain Slide 2.
#     3.  Repeat until done.
#     """
#     return instructions, intro

# async def entrypoint(ctx: JobContext):
#     logger.info(f"🚀 Connecting to room: {ctx.room.name}")
#     await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)

#     try:
#         anam_api_key = os.environ.get("ANAM_API_KEY")
#         gemini_api_key = os.environ.get("GEMINI_API_KEY")
#         avatar_id = os.environ.get("ANAM_AVATAR_ID")

#         if not all([anam_api_key, gemini_api_key, avatar_id]):
#             logger.error("❌ Missing API Keys")
#             return

#         instructions_text, greeting_text = build_instructions()

#         # --- 4. ROBUST TOOL (With Debounce) ---
#         @function_tool
#         async def update_slide(slide_number: int):
#             """Change the visible slide."""
#             global last_slide_time
#             current_time = time.time()
            
#             # Prevent spamming the same slide within 2 seconds
#             if current_time - last_slide_time < 2:
#                 return f"Slide {slide_number} is already active."
            
#             last_slide_time = current_time
#             logger.info(f"📸 SWITCHING TO SLIDE {slide_number}")
            
#             data = json.dumps({
#                 "type": "slide_change", 
#                 "slide_number": slide_number,
#                 "image_url": f"/slides/Slide{slide_number}.jpg"
#             })
            
#             # Send reliably
#             try:
#                 await ctx.room.local_participant.publish_data(payload=data, reliable=True)
#             except Exception as e:
#                 logger.error(f"Failed to send slide signal: {e}")

#             return f"Screen updated to Slide {slide_number}"

#         # Initialize Model
#         llm_model = google.realtime.RealtimeModel(
#             model="gemini-2.5-flash-native-audio-preview-09-2025", 
#             api_key=gemini_api_key,
#             voice="Aoede", 
#             instructions=instructions_text,
#             temperature=0.6,
#         )

#         avatar = anam.AvatarSession(
#             persona_config=anam.PersonaConfig(name="Presenter", avatarId=avatar_id),
#             api_key=anam_api_key,
#             api_url="https://api.anam.ai",
#         )

#         session = AgentSession(
#             llm=llm_model,
#             video_sampler=VoiceActivityVideoSampler(speaking_fps=0.5, silent_fps=0.1),
#             preemptive_generation=True, 
#         )

#         # --- 5. START WITH CRASH PROTECTION ---
#         try:
#             await avatar.start(session, room=ctx.room)
            
#             await session.start(
#                 agent=Agent(
#                     instructions=instructions_text,
#                     tools=[update_slide]
#                 ),
#                 room=ctx.room,
#                 room_input_options=room_io.RoomInputOptions(video_enabled=True),
#             )

#             session.generate_reply(instructions=f"Say exactly: '{greeting_text}'")
#             logger.info("✅ Agent Active")

#             # Universal Keep-Alive
#             shutdown_future = asyncio.Future()
#             @ctx.room.on("disconnected")
#             def on_disconnected(reason):
#                 if not shutdown_future.done():
#                     shutdown_future.set_result(None)
            
#             await shutdown_future

#         except asyncio.CancelledError:
#             logger.info("Agent task cancelled")
#         except Exception as inner_e:
#             # Swallow the ChanClosed error so the script doesn't exit
#             if "ChanClosed" in str(inner_e):
#                 logger.warning("⚠️ Ignored Audio Channel Closure")
#             else:
#                 logger.error(f"⚠️ Session Error: {inner_e}")

#     except Exception as e:
#         logger.error(f"❌ Critical Error: {e}", exc_info=True)

# if __name__ == "__main__":
#     cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
    
    
    
    
    
    
    
    
    
    
    
import asyncio
import logging
import os
import json
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# --- 1. SETUP PATHS ---
CURRENT_DIR = Path(__file__).parent.absolute()
PARENT_DIR = CURRENT_DIR.parent
sys.path.append(str(PARENT_DIR))

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
    function_tool,
)
from livekit.agents.voice import VoiceActivityVideoSampler, room_io
from livekit.plugins import anam, google

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ppt-agent")

last_slide_time = 0

# --- 2. LOAD DATA ---
def get_presentation_data():
    json_path = PARENT_DIR / "presentation.json"
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                context_str = json.dumps(data, indent=2, ensure_ascii=False)
                return context_str, len(data)
        except Exception as e:
            logger.error(f"Error reading JSON: {e}")
    return None, 0

# --- 3. BUILD PROMPT ---
def build_instructions():
    context_str, slide_count = get_presentation_data()
    
    if context_str:
        intro = f"Namaste! I have loaded {slide_count} slides. I am ready. Shall I start?"
        source_material = f"### PRESENTATION CONTENT:\n{context_str}"
    else:
        intro = "Namaste! Please upload a presentation."
        source_material = "No presentation loaded."
        slide_count = 0

    instructions = f"""
    You are **Dia**, a professional Indian Presentation Assistant.

    {source_material}
    
    **TOTAL SLIDES:** {slide_count}

    ### YOUR STRICT BEHAVIOR LOOP:
    1.  **EXPLAIN:** Explain the current slide in **MAX 2 SENTENCES**. Brief explanations prevent errors.
    2.  **CHECK PROGRESS:**
        - **IF** this is NOT the last slide (Slide Number < {slide_count}):
            - Ask exactly: **"Shall I move to the next slide?"**
            - **STOP TALKING.** Wait for the user to say "Yes".
            - When user says "Yes", call `update_slide(current + 1)`.
        - **IF** this IS the last slide (Slide Number == {slide_count}):
            - Say exactly: **"That concludes the presentation. Do you have any questions?"**
            - **STOP TALKING.** Wait for questions.

    ### RULES:
    - Never change slides without confirmation.
    - Keep it short.
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
            logger.error("❌ Missing API Keys")
            return

        instructions_text, greeting_text = build_instructions()

        # --- 4. TOOL DEFINITION ---
        @function_tool
        async def update_slide(slide_number: int):
            """Change the visible slide."""
            global last_slide_time
            current_time = time.time()
            
            if current_time - last_slide_time < 2:
                return f"Slide {slide_number} is already active."
            
            last_slide_time = current_time
            logger.info(f"📸 SWITCHING TO SLIDE {slide_number}")
            
            # Send double signal for reliability
            for _ in range(2):
                data = json.dumps({
                    "type": "slide_change", 
                    "slide_number": slide_number,
                    "image_url": f"/slides/Slide{slide_number}.jpg"
                })
                try:
                    await ctx.room.local_participant.publish_data(payload=data, reliable=True)
                except:
                    pass
                await asyncio.sleep(0.1)

            return f"Screen updated to Slide {slide_number}"

        # Initialize Model
        llm_model = google.realtime.RealtimeModel(
            model="gemini-2.5-flash-native-audio-preview-09-2025", 
            api_key=gemini_api_key,
            voice="Aoede", 
            instructions=instructions_text,
            temperature=0.6,
        )

        avatar = anam.AvatarSession(
            persona_config=anam.PersonaConfig(name="Presenter", avatarId=avatar_id),
            api_key=anam_api_key,
            api_url="https://api.anam.ai",
        )

        session = AgentSession(
            llm=llm_model,
            # *** CRITICAL FIX FOR CRASHES ***
            # 1. speaking_fps=0 means "Don't stress the video encoder"
            video_sampler=VoiceActivityVideoSampler(speaking_fps=0, silent_fps=0),
            # 2. preemptive_generation=False stops the "Buffer Overflow"
            preemptive_generation=False, 
        )

        try:
            await avatar.start(session, room=ctx.room)
            
            await session.start(
                agent=Agent(
                    instructions=instructions_text,
                    tools=[update_slide]
                ),
                room=ctx.room,
                room_input_options=room_io.RoomInputOptions(video_enabled=True),
            )

            session.generate_reply(instructions=f"Say exactly: '{greeting_text}'")
            logger.info("✅ Agent Active")

            # Universal Keep-Alive
            shutdown_future = asyncio.Future()
            @ctx.room.on("disconnected")
            def on_disconnected(reason):
                if not shutdown_future.done():
                    shutdown_future.set_result(None)
            
            await shutdown_future

        except Exception as inner_e:
            err_str = str(inner_e)
            if "RpcError" in err_str or "ChanClosed" in err_str or "Connection timeout" in err_str:
                logger.warning(f"⚠️ Network Glitch Ignored: {inner_e}")
            else:
                logger.error(f"⚠️ Session Error: {inner_e}")

    except Exception as e:
        logger.error(f"❌ Critical Error: {e}", exc_info=True)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))