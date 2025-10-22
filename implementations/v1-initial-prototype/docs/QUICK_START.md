# Quick Start Guide – Gemini Live Professor Console

This project wraps Google’s Gemini Live Web Console with a Neil A. Morgan persona and animated avatar. Follow this guide to get running quickly and understand the major controls.

## 1. Prerequisites

- Node.js 18+ (Homebrew install example: `brew install node`)
- A Gemini API key with Live access
- macOS microphone and browser (Chrome recommended)

## 2. First-Time Setup

1. **Clone & install**
   ```bash
   git clone https://github.com/google-gemini/live-api-web-console.git
   cd live-api-web-console
   npm install
   ```
2. **Configure env**
   ```bash
   cp .env .env.local
   echo "REACT_APP_GEMINI_API_KEY='<YOUR_KEY>'" > .env.local
   ```
   Keep the key out of Git; only `.env.local` should contain it.

## 3. Run the Dev Server

```bash
npm start
```

Your browser opens `http://localhost:3000`. If something already uses port 3000, stop that process or run `PORT=3001 npm start`.

## 4. Using the Console

1. **Allow microphone access** when prompted.
2. **Press the green Play button** in the Control Tray to establish a Live session.
3. **Tap the mic icon** to start/stop sending audio. Speak normally; Gemini replies with low-latency audio.
4. The bottom-right avatar mouth opens while the model is speaking.

### Persona & Voice Defaults

- System instruction: Neil A. Morgan persona (authoritative marketing strategist).
- Voice: `Fenrir` (male) prebuilt voice.
- Response modality: `AUDIO`.

These defaults are baked into `src/hooks/use-live-api.ts` (`baseConfig`). Clearing browser storage or opening an incognito window restores them.

## 5. Settings Dialog

Open the gear icon before connecting to the session. You can:
- Inspect or tweak the system instruction (textarea).
- Choose response modalities (AUDIO/TEXT) with persistence in localStorage.
- Switch voices (select component). Selecting a new voice updates the config while preserving the persona.

Changes apply on the next connection. Once connected, all fields are locked until you disconnect.

## 6. Troubleshooting

- **Mic errors**: Ensure the browser has mic permissions. Revoke any blocks in Site Settings.
- **Persona reset**: If settings look wrong, click the gear icon and confirm the instruction text. Use an incognito window to avoid cached localStorage overrides.
- **Altair tool panel**: When the logger requests charts, Gemini uses the provided `render_altair` function without altering the persona/voice.
- **Port conflicts**: Run `pkill -f react-scripts` to stop lingering dev servers.

## 7. Customization

- Modify the persona or default voice in `src/hooks/use-live-api.ts` (`baseConfig`).
- Adjust the avatar style in `src/Avatar.tsx` (inline styles).
- Dispatch logic for speech detection lives in `src/lib/genai-live-client.ts`.

Happy testing! Ensure you commit only source changes—never your API key or `.env.local`.

