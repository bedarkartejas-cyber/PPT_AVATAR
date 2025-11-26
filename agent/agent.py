"""
LiveKit Agent with Anam Avatar + Gemini Live for Onboarding Assistant

- Anam avatar for visual presence and TTS
- Gemini Live for multimodal conversation (audio + screen share vision)
- Browser control tools for form filling
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from livekit import rtc  # noqa: E402
from livekit.agents import (  # noqa: E402
    Agent,
    AgentSession,
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    function_tool,
)
from livekit.agents.voice import VoiceActivityVideoSampler, room_io  # noqa: E402
from livekit.plugins import anam, google  # noqa: E402

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Reduce noise from verbose libraries
for lib in ["websockets", "httpx", "httpcore"]:
    logging.getLogger(lib).setLevel(logging.WARNING)

# Global room reference for function tools
_current_room: Optional[rtc.Room] = None


async def send_control_command(command: str, data: dict) -> None:
    """Send a control command to the frontend via data channel."""
    if _current_room is None:
        logger.error("Room not initialized")
        return

    message = json.dumps({"type": command, **data})
    await _current_room.local_participant.publish_data(
        message.encode("utf-8"),
        reliable=True,
        topic="browser-control",
    )
    logger.info(f"→ {command}: {data}")


@function_tool
async def fill_form_field(field_identifier: str, value: str) -> str:
    """Fill in a form field on the current page.

    Args:
        field_identifier: The field to fill (e.g. "Full Name", "Email Address")
        value: The value to enter into the field

    Returns:
        A confirmation message
    """
    logger.info(f"🔧 fill_form_field({field_identifier}, {value})")
    try:
        await send_control_command(
            "fill_field", {"field": field_identifier, "value": value}
        )
        return "ok"
    except asyncio.CancelledError:
        logger.warning(f"⚠️ fill_form_field cancelled: {field_identifier}")
        raise


@function_tool
async def click_element(element_description: str) -> str:
    """Click a button or link on the page.

    Args:
        element_description: Button/element text (e.g. "Submit", "Next")

    Returns:
        A confirmation message
    """
    logger.info(f"🔧 click_element({element_description})")
    try:
        await send_control_command("click", {"element": element_description})
        return "ok"
    except asyncio.CancelledError:
        logger.warning(f"⚠️ click_element cancelled: {element_description}")
        raise


async def entrypoint(ctx: JobContext):
    """Main entry point for the agent."""
    logger.info("🚀 Agent starting...")

    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    logger.info(f"✅ Connected to room: {ctx.room.name}")

    global _current_room
    _current_room = ctx.room

    # Agent instructions - concise and explicit about form fields
    instructions = (
        "You are Maya, a friendly HR onboarding assistant. "
        "You can see the user's screen share.\n\n"
        "THE FORM HAS THESE 6 FIELDS (fill ALL before submitting):\n"
        "1. Full Name\n"
        "2. Email Address\n"
        "3. Phone Number\n"
        "4. Department\n"
        "5. Job Title\n"
        "6. Start Date\n\n"
        "Tools:\n"
        "- fill_form_field(field_name, value) - use EXACT field names above\n"
        "- click_element('Submit') - ONLY after ALL 6 fields are filled\n\n"
        "IMPORTANT: You MUST fill ALL 6 fields before clicking Submit."
    )

    try:
        # Get API keys
        anam_api_key = os.environ.get("ANAM_API_KEY")
        if not anam_api_key:
            raise ValueError("ANAM_API_KEY not set")

        gemini_api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get(
            "GOOGLE_API_KEY"
        )
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not set")

        avatar_id = os.environ.get("ANAM_AVATAR_ID") or os.environ.get(
            "ANAM_PERSONA_ID"
        )
        if not avatar_id:
            raise ValueError("ANAM_AVATAR_ID or ANAM_PERSONA_ID not set")

        # Create Gemini Live model
        llm = google.realtime.RealtimeModel(
            model="gemini-2.0-flash-exp",
            api_key=gemini_api_key,
            voice="Aoede",
            instructions=instructions,
        )

        # Create Anam Avatar session
        avatar = anam.AvatarSession(
            persona_config=anam.PersonaConfig(name="Maya", avatarId=avatar_id),
            api_key=anam_api_key,
            api_url="https://api.anam.ai",
        )

        # Create agent session with tools
        session = AgentSession(
            llm=llm,
            video_sampler=VoiceActivityVideoSampler(
                speaking_fps=0.2,  # 1 frame every 5 sec when speaking
                silent_fps=0.1,  # 1 frame every 10 sec when silent
            ),
            tools=[fill_form_field, click_element],
        )

        # Start avatar and agent
        await avatar.start(session, room=ctx.room)
        await session.start(
            agent=Agent(instructions=instructions),
            room=ctx.room,
            room_input_options=room_io.RoomInputOptions(video_enabled=True),
        )

        logger.info("✅ Agent ready - Anam avatar + Gemini Live")
        await asyncio.sleep(1.5)

    except Exception as e:
        logger.error(f"Failed to start: {e}")
        raise


if __name__ == "__main__":
    logger.info("Starting agent worker...")
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
