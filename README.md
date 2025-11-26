# AI Onboarding Assistant - Anam + LiveKit + Gemini Demo

This demo showcases **Anam's LiveKit integration** with a custom use case for employee onboarding. It combines Anam's avatar technology with Gemini's AI capabilities to create an intelligent, visual onboarding assistant.

**✨ Key Demo Features:**
- 👤 **Anam avatar** for natural visual presence and voice
- 🧠 **Gemini LLM** powering intelligent conversation
- 🖥️ **Screen share analysis** using Gemini's vision capabilities  
- 📋 Interactive onboarding form that the AI helps you complete
- 🤖 Context-aware guidance based on what's visible on your screen

**Why this demo matters:** It demonstrates Anam's flexibility to integrate custom LLMs and unique use cases (like screen analysis) that aren't available out-of-the-box.

Also available for:
[Android](https://github.com/livekit-examples/agent-starter-android) • [Flutter](https://github.com/livekit-examples/agent-starter-flutter) • [Swift](https://github.com/livekit-examples/agent-starter-swift) • [React Native](https://github.com/livekit-examples/agent-starter-react-native)

<picture>
  <source srcset="./.github/assets/readme-hero-dark.webp" media="(prefers-color-scheme: dark)">
  <source srcset="./.github/assets/readme-hero-light.webp" media="(prefers-color-scheme: light)">
  <img src="./.github/assets/readme-hero-light.webp" alt="App screenshot">
</picture>

### Features:

- **Anam Avatar Integration** - Visual avatar with lip-sync and natural movements
- **Custom LLM (Gemini)** - Demonstrates using your own AI model with Anam
- **Screen sharing with AI vision** - Gemini analyzes what's on your screen
- **Employee onboarding demo** - Interactive multi-step form
- **Context-aware assistance** - AI provides specific help based on screen content
- **Audio visualization** and level monitoring
- **Light/dark theme** switching with system preference detection
- **Customizable branding** - colors, logos, and UI text via configuration

This demo is built with Next.js (frontend), Python (agent backend), Anam (avatar), and Gemini (AI), and is free for you to use or modify as you see fit.

### Project structure

```
livekit-onboarding-demo/
├── app/                          # Next.js frontend
│   ├── (app)/                    # Main app route
│   ├── api/                      # API routes (token generation)
│   ├── onboarding-demo/          # Demo onboarding form page
│   ├── components/
│   ├── fonts/
│   ├── globals.css
│   └── layout.tsx
├── agent/                        # Python agent backend
│   ├── agent.py                  # Main agent logic
│   ├── requirements.txt          # Python dependencies
│   ├── env.example               # Environment variables template
│   ├── Dockerfile                # Docker configuration
│   └── README.md                 # Agent documentation
├── components/
│   ├── livekit/                  # LiveKit UI components
│   ├── ui/                       # shadcn/ui components
│   ├── onboarding-form.tsx       # Interactive onboarding form
│   ├── app.tsx
│   ├── session-view.tsx
│   └── welcome.tsx
├── hooks/
├── lib/
├── public/
└── package.json
```

## Getting started

This demo requires running both a **frontend** (Next.js) and a **backend agent** (Python). Follow these steps to get everything running:

### 1. Frontend Setup

Install and run the Next.js frontend:

```bash
pnpm install
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 2. Agent Setup

The agent backend handles voice interaction and screen analysis with Gemini.

```bash
cd agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the `agent/` directory (copy from `env.example`) with your credentials:

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
GEMINI_API_KEY=your_gemini_api_key
```

Run the agent:

```bash
python agent.py dev
```

For detailed agent setup instructions, see [agent/README.md](./agent/README.md).

### 3. Try the Demo

1. Open the frontend at [http://localhost:3000](http://localhost:3000)
2. Click the link to open the onboarding form in a new tab
3. Start the call
4. Share your screen (select the tab with the onboarding form)
5. The AI assistant will guide you through the onboarding process!

### Getting API Keys

- **LiveKit**: Sign up at [livekit.io](https://livekit.io) for free API credentials
- **Anam**: Get your API key from [Anam Dashboard](https://dashboard.anam.dev)
- **Gemini**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey) (for Gemini Live)

## Configuration

### Frontend Configuration

Customize the app's appearance and features in [`app-config.ts`](./app-config.ts):

```ts
export const APP_CONFIG_DEFAULTS = {
  companyName: 'Anam',
  pageTitle: 'AI Onboarding Assistant',
  pageDescription: 'Your personal AI assistant for seamless employee onboarding',
  supportsChatInput: true,
  supportsVideoInput: false,
  supportsScreenShare: true,  // Required for this demo
  startButtonText: 'Start Onboarding',
  agentName: 'Onboarding Assistant',
};
```

### Environment Variables

#### Frontend (`.env.local`)

Create a `.env.local` file in the project root:

```env
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=wss://your-livekit-server-url
```

#### Agent (`agent/.env`)

Create a `.env` file in the `agent/` directory:

```env
LIVEKIT_URL=wss://your-livekit-server-url
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
ANAM_API_KEY=your_anam_api_key
ANAM_AVATAR_ID=your_persona_id  # Required: Your persona ID from Anam dashboard
GEMINI_API_KEY=your_gemini_api_key  # For Gemini Live
```

## How It Works

This demo showcases Anam's flexibility with custom AI and unique use cases:

1. **User joins** the call via the Next.js frontend
2. **Anam avatar agent** connects to the LiveKit room (Python backend)
3. **Avatar appears** - Users see Maya, the onboarding assistant
4. **User shares screen** showing the onboarding form
5. **Gemini vision analyzes** video frames to understand what's on screen
6. **Gemini LLM decides** what guidance to provide
7. **Anam avatar speaks** the response with natural lip-sync
8. **Natural conversation** flows as user completes onboarding

### Key Technologies

- **Anam**: Avatar visual presence, lip-sync, and TTS
- **LiveKit**: Real-time communication infrastructure  
- **Gemini 2.5 Flash**: Custom LLM for conversation + vision analysis
- **Deepgram Flux**: Latest ASR model with integrated turn-taking (~260ms latency)
- **Next.js**: Modern React framework for the frontend
- **Python Agents SDK**: Backend agent framework

### Architecture Highlight

This demo uses **Anam as the TTS** (avatar video + voice) while **Gemini powers the intelligence**. This showcases that Anam can integrate with any LLM, making it perfect for:

- Custom AI models trained on your data
- Specialized use cases (like screen analysis)
- Cost optimization with different LLM providers
- Advanced features not in standard avatar platforms

## Use Cases

This demo is specifically designed for employee onboarding, but the same pattern can be applied to many scenarios:

- 📚 **Educational tutoring** - Help students with homework by seeing their work
- 🏥 **Healthcare onboarding** - Guide patients through medical forms
- 💰 **Financial services** - Assist with account opening and KYC processes
- 🛠️ **Technical support** - See customer's screen and provide visual guidance
- 📝 **Document review** - Help users fill out complex legal or compliance forms

The key is combining **voice interaction** with **visual understanding** for a natural, helpful experience.

## Deployment

### Frontend

Deploy the Next.js frontend to Vercel, Netlify, or any platform supporting Next.js:

```bash
pnpm build
pnpm start
```

### Agent

The Python agent can be deployed to:

- **Docker**: Use the included `Dockerfile`
- **Cloud VMs**: Deploy to AWS EC2, Google Cloud, Azure, etc.
- **Container platforms**: Kubernetes, ECS, Cloud Run, etc.

See [agent/README.md](./agent/README.md) for detailed deployment instructions.

## Troubleshooting

### Agent won't connect
- Verify your LiveKit credentials are correct
- Check that the agent and frontend use the same `LIVEKIT_URL`
- Ensure WebSocket connections aren't blocked by firewall

### Screen share not detected
- Confirm you're sharing the correct tab/window
- Check browser permissions for screen sharing
- Look for "Screen share track detected!" in agent logs

### Gemini API errors
- Verify your `GEMINI_API_KEY` is valid
- Check you have access to Gemini 2.0
- Monitor your API quota and rate limits

## Contributing

This demo is open source and we welcome contributions! Please open a PR or issue through GitHub, and don't forget to join us in the [LiveKit Community Slack](https://livekit.io/join-slack)!

## Resources

- [LiveKit Documentation](https://docs.livekit.io)
- [LiveKit Agents Guide](https://docs.livekit.io/agents)
- [Google Gemini API](https://ai.google.dev/docs)
- [Agent Setup Guide](./agent/README.md)
