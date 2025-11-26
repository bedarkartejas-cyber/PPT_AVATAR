# Anam Onboarding Assistant Agent

This LiveKit agent showcases **Anam's avatar** powered by **Gemini's AI** for intelligent onboarding assistance. It demonstrates Anam's flexibility to integrate custom LLMs and unique capabilities like screen share analysis.

## Features

- **Anam Avatar**: Beautiful visual presence with natural lip-sync and movements
- **Custom LLM (Gemini)**: Intelligent conversation powered by Gemini 2.5 Flash
- **Screen Share Analysis**: Watches the user's screen and analyzes it with Gemini Vision
- **Contextual Guidance**: Provides specific help based on what the user is looking at
- **Onboarding Expertise**: Trained to guide users through employee onboarding forms and processes

## Architecture

```
User Input (Voice + Screen Share)
    ↓
Gemini Live (Multimodal: Audio + Vision Input)
    ↓
Gemini 2.0 LLM (processes and decides response)
    ↓
Text Output → Anam Avatar (TTS + Video)
    ↓
User sees/hears Maya the assistant
```

**Key Features:**
- **Gemini Live**: Handles audio input (built-in STT) and vision (screen analysis) together
- **Low Latency**: Single AI service for input processing reduces hops
- **Multimodal Understanding**: Gemini sees audio + video context simultaneously
- **Anam Avatar**: Provides beautiful TTS and video output

## Prerequisites

Before running the agent, you'll need:

1. **Python 3.10 or higher**
2. **LiveKit Account**: Sign up at [livekit.io](https://livekit.io) to get your credentials
3. **Anam API Key**: Sign up at [Anam Dashboard](https://dashboard.anam.dev) to get your API key
4. **Google Gemini API Key**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey) (used for both LLM and STT)

## Installation

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

Copy the `env.example` file to `.env` and fill in your credentials:

```bash
cp env.example .env
```

Edit `.env` with your actual credentials:

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
ANAM_API_KEY=your_anam_api_key
ANAM_AVATAR_ID=your_persona_id  # Required: Your persona ID from Anam dashboard
GEMINI_API_KEY=your_gemini_api_key  # For Gemini Live (audio+vision input + LLM)
```

## Running the Agent

There are two ways to run the agent:

### Option 1: Using LiveKit CLI (Recommended)

If you have the LiveKit CLI installed:

```bash
python agent.py dev
```

This will:
- Connect to your LiveKit server
- Wait for rooms to be created
- Automatically join when a participant connects

### Option 2: Direct Python Execution

For development and testing:

```bash
python agent.py
```

## Usage

1. **Start the agent** using one of the methods above
2. **Open the frontend** in your browser (typically at `http://localhost:3000`)
3. **Select your environment** (dev/prod) and start the call
4. **Open the onboarding form** in a new tab (`/onboarding-demo`)
5. **Share your screen** (select the tab with the onboarding form)
6. **Interact with the agent** - it will guide you through the onboarding process

## How It Works

### Agent Architecture

The agent consists of several components:

1. **Anam Avatar**: Provides visual presence and voice synthesis with lip-sync
2. **Gemini Live (Multimodal Live API)**: Handles audio input, vision processing, and intelligent conversation
3. **Gemini 2.0 Flash**: Powers the LLM decision-making with multimodal understanding
4. **LiveKit**: Manages real-time communication and media tracks

This architecture demonstrates **Anam's flexibility** - you can use any LLM (Gemini, GPT-4, Claude, custom models) while still getting Anam's beautiful avatar experience.

### Screen Share Processing

When a user shares their screen:

1. The agent subscribes to the screen share video track
2. Frames are extracted and sampled (every 2 seconds by default)
3. Frames are sent to Gemini's vision model for analysis
4. Gemini identifies what the user is looking at and provides guidance
5. The agent speaks the guidance back to the user

### Prompt Engineering

The agent uses a specialized system prompt that:
- Positions it as a friendly HR onboarding assistant
- Instructs it to provide step-by-step guidance
- Keeps responses concise for voice interaction
- Focuses on the specific context of employee onboarding

## Configuration

You can customize the agent's behavior by modifying these parameters in `agent.py`:

- `frame_analysis_interval`: How often to analyze screen frames (default: 2 seconds)
- `initial_context`: The system prompt that defines the agent's personality and role
- **Deepgram Flux turn detection** (optional):
  - `eot_threshold`: Confidence required for EndOfTurn (default: 0.7, range: 0.5-0.9)
  - `eager_eot_threshold`: Enable early response generation (range: 0.3-0.9)
  - `eot_timeout_ms`: Max silence before forcing EndOfTurn (default: 5000ms, range: 500-10000ms)

## Troubleshooting

### Agent won't connect

- Verify your `LIVEKIT_URL`, `LIVEKIT_API_KEY`, and `LIVEKIT_API_SECRET` are correct
- Check that your LiveKit server is accessible
- Ensure you're not behind a firewall blocking WebSocket connections

### No voice response

- Verify your `GEMINI_API_KEY` is valid
- Check the agent logs for errors
- Ensure your microphone permissions are enabled in the browser

### Screen share not working

- Make sure you're sharing the correct tab/window
- Check browser permissions for screen sharing
- Verify the agent logs show "Screen share track detected!"

### Gemini API errors

- Check your API key is valid and has access to Gemini 2.0
- Verify you haven't exceeded your API quota
- Review the agent logs for specific error messages

## Development

### Adding New Capabilities

To extend the agent's capabilities:

1. **Modify the system prompt** in `initial_context` to add new behaviors
2. **Adjust frame processing** in `process_frame()` to change analysis frequency
3. **Add new handlers** for different types of tracks or events

### Testing Locally

For local development:

1. Run the agent with increased logging: `LOG_LEVEL=DEBUG python agent.py dev`
2. Use LiveKit's [Meet example](https://meet.livekit.io) to test connectivity
3. Check the agent logs for detailed information about track subscriptions and analysis

## Architecture Notes

### Gemini Vision Integration

The current implementation uses Gemini's vision capabilities to analyze screen share frames. This is ideal for:

- Understanding form layouts and content
- Detecting errors or incomplete fields
- Providing context-aware guidance

### Scaling Considerations

For production deployments:

- Consider adding frame caching to reduce API calls
- Implement rate limiting for Gemini API requests
- Use LiveKit's [Cloud](https://livekit.io/cloud) for reliable infrastructure
- Monitor API usage and costs

## Resources

- [LiveKit Agents Documentation](https://docs.livekit.io/agents)
- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [LiveKit Python SDK](https://github.com/livekit/python-sdks)
- [LiveKit Components](https://github.com/livekit/components-js)

## Support

For issues or questions:

- LiveKit: [LiveKit Community Slack](https://livekit.io/join-slack)
- Gemini: [Google AI Forum](https://discuss.ai.google.dev)
- This project: Open an issue on GitHub

